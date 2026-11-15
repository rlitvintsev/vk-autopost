import datetime
import os
import random
import textwrap
import urllib.parse
import requests
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

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

def ensure_font():
    font_path = "font.ttf"
    if not os.path.exists(font_path):
        font_url = "https://github.com"
        try:
            r = requests.get(font_url, timeout=20)
            if r.status_code == 200 and len(r.content) > 10000:
                with open(font_path, "wb") as f:
                    f.write(r.content)
        except Exception as e:
            print("Не удалось скачать шрифт:", e)
    return font_path if os.path.exists(font_path) else None

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

def apply_text_overlay(img, quote_text):
    # Отрезаем нижние 85px, чтобы гарантированно убрать логотип pollinations.ai
    crop_h = max(100, img.height - 85)
    img = img.crop((0, 0, img.width, crop_h))
    
    # Делаем черно-белым, повышаем контраст и приводим к квадрату 1080x1080
    img = img.convert("L")
    img = ImageEnhance.Contrast(img).enhance(1.25)
    img = img.resize((1080, 1080), Image.Resampling.LANCZOS)
    img = img.convert("RGBA")

    # Накладываем темный слой поверх картинки для читаемости текста
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 145))
    img = Image.alpha_composite(img, overlay)

    draw = ImageDraw.Draw(img)
    font_path = ensure_font()

    if font_path:
        font_main = ImageFont.truetype(font_path, 48)
        font_wm = ImageFont.truetype(font_path, 26)
        try:
            font_main.set_variation_by_axes([700])
            font_wm.set_variation_by_axes([600])
        except Exception:
            pass
    else:
        font_main = ImageFont.load_default()
        font_wm = ImageFont.load_default()

    # Разбиваем цитату на строки по 30 символов
    lines = textwrap.wrap(quote_text, width=30)
    line_height = 66
    total_text_height = len(lines) * line_height
    start_y = (1080 - total_text_height) // 2 - 20

    # Рисуем каждую строку по центру с тенью
    for i, line in enumerate(lines):
        left, top, right, bottom = draw.textbbox((0, 0), line, font=font_main)
        text_w = right - left
        x = (1080 - text_w) // 2
        y = start_y + i * line_height

        draw.text((x + 3, y + 3), line, font=font_main, fill=(0, 0, 0, 230))
        draw.text((x, y), line, font=font_main, fill=(255, 255, 255, 255))

    # Рисуем водяной знак сообщества внизу
    watermark = "БРАТ ЗА БРАТА"
    wm_left, wm_top, wm_right, wm_bottom = draw.textbbox((0, 0), watermark, font=font_wm)
    wm_w = wm_right - wm_left
    wm_x = (1080 - wm_w) // 2
    draw.text((wm_x, 995), watermark, font=font_wm, fill=(255, 255, 255, 175))

    return img.convert("RGB")

def generate_image(quote_text):
    img_prompt = random.choice(IMAGE_PROMPTS)
    seed = random.randint(1, 999999)
    headers = {"User-Agent": "Mozilla/5.0"}
    
    targets = [
        (".".join(["image", "pollinations", "ai"]), ["prompt", img_prompt], {"width": 1080, "height": 1150, "seed": seed, "model": "flux", "nologo": "true"}),
        (".".join(["picsum", "photos"]), ["seed", str(seed), "1080", "1150"], None)
    ]
    
    for host, parts, params in targets:
        try:
            url = build_url(host, parts, params)
            resp = requests.get(url, headers=headers, timeout=45, allow_redirects=True)
            if resp.status_code == 200 and len(resp.content) > 10000:
                with open("raw.jpg", "wb") as f:
                    f.write(resp.content)
                with Image.open("raw.jpg") as img:
                    final_img = apply_text_overlay(img, quote_text)
                    final_img.save("post.jpg", "JPEG", quality=92)
                if os.path.exists("raw.jpg"):
                    os.remove("raw.jpg")
                print("Картинка успешно обработана из:", host)
                return seed
        except Exception as e:
            print("Ошибка на источнике:", host, e)
            
    return seed

if __name__ == "__main__":
    quote = generate_text()
    print("Сгенерирован текст:", quote)
    img_seed = generate_image(quote)
    
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
    <description>#цитаты</description>
    <enclosure url="{direct_img_url}" type="image/jpeg" />
    <guid>post-{img_seed}</guid>
    <pubDate>{now}</pubDate>
  </item>
</channel>
</rss>"""

    with open("feed.xml", "w", encoding="utf-8") as f:
        f.write(rss)
