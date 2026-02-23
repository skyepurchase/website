#!/usr/bin/python3
# Wrapper for the newsletter answer method

import os
import sys
from wrap import wrap  # Safe import


def run():
    # An ugly hack
    newsletter_path = os.path.join(os.path.dirname(__file__), "newsletter")
    if newsletter_path not in sys.path:
        sys.path.append(newsletter_path)

    # All unsafe code that will now be caught
    from http_lib import params, get_cookies, verify_token, HttpResponse
    from newsletter.endpoints import answer
    from newsletter.utils.type_hints import NewsletterException

    cookies = get_cookies()
    if "newsletter_token" not in cookies:
        raise HttpResponse(
            401, "No authentication cookie found. Please unlock the newsletter again."
        )

    success, msg, _ = verify_token(cookies["newsletter_token"])

    if not success:
        raise HttpResponse(400, msg)

    parameters = params("POST")

    try:
        answer(parameters)
    except NewsletterException as res:
        raise HttpResponse(res.status, res.msg)


wrap(run)
