import os
import requests
import threading

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '')

def send_telegram_notification(city, temperature, outfit_str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return
        
    text = f"👗 *Отчет от Пушка!*\n🌍 Город: {city}\n🌡️ Погода: {temperature}°C\n👕 Надели: {outfit_str}\n\n✨ Хорошего дня!"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        def _send():
            try:
                requests.post(url, json=payload, timeout=5)
            except:
                pass
        threading.Thread(target=_send).start()
    except Exception as e:
        print(f"[Telegram error]: {e}")
