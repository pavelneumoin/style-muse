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

# YandexGPT Configuration
YANDEX_FOLDER_ID = os.environ.get('YANDEX_FOLDER_ID', '')
YANDEX_API_KEY = os.environ.get('YANDEX_API_KEY', '')
YANDEX_GPT_MODEL = f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite/latest"

# Проверка при старте
print(f"[STARTUP] YANDEX_FOLDER_ID: {YANDEX_FOLDER_ID}")
print(f"[STARTUP] YANDEX_API_KEY loaded: {bool(YANDEX_API_KEY)}")

# ========== Цветовая палитра гардероба ==========
import random

COLOR_PALETTE = [
    # Базовые цвета
    {"hex": "#FFFFFF", "name": "Белый"},
    {"hex": "#1A1A1A", "name": "Чёрный"},
    {"hex": "#808080", "name": "Серый"},
    {"hex": "#5D6D7E", "name": "Тёмно-серый"},
    
    # Красные оттенки
    {"hex": "#DC143C", "name": "Красный"},
    {"hex": "#B22222", "name": "Тёмно-красный"},
    {"hex": "#FF6B6B", "name": "Коралловый"},
    {"hex": "#722F37", "name": "Бордовый"},
    {"hex": "#C0392B", "name": "Алый"},
    
    # Розовые оттенки
    {"hex": "#FFB6C1", "name": "Нежно-розовый"},
    {"hex": "#FF69B4", "name": "Ярко-розовый"},
    {"hex": "#FF6B9D", "name": "Розовый"},
    {"hex": "#E8C4C4", "name": "Пудровый"},
    {"hex": "#FFC0CB", "name": "Светло-розовый"},
    
    # Оранжевые оттенки
    {"hex": "#FF8C00", "name": "Оранжевый"},
    {"hex": "#FF7F50", "name": "Коралловый"},
    {"hex": "#E67E22", "name": "Тёплый оранжевый"},
    {"hex": "#D35400", "name": "Тыквенный"},
    
    # Жёлтые оттенки
    {"hex": "#FFD700", "name": "Золотой"},
    {"hex": "#F1C40F", "name": "Жёлтый"},
    {"hex": "#FFFACD", "name": "Лимонный"},
    {"hex": "#DEB887", "name": "Песочный"},
    
    # Бежевые оттенки
    {"hex": "#F5DEB3", "name": "Бежевый"},
    {"hex": "#D2B48C", "name": "Тёмно-бежевый"},
    {"hex": "#E8D4C4", "name": "Кремовый"},
    {"hex": "#FFFAF0", "name": "Слоновая кость"},
    
    # Коричневые оттенки
    {"hex": "#8B4513", "name": "Коричневый"},
    {"hex": "#5C4033", "name": "Шоколадный"},
    {"hex": "#A0522D", "name": "Терракотовый"},
    {"hex": "#2F1810", "name": "Тёмно-коричневый"},
    
    # Зелёные оттенки
    {"hex": "#50C878", "name": "Изумрудный"},
    {"hex": "#355E3B", "name": "Тёмно-зелёный"},
    {"hex": "#2ECC71", "name": "Мятный"},
    {"hex": "#808000", "name": "Оливковый"},
    {"hex": "#27AE60", "name": "Зелёный"},
    {"hex": "#1ABC9C", "name": "Бирюзово-зелёный"},
    
    # Синие оттенки
    {"hex": "#4169E1", "name": "Синий"},
    {"hex": "#6CA0DC", "name": "Голубой"},
    {"hex": "#2C3E50", "name": "Тёмно-синий"},
    {"hex": "#3498DB", "name": "Небесный"},
    {"hex": "#4A90D9", "name": "Васильковый"},
    {"hex": "#1E3A5F", "name": "Полуночный синий"},
    
    # Фиолетовые оттенки
    {"hex": "#B19CD9", "name": "Лавандовый"},
    {"hex": "#9B59B6", "name": "Фиолетовый"},
    {"hex": "#8E44AD", "name": "Пурпурный"},
    {"hex": "#E6E6FA", "name": "Светло-лавандовый"},
    {"hex": "#663399", "name": "Индиго"},
    
    # Металлические оттенки
    {"hex": "#C0C0C0", "name": "Серебро"},
    {"hex": "#CD7F32", "name": "Бронза"},
]

def get_random_color():
    """Возвращает случайный цвет из палитры"""
    color = random.choice(COLOR_PALETTE)
    return color["hex"], color["name"]

def get_color_by_hex(hex_code):
    """Находит название цвета по HEX-коду"""
    for color in COLOR_PALETTE:
        if color["hex"].lower() == hex_code.lower():
            return color["name"]
    return "Неизвестный"


def call_yandexgpt(prompt, temperature=0.7, max_tokens=200, retries=3):
    """Вызов YandexGPT API с retry логикой"""
    import time
    import random
    
    if not YANDEX_API_KEY:
        print("[DEBUG] No YANDEX_API_KEY", flush=True)
        return None
    
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Api-Key {YANDEX_API_KEY}'
    }
    
    # Добавляем случайность в промпт для разнообразия
    random_seed = random.randint(1, 1000)
    enhanced_prompt = f"{prompt}\n\n[Вариация #{random_seed}]"
    
    payload = {
        "modelUri": YANDEX_GPT_MODEL,
        "completionOptions": {
            "stream": False,
            "temperature": min(temperature + 0.1, 1.0),  # Чуть выше температура для разнообразия
            "maxTokens": str(max_tokens)
        },
        "messages": [
            {"role": "user", "text": enhanced_prompt}
        ]
    }
    
    for attempt in range(retries):
        try:
            print(f"[DEBUG] YandexGPT attempt {attempt + 1}/{retries}", flush=True)
            response = requests.post(url, headers=headers, json=payload, timeout=25)
            print(f"[DEBUG] YandexGPT response status: {response.status_code}", flush=True)
            
            if response.status_code == 200:
                result = response.json()
                text = result['result']['alternatives'][0]['message']['text']
                print(f"[DEBUG] YandexGPT SUCCESS: {text[:50]}...", flush=True)
                return text
            elif response.status_code == 429:  # Rate limit
                print(f"[DEBUG] Rate limited, waiting...", flush=True)
                time.sleep(2 * (attempt + 1))
                continue
            else:
                print(f"[DEBUG] YandexGPT ERROR: {response.text[:200]}", flush=True)
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
        except requests.exceptions.Timeout:
            print(f"[DEBUG] Timeout on attempt {attempt + 1}", flush=True)
            if attempt < retries - 1:
                time.sleep(1)
                continue
        except Exception as e:
            print(f"[DEBUG] YandexGPT EXCEPTION: {e}", flush=True)
            if attempt < retries - 1:
                time.sleep(1)
                continue
    
    return None


def get_ai_recommendation(temperature, description, humidity, wind_speed):
    """Получаем рекомендации от YandexGPT AI"""
    prompt = f"""Ты персональный стилист для девушки. Погода сейчас: температура {temperature}°C, {description}, влажность {humidity}%, ветер {wind_speed} м/с.
        
Дай краткую стильную рекомендацию по одежде (2-3 предложения). Используй эмодзи. Будь дружелюбной и современной. Предложи конкретные вещи и цвета."""

    result = call_yandexgpt(prompt, temperature=0.7, max_tokens=200)
    if result:
        return result
    
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


def get_combined_advice(temperature, description, wind_speed, humidity, magnetic_level):
    """Получаем объединенный совет (здоровье + стиль) от YandexGPT"""
    prompt = f"""Ты добрый помощник для маленьких детей. Погода: {temperature}°C, {description}, ветер {wind_speed} м/с, влажность {humidity}%. Магнитная обстановка: {magnetic_level}.
        
        Придумай ОДИН короткий и веселый совет, который объединяет:
        1. Что лучше надеть (стиль).
        2. Как сберечь здоровье (здоровье).
        
        Пиши очень просто, как для ребенка 5-7 лет. Используй смайлики. Не больше 3 предложений."""

    result = call_yandexgpt(prompt, temperature=0.7, max_tokens=300)
    if result:
        return result
    
    return "Сегодня отличный день! Одевайся тепло и не забывай улыбаться! ☀️"


def get_ai_explanation(topic):
    """Получаем объяснение погодного или научного термина для детей"""
    print(f"[DEBUG] get_ai_explanation called with topic: {topic}")
    
    prompt = f"""Ты — весёлый учитель природоведения для детей 5-8 лет. 

Тема: {topic}

Расскажи про это интересно и понятно:
1. Что это такое? (простыми словами)
2. Почему это важно знать?
3. Интересный факт или совет!

Используй много эмодзи! Пиши весело и дружелюбно, как будто разговариваешь с ребёнком. 
Примерно 4-6 предложений. Каждый раз придумывай что-то НОВОЕ и уникальное!"""

    result = call_yandexgpt(prompt, temperature=0.95, max_tokens=400)
    if result:
        return result
    
    return f"{topic} — это очень интересно! Спроси у взрослых, они расскажут! 🤓"


def get_clothing_history_fact():
    """Генерирует интересный исторический факт об одежде"""
    prompt = """Расскажи один удивительный исторический факт про какой-нибудь предмет одежды (шапку, шарф, пальто, пуговицы и т.д.) для детей. 
        Например: откуда это взялось или из чего делали раньше. 
        Очень кратко, увлекательно, с эмодзи."""

    result = call_yandexgpt(prompt, temperature=0.8, max_tokens=200)
    if result:
        return result
    
    return "Одежда имеет долгую и интересную историю! 🧵"


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
    
    # === ФИЛЬТРАЦИЯ АКСЕССУАРОВ (удаляем кольца/серьги, добавляем зонт/очки) ===
    # Это сделано через выбор категорий. Предполагаем, что в БД есть категории "Аксессуар"
    # Мы будем специально искать нужные аксессуары по имени или тегу, если они есть.
    
    outfit = {}
    
    # Вспомогательная функция для поиска конкретного аксессуара
    def find_specific_accessory(keywords):
        for item in items:
            if item.get('category') == 'Аксессуар':
                name_lower = item.get('name', '').lower()
                if any(k in name_lower for k in keywords):
                    return item
        return None

    pass_earrings = True # Флаг чтобы пропускать "сережки", "кольца" в общем выборе
    
    if temperature > 25:
        # Лето
        if gender == 'женский':
            outfit['dress'] = filter_items('Платья', gender)
            if not outfit['dress']:
                outfit['top'] = filter_items('Верх', gender)
                outfit['bottom'] = filter_items('Низ', gender)
        else:
            outfit['top'] = filter_items('Верх', gender)
            outfit['bottom'] = filter_items('Низ', gender)
        
        # Аксессуары для жары
        sunglasses = find_specific_accessory(['очки', 'солнечные'])
        if sunglasses:
            outfit['accessory_special'] = sunglasses
        
    elif temperature >= 15:
        # Весна
        outfit['top'] = filter_items('Верх', gender)
        outfit['bottom'] = filter_items('Низ', gender)
        
    elif temperature >= 5:
        # Осень
        outfit['top'] = filter_items('Верх', gender)
        outfit['bottom'] = filter_items('Низ', gender)
        outfit['coat'] = filter_items('Верхняя одежда', gender)
        
    else:
        # Зима
        outfit['top'] = filter_items('Верх', gender)
        outfit['bottom'] = filter_items('Низ', gender)
        outfit['coat'] = filter_items('Верхняя одежда', gender)
        outfit['hat'] = filter_items('Головной убор', gender)
        
    # Обувь всегда
    outfit['shoes'] = filter_items('Обувь', gender)
    
    # Дополнительные проверки на зонт (если сыро, но мы не знаем точно влажность здесь,
    # но можно добавить рандомно или если бы передавали description. 
    # В текущей сигнатуре description нет. Оставим просто общий аксессуар если не спец.)
    
    if 'accessory_special' not in outfit:
        # Пытаемся найти общий аксессуар, но фильтруем лишнее
        general_acc = filter_items('Аксессуар', gender)
        if general_acc:
            name_lower = general_acc['name'].lower()
            bad_words = ['серьг', 'кольц', 'бусы', 'украшение']
            if not any(bw in name_lower for bw in bad_words):
                outfit['accessory'] = general_acc

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
    
    # Получаем AI рекомендации (объединенные)
    if weather_data and 'error' not in weather_data:
        # Combined advice
        ai_recommendation = get_combined_advice(
            weather_data['temperature'],
            weather_data['description'],
            weather_data['wind_speed'],
            weather_data['humidity'],
            magnetic_data['level']
        )
        
        # Подбираем одежду
        female_outfit = get_outfit_for_avatar(weather_data['temperature'], 'женский')
        male_outfit = get_outfit_for_avatar(weather_data['temperature'], 'мужской')

    return render_template('index.html', 
                         weather_data=weather_data, 
                         ai_recommendation=ai_recommendation,
                         # health_tips удален т.к. объединен
                         city=city,
                         magnetic_level=magnetic_data['level'],
                         magnetic_text=magnetic_data['text'],
                         k_index=magnetic_data['k_index'],
                         female_outfit=female_outfit,
                         male_outfit=male_outfit,
                         colors=COLOR_PALETTE)  # передаем все цвета

@app.route('/api/explain_term', methods=['POST'])
def api_explain_term():
    data = request.json
    term = data.get('term')
    if not term:
        return jsonify({'error': 'No term provided'}), 400
    explanation = get_ai_explanation(term)
    return jsonify({'explanation': explanation})

@app.route('/api/clothing_fact', methods=['POST'])
def api_clothing_fact():
    fact = get_clothing_history_fact()
    return jsonify({'fact': fact})


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
        
        # Получаем цвет: если выбран пользователем - используем его, иначе случайный
        selected_color = request.form.get('color', '')
        if selected_color:
            color_hex = selected_color
            color_name = get_color_by_hex(selected_color)
        else:
            color_hex, color_name = get_random_color()
        
        new_item = {
            'id': get_next_id(),
            'name': request.form['name'],
            'category': request.form['category'],
            'color': color_hex,
            'colorName': color_name,
            'warmth': request.form['warmth'],
            'waterproof': 'waterproof' in request.form,
            'seasons': [season for season in ['лето', 'осень', 'зима', 'весна', 'межсезонье'] if season in request.form]
        }
        
        items.append(new_item)
        save_items(items)
        
        return redirect(url_for('wardrobe'))
    
    return render_template('add_item.html', colors=COLOR_PALETTE)

@app.route('/edit_item/<int:id>', methods=['GET', 'POST'])
def edit_item(id):
    items = load_items()
    item = next((item for item in items if item['id'] == id), None)
    
    if not item:
        return redirect(url_for('wardrobe'))
    
    if request.method == 'POST':
        item['name'] = request.form['name']
        item['category'] = request.form['category']
        
        # Обновляем цвет
        selected_color = request.form.get('color', '')
        if selected_color:
            item['color'] = selected_color
            item['colorName'] = get_color_by_hex(selected_color)
        
        item['warmth'] = request.form['warmth']
        item['waterproof'] = 'waterproof' in request.form
        item['seasons'] = [season for season in ['лето', 'осень', 'зима', 'весна', 'межсезонье'] if season in request.form]
        
        save_items(items)
        return redirect(url_for('wardrobe'))
    
    return render_template('edit_item.html', item=item, colors=COLOR_PALETTE)

if __name__ == '__main__':
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    app.run(debug=True)