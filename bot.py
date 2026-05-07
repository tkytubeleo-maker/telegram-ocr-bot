from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from openai import OpenAI
import base64
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
Bạn là bot chuyên format bài Telegram.

NHIỆM VỤ:
- Đọc ảnh ghi tay.
- Giữ nguyên tất cả số.
- Không tự bịa.
- Không thêm nội dung không có trong ảnh.
- Output phải giống format mẫu dưới đây 100%.

QUY TẮC FORMAT:

1. Không thêm giải thích.
2. Không markdown.
3. Mỗi nhóm cách nhau 1 dòng trống.
4. Luôn dùng emoji giống mẫu.
5. Sau mỗi số phải có 🌸
6. Không đổi thứ tự số.
7. Tự đếm số lượng.

MAP:
S = S牌
W = W牌
Q = Q牌
T = T牌
佳 = 佳丽
至 = 至尊
车 = 车模
享 = 皇后

GIÁ:

S牌:
原价199
特价99

W牌:
原价259
半价135

Q牌:
原价289
半价160

T牌:
原价339
半价185

佳丽:
原价389
半价215

至尊:
原价459
半价249

车模:
原价519
半价280

皇后:
原价599
半价329

FORMAT CHUẨN:

🌹Q牌🌹（原价289💲，半价160💲）7个
🌸318🌸328🌸306🌸369🌸311🌸355🌸

🌹S牌🌹（原价199💲，特价99💲）2个
🌸167🌸156🌸

Nếu nhóm không có số thì bỏ qua nhóm đó.
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