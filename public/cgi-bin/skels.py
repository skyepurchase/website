#!/usr/bin/python3
import cgi
import requests
from typing import Dict, Tuple, Union
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
print(f"""
<html>
<head>
<meta charset="UTF-8">
<meta http-equiv="X-UA-Compatible" content="IE-edge">
<meta name="viewpoint" content="width=device.width, initial-scale=1.0">
<title>The Skel Scale</title>
<link rel="stylesheet" href="../../css/style.css"/>
</head>
<body>
    <section class="main">
        <nav>
            <!--logo-->
            <a href="../../" class="logo">
                <p>Home</p> 
            </a>
            <input class="menu-btn" type="checkbox" id="menu-btn"/>
            <label class="menu-icon" for="menu-btn">
                <span class="nav-icon"></span>
            </label>
            <!--menu-->
            <ul class="menu">
                <li><a href="../">Projects</a></li>
                <li><a href="../../blog/" class="blog">Blog</a></li>
            </ul>
        </nav>

        <div class="container">
            <div class="center">
                <h2>The termperature in Cambridge is {round(value, 2) * 1000}</h2>
                <form action="skels">
                    <label for="min">Minimum temperature:</label>
                    <input type="number" id="min" name="min_temp" value="{minT}" step="0.1">
                    <label for="mid">Comfortable temperature:</label>
                    <input type="number" id="mid" name="mid_temp" value="{midT}" step="0.1">
                    <label for="max">Maximum temperature:</label>
                    <input type="number" id="max" name="max_temp" value="{maxT}" step="0.1">
                    <input type="submit" name="Get temperature", id="scale_submit" value="Generate scale">
            </div>

            <div class="post">
                <h1 id="a-better-temperature-system">A Better Temperature System</h1>
                <p>There are 3 standard temperature systems (at least that are talked
                about in public discourse): Kelvin, Celsius, and Fahrenheit.</p>
                <p>Kelvin is impractical for every day use but excellent for scientific
                purposes though, I feel, primarily physics/physical systems. The problem
                is standard temperatures range from 268.15K to 313.15K. Huge numbers
                with little changing between them.</p>
                <p>Celsius has wide spread use across the globe (barring a few
                countries). It’s neat, 0&#176C
                freezing point and 100&#176C
                boiling point for water. Definitely a useful system expecially in
                scientific applications (especially with its direct relation to Kelvin)
                and cooking applications. But standard human temperatures range from
                -5&#176C to 40&#176C. A weird range where a value
                changing by 3 can have huge effects.</p>
                <p>Fahrenheit! This is awful, this is not about how we should switch to
                Fahrenheit. Typical temperatures range from 23&#176F to 104&#176F which is fairly impractical but
                it is very close to a “percentage temperature scale” for humans. Think
                0&#176F = -18&#176C and 100&#176F = 37.8&#176C. This is close to a good
                system.</p>
                <h2 id="the-better-system">The better system</h2>
                <p>A better system:</p> 
                <ul>
                    <li>* neatly covers the typical temperature range (-5 to 40) wrapping it ~-1 to ~1.</li>
                    <li>* places room temperature (or comfortable temperature) at 0.</li>
                    <li>* places a fever (though not sure if this will stick around) at ~1.</li>
                    <li>* places (water) freezing temperature at ~-1.</li>
                    <li>* places (water) boiling temperature at some whole number.</li>
                </ul>
                <p>If we go with a first attempt of fitting a linear curve to 2 of the above points we have:</p>
                <ul>
                    <li>* typical temperature range is -1.27 to 1.12 (which is okay)</li>
                    <li>* room temperature is ~0 (depends on definition but cool it popped out!)</li>
                    <li>* a fever (~37.8&#176C) is 1 (one of our chosen points)</li>
                    <li>* water freezes is -1 (one of our chosen points)</li>
                    <li>* water boils at 4.29 (Oh no! that’s not great)</li>
                </ul>
                <p>This is fine though, because now we have some scale that gives a good percentage for humans. Some cool temperature points:</p>
                <ul>
                    <li>* 0.5 means its not boiling but it’s warm and starting to get uncomfortable if you’re not careful. 28.5&#176C pretty spot on</li>
                    <li>* -0.5 means its not freezing but it’s cold and you should wrap up. 9.5&#176C is pretty close</li>
                    <li>* 1 means its boiling and you should deal with it appropriately</li>
                    <li>* -1 means its freezing and you should deal with it appropriately</li>
                </ul>
                <p>The small issue is that 28&#176C to 32&#176C is far larger a temperature jump (subjectively) than 10&#176C to 5&#176C. This non-uniformity will be addressed as this system improves.</p>
                <p>For now (if you are in Cambridge) here is a little temperature guage for you.</p>
            </div>
        </div>
    </section>
</body>
</html>
""")
