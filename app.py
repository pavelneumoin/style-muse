from flask import Flask, render_template, request, jsonify
import os
import requests
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)

# Получаем API ключ
API_KEY = os.getenv('OPENWEATHER_API_KEY', 'f047613185f40b38100e65c37450b05a')

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    recommendation = None
    city = 'Москва'
    
    if request.method == 'POST':
        city = request.form.get('city', 'Москва').strip()
        
        if not city:
            city = 'Москва'
        
        # Запрос к OpenWeatherMap API
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&lang=ru&appid={API_KEY}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                weather_data = {
                    'city': data['name'],
                    'temperature': round(data['main']['temp']),
                    'feels_like': round(data['main']['feels_like']),
                    'description': data['weather'][0]['description'].capitalize(),
                    'icon': data['weather'][0]['icon'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': round(data['wind']['speed'], 1)
                }
                
                # Формируем рекомендацию по одежде
                temp = weather_data['temperature']
                has_precipitation = any(data['weather'][0]['main'].lower() in ['rain', 'drizzle', 'snow'] for w in data['weather'])
                
                if temp > 25 and not has_precipitation:
                    recommendation = 'Легкая одежда, футболка, головной убор от солнца'
                elif temp >= 15 and temp <= 25:
                    recommendation = 'Джинсы, лёгкая кофта'
                elif temp >= 5 and temp < 15:
                    recommendation = 'Свитер, ветровка, куртка'
                elif temp <= 5 and not has_precipitation:
                    recommendation = 'Тёплая куртка, шапка, шарф'
                elif temp <= 10 and has_precipitation:
                    recommendation = 'Тёплая одежда + зонт или дождевик'
                else:
                    recommendation = 'Подходящая одежда для текущих условий'
            
            elif response.status_code == 404:
                weather_data = {'error': 'Город не найден'}
            else:
                weather_data = {'error': 'Ошибка получения данных о погоде'}
                
        except requests.exceptions.RequestException:
            weather_data = {'error': 'Ошибка сети. Проверьте подключение к интернету'}
        
    elif request.method == 'GET':
        # При GET-запросе получаем погоду для Москвы по умолчанию
        try:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&lang=ru&appid={API_KEY}"
            response = requests.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                weather_data = {
                    'city': data['name'],
                    'temperature': round(data['main']['temp']),
                    'feels_like': round(data['main']['feels_like']),
                    'description': data['weather'][0]['description'].capitalize(),
                    'icon': data['weather'][0]['icon'],
                    'humidity': data['main']['humidity'],
                    'wind_speed': round(data['wind']['speed'], 1)
                }
                
                # Формируем рекомендацию по одежде
                temp = weather_data['temperature']
                has_precipitation = any(data['weather'][0]['main'].lower() in ['rain', 'drizzle', 'snow'] for w in data['weather'])
                
                if temp > 25 and not has_precipitation:
                    recommendation = 'Легкая одежда, футболка, головной убор от солнца'
                elif temp >= 15 and temp <= 25:
                    recommendation = 'Джинсы, лёгкая кофта'
                elif temp >= 5 and temp < 15:
                    recommendation = 'Свитер, ветровка, куртка'
                elif temp <= 5 and not has_precipitation:
                    recommendation = 'Тёплая куртка, шапка, шарф'
                elif temp <= 10 and has_precipitation:
                    recommendation = 'Тёплая одежда + зонт или дождевик'
                else:
                    recommendation = 'Подходящая одежда для текущих условий'
            
        except:
            pass

    return render_template('index.html', 
                         weather_data=weather_data, 
                         recommendation=recommendation, 
                         city=city)

if __name__ == '__main__':
    app.run(debug=True)