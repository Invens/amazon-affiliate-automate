import requests
import random

# Telegram bot token and channel ID (e.g., "@your_channel")
BOT_TOKEN = "7783337161:AAHk6XGXlOLV-yDMDEkfNZ0j5Xcqiz0oL4Y"
CHANNEL_ID = "-1002269587396"

# Predefined deal tags
DEAL_TAGS = ["🔥 HURRY UP! Limited Time Offer 🔥", "🎉 DON'T MISS OUT! 🎉", "💥 MEGA DEAL! 💥", "🚨 ACT NOW! 🚨"]

def post_to_telegram(product):
    # Randomly select a deal tag
    deal_tag = random.choice(DEAL_TAGS)
    
    # Fancy deal message with more styling
    message = (
        f"{deal_tag}\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"🏷️ **Product:**\n"
        f"📦 **{product['title']}**\n\n"
        f"💰 **Price:** `{product['price']}`\n"
        f"━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔥 **[👉 BUY NOW 👈]({product['affiliate_link']})** 🔥\n\n"
        f"🛒 **LIMITED TIME OFFER! Don't wait, grab this deal now!**\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡️ **Get it before it’s gone!** ⚡️"
    )

    image_url = product['image_url']
    
    # Send the image with the fancy caption
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    data = {
        "chat_id": CHANNEL_ID,
        "caption": message,
        "parse_mode": "Markdown"
    }
    files = {"photo": requests.get(image_url).content}
    
    response = requests.post(url, data=data, files=files)
    if response.status_code == 200:
        print("Product posted to Telegram successfully.")
    else:
        print(f"Failed to post: {response.status_code}, {response.text}")

# Example product data
product = {
    "title": "Ultra HD 4K Smart TV",
    "affiliate_link": "https://www.amazon.com/dp/B08RXY",
    "image_url": "https://example.com/image.jpg",
    "price": "$499.99"
}

# Test the function
post_to_telegram(product)
