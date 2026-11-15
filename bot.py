import datetime
import os
import random
import urllib.parse
import requests
from PIL import Image, ImageEnhance

TOPICS = [
    "одинокий волк, ночь, дождь, верность своим принципам",
    "черная BMW на ночной трассе, туман, путь к цели",
    "пацанская дружба, брат за брата, проверка временем",
    "спортзал, дисциплина, работа над собой без оправданий",
    "советские панельки ночью, тишина, размышления о жизни"
]

IMAGE_PROMPTS = [
    "photorealistic black and white photo, fierce lone wolf standing in rainy dark alley at night, glowing eyes, cinematic lighting, 35mm film",
    "photorealistic moody shot of black tinted BMW E38 parked on wet asphalt at night, fog, glowing angel eyes headlights, dark aesthetic",
    "back view of a man in black hoodie and cap standing on a rooftop looking at misty Soviet panel buildings at night, atmospheric dark photography",
    "vintage black Mercedes W124 driving through heavy night fog on empty highway, red taillights reflection on wet road, cinematic moody"
]

BACKUP_QUOTES = [
    "Волк слабее льва и тигра, но в цирке он не выступает. Держи свой курс и не прогибайся под толпу.",
    "Брат за брата — это не красивая фраза для статуса, а проверка в самый темный час. Настоящих единицы, остальные просто массовка.",
    "Ночной город лечит лучше любого психолога. Включил фары, выехал на пустую трассу и все лишние мысли остались за спиной.",
    "Не важно, сколько раз ты упал на холодном асфальте. Важно, с каким взглядом ты поднялся и пошел дальше.",
    "Тишина громче любых обещаний. Кто реально делает вещи, тому не нужно кричать об этом на каждом перекрестке."
]

def build_url(host, path_parts, query_dict=None):
    path = "/" + "/".join(urllib.parse.quote(str(p), safe="") for p in path_parts)
    query = urllib.parse.urlencode(query_dict) if query_dict else ""
    return urllib.parse.urlunparse(("https", host, path, "", query, ""))

def generate_text():
    topic = random.choice(TOPICS)
    prompt = (
        f"Напиши одну короткую, суровую пацанскую цитату на русском языке для ВК на тему: {topic}. "
        "Максимум 2 предложения. Без кавычек, без хэштегов и без вступлений."
    )
    seed = random.randint(1, 999999)
    host = ".".join(["text", "pollinations", "ai"])
    
    try:
        url = build_url(host, [prompt], {"seed": seed})
        r = requests.get(url, timeout=25)
        if r.status_code == 200 and len(r.text.strip()) > 10:
            clean = r.text.strip().strip('"«»')
            if not clean.startswith("<!DOCTYPE") and not clean.startswith("<html"):
                return clean
    except Exception as e:
        print("Ошибка генерации текста:", e)
        
    return random.choice(BACKUP_QUOTES)

def generate_image():
    img_prompt = random.choice(IMAGE_PROMPTS)
    seed = random.randint(1, 999999)
    headers = {"User-Agent": "Mozilla/5.0"}
    
    targets = [
        (".".join(["image", "pollinations", "ai"]), ["prompt", img_prompt], {"width": 1080, "height": 1400, "seed": seed, "model": "flux", "nologo": "true"}),
        (".".join(["picsum", "photos"]), ["seed", seed, "1080", "1350"], None)
    ]
    
    for host, parts, params in targets:
        try:
            url = build_url(host, parts, params)
            resp = requests.get(url, headers=headers, timeout=45, allow_redirects=True)
            if resp.status_code == 200 and len(resp.content) > 10000:
                with open("post.jpg", "wb") as f:
                    f.write(resp.content)
                with Image.open("post.jpg") as img:
                    img = img.crop((0, 0, img.width, img.height - 50))
                    img = img.convert("L")
                    img = ImageEnhance.Contrast(img).enhance(1.25)
                    img = img.convert("RGB")
                    img.save("post.jpg", "JPEG", quality=92)
                print("Картинка сохранена из:", host)
                return seed
        except Exception as e:
            print("Источник не ответил:", host, e)
            
    return seed

if __name__ == "__main__":
    quote = generate_text()
    print("Сгенерирован текст:", quote)
    img_seed = generate_image()
    
    raw_host = ".".join(["raw", "githubusercontent", "com"])
    vk_host = ".".join(["vk", "com"])
    direct_img_url = build_url(raw_host, ["rlitvintsev", "vk-autopost", "main", "post.jpg"], {"v": img_seed})
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

    rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>Брат за брата</title>
  <link>https://{vk_host}</link>
  <description>Цитаты со смыслом</description>
  <item>
    <title></title>
    <description>{quote}</description>
    <enclosure url="{direct_img_url}" type="image/jpeg" />
    <guid>post-{img_seed}</guid>
    <pubDate>{now}</pubDate>
  </item>
</channel>
</rss>"""

    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(rss)
