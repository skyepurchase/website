from io import BufferedRandom
import os, traceback, logging, json, base64, hashlib, hmac

from os import environ
from sys import stdin
from datetime import datetime

from PIL import Image, UnidentifiedImageError
if not hasattr(Image, 'Resampling'):
    # PIL changes after 9.0
    # The server may be different from local development
    Image.Resampling = Image

from urllib.parse import parse_qs
from urllib.parse import unquote
import python_multipart

from typing import Tuple


DOWNLOAD_FOLDER = "/home/atp45/downloads"
NOW = datetime.now()
ITERATIONS = 100000
HASH_ALGO = 'sha256'

with open("/home/atp45/.secrets.json", "r") as f:
    SECRETS = json.loads(f.read())


formatter = logging.Formatter(
    '[%(asctime)s %(levelname)s] %(message)s',
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)
handler = logging.FileHandler("/home/atp45/logs/http_lib")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)


class HttpResponse(Exception):
    def __init__(self, status, text):
        self.status = status
        self.text = text


def format_html(html: str, replacements: dict) -> str:
    for key, value in replacements.items():
        html = html.replace(f"[{key}]", value)

    return html


def render_status(status: int, msg: str) -> None:
    if status > 499:
        logger.warning("HTTP status %s: %s", status, msg)

    try:
        html = open(f"status_template.html", "r").read()
        values = {
            "STATUS": str(status),
            "MESSAGE": msg
        }
        print(f"Status: {status}")
        print("Content-Type: text/html")
        print()
        print(format_html(html, values))
    except Exception as e:
        # Logging for debugging later
        logger.debug("Error displaying HTTP status:\n%s", traceback.format_exc())
        # Let wrap deal with it
        raise e


def generate_token(data: dict) -> str:
    """
    Generate JSON Web Token with the given payload

    Parameters
    ----------
    payload : dict
        The payload as a JSON object

    Returns
    -------
    jwt : str
        The JSON web token as a string
    """
    header: bytes = base64.b64encode(
        json.dumps({
            "alg": "HS256",
            "typ": "JWT"
        }).encode('ascii')
    )
    payload: bytes = base64.b64encode(
        json.dumps(data).encode('ascii')
    )

    secret = SECRETS['JWT_SEED'].encode('utf-8')
    signature: str = hmac.new(
        secret,
        header + '.'.encode('ascii') + payload,
        hashlib.sha256
    ).hexdigest()

    jwt = header.decode('ascii') + '.' + payload.decode('ascii') + '.' + signature

    return jwt


def verify_token(jwt: str) -> Tuple[bool, str, dict]:
    """
    Verify the JSON Web Token returning the error message or JSON payload data

    Parameters
    ----------
    jwt : str
        The JSON Web Token as a string

    Returns
    -------
    success : bool
        If the token was successfully verified
    message : str
        The error message
    data    : dict
        The token payload
    """
    secret = SECRETS["JWT_SEED"].encode('utf-8')
    header, payload, signature = jwt.split('.')

    # Unsafe header decode to verify correct data
    try:
        header_d = json.loads(base64.b64decode(header))
    except json.JSONDecodeError:
        logger.debug(f"Failed to decode header from bytes {base64.b64decode(header).decode('ascii')}")
        return False, "Failed to decode header", {}
    except Exception:
        logger.debug(f"Failed to decode header {header}: {traceback.format_exc()}")
        return False, "Unknown error likely with base64 decoding", {}

    if (
        header_d.get("typ") != "JWT" or
        header_d.get("alg") != "HS256"
    ):
        logger.debug(f"Header validation failed, received {header_d}")
        return False, "Invalid header", {}

    test_sig = hmac.new(
        secret,
        (header + '.' + payload).encode('ascii'),
        hashlib.sha256
    ).hexdigest()

    if test_sig == signature:
        try:
            data = json.loads(base64.b64decode(payload))
        except json.JSONDecodeError:
            logger.debug(f"Failed to decode payload from bytes {base64.b64decode(payload).decode('ascii')}")
            return False, "Failed to decode payload", {}
        except Exception:
            logger.debug(f"Failed to decode payload {payload}: {traceback.format_exc()}")
            return False, "Unknown error likely with base64 decoding", {}

        if "exp" in data:
            if datetime.now() > datetime.fromtimestamp(data["exp"]):
                return False, "Timestamp expired", {}

        return True, "success", data

    return False, "Signatures do not match", {}


def get_cookies() -> dict:
    """
    Retrieve and process the passed cookies

    Returns
    -------
    cookies : dict
        A dictionary of cookies
    """
    cookie_string = os.environ.get('HTTP_COOKIE')

    if cookie_string is None:
        return {}

    cookies = {}
    for cookie in cookie_string.split(';'):
        # Some cookie values with contain '=' T.T
        key, *value = cookie.split('=')
        cookies[key] = "=".join(value)

    return cookies


def params(method: str = "GET") -> dict:
    """
    Parse the incoming data. To simulate end points having specific method types
    the caller has to provide a method and that is checked against.

    POST requests are either decoded as if the input is in plain/text or
    multipart/form-data. None of my sites use anything else but you may want
    to change that.
    """
    # Assert the request method matched expectation
    if 'REQUEST_METHOD' in environ:
        if environ['REQUEST_METHOD'] != method:
            raise HttpResponse(405, f"Expected {method} request but received {environ['REQUEST_METHOD']} request")

    if method == "GET":
        # Courtesy of ellie.clifford.lol provided WTFPL
        return {
            x: None if len(y) == 0 else y[0] if len(y) == 1 else y
            for x, y in parse_qs(
                environ.get("QUERY_STRING", ""),
                keep_blank_values=True,
            ).items()
        }
    if method == "POST":
        # The pain begins
        read_in = stdin.buffer.read()

        # Get the content type
        content_type = environ.get('CONTENT_TYPE', '')

        # And parse accordingly
        if not content_type.startswith('multipart/'):
            raw_data = read_in.decode('utf-8')

            param_data = {}
            for content in raw_data.split("&"):
                s = content.split("=")
                if len(s) != 2:
                    render_status(400, "Invalid input")
                    quit(1)

                param_data[s[0]] = unquote(s[1].replace("+", " "))
        else:
            param_data = {}

            def on_field(field):
                """
                What to do when a field is parsed.
                """
                key = field.field_name.decode('utf-8')
                value = field.value.decode('utf-8')
                param_data[key] = value

            def on_file(file):
                """
                What to do when a file is parsed.
                """
                # Get the filename and byte data
                key = file.field_name.decode('utf-8')
                filename = file.file_name.decode('utf-8')
                file_obj = file.file_object

                if (
                    isinstance(file_obj, BytesIO) and file_obj.getbuffer().nbytes == 0 or
                    isinstance(file_obj, BufferedRandom) and file_obj.tell() == 0
                ):
                    logger.info("No file uploaded. Skipping and continuing with decoding.")
                    return

                file_parts = filename.split('.')
                # At this resolution all file uploads should be unique
                new_filename = f"{''.join(file_parts[:-1])}_{NOW.strftime('%Y%m%d%H%M%S')}.{file_parts[-1]}"
                path = os.path.join(
                    DOWNLOAD_FOLDER, new_filename
                )

                # Decode and save as an image
                # multipart-python does not support mimetypes yet: https://github.com/Kludex/python-multipart/issues/207
                # TODO: don't assume this is an image!!
                try:
                    image = Image.open(file_obj)
                    # Scale images for space
                    width, height = image.size
                    scale = 500 / width
                    image.resize(
                        (500,int(height*scale)),
                        Image.Resampling.LANCZOS
                    )
                    image.save(path)
                except UnidentifiedImageError:
                    logger.warning("Image decoding error, skipping decoding")
                    logger.debug("Image decoding traceback:\n%s", traceback.format_exc())
                    return

                param_data[key] = {
                    'filename': new_filename,
                    'path': path
                }

                file_obj.seek(0)

            try:
                from io import BytesIO

                # Create a byte stream
                data_stream = BytesIO(read_in)

                # supply headers, not always available in environ
                headers = {
                    'Content-Type': content_type.encode('utf-8'),
                    'Content-Length': str(len(read_in)).encode('utf-8')
                }

                python_multipart.parse_form(
                    headers,
                    data_stream,
                    on_field,
                    on_file
                )
            except Exception:
                logger.debug("Multipart parsing failed:\n%s", traceback.format_exc())
                render_status(400, f"Multipart parsing error")
                quit(1)

        logger.info(param_data)
        return param_data

    raise HttpResponse(405, "Invalid REST API call")
