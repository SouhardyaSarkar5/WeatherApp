from flask import Flask, request, jsonify, render_template
import requests
import logging
from datetime import datetime
import os

PORT = 8081

app = Flask(__name__)

def fetch_current_weather(city):
    api_key = "YOUR_API_KEY"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data

def fetch_current_weather_by_coordinates(lat, lon):
    api_key = "YOUR_API_KEY"
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data

def fetch_forecast_weather(city):
    api_key = "YOUR_API_KEY"
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data

def fetch_forecast_weather_by_coordinates(lat, lon):
    api_key = "YOUR_API_KEY"
    url = f"http://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data

def get_weather_image(description):
    description = description.lower()
    if "cloud" in description:
        return "/static/cloudbg.gif"
    elif "rain" in description:
        return "/static/rainbg.gif"
    elif "haze" in description or "mist" in description:
        return "/static/hazebg.gif"
    elif "clear" in description:
        return "/static/clear skybg.gif"
    elif "snow" in description:
        return "/static/snowbg.gif"
    elif "drizzle" in description:
        return "/static/rainbg.gif"
    else:
        return "/static/defaultbackground.gif"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/fetch_weather')
def fetch_weather():
    city = request.args.get('city')
    lat = request.args.get('lat')
    lon = request.args.get('lon')

    if city:
        current_weather = fetch_current_weather(city)
        forecast_weather = fetch_forecast_weather(city)
    elif lat and lon:
        current_weather = fetch_current_weather_by_coordinates(lat, lon)
        forecast_weather = fetch_forecast_weather_by_coordinates(lat, lon)
    else:
        return jsonify({"error": "Missing parameters"}), 400

    if current_weather.get("cod") != 200 or forecast_weather.get("cod") != "200":
        return jsonify({"error": "Weather data not found"}), 404

    weather_description = current_weather['weather'][0]['description']
    current_date = datetime.utcfromtimestamp(current_weather['dt']).strftime('%Y-%m-%d %H:%M')
    current_temp = current_weather['main']['temp']
    current_feels_like = current_weather['main']['feels_like']
    current_wind_speed = current_weather['wind']['speed']
    current_icon = current_weather['weather'][0]['icon']
    current_weather_description = current_weather['weather'][0]['description']

    forecast_items = []
    for item in forecast_weather['list']:
        dt = datetime.utcfromtimestamp(item['dt'])
        temp = item['main']['temp']
        weather_desc = item['weather'][0]['description']
        icon = item['weather'][0]['icon']
        feels_like = item['main']['feels_like']
        wind_speed = item['wind']['speed']

        weather_card = f"""
        <div class="weather-box">
            <span class="weather-date">
            <div class="date-part">{dt.strftime('%Y-%m-%d')}</div>
            <div class="time-part">{dt.strftime('%H:%M')}</div>
            </span>
            <img src="http://openweathermap.org/img/wn/{icon}.png" alt="{weather_desc}">
            <div class="weather-details">
                <div>
                <span class="weather-temp">{temp}°C</span>
                </div>
                <div>
                <span class="weather-desc" style="text-transform: capitalize;">{weather_desc}</span>
                </div>
                <div>
                <span class="weather-feels-like">Feels Like {feels_like}°C</span>
                </div>
                <span class="weather-wind">Wind: {wind_speed} km/h</span>
            </div>
        </div>
        """
        forecast_items.append(weather_card)

    forecast_html = "".join(forecast_items)
    response_data = {
        "html": forecast_html,
        "weatherDescription": weather_description,
        "currentDate": current_date,
        "currentTemp": current_temp,
        "currentFeelsLike": current_feels_like,
        "currentWindSpeed": current_wind_speed,
        "currentIcon": current_icon,
        "currentWeatherDescription": current_weather_description,
        "cityName": current_weather['name'] if 'name' in current_weather else ""
    }

    return jsonify(response_data)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(port=PORT, debug=True)