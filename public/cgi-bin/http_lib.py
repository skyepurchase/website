import os
import traceback

from os import environ
from sys import stdin
from datetime import datetime
from PIL import Image, UnidentifiedImageError

from urllib.parse import parse_qs
from urllib.parse import unquote
import python_multipart


LOG_FILE = "/home/atp45/logs/http_lib"
DOWNLOAD_FOLDER = "/home/atp45/downloads"
NOW = datetime.now()


class HttpResponse(Exception):
    def __init__(self, status, text):
        self.status = status
        self.text = text


def format_html(html: str, replacements: dict) -> str:
    for key, value in replacements.items():
        html = html.replace(f"[{key}]", value)

    return html


def render_status(status: int, msg: str) -> None:
    header = "WARN" if status > 499 else "INFO"
    open(LOG_FILE, "a").write(f"[{header}: {NOW.isoformat()}] HTTP status {status}: {msg}\n")

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
        open(LOG_FILE, "a").write(f"[WARN: {NOW.isoformat()}] Error displaying HTTP status:\n{traceback.format_exc()}]\n")
        # Let wrap deal with it
        raise e


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

        open(LOG_FILE, "a").write(
            f"[INFO: {NOW.isoformat()}] Received {len(read_in)} bytes of data\n"
        )

        # Get the content type
        content_type = environ.get('CONTENT_TYPE', '')

        # And parse accordingly
        if not content_type.startswith('multipart/'):
            raw_data = read_in.decode('utf-8')

            open(LOG_FILE, "a").write(f"[INFO: {NOW.isoformat()}] {raw_data}\n")

            get_data = {}
            for content in raw_data.split("&"):
                s = content.split("=")
                if len(s) != 2:
                    render_status(400, "Invalid input")
                    quit(1)

                get_data[s[0]] = unquote(s[1].replace("+", " "))
            open(LOG_FILE, "a").write(f"[INFO: {NOW.isoformat()}] {get_data}\n")
        else:
            # Let me know something big is going on
            open(LOG_FILE, "a").write(f"[INFO: {NOW.isoformat()}] Parsing multipart data...\n")

            post_data = {}

            def on_field(field):
                """
                What to do when a field is parsed.
                """
                key = field.field_name.decode('utf-8')
                value = field.value.decode('utf-8')
                post_data[key] = value

                open(LOG_FILE, "a").write(
                    f"[INFO: {NOW.isoformat()}] Parsed field '{key}' = '{value}'\n"
                )

            def on_file(file):
                """
                What to do when a file is parsed.
                """
                # Get the filename and byte data
                key = file.field_name.decode('utf-8')
                filename = file.file_name.decode('utf-8')
                file_obj: BytesIO = file.file_object

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
                    image.save(path)
                except UnidentifiedImageError:
                    open(LOG_FILE, "a").write(
                        f"[WARN: {NOW.isoformat()}] Image decoding error. Likely lack of data\n"
                    )
                    return

                post_data[key] = {
                    'filename': new_filename,
                    'path': path
                }

                file_obj.seek(0)
                open(LOG_FILE, "a").write(
                    f"[INFO: {NOW.isoformat()}] Parsed file '{key}', filename='{new_filename}', path={path}\n"
                )
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
            except Exception as e:
                open(LOG_FILE, "a").write(
                    f"[ERROR: {NOW.isoformat()}] Multipart parsing failed: {traceback.format_exc()}\n"
                )
                render_status(400, f"Multipart parsing error")
                quit(1)

        open(LOG_FILE, "a").write(f"[INFO: {NOW.isoformat()}] {post_data}\n")
        return post_data

    raise HttpResponse(405, "Invalid REST API call")
