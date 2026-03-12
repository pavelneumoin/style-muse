from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from database import save_log, load_items, add_item_db, delete_item_db
from services.weather import get_weather_data, get_tomorrow_weather_data, get_magnetic_storms
from services.yandex import get_combined_advice, call_yandexart, get_ai_explanation, get_clothing_history_fact
from services.wardrobe import get_outfit_for_avatar
from app_config import send_telegram_notification

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET', 'POST'], strict_slashes=False)
def index():
    
    weather_data = None
    ai_recommendation = None
    city = 'Москва'
    female_outfit = {}
    male_outfit = {}
    
    if request.method == 'POST':
        city = request.form.get('city', 'Москва').strip()
        if not city:
            city = 'Москва'
            
        action = request.form.get('action')
        if action == 'tomorrow':
            weather_data = get_tomorrow_weather_data(city)
        else:
            weather_data = get_weather_data(city)
    else:
        weather_data = get_weather_data(city)
    
    magnetic_data = get_magnetic_storms()
    
    ai_image_base64 = None
    if weather_data and 'error' not in weather_data:
        ai_recommendation = get_combined_advice(
            weather_data['temperature'],
            weather_data['description'],
            weather_data['wind_speed'],
            weather_data['humidity'],
            magnetic_data['level']
        )
        
        female_outfit = get_outfit_for_avatar(weather_data['temperature'], 'женский')
        male_outfit = get_outfit_for_avatar(weather_data['temperature'], 'мужской')

        if request.method == 'POST':
            female_names = [f'{item["colorName"].lower()} {item["name"].lower()}' for item in female_outfit.values() if item]
            male_names = [f'{item["colorName"].lower()} {item["name"].lower()}' for item in male_outfit.values() if item]
            
            target_outfit = female_names + male_names
                
            outfit_str = ", ".join(target_outfit) if target_outfit else "милая одежда"
            
            art_prompt = f"Уютная 3D иллюстрация в стиле Pixar. Погода: {weather_data['description']}. Рядом стоит шкаф с одеждой: {outfit_str}. Детская книжная сказка, яркие цвета, мягкий свет, без текста."
            ai_image_base64 = call_yandexart(art_prompt)
            
            send_telegram_notification(city, weather_data['temperature'], outfit_str)

        if request.method == 'POST':
            save_log(city, weather_data['temperature'], ai_recommendation, female_outfit, male_outfit, ai_image_base64)

    return render_template('index.html', 
                         weather_data=weather_data, 
                         ai_recommendation=ai_recommendation,
                         ai_image_base64=ai_image_base64,
                         city=city,
                         magnetic_level=magnetic_data['level'],
                         magnetic_text=magnetic_data['text'],
                         k_index=magnetic_data['k_index'],
                         female_outfit=female_outfit,
                         male_outfit=male_outfit)

@main_bp.route('/wardrobe')
def wardrobe():
    all_items = load_items()
    return render_template('wardrobe.html', items=all_items)

@main_bp.route('/add_item', methods=['GET', 'POST'])
def add_item_route():    
    
    if request.method == 'POST':
        item = {
            'name': request.form.get('name'),
            'category': request.form.get('category'),
            'colorHex': request.form.get('colorHex'),
            'colorName': request.form.get('colorName'),
            'seasons': request.form.getlist('seasons'),
            'warmth': request.form.get('warmth'),
            'gender': request.form.get('gender', 'унисекс')
        }
        add_item_db(item)
        return redirect(url_for('main.wardrobe'))
    return render_template('add_item.html')

@main_bp.route('/delete_item/<item_id>', methods=['POST'])
def delete_item_route(item_id):
    try:
        delete_item_db(item_id)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@main_bp.route('/api/ask_ai', methods=['POST'])
def api_ask_ai():
    data = request.json
    topic = data.get('topic')
    category = data.get('category')
    
    if category == 'fact':
        answer = get_clothing_history_fact()
    else:
        answer = get_ai_explanation(topic)
        
    return jsonify({'answer': answer})
