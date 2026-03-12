import os
import requests
import random
import time

YANDEX_FOLDER_ID = os.environ.get('YANDEX_FOLDER_ID', '')
YANDEX_API_KEY = os.environ.get('YANDEX_API_KEY', '')
YANDEX_GPT_MODEL = f"gpt://{YANDEX_FOLDER_ID}/yandexgpt-lite/latest"

def call_yandexgpt(prompt, temperature=0.7, max_tokens=200, retries=3):
    """Вызов YandexGPT API с retry логикой"""
    if not YANDEX_API_KEY:
        print("[DEBUG] No YANDEX_API_KEY", flush=True)
        return None
    
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Api-Key {YANDEX_API_KEY}'
    }
    
    random_seed = random.randint(1, 1000)
    enhanced_prompt = f"{prompt}\n\n[Вариация #{random_seed}]"
    
    payload = {
        "modelUri": YANDEX_GPT_MODEL,
        "completionOptions": {
            "stream": False,
            "temperature": min(temperature + 0.1, 1.0),
            "maxTokens": str(max_tokens)
        },
        "messages": [
            {"role": "user", "text": enhanced_prompt}
        ]
    }
    
    for attempt in range(retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=25)
            if response.status_code == 200:
                result = response.json()
                return result['result']['alternatives'][0]['message']['text']
            elif response.status_code == 429:
                time.sleep(2 * (attempt + 1))
                continue
            else:
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(1)
                continue
    return None

def call_yandexart(prompt, retries=15):
    """Вызов YandexArt API для генерации картинки"""
    if not YANDEX_API_KEY:
        print("[DEBUG] No YANDEX_API_KEY for Art", flush=True)
        return None
        
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/imageGenerationAsync"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Api-Key {YANDEX_API_KEY}'
    }
    
    payload = {
        "modelUri": f"art://{YANDEX_FOLDER_ID}/yandex-art/latest",
        "generationOptions": {
            "seed": str(random.randint(1, 10000)),
            "aspectRatio": {"widthRatio": 1, "heightRatio": 1}
        },
        "messages": [
            {"weight": 1, "text": prompt}
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        if response.status_code == 200:
            operation_id = response.json().get('id')
            if not operation_id:
                return None
                
            poll_url = f"https://llm.api.cloud.yandex.net/operations/{operation_id}"
            poll_headers = {'Authorization': f'Api-Key {YANDEX_API_KEY}'}
            
            for _ in range(retries):
                time.sleep(2)
                poll_resp = requests.get(poll_url, headers=poll_headers, timeout=5)
                if poll_resp.status_code == 200:
                    poll_data = poll_resp.json()
                    if poll_data.get('done'):
                        try:
                            return f"data:image/jpeg;base64,{poll_data['response']['image']}"
                        except KeyError:
                            return None
    except Exception as e:
        pass
        
    return None

def get_combined_advice(temperature, description, wind_speed, humidity, magnetic_level):
    prompt = f"Ты добрый помощник для маленьких детей. Погода: {temperature}°C, {description}, ветер {wind_speed} м/с, влажность {humidity}%. Магнитная обстановка: {magnetic_level}. Придумай ОДИН короткий и веселый совет, который объединяет: 1. Что лучше надеть (стиль). 2. Как сберечь здоровье (здоровье). Пиши очень просто, как для ребенка 5-7 лет. Используй смайлики. Не больше 3 предложений."
    result = call_yandexgpt(prompt, temperature=0.7, max_tokens=300)
    return result if result else "Сегодня отличный день! Одевайся тепло и не забывай улыбаться! ☀️"

def get_ai_explanation(topic):
    prompt = f"Ты — весёлый учитель природоведения для детей 5-8 лет. Тема: {topic}. Расскажи про это интересно и понятно: 1. Что это такое? 2. Почему это важно знать? 3. Интересный факт или совет! Используй много эмодзи! Примерно 4-6 предложений."
    result = call_yandexgpt(prompt, temperature=0.95, max_tokens=400)
    return result if result else f"{topic} — это очень интересно! Спроси у взрослых, они расскажут! 🤓"

def get_clothing_history_fact():
    prompt = "Расскажи один удивительный исторический факт про какой-нибудь предмет одежды для детей. Очень кратко, увлекательно, с эмодзи."
    result = call_yandexgpt(prompt, temperature=0.8, max_tokens=200)
    return result if result else "Одежда имеет долгую и интересную историю! 🧵"
