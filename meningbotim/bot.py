import os
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import telebot

# Render platformasi uchun kichik veb-server (HealthCheck)
class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

def run_server():
    port = int(os.environ.get("PORT", 8080))
    server = HTTPServer(("0.0.0.0", port), HealthCheckHandler)
    server.serve_forever()

# Veb-serverni alohida oqimda (thread) ishga tushiramiz
threading.Thread(target=run_server, daemon=True).start()

# --- TELEGRAM BOT QISMI ---
# Tokenni Render'dagi Environment Variables (BOT_TOKEN) orqali avtomatik o'qiydi
TOKEN = os.environ.get("BOT_TOKEN")
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Assalomu alaykum! Botimiz 24 soat davomida muvaffaqiyatli ishlamoqda.")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"Xabaringiz qabul qilindi: {message.text}")

# Botni doimiy ishlab turish uchun ishga tushiramiz
bot.infinity_polling()
