#!/usr/bin/python3
# Wrapper for the newsletter answer method

from wrap import wrap # Safe import

def run():
    # All unsafe code that will now be caught
    from http_lib import params, HttpResponse
    from newsletter.cgi import question_submit

    PARAMETERS = params("POST")

    question_submit(PARAMETERS, HttpResponse)

wrap(run)
