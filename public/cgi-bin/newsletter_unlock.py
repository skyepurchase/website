#!/usr/bin/python3
# Wrapper for the newsletter main method

from wrap import wrap # Safe import

def run():
    # All unsafe code that will now be caught
    from http_lib import params, generate_token, HttpResponse
    from newsletter.cgi import authenticate

    PARAMETERS = params("POST")

    passcode = PARAMETERS.get("unlock")
    if not isinstance(passcode, str):
        raise HttpResponse(
            400,
            f"Expected 'unlock' to be of type `str` but received {type(passcode)}"
        )

    success, n_id, n_title, n_folder = authenticate(passcode)

    if not success:
        raise HttpResponse(401, "Nice try, but that is not the passcode! If you are meant to find something try typing it in again.")

    payload = {
        "newsletter_id": n_id,
        "newsletter_title": n_title,
        "newsletter_folder": n_folder
    }
    jwt = generate_token(payload)

    print(f"Set-Cookie: newsletter_token={jwt}; HttpOnly; Secure")
    print("Location: https://skye.purchasethe.uk/cgi-bin/newsletter.py")
    print("Content-Type: text/html")
    print("Content-Length: 0")
    print("Status: 303\n")


wrap(run)
