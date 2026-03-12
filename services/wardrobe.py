from database import load_items

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
    
    outfit = {}
    
    def find_specific_accessory(keywords):
        for item in items:
            if item.get('category') == 'Аксессуар':
                name_lower = item.get('name', '').lower()
                if any(k in name_lower for k in keywords):
                    return item
        return None

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
        
    outfit['shoes'] = filter_items('Обувь', gender)
    
    if 'accessory_special' not in outfit:
        general_acc = filter_items('Аксессуар', gender)
        if general_acc:
            name_lower = general_acc['name'].lower()
            bad_words = ['серьг', 'кольц', 'бусы', 'украшение']
            if not any(bw in name_lower for bw in bad_words):
                outfit['accessory'] = general_acc

    return {k: v for k, v in outfit.items() if v}
