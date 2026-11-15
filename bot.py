import os
import random
import urllib.parse
import requests

VK_TOKEN = os.environ["VK_TOKEN"]
VK_GROUP_ID = int(os.environ["VK_GROUP_ID"])

TOPICS = [
    "одинокий волк, ночь, дождь, верность своим принципам",
    "черная BMW на ночной трассе, туман, путь к цели",
    "пацанская дружба, брат за брата, проверка временем",
    "спортзал, турники, дисциплина, работа над собой без оправданий",
    "советские панельки ночью, тишина, размышления о жизни"
]

IMAGE_PROMPTS = [
    "black and white photography, fierce lone wolf in rainy dark city night, cinematic lighting, 8k",
    "black tinted BMW E38 on empty foggy night road, glowing headlights, wet asphalt, moody, 8k",
    "athletic man doing pull-ups on outdoor street workout bar at night, misty lights, black and white, 8k",
    "moody Soviet panel apartment district at night, fog, dim yellow lights, 35mm film grain, cinematic"
]

def generate_text():
    topic = random.choice(TOPICS)
    prompt = (
        f"Напиши одну короткую, суровую и глубокую пацанскую цитату на русском языке для паблика ВКонтакте на тему: {topic}. "
        "Максимум 2 предложения. Без кавычек, без хэштегов, без вступлений и пояснений. "
        "Только сам текст цитаты в брутальном жизненном стиле."
    )
    
    response = requests.post(
        url="https://pollinations.ai",
        json={
            "messages": [{"role": "user", "content": prompt}],
            "model": "openai",
            "seed": random.randint(1, 999999)
        },
        timeout=30
    )
    response.raise_for_status()
    return response.text.strip()

def download_image():
    img_prompt = random.choice(IMAGE_PROMPTS)
    seed = random.randint(1, 999999)
    encoded_prompt = urllib.parse.quote(img_prompt)
    url = f"https://pollinations.ai{encoded_prompt}?width=1080&height=1350&seed={seed}&nologo=true"
    
    img_data = requests.get(url, timeout=60).content
    with open("post.jpg", "wb") as f:
        f.write(img_data)

def post_to_vk(text):
    # 1. Получаем сервер для загрузки фото на стену
    upload_url_resp = requests.get(
        "https://vk.com",
        params={"group_id": VK_GROUP_ID, "access_token": VK_TOKEN, "v": "5.199"}
    ).json()
    upload_url = upload_url_resp["response"]["upload_url"]

    # 2. Загружаем картинку
    with open("post.jpg", "rb") as f:
        upload_resp = requests.post(upload_url, files={"photo": f}).json()

    # 3. Сохраняем фото в альбоме стены
    save_resp = requests.post(
        "https://vk.com",
        params={
            "group_id": VK_GROUP_ID,
            "photo": upload_resp["photo"],
            "server": upload_resp["server"],
            "hash": upload_resp["hash"],
            "access_token": VK_TOKEN,
            "v": "5.199"
        }
    ).json()
    
    photo_info = save_resp["response"][0]
    attachment = f"photo{photo_info['owner_id']}_{photo_info['id']}"

    # 4. Публикуем пост от имени группы
    post_resp = requests.post(
        "https://vk.com",
        params={
            "owner_id": -VK_GROUP_ID,
            "from_group": 1,
            "message": text,
            "attachments": attachment,
            "access_token": VK_TOKEN,
            "v": "5.199"
        }
    ).json()
    print("Результат публикации:", post_resp)

if __name__ == "__main__":
    quote = generate_text()
    print("Сгенерирован текст:", quote)
    download_image()
    post_to_vk(quote)
