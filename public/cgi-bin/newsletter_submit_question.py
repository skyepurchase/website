#!/usr/bin/python3
# Wrapper for the newsletter answer method

from wrap import wrap  # Safe import


def run():
    # All unsafe code that will now be caught
    from http_lib import params, get_cookies, verify_token, HttpResponse
    from newsletter.cgi import question_submit
    from newsletter.utils.type_hints import NewsletterToken

    cookies = get_cookies()
    if "newsletter_token" not in cookies:
        raise HttpResponse(
            401, "No authentication cookie found. Please unlock the newsletter again."
        )

    success, msg, raw_data = verify_token(cookies["newsletter_token"])

    data = NewsletterToken(
        title=raw_data["newsletter_title"],
        folder=raw_data["newsletter_folder"],
        id=raw_data["newsletter_id"],
    )

    if success:
        parameters = params("POST")

        question_submit(data, parameters, HttpResponse)
    else:
        raise HttpResponse(400, msg)


wrap(run)
