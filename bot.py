import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.environ.get("BOT_TOKEN")
if not TOKEN:
    raise ValueError("BOT_TOKEN environment variable is not set!")


# Minimal HTTP server
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

    def log_message(self, format, *args):
        pass  # server loglarını sustur


def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), Handler)
    server.serve_forever()


def check_billie_jean():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)
    try:
        driver.get("https://www.youtube.com")
        time.sleep(3)
        search_box = driver.find_element(By.NAME, "search_query")
        search_box.send_keys("Billie Jean")
        search_box.send_keys(Keys.RETURN)
        time.sleep(3)
        if "Michael Jackson - Billie Jean (Official Video)" in driver.page_source:
            return True
        return False
    finally:
        driver.quit()


async def billie_jean(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        result = check_billie_jean()
        if result:
            await update.message.reply_text("✅ Success")
        else:
            await update.message.reply_text("❌ Not found")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Xəta: {str(e)}")
        print(f"Error: {e}")


if __name__ == "__main__":
    threading.Thread(target=run_server, daemon=True).start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("billie_jean", billie_jean))
    app.run_polling(drop_pending_updates=True)
