import telebot
import requests
import time
import threading
import os
from flask import Flask
from datetime import datetime

# ===== КОНФИГ =====
BOT_TOKEN = "8936789193:AAF1ZwRjlIzXDTbYhRIrVjAnVBxfUFKyuNU"
CHANNEL_ID = "-1002693821872"

# Flask приложение для Render (обязательно!)
app = Flask(__name__)
bot = telebot.TeleBot(BOT_TOKEN)

# API для реального стока
STOCK_API = "https://api.joshlei.com/v2/growagarden/info/"

ITEM_NAMES = {
    "carrot": "🥕 Carrot",
    "strawberry": "🍓 Strawberry", 
    "blueberry": "🫐 Blueberry",
    "tulip": "🌷 Tulip",
    "tomato": "🍅 Tomato",
    "apple": "🍎 Apple",
    "bamboo": "🎋 Bamboo",
    "corn": "🌽 Corn",
    "cactus": "🌵 Cactus",
    "mushroom": "🍄 Mushroom",
    "banana": "🍌 Banana",
    "dragon_fruit": "🐉 Dragon Fruit",
    "acorn": "🌰 Acorn",
}

def get_real_seed_shop():
    try:
        response = requests.get(STOCK_API, timeout=10)
        response.raise_for_status()
        data = response.json()
        seed_shop = data.get("seed_shop", {})
        available = []
        for item_id, stock_info in seed_shop.items():
            if isinstance(stock_info, dict):
                stock = stock_info.get("stock", 0)
                if stock and stock > 0:
                    display_name = ITEM_NAMES.get(item_id, item_id.replace("_", " ").title())
                    price = stock_info.get("price", "?")
                    available.append({"name": display_name, "price": price})
        return available
    except Exception as e:
        print(f"API Error: {e}")
        return None

def format_shop_message(seeds):
    if seeds is None:
        return "⚠️ Ошибка API"
    if not seeds:
        return "🌱 SEED SHOP — пусто"
    lines = ["🌱 **SEED SHOP — GROW A GARDEN 2** 🌱", ""]
    for seed in seeds:
        lines.append(f"• {seed['name']} — {seed['price']} Sheckles")
    lines.append("")
    lines.append(f"🕐 Обновлено: {datetime.now().strftime('%H:%M:%S')}")
    lines.append("🔄 Следующее обновление через 5 минут")
    return "\n".join(lines)

def send_to_channel():
    while True:
        seeds = get_real_seed_shop()
        message = format_shop_message(seeds)
        try:
            bot.send_message(CHANNEL_ID, message, parse_mode="Markdown")
            print(f"[{datetime.now()}] Отправлено")
        except Exception as e:
            print(f"Ошибка: {e}")
        time.sleep(300)

# Flask маршруты (нужны для Render!)
@app.route('/')
def home():
    return "Telegram Bot is running!"

@app.route('/health')
def health():
    return "OK"

if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=send_to_channel, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask сервер (Render требует порт)
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)