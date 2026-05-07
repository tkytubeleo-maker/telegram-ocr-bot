from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from openai import OpenAI
import base64
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
Bạn là bot format telegram.

Nhiệm vụ:
- đọc ảnh viết tay
- lấy toàn bộ số
- format đẹp kiểu telegram
- tự đếm số lượng
- dùng emoji

Ví dụ format:

🌹Q牌🌹（原价：289💲，半价：160💲）7个
🌸318🌸328🌸306🌸369🌸311🌸355🌸

Không giải thích.
"""

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]

    file = await context.bot.get_file(photo.file_id)

    path = "temp.jpg"

    await file.download_to_drive(path)

    with open(path, "rb") as image_file:
        base64_image = base64.b64encode(image_file.read()).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-5.5",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Đọc ảnh này"
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ],
        max_completion_tokens=2000
    )

    result = response.choices[0].message.content

    await update.message.reply_text(result)

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

print("Bot running...")

app.run_polling()