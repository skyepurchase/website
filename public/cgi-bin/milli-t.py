#!/usr/bin/python3
from typing import Dict, Union
import requests
from xml.etree import ElementTree
from requests.exceptions import RequestException
from requests.models import Response


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


def convert(temperature):
    # TODO: use user inputted points
    T = (temperature / 18.9) - 1
    return T


print("Content-Type: text/plain")
print("Status: 200\n")

table = get_data("https://www.cl.cam.ac.uk/weather/rss.xml")
if table is None: print("Table could not be generated")
else: print('{0:.3f}'.format(convert(float(table['Temp'][:-2]))))
