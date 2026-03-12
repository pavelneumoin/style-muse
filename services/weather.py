import os
import requests
import datetime

API_KEY = os.getenv('OPENWEATHER_API_KEY', 'f047613185f40b38100e65c37450b05a')

def get_magnetic_storms():
    """Получаем данные о геомагнитной обстановке"""
    try:
        url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if len(data) > 1:
                latest = data[-1]
                k_index = int(float(latest[1]))
                
                if k_index >= 5:
                    return {'level': 'high', 'text': 'Магнитная буря', 'k_index': f'{k_index}'}
                elif k_index >= 3:
                    return {'level': 'medium', 'text': 'Повышенная активность', 'k_index': f'{k_index}'}
                else:
                    return {'level': 'low', 'text': 'Спокойно', 'k_index': f'{k_index}'}
    except:
        pass
    
    return {'level': 'low', 'text': 'Спокойно', 'k_index': '1-2'}

def get_weather_data(city):
    """Получаем текущую погоду"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&units=metric&lang=ru&appid={API_KEY}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'city': data['name'],
                'temperature': round(data['main']['temp']),
                'feels_like': round(data['main']['feels_like']),
                'description': data['weather'][0]['description'].capitalize(),
                'icon': data['weather'][0]['icon'],
                'humidity': data['main']['humidity'],
                'wind_speed': round(data['wind']['speed'], 1)
            }
        elif response.status_code == 404:
            return {'error': 'Город не найден 🔍'}
        else:
            return {'error': 'Ошибка получения данных о погоде'}
            
    except requests.exceptions.RequestException:
        return {'error': 'Ошибка сети. Проверьте подключение к интернету'}

def get_tomorrow_weather_data(city):
    """Получаем прогноз погоде на завтра"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&units=metric&lang=ru&appid={API_KEY}"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            tomorrow = datetime.date.today() + datetime.timedelta(days=1)
            target_time = f"{tomorrow.isoformat()} 12:00:00"
            
            tomorrow_data = None
            for item in data['list']:
                if item['dt_txt'] >= target_time:
                    tomorrow_data = item
                    break
                    
            if not tomorrow_data:
                tomorrow_data = data['list'][8]
                
            return {
                'city': data['city']['name'],
                'temperature': round(tomorrow_data['main']['temp']),
                'feels_like': round(tomorrow_data['main']['feels_like']),
                'description': tomorrow_data['weather'][0]['description'].capitalize() + " (Завтра)",
                'icon': tomorrow_data['weather'][0]['icon'],
                'humidity': tomorrow_data['main']['humidity'],
                'wind_speed': round(tomorrow_data['wind']['speed'], 1)
            }
        elif response.status_code == 404:
            return {'error': 'Город не найден 🔍'}
        else:
            return {'error': 'Ошибка получения прогноза'}
            
    except requests.exceptions.RequestException:
        return {'error': 'Ошибка сети. Проверьте подключение к интернету'}
