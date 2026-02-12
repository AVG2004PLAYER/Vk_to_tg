import requests
import json
import os
from datetime import datetime

# ===== ТОКЕНЫ ИЗ СЕКРЕТОВ GITHUB =====
VK_TOKEN = os.environ.get("VK_TOKEN")
TG_TOKEN = os.enokenviron.get("TG_TOKEN")
TG_CHAT_ID = os.environ.get("TG_CHAT_ID")

# ID источников: беседы и личка группы
SOURCES = {
    2000000001: "ПТЭ-22",
    2000000002: "ПТЭ-22 с О.В. Денисовой",
    2000000003: "ПТЭ-22 с Е.А.",
    -235917989: "Файлы Эпштейна"
}

FILE_NAME = "last_ids.json"

def get_user_name(user_id):
    """Получает имя пользователя по ID"""
    try:
        url = "https://api.vk.com/method/users.get"
        params = {
            "user_ids": user_id,
            "access_token": VK_TOKEN,
            "v": "5.199"
        }
        resp = requests.get(url, params=params).json()
        if resp.get("response"):
            user = resp["response"][0]
            return f"{user['first_name']} {user['last_name']}"
    except:
        pass
    return f"id{user_id}"

def load_ids():
    """Загружает последние ID из файла"""
    try:
        if os.path.exists(FILE_NAME):
            with open(FILE_NAME, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def save_ids(ids):
    """Сохраняет ID в файл"""
    with open(FILE_NAME, 'w') as f:
        json.dump(ids, f)

def main():
    print("=" * 50)
    print("🚀 VK → TG Бот запущен")
    print(f"📊 Слушаю {len(SOURCES)} источников")
    print("=" * 50)
    
    # Загружаем сохраненные ID
    ids = load_ids()
    print(f"📁 Загружены last_id: {ids}")
    
    for peer_id, chat_name in SOURCES.items():
        peer_key = str(peer_id)
        last_id = ids.get(peer_key, 0)
        
        print(f"\n📬 {chat_name} (ID: {peer_id})")
        print(f"   🆔 Последний ID: {last_id}")
        
        # Получаем сообщения из VK
        try:
            resp = requests.get(
                "https://api.vk.com/method/messages.getHistory",
                params={
                    "peer_id": peer_id,
                    "count": 200,
                    "access_token": VK_TOKEN,
                    "v": "5.199"
                },
                timeout=30
            ).json()
        except Exception as e:
            print(f"   ❌ Ошибка запроса к VK: {e}")
            continue
        
        if "response" in resp:
            items = resp["response"]["items"]
            new_msgs = [m for m in items if m["id"] > last_id]
            
            print(f"   📨 Всего: {len(items)}, Новых: {len(new_msgs)}")
            
            for msg in reversed(new_msgs):
                msg_id = msg["id"]
                from_id = msg["from_id"]
                text = msg["text"]
                date = datetime.fromtimestamp(msg["date"]).strftime("%d.%m %H:%M")
                
                if not text.strip():
                    continue
                
                # Определяем автора
                if from_id < 0:
                    author = "📢 Эпштейн"
                else:
                    author = get_user_name(from_id)
                
                # Формируем сообщение
                tg_text = f"""📌 <b>{chat_name}</b>
👤 {author}
🕐 {date}

💬 {text}"""
                
                # Отправляем в Telegram
                try:
                    tg_resp = requests.post(
                        f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage",
                        json={
                            "chat_id": TG_CHAT_ID,
                            "text": tg_text,
                            "parse_mode": "HTML"
                        },
                        timeout=10
                    )
                    
                    if tg_resp.status_code == 200:
                        print(f"   ✅ [{date}] {author}: {text[:30]}...")
                    else:
                        print(f"   ❌ Ошибка TG: {tg_resp.text}")
                        
                except Exception as e:
                    print(f"   ❌ Ошибка отправки: {e}")
                
                # Обновляем last_id
                if msg_id > last_id:
                    last_id = msg_id
            
            # Сохраняем прогресс
            if last_id > ids.get(peer_key, 0):
                ids[peer_key] = last_id
                print(f"   💾 Новый last_id: {last_id}")
        else:
            error = resp.get('error', {}).get('error_msg', 'Неизвестно')
            print(f"   ❌ Ошибка VK: {error}")
    
    # Сохраняем все ID
    save_ids(ids)
    print(f"\n💾 Все ID сохранены в {FILE_NAME}")
    print("✅ Бот завершил работу")

if __name__ == "__main__":
    main()
