#!/usr/bin/python3
# Wrapper for the newsletter answer method

from http_lib import params, wrap, HttpResponse
from newsletter.cgi import answer

PARAMETERS = params("post")

wrap(answer, PARAMETERS, HttpResponse)
