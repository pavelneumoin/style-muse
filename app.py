from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import requests
import json
import uuid
from dotenv import load_dotenv
from datetime import datetime

# Загружаем переменные окружения
load_dotenv()

app = Flask(__name__)

# API ключи
API_KEY = os.getenv('OPENWEATHER_API_KEY', 'f047613185f40b38100e65c37450b05a')

# GigaChat Configuration
# For Render: uses environment variable
# For local: uses hardcoded key
GIGACHAT_CREDENTIALS = os.environ.get('GIGACHAT_CREDENTIALS', 'MDE5Yjg3ZGQtYmQ2My03ZTYwLTk1ZmUtYjk4ZmZiYTVjMmI3OmY3YzZjZmNjLWQ2MzctNDMxNy04NTgzLWY0YzIzMDJkNTdmYQ==')
GIGACHAT_SCOPE = os.environ.get('GIGACHAT_SCOPE', 'GIGACHAT_API_CORP')


def get_gigachat_token():
    """Получаем токен для GigaChat API"""
    try:
        # Если нет ключей, возвращаем None
        if not GIGACHAT_CREDENTIALS:
            return None
        
        url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'RqUID': str(uuid.uuid4()),
            'Authorization': f'Basic {GIGACHAT_CREDENTIALS}'
        }
        data = {'scope': GIGACHAT_SCOPE}
        
        response = requests.post(url, headers=headers, data=data, verify=False, timeout=10)
        
        if response.status_code == 200:
            return response.json().get('access_token')
    except Exception as e:
        print(f"GigaChat token error: {e}")
    return None


def get_ai_recommendation(temperature, description, humidity, wind_speed):
    """Получаем рекомендации от GigaChat AI"""
    token = get_gigachat_token()
    
    if not token:
        # Fallback рекомендации без AI
        return get_fallback_recommendation(temperature, description)
    
    try:
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        prompt = f"""Ты персональный стилист для девушки. Погода сейчас: температура {temperature}°C, {description}, влажность {humidity}%, ветер {wind_speed} м/с.
        
Дай краткую стильную рекомендацию по одежде (2-3 предложения). Используй эмодзи. Будь дружелюбной и современной. Предложи конкретные вещи и цвета."""

        payload = {
            "model": "GigaChat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 200
        }
        
        response = requests.post(url, headers=headers, json=payload, verify=False, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"GigaChat API error: {e}")
    
    return get_fallback_recommendation(temperature, description)


def get_fallback_recommendation(temperature, description):
    """Рекомендации без AI"""
    desc_lower = description.lower()
    has_rain = 'дождь' in desc_lower or 'ливень' in desc_lower or 'осадки' in desc_lower
    has_snow = 'снег' in desc_lower
    
    if temperature > 25:
        base = "👗 Лёгкое платье или льняной топ с шортами. Не забудь солнцезащитные очки и крем SPF!"
        if has_rain:
            base += " ☂️ Возьми компактный зонтик."
    elif temperature >= 15:
        base = "💜 Идеально для блузки с джинсами или юбки миди. Добавь лёгкий кардиган на вечер!"
        if has_rain:
            base += " 🌧️ Лучше взять непромокаемую куртку."
    elif temperature >= 5:
        base = "🧥 Уютный свитер или худи + тренч или куртка. Не забудь лёгкий шарфик!"
        if has_rain:
            base += " ☔ Водонепроницаемая обувь — must have!"
    else:
        base = "❄️ Тёплое пальто или пуховик, шапка и шарф. Тёплые сапоги согреют ножки!"
        if has_snow:
            base += " ⛄ Выбирай обувь с нескользящей подошвой."
    
    return base


def get_health_tips(temperature, description, magnetic_level):
    """Получаем советы по здоровью для детей от GigaChat"""
    token = get_gigachat_token()
    
    if not token:
        return get_fallback_health_tips(temperature, description, magnetic_level)
    
    try:
        url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}'
        }
        
        prompt = f"""Ты детский врач-педиатр. Погода сейчас: {temperature}°C, {description}. Магнитная активность: {magnetic_level}.

Дай 3 коротких полезных совета для детей по здоровью на сегодня с учетом погоды. Используй эмодзи. Будь дружелюбным и понятным для детей. Каждый совет — одно предложение."""

        payload = {
            "model": "GigaChat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 250
        }
        
        response = requests.post(url, headers=headers, json=payload, verify=False, timeout=15)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
    except Exception as e:
        print(f"GigaChat health tips error: {e}")
    
    return get_fallback_health_tips(temperature, description, magnetic_level)


def get_fallback_health_tips(temperature, description, magnetic_level):
    """Советы по здоровью без AI"""
    tips = []
    desc_lower = description.lower()
    
    if temperature > 25:
        tips.append("☀️ Пей больше воды — минимум 6-8 стаканов в день!")
        tips.append("🧴 Наноси солнцезащитный крем перед прогулкой.")
        tips.append("🕐 Гуляй утром или вечером, когда не так жарко.")
    elif temperature >= 15:
        tips.append("🚶 Отличная погода для прогулки! Проведи на улице час.")
        tips.append("🍎 Ешь свежие фрукты и овощи для витаминов.")
        tips.append("😴 Ложись спать вовремя — отдых важен!")
    elif temperature >= 5:
        tips.append("🧣 Надень шарф, чтобы не простудить горло.")
        tips.append("🍵 Пей тёплый чай с мёдом для иммунитета.")
        tips.append("🧤 Не забудь перчатки, если руки мёрзнут!")
    else:
        tips.append("❄️ Одевайся тепло — береги себя от холода!")
        tips.append("🍊 Ешь витамин C — апельсины и лимоны.")
        tips.append("🏠 После прогулки сразу переодевайся в сухое.")
    
    if 'дождь' in desc_lower:
        tips[2] = "☔ Не гуляй под дождём — можно промокнуть и заболеть."
    
    if magnetic_level == 'high':
        tips[0] = "💧 Пей много воды и отдыхай — сегодня магнитная буря."
    
    return "\n".join(tips)


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
    """Получаем данные о погоде"""
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


def get_outfit_for_avatar(temperature, gender):
    """Выбираем одежду из гардероба по температуре и полу"""
    items = load_items()
    
    # Определяем сезон по температуре
    if temperature > 25:
        season = 'лето'
        warmth_priority = ['Лёгкий', 'Средняя']
    elif temperature >= 15:
        season = 'весна'
        warmth_priority = ['Лёгкий', 'Средняя']
    elif temperature >= 5:
        season = 'осень'
        warmth_priority = ['Средняя', 'Тёплый']
    else:
        season = 'зима'
        warmth_priority = ['Тёплый', 'Средняя']
    
    def filter_items(category, prefer_gender):
        """Фильтруем вещи по категории, сезону и полу"""
        matching = []
        for item in items:
            if item.get('category') != category:
                continue
            item_gender = item.get('gender', 'унисекс')
            if item_gender not in [prefer_gender, 'унисекс']:
                continue
            if season not in item.get('seasons', []):
                continue
            matching.append(item)
        
        # Сортируем по приоритету теплоты
        def warmth_score(item):
            w = item.get('warmth', 'Средняя')
            return warmth_priority.index(w) if w in warmth_priority else 10
        
        matching.sort(key=warmth_score)
        return matching[0] if matching else None
    
    # Выбираем по категориям в зависимости от температуры
    outfit = {}
    
    if temperature > 25:
        # Лето - платье или топ + шорты
        if gender == 'женский':
            outfit['dress'] = filter_items('Платья', gender)
            if not outfit['dress']:
                outfit['top'] = filter_items('Верх', gender)
                outfit['bottom'] = filter_items('Низ', gender)
        else:
            outfit['top'] = filter_items('Верх', gender)
            outfit['bottom'] = filter_items('Низ', gender)
    elif temperature >= 15:
        # Весна - блузка/рубашка + джинсы
        outfit['top'] = filter_items('Верх', gender)
        outfit['bottom'] = filter_items('Низ', gender)
    elif temperature >= 5:
        # Осень - свитер/куртка + брюки
        outfit['top'] = filter_items('Верх', gender)
        outfit['bottom'] = filter_items('Низ', gender)
        outfit['coat'] = filter_items('Верхняя одежда', gender)
    else:
        # Зима - пальто/пуховик + тёплые вещи
        outfit['top'] = filter_items('Верх', gender)
        outfit['bottom'] = filter_items('Низ', gender)
        outfit['coat'] = filter_items('Верхняя одежда', gender)
        outfit['hat'] = filter_items('Головной убор', gender)
        outfit['accessory'] = filter_items('Аксессуар', gender)
    
    # Обувь всегда
    outfit['shoes'] = filter_items('Обувь', gender)
    
    return {k: v for k, v in outfit.items() if v}  # Убираем None


@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    ai_recommendation = None
    health_tips = None
    city = 'Москва'
    female_outfit = {}
    male_outfit = {}
    
    if request.method == 'POST':
        city = request.form.get('city', 'Москва').strip()
        if not city:
            city = 'Москва'
    
    # Получаем данные о погоде
    weather_data = get_weather_data(city)
    
    # Получаем данные о магнитных бурях
    magnetic_data = get_magnetic_storms()
    
    # Получаем AI рекомендации и советы по здоровью
    if weather_data and 'error' not in weather_data:
        ai_recommendation = get_ai_recommendation(
            weather_data['temperature'],
            weather_data['description'],
            weather_data['humidity'],
            weather_data['wind_speed']
        )
        # Подбираем одежду из гардероба для аватаров
        female_outfit = get_outfit_for_avatar(weather_data['temperature'], 'женский')
        male_outfit = get_outfit_for_avatar(weather_data['temperature'], 'мужской')
        # Получаем советы по здоровью для детей
        health_tips = get_health_tips(
            weather_data['temperature'],
            weather_data['description'],
            magnetic_data['level']
        )

    return render_template('index.html', 
                         weather_data=weather_data, 
                         ai_recommendation=ai_recommendation,
                         health_tips=health_tips,
                         city=city,
                         magnetic_level=magnetic_data['level'],
                         magnetic_text=magnetic_data['text'],
                         k_index=magnetic_data['k_index'],
                         female_outfit=female_outfit,
                         male_outfit=male_outfit)


# ========== Wardrobe Functions ==========

def load_items():
    if not os.path.exists('data/wardrobe.json'):
        return []
    with open('data/wardrobe.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def save_items(items):
    with open('data/wardrobe.json', 'w', encoding='utf-8') as f:
        json.dump(items, f, ensure_ascii=False, indent=2)

def get_next_id():
    items = load_items()
    return max([item['id'] for item in items], default=0) + 1

@app.after_request
def add_header(r):
    # Disable caching for development
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    return r

@app.route('/delete_item/<int:id>', methods=['POST'])
def delete_item(id):
    items = load_items()
    items = [item for item in items if item['id'] != id]
    save_items(items)
    return redirect(url_for('wardrobe'))

@app.route('/wardrobe')
def wardrobe():
    items = load_items()
    return render_template('wardrobe.html', items=items)

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        items = load_items()
        
        new_item = {
            'id': get_next_id(),
            'name': request.form['name'],
            'category': request.form['category'],
            'warmth': request.form['warmth'],
            'waterproof': 'waterproof' in request.form,
            'seasons': [season for season in ['лето', 'осень', 'зима', 'весна', 'межсезонье'] if season in request.form]
        }
        
        items.append(new_item)
        save_items(items)
        
        return redirect(url_for('wardrobe'))
    
    return render_template('add_item.html')

@app.route('/edit_item/<int:id>', methods=['GET', 'POST'])
def edit_item(id):
    items = load_items()
    item = next((item for item in items if item['id'] == id), None)
    
    if not item:
        return redirect(url_for('wardrobe'))
    
    if request.method == 'POST':
        item['name'] = request.form['name']
        item['category'] = request.form['category']
        item['warmth'] = request.form['warmth']
        item['waterproof'] = 'waterproof' in request.form
        item['seasons'] = [season for season in ['лето', 'осень', 'зима', 'весна', 'межсезонье'] if season in request.form]
        
        save_items(items)
        return redirect(url_for('wardrobe'))
    
    return render_template('edit_item.html', item=item)

if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    app.run(debug=True)