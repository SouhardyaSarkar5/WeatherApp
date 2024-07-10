import http.server
import requests
import urllib.parse
import logging
from datetime import datetime
import json
import os

PORT = 8081

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weather App</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@700&display=swap" rel="stylesheet">
    <style>
        body {
            background-image: url("/static/defaultbackground.gif");
            font-family: system-ui;
            margin: 0;
            padding: 0;
            background-size: cover;
            background-position: center;
            color: white;
            height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .weather-container {
            max-width: 900px;
            padding: 20px;
            # background-color: rgba(255, 255, 255, 0.8);
            border-radius: 10px;
            # box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            color: black;
            text-align: center;
            display: grid;
            grid-template-columns: 1fr;
            grid-template-rows: auto auto 1fr auto;
            gap: 20px;
        }
        .search-form-container {
            grid-column: 1;
            grid-row: 1;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .search-form-container input[type="text"] {
            padding: 10px;
            border: 1px solid #372b2b;
            border-radius: 5px;
            margin-right: 10px;
            width: 780px;
        }
        
        /* Media query for screen widths 1200px and above */
    @media (min-width: 1200px) {
        .search-form-container input[type="text"] {
            width: 780px;
        }
    }

    /* Media query for screen widths between 992px and 1199px */
    @media (min-width: 992px) and (max-width: 1199px) {
        .search-form-container input[type="text"] {
            width: 600px;
        }
    }

    /* Media query for screen widths between 768px and 991px */
    @media (min-width: 768px) and (max-width: 991px) {
        .search-form-container input[type="text"] {
            width: 500px;
        }
    }

    /* Media query for screen widths below 768px */
    @media (max-width: 767px) {
        .search-form-container input[type="text"] {
            width: 100%;
            margin-right: 0;
            box-sizing: border-box;
        }
    }
        
        .search-form-container button {
            padding: 10px;
            border: none;
            background-color: transparent;
            background-size: contain;
            background-repeat: no-repeat;
            cursor: pointer;
            width: 30px;
            height: 30px;
        }
        .search-form-container button:hover {
            opacity: 0.8;
        }
        .search-form-container button:focus {
            outline: none;
        }
        
        .search-form-container .search-button {
            margin-bottom: 20px;
            padding: 10px;
            border: none;
            background-color: transparent;
            background-size: contain;
            background-repeat: no-repeat;
            cursor: pointer;
            width: 30px;
            height: 30px;
        }
        
        .search-form-container .search-button img {
             width: 30px;
            height: auto;
            margin-right: 5px;
        }
        .search-form-container .locate-button {
            padding: 10px;
            border: none;
            background-color: transparent;
            color: white;
            cursor: pointer;
            border-radius: 5px;
            margin-left: 10px;
            display: flex;
            align-items: center;
            margin-right: 10px;
        }
        .search-form-container .locate-button img {
            width: 30px;
            height: auto;
            margin-right: 5px;
        }
        #current-city-time {
            grid-column: 1;
            grid-row: 2;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        #current-city {
            width: 150px;
            padding: 5px;
            border: 1px solid transparent;
            border-radius: 12px;
            background-color: #fff8dc80;
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }
        #time-container {
            margin-right: 15px;
            display: flex;
            align-items: center;
        }
        #clock {
            font-size: 1.2em;
        }
        #current-time-img {
            height: 50px;
            width: auto;
        }
        #current-weather-box {
            grid-column: 1;
            grid-row: 3;
        }
        .weather-cards {
            grid-column: 1;
            grid-row: 4;
            display: flex;
            overflow-x: auto;
            scroll-snap-type: x mandatory;
            gap: 20px;
            padding: 10px 0;
        }
        .weather-box {
            background: linear-gradient(to right, #000000a8, #393c42);
            color: white;
            padding: 20px;
            border-radius: 10px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            text-align: center;
            min-width: 200px;
            scroll-snap-align: center;
        }
        .weather-box img {
            margin: 0 auto;
            height: 50px;
        }
        .weather-details {
            flex-grow: 1;
            margin-top: 10px;
        }
        .current-weather {
            background: linear-gradient(to right, #000000, #00000045)
        }
        
        
    </style>
    <script>
    function updateClock() {
        const now = new Date();
        const hours = now.getHours();
        const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        document.getElementById('clock').textContent = timeString;

        const weatherClock = document.getElementById('weather-clock');
        if (weatherClock) {
            weatherClock.textContent = timeString;
        }

        const currentTimeImg = document.getElementById('current-time-img');
        if (currentTimeImg) {
            if (hours >= 6 && hours < 18) {
                currentTimeImg.src = '/static/day.gif';
            } else {
                currentTimeImg.src = '/static/night.gif';
            }
        }
    }

    function fetchWeather(city) {
        city = city.charAt(0).toUpperCase() + city.slice(1);

        fetch('/fetch_weather?city=' + city)
            .then(response => response.json())
            .then(data => {
                const weatherContainer = document.getElementById('weather-output');
                weatherContainer.innerHTML = data.html;
                updateClock();
                updateBackground(data.weatherDescription);

                const currentWeatherBox = `
<div class="weather-box current-weather">
    <img src="http://openweathermap.org/img/wn/${data.currentIcon}.png" alt="${data.currentWeatherDescription}">
    <div class="weather-details">
         <div>
                            <span class="weather-temp">${data.currentTemp}°C</span>
                            </div>
                            <div>
                            <span class="weather-desc" style="text-transform: capitalize;">${data.currentWeatherDescription}</span>
                            <span class="weather-feels-like"> | Feels Like ${data.currentFeelsLike}°C</span>
                            </div>
                            <span class="weather-wind">Wind: ${data.currentWindSpeed} km/h</span>
    </div>
</div>
`;

                const currentWeatherBoxContainer = document.getElementById('current-weather-box');
                currentWeatherBoxContainer.innerHTML = currentWeatherBox;

                document.getElementById('current-city').textContent = city;
            });
    }

    function fetchWeatherByCoordinates(lat, lon) {
        fetch('/fetch_weather?lat=' + lat + '&lon=' + lon)
            .then(response => response.json())
            .then(data => {
                const weatherContainer = document.getElementById('weather-output');
                weatherContainer.innerHTML = data.html;
                updateClock();
                updateBackground(data.weatherDescription);

                const currentWeatherBox = `
                    <div class="weather-box current-weather">
                        <img src="http://openweathermap.org/img/wn/${data.currentIcon}.png" alt="${data.currentWeatherDescription}">
                        <div class="weather-details">
                            <div>
                            <span class="weather-temp">${data.currentTemp}°C</span>
                            </div>
                            <div>
                            <span class="weather-desc" style="text-transform: capitalize;">${data.currentWeatherDescription}</span>
                            <span class="weather-feels-like"> | Feels Like ${data.currentFeelsLike}°C</span>
                            </div>
                            <span class="weather-wind">Wind: ${data.currentWindSpeed} km/h</span>
                        </div>
                    </div>
                `;
                const currentWeatherBoxContainer = document.getElementById('current-weather-box');
                currentWeatherBoxContainer.innerHTML = currentWeatherBox;

                document.getElementById('current-city').textContent = data.cityName;
            });
    }

    function updateBackground(weatherDescription) {
        const body = document.body;
        const lowerCaseDesc = weatherDescription.toLowerCase();  // Convert to lowercase for case insensitivity

        if (lowerCaseDesc.includes('cloud') || lowerCaseDesc.includes('clouds') || lowerCaseDesc.includes('cloudy')) {
            body.style.backgroundImage = "url('/static/cloudbg.gif')";
        } else if (lowerCaseDesc.includes('rain')) {
            body.style.backgroundImage = "url('/static/rainbg.gif')";
        } else if (lowerCaseDesc.includes('haze') || lowerCaseDesc.includes('mist')) {
            body.style.backgroundImage = "url('/static/hazebg.gif')";
        } else if (lowerCaseDesc.includes('clear sky')) {
            body.style.backgroundImage = "url('/static/clear skybg.gif')";
        } else if (lowerCaseDesc.includes('snow')) {
            body.style.backgroundImage = "url('/static/snowbg.gif')";
        } else if (lowerCaseDesc.includes('thunder')) {
            body.style.backgroundImage = "url('/static/thunderbg.gif')";
        } else if (lowerCaseDesc.includes('drizzle') || lowerCaseDesc.includes('shower rain')) {
            body.style.backgroundImage = "url('/static/rainbg.gif')";
        } else if (lowerCaseDesc.includes('snowfall')) {
            body.style.backgroundImage = "url('/static/snowbg.gif')";
        } else if (lowerCaseDesc.includes('atmosphere')) {
        } else {
            body.style.backgroundImage = "url('/static/defaultbackground.gif')";
        }
    }

    document.addEventListener('DOMContentLoaded', function() {
        document.getElementById('search-button').addEventListener('click', function() {
            const city = document.getElementById('city-input').value;
            fetchWeather(city);
        });

        document.getElementById('locate-button').addEventListener('click', function() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(function(position) {
                    const lat = position.coords.latitude;
                    const lon = position.coords.longitude;
                    fetchWeatherByCoordinates(lat, lon);
                });
            } else {
                alert('Geolocation is not supported by this browser.');
            }
        });

        updateClock();
        setInterval(updateClock, 1000);
    });
</script>

</head>
<body>
    <div class="weather-container">
        <div class="search-form-container">
            <input type="text" id="city-input" placeholder="Enter city name">
            <button id="search-button" class="search-button"><img src="/static/magnifying-glass.png" alt="Search"></button>
            <button id="locate-button" class="locate-button"><img src="/static/locateme.png" alt="Locate Me"></button>
        </div>
        <div id="current-city-time">
            <div id="current-city">Search City</div>
            <div id="time-container">
                <img id="current-time-img" src="/static/day.gif" alt="Time Image">
                <div id="clock"></div>
            </div>
       </div>
        <div id="current-weather-box">
            <!-- Current weather details will be dynamically updated here -->
        </div>
        <div class="weather-cards" id="weather-output">
            <!-- Weather forecast cards will be dynamically updated here -->
        </div>
    </div>
</body>
</html>
"""
def fetch_current_weather(city):
    api_key = "942ede6e8b41006a9e425153a47f42b5"
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data

def fetch_current_weather_by_coordinates(lat, lon):
    api_key = "942ede6e8b41006a9e425153a47f42b5"
    url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data

def fetch_forecast_weather(city):
    api_key = "942ede6e8b41006a9e425153a47f42b5"
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    data = response.json()
    return data

def fetch_forecast_weather_by_coordinates(lat, lon):
    api_key = "942ede6e8b41006a9e425153a47f42b5"
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

class WeatherAppHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        elif self.path.startswith("/static/"):
            try:
                with open(os.getcwd() + self.path, 'rb') as file:
                    self.send_response(200)
                    if self.path.endswith('.gif'):
                        self.send_header("Content-type", "image/gif")
                    elif self.path.endswith('.jpg'):
                        self.send_header("Content-type", "image/jpeg")
                    elif self.path.endswith('.png'):
                        self.send_header("Content-type", "image/png")
                    self.end_headers()
                    self.wfile.write(file.read())
            except FileNotFoundError:
                self.send_error(404, "File Not Found: %s" % self.path)
        elif self.path.startswith("/fetch_weather"):
            query = urllib.parse.urlparse(self.path).query
            params = urllib.parse.parse_qs(query)
            api_key = "942ede6e8b41006a9e425153a47f42b5"  # Replace with your OpenWeatherMap API key

            if 'city' in params:
                city = params['city'][0]
                current_weather = fetch_current_weather(city)
                forecast_weather = fetch_forecast_weather(city)
            elif 'lat' in params and 'lon' in params:
                lat = params['lat'][0]
                lon = params['lon'][0]
                current_weather = fetch_current_weather_by_coordinates(lat, lon)
                forecast_weather = fetch_forecast_weather_by_coordinates(lat, lon)

            if current_weather.get("cod") != 200 or forecast_weather.get("cod") != "200":
                self.send_response(404)
                self.end_headers()
                return

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

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response_data).encode("utf-8"))
        else:
            self.send_error(404, "File Not Found: %s" % self.path)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server_address = ("", PORT)
    httpd = http.server.HTTPServer(server_address, WeatherAppHandler)
    logging.info(f"Server started at http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info("Server stopped.")