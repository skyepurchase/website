#!/usr/bin/python3
# Wrapper for the newsletter main method

from wrap import wrap # Safe import

def run():
    # All unsafe code that will now be caught
    from http_lib import params, HttpResponse
    from skel_lib import run as run_skel

    PARAMETERS = params("GET")

    run_skel(PARAMETERS, HttpResponse)

wrap(run)
