# Attribution to https://ellie.clifford.lol
# This is not maintained by https://ellie.clifford.lol any problems should be directed to myself
# Provided under WTFPL

import traceback
from os import environ
from urllib.parse import parse_qs


class HttpResponse(Exception):
    def __init__(self, status, text):
        self.status = status
        self.text = text


def params():
    return {
        x: None if len(y) == 0 else y[0] if len(y) == 1 else y
        for x, y in parse_qs(
            environ.get("QUERY_STRING", ""),
            keep_blank_values=True,
        ).items()
    }


def wrap(func, *args, debug=False, **kwargs):
    try:
        try:
            func(*args, **kwargs)
        except HttpResponse as e:
            print(f"Status: {e.status}")
            print("Content-Type: text/plain")
            print()
            print(e.text)
    except Exception:
        print("Status: 500 Internal Server Error")
        print("Content-Type: text/plain")
        if debug:
            print()
            print(traceback.format_exc())
