#!/usr/bin/python3
import requests

params = {
    'lat': 52.2,
    'lon': 0.1
}

response = requests.get(
    "https://api.openweathermap.org/data/3.0/onecall",
    params=params,
)

print("Content-Type: text/plain")
print("Status: 200\n")

print("This is not implemented yet!")
print(response.json())
