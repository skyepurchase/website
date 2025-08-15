#!/usr/bin/python3
# Wrapper for the newsletter main method

from wrap import wrap # Safe import

def run():
    # All unsafe code that will now be caught
    from http_lib import params, HttpResponse
    from newsletter.cgi import render

    PARAMETERS = params("post")

    render(PARAMETERS, HttpResponse)

wrap(run)
