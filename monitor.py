import requests
from bs4 import BeautifulSoup
import time
import os

# --- CONFIGURATION ---
URL = "https://www.stwdo.de/wohnen/aktuelle-wohnangebote"
# Retrieve secrets from GitHub environment
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_msg(text):
    """Sends a message to your Telegram via the Bot API."""
    base_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(base_url, data=payload)
        if response.status_code == 200:
            print(f"[{time.strftime('%H:%M:%S')}] Telegram alert sent.")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Telegram failed: {e}")

def check_once():
    print(f"[{time.strftime('%H:%M:%S')}] Checking STWDO...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(URL, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        text = soup.get_text()

        # Your logic for "leider" and "sichtbar"
        if "leider" not in text and "sichtbar" not in text:
            print("✨ OFFER DETECTED!")
            msg = f"🏠 <b>HOUSING ALERT!</b>\n\nAn offer appeared! Check immediately:\n{URL}"
            send_telegram_msg(msg)
        else:
            print("🔍 No offers yet.")
            
    except Exception as e:
        print(f"Connection Error: {e}")

if __name__ == "__main__":
    check_once()
