import sqlite3
import json
import os

DB_PATH = os.path.join('data', 'style_muse.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs('data', exist_ok=True)
    conn = get_db()
    c = conn.cursor()
    
    # Таблица вещей
    c.execute('''
        CREATE TABLE IF NOT EXISTS wardrobe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            profile_id INTEGER,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            gender TEXT DEFAULT 'унисекс',
            color TEXT NOT NULL,
            colorName TEXT NOT NULL,
            warmth TEXT NOT NULL,
            waterproof BOOLEAN NOT NULL,
            seasons TEXT NOT NULL
        )
    ''')
    
    # Таблица логов / сохраненных образов
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            city TEXT,
            temperature INTEGER,
            ai_advice TEXT,
            female_outfit TEXT,
            male_outfit TEXT,
            ai_image_url TEXT
        )
    ''')
    
    conn.commit()
    
    conn.commit()
    
    # Миграция из JSON, если БД пустая, а JSON есть
    c.execute('SELECT COUNT(*) FROM wardrobe')
    if c.fetchone()[0] == 0:
        if os.path.exists('data/wardrobe.json'):
            with open('data/wardrobe.json', 'r', encoding='utf-8') as f:
                items = json.load(f)
                for item in items:
                    c.execute('''
                        INSERT INTO wardrobe (name, category, gender, color, colorName, warmth, waterproof, seasons)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        item.get('name'), 
                        item.get('category'), 
                        item.get('gender', 'унисекс'),
                        item.get('color'), 
                        item.get('colorName'), 
                        item.get('warmth'), 
                        1 if item.get('waterproof') else 0, 
                        json.dumps(item.get('seasons', []), ensure_ascii=False)
                    ))
            conn.commit()
            print("[DB] Миграция из wardrobe.json успешно завершена.")
    
    conn.close()

# ========== Функции для гардероба ==========

def load_items():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM wardrobe')
    rows = c.fetchall()
    conn.close()
    
    items = []
    for row in rows:
        item = dict(row)
        item['waterproof'] = bool(item['waterproof'])
        item['seasons'] = json.loads(item['seasons'])
        items.append(item)
    return items

def add_item_db(data):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO wardrobe (name, category, gender, color, colorName, warmth, waterproof, seasons)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data['name'], 
        data['category'], 
        data.get('gender', 'унисекс'),
        data['color'], 
        data['colorName'], 
        data['warmth'], 
        1 if data.get('waterproof') else 0, 
        json.dumps(data.get('seasons', []), ensure_ascii=False)
    ))
    conn.commit()
    conn.close()

def update_item_db(item_id, data):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        UPDATE wardrobe 
        SET name=?, category=?, gender=?, color=?, colorName=?, warmth=?, waterproof=?, seasons=?
        WHERE id=?
    ''', (
        data['name'], 
        data['category'], 
        data.get('gender', 'унисекс'),
        data['color'], 
        data['colorName'], 
        data['warmth'], 
        1 if data.get('waterproof') else 0, 
        json.dumps(data.get('seasons', []), ensure_ascii=False),
        item_id
    ))
    conn.commit()
    conn.close()

def delete_item_db(item_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('DELETE FROM wardrobe WHERE id=?', (item_id,))
    conn.commit()
    conn.close()

def get_item_db(item_id):
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM wardrobe WHERE id=?', (item_id,))
    row = c.fetchone()
    conn.close()
    if row:
        item = dict(row)
        item['waterproof'] = bool(item['waterproof'])
        item['seasons'] = json.loads(item['seasons'])
        return item
    return None

def save_log(city, temperature, ai_advice, female_outfit, male_outfit, ai_image_url=None):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO logs (city, temperature, ai_advice, female_outfit, male_outfit, ai_image_url)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        city, temperature, ai_advice, 
        json.dumps(female_outfit, ensure_ascii=False) if female_outfit else None,
        json.dumps(male_outfit, ensure_ascii=False) if male_outfit else None,
        ai_image_url
    ))
    conn.commit()
    conn.close()

def get_logs():
    conn = get_db()
    c = conn.cursor()
    c.execute('SELECT * FROM logs ORDER BY created_at DESC LIMIT 50')
    rows = c.fetchall()
    conn.close()
    
    logs = []
    for row in rows:
        log = dict(row)
        if log['female_outfit']:
            log['female_outfit'] = json.loads(log['female_outfit'])
        if log['male_outfit']:
            log['male_outfit'] = json.loads(log['male_outfit'])
        logs.append(log)
    return logs
