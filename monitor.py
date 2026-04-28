import requests
from bs4 import BeautifulSoup
import time
import os

# --- CONFIGURATION ---
URL = "https://www.stwdo.de/wohnen/aktuelle-wohnangebote"
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

def send_telegram_msg(text):
    """Sends a message to your Telegram via the Bot API."""
    if not TOKEN or not CHAT_ID:
        print("❌ ERROR: Telegram Token or Chat ID is missing from environment variables!")
        return
        
    base_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(base_url, data=payload)
        if response.status_code == 200:
            print(f"[{time.strftime('%H:%M:%S')}] Telegram alert sent successfully.")
        else:
            print(f"Telegram API Error: {response.text}")
    except Exception as e:
        print(f"Telegram failed: {e}")

def check_once():
    print(f"[{time.strftime('%H:%M:%S')}] Starting STWDO check...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(URL, headers=headers, timeout=10)
        
        # 1. Maintenance & Status Check
        if response.status_code != 200:
            print(f"⚠️ Site returned Status {response.status_code}. Skipping check.")
            return

        soup = BeautifulSoup(response.text, 'html.parser')

        # 2. Look ONLY for the specific "box" that holds the housing list
        offer_list = soup.find('ul', id='residential-offer-list')

        # If the box doesn't exist on the page, there are zero offers
        if not offer_list:
            print("🔍 No offers available right now. (List container missing)")
            return

        # 3. Extract every individual offer card from that list
        offer_cards = offer_list.find_all('li', class_='grid-item')

        if not offer_cards:
            print("🔍 No offers available right now. (No cards inside container)")
            return

        # 4. Check EACH card individually for Dortmund
        dortmund_found = False
        for card in offer_cards:
            # Extract text ONLY from this specific housing card
            card_text = card.get_text().upper() 
            
            if "ISERLOHN" in card_text:
                dortmund_found = True
                break # We found at least one Dortmund offer! Stop looking.

        # 5. Trigger the alert ONLY if Dortmund was found
        if dortmund_found:
            print("✨ FOOLPROOF DORTMUND OFFER DETECTED!")
            msg = f"🏠 <b>DORTMUND HOUSING ALERT!</b>\n\nAn offer actually appeared in Dortmund! Check immediately:\n{URL}"
            send_telegram_msg(msg)
        else:
            print(f"🔍 {len(offer_cards)} offer(s) exist, but none are in Dortmund (e.g., Iserlohn). Ignoring.")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    check_once()
