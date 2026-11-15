
import os
import random
import textwrap
import urllib.parse
import requests
from PIL import Image, ImageDraw, ImageFont

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

BACKUP_QUOTES = [
    "Волк слабее льва и тигра, но в цирке он не выступает. Держи свой курс и не прогибайся под толпу.",
    "Брат за брата — это не красивая фраза для статуса, а проверка в самый темный час. Настоящих единицы, остальные просто массовка.",
    "Ночной город лечит лучше любого психолога. Включил фары, выехал на пустую трассу и все лишние мысли остались за спиной.",
    "Не важно, сколько раз ты упал на холодном асфальте. Важно, с каким взглядом ты поднялся и пошел дальше.",
    "Тишина громче любых обещаний. Кто реально делает вещи, тому не нужно кричать об этом на каждом перекрестке.",
    "Время расставит всех по своим местам. Главное — самому остаться человеком, когда вокруг одни маски."
]

def build_url(host, path_parts, query_dict=None):
    path = "/" + "/".join(urllib.parse.quote(str(p), safe="") for p in path_parts)
    query = urllib.parse.urlencode(query_dict) if query_dict else ""
    return urllib.parse.urlunparse(("https", host, path, "", query, ""))

def generate_text():
    topic = random.choice(TOPICS)
    prompt = (
        f"Напиши одну короткую, суровую пацанскую цитату на русском языке для паблика ВК на тему: {topic}. "
        "Максимум 2 предложения. Без кавычек, без хэштегов и без вступлений."
    )
    seed = random.randint(1, 999999)
    
    targets = [
        ("text.pollinations.ai", [prompt], {"seed": seed}),
        ("gen.pollinations.ai", ["text", prompt], {"seed": seed})
    ]
    
    for host, parts, params in targets:
        try:
            url = build_url(host, parts, params)
            response = requests.get(url, timeout=25)
            if response.status_code == 200 and len(response.text.strip()) > 10:
                text = response.text.strip().strip('"').strip("«»")
                if not text.startswith("<!DOCTYPE") and not text.startswith("<html"):
                    return text
        except Exception as e:
            print("Ошибка текстового API:", e)
            
    return random.choice(BACKUP_QUOTES)

def create_fallback_card(text):
    print("Генерирую стильную пацанскую карточку локально...")
    width, height = 1080, 1350
    img = Image.new("RGB", (width, height), color=(15, 17, 21))
    draw = ImageDraw.Draw(img)
    
    # Рисуем тонкую серую рамку по краям
    draw.rectangle([50, 50, width - 50, height - 50], outline=(80, 85, 95), width=3)
    
    # Подключаем системный шрифт Ubuntu с поддержкой кириллицы
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    ]
    font = None
    for fp in font_paths:
        if os.path.exists(fp):
            font = ImageFont.truetype(fp, 48)
            break
    if font is None:
        font = ImageFont.load_default()
        
    wrapped_text = textwrap.fill(text.upper(), width=26)
    bbox = draw.multiline_textbbox((0, 0), wrapped_text, font=font, spacing=18)
    text_w = bbox - bbox
    text_h = bbox - bbox
    
    x = (width - text_w) / 2
    y = (height - text_h) / 2
    draw.multiline_text((x, y), wrapped_text, fill=(240, 240, 245), font=font, align="center", spacing=18)
    img.save("post.jpg", "JPEG", quality=95)

def download_image(quote_text):
    img_prompt = random.choice(IMAGE_PROMPTS)
    seed = random.randint(1, 999999)
    headers = {"User-Agent": "Mozilla/5.0"}
    
    img_targets = [
        ("image.pollinations.ai", ["prompt", img_prompt], {"width": 1080, "height": 1350, "seed": seed, "nologo": "true"}),
        ("picsum.photos", ["seed", seed, "1080", "1350"], None)
    ]
    
    for host, parts, params in img_targets:
        try:
            url = build_url(host, parts, params)
            resp = requests.get(url, headers=headers, timeout=45, allow_redirects=True)
            if resp.status_code == 200 and len(resp.content) > 10000:
                with open("post.jpg", "wb") as f:
                    f.write(resp.content)
                # Проверяем, что скачалась именно картинка, а не HTML-страница ошибки
                with Image.open("post.jpg") as test_img:
                    test_img = test_img.convert("L").convert("RGB")
                    test_img.save("post.jpg", "JPEG", quality=95)
                print("Картинка успешно скачана с:", host)
                return
        except Exception as e:
            print("Не сработал источник:", host, e)
            
    # Если ни один сервис не отдал фото — рисуем карточку с цитатой сами
    create_fallback_card(quote_text)

def post_to_vk(text):
    vk_host = ".".join(["api", "vk", "com"])
    
    # 1. Получаем сервер для загрузки фото на стену
    url_1 = build_url(vk_host, ["method", "photos.getWallUploadServer"])
    upload_url_resp = requests.get(
        url_1,
        params={"group_id": VK_GROUP_ID, "access_token": VK_TOKEN, "v": "5.199"}
    ).json()
    print("Ответ getWallUploadServer:", upload_url_resp)
    upload_url = upload_url_resp["response"]["upload_url"]

    # 2. Загружаем картинку
    with open("post.jpg", "rb") as f:
        upload_resp = requests.post(upload_url, files={"photo": f}).json()

    # 3. Сохраняем фото в альбоме стены
    url_3 = build_url(vk_host, ["method", "photos.saveWallPhoto"])
    save_resp = requests.post(
        url_3,
        params={
            "group_id": VK_GROUP_ID,
            "photo": upload_resp["photo"],
            "server": upload_resp["server"],
            "hash": upload_resp["hash"],
            "access_token": VK_TOKEN,
            "v": "5.199"
        }
    ).json()
    print("Ответ saveWallPhoto:", save_resp)
    
    resp_data = save_resp["response"]
    photo_info = resp_data if isinstance(resp_data, list) else resp_data
    attachment = f"photo{photo_info['owner_id']}_{photo_info['id']}"

    # 4. Публикуем пост от имени группы
    url_4 = build_url(vk_host, ["method", "wall.post"])
    post_resp = requests.post(
        url_4,
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
    download_image(quote)
    post_to_vk(quote)
