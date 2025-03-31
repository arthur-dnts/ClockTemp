"""
# temperature.py - Copyright (c) 2025 Arthur Dantas
# This file is part of ClockTemp, licensed under the GNU General Public License v3.
# See <https://www.gnu.org/licenses/> for details.
"""

import requests

# Get weather data from Open-Meteo
def get_weather(lat=0, lon=0):
    if lat == "0" and lon == "0":
        return "N/A"
    else:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        try:
            response = requests.get(url)
            temp = response.json()["current_weather"]["temperature"]
            temp_formated = "{:04.1f}".format(float(temp)) # Ensures the temperature has 4 characters
            return temp_formated
        except requests.RequestException as e:
            return f"Error: {e}"
