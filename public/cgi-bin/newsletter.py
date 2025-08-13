#!/usr/bin/python3
# Wrapper for the newsletter main method

from http_lib import params, wrap, HttpResponse
from newsletter.cgi import render

PARAMETERS = params()

wrap(render, PARAMETERS, HttpResponse)
