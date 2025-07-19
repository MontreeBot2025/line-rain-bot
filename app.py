
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import requests

app = Flask(__name__)

# ใส่ Token และ Secret ที่ได้จาก LINE Developers
LINE_CHANNEL_ACCESS_TOKEN = 'YOUR_CHANNEL_ACCESS_TOKEN'
LINE_CHANNEL_SECRET = 'YOUR_CHANNEL_SECRET'

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

# เมื่อมีข้อความเข้ามา
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
    API_KEY = 'YOUR_OPENWEATHER_API_KEY'
    url = f'https://api.openweathermap.org/data/2.5/weather?q={city},TH&appid=' + API_KEY + '&units=metric&lang=th'
    try:
        res = requests.get(url)
        data = res.json()
        desc = data['weather'][0]['description']
        temp = data['main']['temp']
        chance_of_rain = data.get('rain', {}).get('1h', 0)
        return f"🌧 สภาพอากาศที่ {city}:
- {desc}
- อุณหภูมิ {temp}°C
- โอกาสฝนตกใน 1 ชม.: {chance_of_rain} มม."
    except:
        return "❌ ไม่พบข้อมูล หรือชื่อจังหวัดไม่ถูกต้อง ลองใหม่อีกครั้งครับ"

if __name__ == "__main__":
    app.run()
