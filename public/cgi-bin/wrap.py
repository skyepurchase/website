# Courtesy of ellie.clifford.lol provided WTFPL
import traceback # A safe import, at least it should be


def wrap(func, *args, **kwargs):
    try:
        # Wrap self-written libraries within an try-catch
        from http_lib import render_status, HttpResponse

        try:
            func(*args, **kwargs)
        except HttpResponse as e:
            render_status(e.status, e.text)

    except Exception:
        print("Status: 500")
        print("Content-Type: text/plain")
        print()
        # This is a content leak HOWEVER if it fails this bad you need the traceback
        print(traceback.format_exc())
