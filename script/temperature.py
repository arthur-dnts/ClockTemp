import requests

# Get weather data from Open-Meteo
def get_weather(lat=0, lon=0):
    if "0" in lat and "0" in lon:
        return "N/A"
    else:
        url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
        try:
            response = requests.get(url)
            return response.json()["current_weather"]["temperature"]
        except requests.RequestException as e:
            return f"Erro: {e}"
