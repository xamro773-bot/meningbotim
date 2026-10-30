import os
import logging
import sqlite3
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

DB_FILE = 'clients.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT UNIQUE,
            name TEXT,
            balance_uzs REAL DEFAULT 0,
            balance_usd REAL DEFAULT 0
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT,
            amount REAL,
            currency TEXT,
            comment TEXT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Doimiy mini-menyu tugmalari
reply_keyboard = [
    ["👥 Mijozlar", "➕ Mijoz qo'shish"],
    ["💰 Qarz qo'shish", "📊 Qarzdorlar"],
    ["💵 To'lov olish"]
]
markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! Kerakli amalni pastdagi tugmalardan tanlang:",
        reply_markup=markup
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "👥 Mijozlar":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name, phone, balance_uzs, balance_usd FROM clients")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            await update.message.reply_text("Hozircha bazada mijozlar yo'q.")
        else:
            msg = "👥 *Mijozlar ro'yxati (So'm va Dollar):*\n\n"
            for r in rows:
                msg += f"👤 Ism: {r[0]}\n📞 Tel: {r[1]}\n🇺🇿 Qarz (So'm): {r[2]:,.0f} so'm\n🇺🇸 Qarz (Dollar): ${r[3]:,.2f}\n-------------------\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
            
    elif text == "➕ Mijoz qo'shish":
        await update.message.reply_text(
            "Yangi mijoz qo'shish uchun:\n"
            "`/klient_qosh Ism Tel_raqam`\n"
            "Masalan: `/klient_qosh Ali +998901234567`",
            parse_mode="Markdown"
        )
        
    elif text == "💰 Qarz qo'shish":
        await update.message.reply_text(
            "Qarz qo'shish uchun (valyuta oxirida `uzs` yoki `usd` ko'rsatiladi):\n"
            "`/qarz_qosh Tel_raqam Summa Valyuta Izoh`\n"
            "Masalan (So'm): `/qarz_qosh +998901234567 500000 uzs Kraska`\n"
            "Masalan (Dollar): `/qarz_qosh +998901234567 100 usd Kraska`",
            parse_mode="Markdown"
        )
        
    elif text == "📊 Qarzdorlar":
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("SELECT name, phone, balance_uzs, balance_usd FROM clients WHERE balance_uzs > 0 OR balance_usd > 0")
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            await update.message.reply_text("Hozircha qarzdorlar yo'q. Hammaning qarzi yopilgan! ✅")
        else:
            msg = "📊 *Qarzdorlar ro'yxati:*\n\n"
            for r in rows:
                msg += f"👤 Ism: {r[0]}\n📞 Tel: {r[1]}\n🇺🇿 So'm: {r[2]:,.0f}\n🇺🇸 Dollar: ${r[3]:,.2f}\n-------------------\n"
            await update.message.reply_text(msg, parse_mode="Markdown")
            
    elif text == "💵 To'lov olish":
        await update.message.reply_text(
            "To'lov olish uchun:\n"
            "`/tolov Tel_raqam Summa Valyuta`\n"
            "Masalan (So'm): `/tolov +998901234567 200000 uzs`\n"
            "Masalan (Dollar): `/tolov +998901234567 50 usd`",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text("Iltimos, pastdagi tugmalardan foydalaning.")

if __name__ == '__main__':
    token = os.getenv("BOT_TOKEN", "9270197178:AAGplz_H8fBYok4_6eIKb85jGP1aC_J7cbk")
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), message_handler))

    print("Bot ishga tushdi (Serverga moslashgan)...")
    app.run_polling()