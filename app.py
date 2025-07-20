from dotenv import load_dotenv
import os
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests

load_dotenv()  # โหลดค่าจาก .env

app = Flask(__name__)

# ใส่ Token และ Secret ที่ได้จาก LINE Developers
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# Webhook callback
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


# เมื่มีข้อความเข้ามา
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    text = event.message.text.strip()
    reply = get_rain_forecast(text)
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )


# ดึงข้อมูลพยากรณ์ฝนจาก OpenWeather (API ฟรี)
def get_rain_forecast(city):
    API_KEY = os.getenv('OPENWEATHER_API_KEY')
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city},TH&appid=' + API_KEY + '&units=metric&lang=th'

    try:
        res = requests.get(url)
        data = res.json()
        desc = data['weather'][0]['description']
        temp = data['main']['temp']
        chance_of_rain = data.get('1h', 0)
        return "\n".join([
            f"🌤 สภาพอากาศที่ {city}:",
            f"โอกาสฝนตก {chance_of_rain} มม.",
            f"สภาพอากาศ: {desc}, อุณหภูมิ {temp}°C"
        ])
    except Exception as e:
        return f"เกิดข้อผิดพลาดในการดึงข้อมูล: {e}"


# 🔧 จุดเริ่มต้นโปรแกรม
if __name__ == "__main__":
    app.run()
