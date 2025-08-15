# Attribution to https://ellie.clifford.lol
# This is not maintained by https://ellie.clifford.lol any problems should be directed to myself
# Provided under WTFPL

import traceback

from os import environ
from sys import stdin
from datetime import datetime
from urllib.parse import parse_qs
from urllib.parse import unquote


LOG_FILE = "/home/atp45/logs/http_lib"
now = datetime.now()


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
    open(LOG_FILE, "a").write(f"[{header}: {now.isoformat()}] http status {status}: {msg}\n")

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
        open(LOG_FILE, "a").write(f"[WARN: {now.isoformat()}] Error displaying HTTP status:\n{traceback.format_exc()}]\n")
        # Let wrap deal with it
        raise e


def params(rest: str = "get") -> dict:
    if rest == "get":
        return {
            x: None if len(y) == 0 else y[0] if len(y) == 1 else y
            for x, y in parse_qs(
                environ.get("QUERY_STRING", ""),
                keep_blank_values=True,
            ).items()
        }
    if rest == "post":
        # Much more of a pain
        raw_data = stdin.read()

        # TODO: proper logging
        open(LOG_FILE, "a").write(
            f"[INFO: {now.isoformat()}] {raw_data}\n"
        )

        post_data = {}
        for variable in raw_data.split("&"):
            s = variable.split("=")
            if len(s) != 2:
                render_status(400, "Invalid input")
                quit(1)

            post_data[s[0]] = unquote(s[1].replace("+", " "))

        open(LOG_FILE, "a").write(f"[INFO: {now.isoformat()}] {post_data}\n")

        return post_data

    render_status(405, "Invalid REST API call")
    quit(1)
