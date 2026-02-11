import requests
import json
import os
from datetime import datetime

VK_TOKEN = "vk1.a.IXBT-TIZANhoDpDtjcyZJvPOWQfhwLrbatck_qYckqKAUfNopPYJxqpJRuk5aPtB_xihHfMeRZklj-bcCoH0VPqvTes48geqiSDg3HTQRN9hORNcKJNY81znSMMdDw-kqabzfFmzlGrbOaIJlymOvsTfod2upwa0RYt8Kzvds8ZyGYUt8PmFJgMr_dU5koYh43BViXFymHMWKICo-vu6YQ"


TG_TOKEN = "8550071219:AAGFYpOWPfkwRa4J7ZeJ1pKDAwfTBolgy-o"
TG_CHAT_ID = "-5116486001"
CHAT_ID = 2000000001
CHAT_ID1 = 2000000002
CHAT_ID2 = 2000000003
CHAT_ID3 = -235917989
FILE_NAME = "last_id.json"

def main():
    # Загружаем последний ID
    last_id = 0
    if os.path.exists(FILE_NAME):
        with open(FILE_NAME) as f:
            last_id = json.load(f).get('id', 0)
    
    # Получаем 200 последних сообщений
    resp = requests.get("https://api.vk.com/method/messages.getHistory", params={
        "peer_id": CHAT_ID3,
        "count": 200,
        "access_token": VK_TOKEN,
        "v": "5.199"
    }).json()
    
    if "response" in resp:
        # Берем только новые (ID больше last_id)
        new_msgs = [m for m in resp["response"]["items"] if m["id"] > last_id]
        
        # Отправляем от старых к новым
        for msg in reversed(new_msgs):
            text = msg["text"]
            if text.strip():
                requests.post(f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage", json={
                    "chat_id": TG_CHAT_ID,
                    "text": f"💬 {text}....GOIDA"
                })
            
            # Запоминаем самый большой ID
            if msg["id"] > last_id:
                last_id = msg["id"]
        
        # Сохраняем
        with open(FILE_NAME, 'w') as f:
            json.dump({'id': last_id, 'time': str(datetime.now())}, f)
        
        print(f"✅ Отправлено {len(new_msgs)} сообщений, last_id={last_id}")

if __name__ == "__main__":
    main()