import datetime
import io
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
    "black and white photo, lone wolf in rainy dark alley at night, cinematic lighting, 35mm film",
    "moody shot of black BMW E38 parked on wet asphalt at night, fog, glowing headlights, dark aesthetic",
    "back view of a man in black hoodie standing on a rooftop looking at misty city at night, dark photography",
    "vintage black Mercedes W124 driving through night fog on empty highway, wet road, cinematic moody"
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

def load_working_font(size):
    candidates = [
        "font.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    ]
    
    # Если локальный font.ttf битый — удаляем его и пробуем скачать заново
    if os.path.exists("font.ttf"):
        try:
            ImageFont.truetype("font.ttf", size)
        except Exception:
            print("Обнаружен битый font.ttf, удаляем...")
            os.remove("font.ttf")

    if not os.path.exists("font.ttf"):
        font_urls = [
            "https://githubusercontent.com",
            "https://github.com"
        ]
        for url in font_urls:
            try:
                r = requests.get(url, timeout=15)
                if r.status_code == 200 and len(r.content) > 20000:
                    with open("font.ttf", "wb") as f:
                        f.write(r.content)
                    ImageFont.truetype("font.ttf", size)
                    print("Успешно скачан и проверен шрифт из:", url)
                    break
            except Exception as e:
                print("Не подошел источник шрифта:", url, e)
                if os.path.exists("font.ttf"):
                    os.remove("font.ttf")

    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue

    return ImageFont.load_default()

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

def create_fallback_bg():
    img = Image.new("RGB", (1080, 1080), (18, 18, 22))
    draw = ImageDraw.Draw(img)
    for y in range(1080):
        shade = int(15 + (y / 1080) * 25)
        draw.line([(0, y), (1080, y)], fill=(shade, shade, shade + 4))
    return img

def apply_text_overlay(img, quote_text):
    # Отрезаем нижние 80px, чтобы убрать логотип pollinations.ai
    if img.height > 200:
        img = img.crop((0, 0, img.width, img.height - 80))
    
    # Делаем черно-белым, повышаем контраст и приводим к квадрату 1080x1080
    img = img.convert("L")
    img = ImageEnhance.Contrast(img).enhance(1.25)
    img = img.resize((1080, 1080), Image.Resampling.LANCZOS)
    img = img.convert("RGBA")

    # Накладываем темный слой поверх картинки для читаемости текста
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 145))
    img = Image.alpha_composite(img, overlay)

    draw = ImageDraw.Draw(img)
    font_main = load_working_font(48)
    font_wm = load_working_font(26)

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
        (".".join(["image", "pollinations", "ai"]), ["prompt", img_prompt], {"width": 1024, "height": 1024, "seed": seed, "model": "flux", "nologo": "true"}),
        (".".join(["picsum", "photos"]), ["seed", str(seed), "1080", "1080"], None)
    ]
    
    base_img = None
    for host, parts, params in targets:
        try:
            url = build_url(host, parts, params)
            resp = requests.get(url, headers=headers, timeout=45, allow_redirects=True)
            ctype = resp.headers.get("Content-Type", "")
            print(f"Ответ от {host}: статус={resp.status_code}, тип={ctype}, байт={len(resp.content)}")
            if resp.status_code == 200 and "image" in ctype and len(resp.content) > 10000:
                base_img = Image.open(io.BytesIO(resp.content))
                base_img.load()
                print("Успешно загружен фон из:", host)
                break
        except Exception as e:
            print("Ошибка на источнике:", host, e)

    if base_img is None:
        print("Используем запасной темный фон")
        base_img = create_fallback_bg()

    final_img = apply_text_overlay(base_img, quote_text)
    final_img.save("post.jpg", "JPEG", quality=92)
    print("Итоговый post.jpg успешно сохранен")
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

