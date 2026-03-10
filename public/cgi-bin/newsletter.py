#!/usr/bin/python3
# Wrapper for the newsletter main method

import os
import sys
from wrap import wrap  # Safe import


def run():
    # An ugly hack
    newsletter_path = os.path.join(os.path.dirname(__file__), "newsletter")
    if newsletter_path not in sys.path:
        sys.path.append(newsletter_path)

    # All unsafe code that will now be caught
    from http_lib import get_cookies, verify_token, params, HttpResponse
    from newsletter.endpoints import render
    from newsletter.utils.type_hints import NewsletterToken

    cookies = get_cookies()
    if "newsletter_token" not in cookies:
        raise HttpResponse(
            401, "No authentication cookie found. Please unlock the newsletter again."
        )

    success, msg, raw_data = verify_token(cookies["newsletter_token"])

    if not success:
        raise HttpResponse(400, msg)

    issue = params("GET").get("issue")
    if issue:
        try:
            issue = int(issue)
        except ValueError:
            raise HttpResponse(400, "Issue must be an integer")

    data = NewsletterToken(
        title=raw_data["newsletter_title"],
        folder=raw_data["newsletter_folder"],
        id=raw_data["newsletter_id"],
    )

    res = render(data, issue)

    raise HttpResponse(res.status, res.content, content_type=res.content_type)


wrap(run)
