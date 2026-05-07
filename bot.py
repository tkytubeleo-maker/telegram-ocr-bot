from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    filters,
    ContextTypes
)

from openai import OpenAI

import base64
import os
import json

BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_PROMPT = """
Đọc ảnh viết tay.

Trả về JSON duy nhất.

Không giải thích.
Không markdown.
Không thêm text.

Format JSON:

{
  "S": [],
  "W": [],
  "Q": [],
  "T": [],
  "佳": [],
  "至": [],
  "车": [],
  "享": []
}

Chỉ trả JSON.
"""

PRICE = {
    "S": ("S牌", "199", "99", "特价"),
    "W": ("W牌", "259", "135", "半价"),
    "Q": ("Q牌", "289", "160", "半价"),
    "T": ("T牌", "339", "185", "半价"),
    "佳": ("佳丽", "389", "215", "半价"),
    "至": ("至尊", "459", "249", "半价"),
    "车": ("车模", "519", "280", "半价"),
    "享": ("皇后", "599", "329", "半价"),
}

ORDER = ["享", "车", "至", "佳", "T", "Q", "W", "S"]


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        photo = update.message.photo[-1]

        file = await context.bot.get_file(photo.file_id)

        path = "temp.jpg"

        await file.download_to_drive(path)

        with open(path, "rb") as image_file:
            base64_image = base64.b64encode(
                image_file.read()
            ).decode("utf-8")

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

        content = response.choices[0].message.content

        print(content)

        data = json.loads(content)

        text = ""

        text += "👑👑五象大浪淘沙👑👑\n\n"

        text += "        5月7日出勤47人\n"

        text += "🌹日韩🌹 预约价4 9 9 💲\n\n"

        if len(data.get("享", [])) > 0:

            text += "🌹皇后🌹原价599，半价3 2 9💲）\n\n"

            for n in data["享"]:
                text += f"🌸{n}🌸"

            text += "\n\n"

        text += "🌹皇贵妃🌹原价569$，半价2 9 9$\n\n"

        for key in ORDER:

            if key == "享":
                continue

            numbers = data.get(key, [])

            if len(numbers) == 0:
                continue

            name, old_price, half_price, half_text = PRICE[key]

            text += f"🌹{name}🌹（原价：{old_price}💲，{half_text}{half_price}💲）{len(numbers)}个\n\n"

            for n in numbers:
                text += f"🌸{n}🌸"

            text += "\n\n"

        text += "🌹K T V组🌹\n"
        text += "🌼全场可上🌼\n\n\n"

        text += "🌹晚到🌷628-885-635-711-788-608\n"

        text += "🌹外送🌹-766-500-508-579-501-686-502-318-609-885-\n\n"

        text += "🌹包夜：🌷凌晨2点前4小时，2点后5小时🌷\n\n"

        text += "注意：相册上两个🐻🐻是假胸 一个🐻为真胸"

        await update.message.reply_text(text)

    except Exception as e:

        print(e)

        await update.message.reply_text(
            f"Lỗi:\n{str(e)}"
        )


app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(
    MessageHandler(
        filters.PHOTO,
        handle_photo
    )
)

print("Bot running...")

app.run_polling()