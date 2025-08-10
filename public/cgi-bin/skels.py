#!/usr/bin/python3
import cgi
import requests
from typing import Dict, Tuple, Union
from xml.etree import ElementTree
from requests.exceptions import RequestException
from requests.models import Response

from utils import format_html


def get_source(url: str) -> Union[Response, RequestException]:
    try:
        return requests.get(url)

    except requests.exceptions.RequestException as e:
        return e


def get_data(url: str) -> Union[Dict, None]:
    response:Union[Response, RequestException] = get_source(url)

    if isinstance(response, RequestException):
        print("Invalid response")
        print(response)
    else:
        tree = ElementTree.fromstring(response.content)

        channel: Union[ElementTree.Element, None] = tree.find('channel')
        if channel is None:
            print("Cannot find 'channel'")
            return

        item: Union[ElementTree.Element, None] = channel.find('item')
        if item is None:
            print("Cannot find 'item'")
            return

        data: Union[ElementTree.Element, None] = item.find('description')
        if data is None or data.text is None:
            print("Cannot find 'data' or related data")
            return

        table = ElementTree.XML(data.text)
        rows = iter(table)
        data_table = {}
        for row in rows:
            data_table[row[0].text] = row[1].text

        return data_table


def get_input() -> Tuple[float, float, float]:
    form = cgi.FieldStorage()
    minTemp = float(form.getvalue("min_temp"))
    midTemp = float(form.getvalue("mid_temp"))
    maxTemp = float(form.getvalue("max_temp"))
    return (minTemp, midTemp, maxTemp)


def convert(temperature):
    minT, midT, maxT = get_input()
    grad = 1 / 18.9
    intercept = -1

    if temperature > midT:
        grad = 1 / (maxT - midT)
        intercept = -midT * grad
    else:
        grad = 1 / (midT - minT)
        intercept = (-minT * grad) - 1

    T = (grad * temperature) + intercept
    return T


print("Content-Type: text/html")
print("Status: 200\n")

table = get_data("https://www.cl.cam.ac.uk/weather/rss.xml")
minT, midT, maxT = get_input()

value = convert(float(table['Temp'][:-2])) if table is not None else 0

# HTML response
with open("templates/skel/template.html") as template:
    html = template.read()

values = {
    "termperature": str(round(value, 2) * 1000),
    "minT": str(minT),
    "midT": str(midT),
    "maxT": str(maxT)
}

print(format_html(html, values))
