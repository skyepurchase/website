#!/usr/bin/python3
# Wrapper for the newsletter main method

from wrap import wrap  # Safe import


def run():
    # All unsafe code that will now be caught
    from http_lib import get_cookies, verify_token, params, HttpResponse
    from newsletter.cgi import render
    from newsletter.utils.type_hints import NewsletterToken, NewsletterException

    cookies = get_cookies()
    if "newsletter_token" not in cookies:
        raise HttpResponse(
            401, "No authentication cookie found. Please unlock the newsletter again."
        )

    success, msg, raw_data = verify_token(cookies["newsletter_token"])

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

    if success:
        try:
            render(data, issue)
        except NewsletterException as res:
            raise HttpResponse(res.status, res.msg)
    else:
        raise HttpResponse(400, msg)


wrap(run)
