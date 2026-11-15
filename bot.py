import datetime
import random
import urllib.parse
import requests

TOPICS = [
    "одинокий волк, ночь, дождь, верность своим принципам",
    "черная BMW на ночной трассе, туман, путь к цели",
    "пацанская дружба, брат за брата, проверка временем",
    "спортзал, турники, дисциплина, работа над собой без оправданий",
    "советские панельки ночью, тишина, размышления о жизни"
]

BACKUP_QUOTES = [
    "Волк слабее льва и тигра, но в цирке он не выступает. Держи свой курс и не прогибайся под толпу.",
    "Брат за брата — это не красивая фраза для статуса, а проверка в самый темный час. Настоящих единицы, остальные просто массовка.",
    "Ночной город лечит лучше любого психолога. Включил фары, выехал на пустую трассу и все лишние мысли остались за спиной.",
    "Не важно, сколько раз ты упал на холодном асфальте. Важно, с каким взглядом ты поднялся и пошел дальше."
]

def generate_text():
    topic = random.choice(TOPICS)
    prompt = urllib.parse.quote(
        f"Напиши короткую, суровую пацанскую цитату на русском языке для ВК на тему: {topic}. "
        "Максимум 2 предложения, без кавычек и хэштегов."
    )
    seed = random.randint(1, 999999)
    text_host = ".".join(["text", "pollinations", "ai"])
    
    try:
        r = requests.get(f"https://{text_host}/{prompt}?seed={seed}", timeout=25)
        if r.status_code == 200 and len(r.text.strip()) > 10:
            clean = r.text.strip().strip('"«»')
            if not clean.startswith("<!DOCTYPE") and not clean.startswith("<html"):
                return clean
    except Exception as e:
        print("Ошибка генерации текста:", e)
        
    return random.choice(BACKUP_QUOTES)

quote = generate_text()
print("Сгенерирован пост:", quote)

seed = random.randint(1, 999999)
img_host = ".".join(["picsum", "photos"])
vk_host = ".".join(["vk", "com"])
img_url = f"https://{img_host}/seed/{seed}/1080/1350?grayscale"
now = datetime.datetime.now(datetime.timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

rss = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
<channel>
  <title>Пацанский паблик</title>
  <link>https://{vk_host}</link>
  <description>Цитаты со смыслом</description>
  <item>
    <title>{quote[:45]}...</title>
    <description>{quote}</description>
    <enclosure url="{img_url}" type="image/jpeg" />
    <guid>{seed}</guid>
    <pubDate>{now}</pubDate>
  </item>
</channel>
</rss>"""

with open("feed.xml", "w", encoding="utf-8") as f:
    f.write(rss)
