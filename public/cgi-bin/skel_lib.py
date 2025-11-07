import requests
from xml.etree import ElementTree

from requests.exceptions import RequestException
from requests.models import Response

from typing import Dict, Tuple, Union


def get_source(
    url: str,
    HttpResponse
) -> Union[Response, RequestException]:
    try:
        return requests.get(url)
    except RequestException:
        raise HttpResponse(424, "Unable to retrieve data")


def get_data(
    url: str,
    HttpResponse
) -> Union[Dict, None]:
    response = get_source(url, HttpResponse)

    if isinstance(response, RequestException):
        raise HttpResponse(424, "Invalid response from weather server")
    else:
        tree = ElementTree.fromstring(response.content)

        channel: Union[ElementTree.Element, None] = tree.find('channel')
        if channel is None:
            raise HttpResponse(424, "Cannot find 'channel' in weather server response")

        item: Union[ElementTree.Element, None] = channel.find('item')
        if item is None:
            raise HttpResponse(424, "Cannot find 'item' in weather server response")

        data: Union[ElementTree.Element, None] = item.find('description')
        if data is None or data.text is None:
            raise HttpResponse(424, "Not weather data returned")

        table = ElementTree.XML(data.text)
        rows = iter(table)
        data_table = {}
        for row in rows:
            data_table[row[0].text] = row[1].text

        return data_table


def get_input(params: dict) -> Tuple[float, float, float]:
    minTemp = float(params["min_temp"])
    midTemp = float(params["mid_temp"])
    maxTemp = float(params["max_temp"])
    return (minTemp, midTemp, maxTemp)


def convert(temperature: float, params: dict):
    minT, midT, maxT = get_input(params)
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


def run(params, HttpResponse):
    table = get_data(
        "https://www.cl.cam.ac.uk/weather/rss.xml",
        HttpResponse
    )
    minT, midT, maxT = get_input(params)

    value = convert(
        float(table['Temp'][:-2]),
        params
    ) if table is not None else 0

    # HTML response
    with open("templates/skel/template.html") as template:
        html = template.read()

    values = {
        "termperature": str(round(value, 2) * 1000),
        "minT": str(minT),
        "midT": str(midT),
        "maxT": str(maxT)
    }

    print("Content-Type: text/html")
    print("Status: 200\n")

    def format_html(html: str, replacements: dict) -> str:
        for key, value in replacements.items():
            html = html.replace(f"[{key}]", value)

        return html

    print(format_html(html, values))
