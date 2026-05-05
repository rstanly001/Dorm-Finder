import requests
from bs4 import BeautifulSoup
import time
import os
from upstash_redis import Redis

# --- CONFIGURATION ---
URL = "https://www.stwdo.de/wohnen/aktuelle-wohnangebote"
TOKEN = os.environ.get("TELEGRAM_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
REDIS_URL = os.environ.get("UPSTASH_REDIS_REST_URL")
REDIS_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN")

# Initialize the Database Connection
if REDIS_URL and REDIS_TOKEN:
    db = Redis(url=REDIS_URL, token=REDIS_TOKEN)
else:
    db = None
    print("⚠️ Warning: Upstash Redis credentials not found. Memory disabled.")

def send_telegram_msg(text):
    # ... (Keep your exact send_telegram_msg function here) ...
    pass 

def check_once():
    print(f"[{time.strftime('%H:%M:%S')}] Starting STWDO check...")
    headers = {'User-Agent': 'Mozilla/5.0...'}
    
    try:
        response = requests.get(URL, headers=headers, timeout=10)
        if response.status_code != 200:
            return

        soup = BeautifulSoup(response.text, 'html.parser')
        offer_list = soup.find('ul', id='residential-offer-list')

        if not offer_list:
            print("🔍 No offers available right now.")
            return

        offer_cards = offer_list.find_all('li', class_='grid-item')
        if not offer_cards:
            return

        new_dortmund_room_found = False

        for card in offer_cards:
            card_text = card.get_text().upper() 
            
            if "ISERLOHN" in card_text:
                # 1. Extract the Unique Room Fingerprint
                teaser_div = card.find('div', class_='teaser js-link-area')
                
                # Failsafe: If we can't find the link, use the raw text as a backup ID
                if teaser_div and 'data-href' in teaser_div.attrs:
                    offer_id = teaser_div['data-href']
                else:
                    offer_id = "backup_id_" + str(hash(card_text))

                # 2. Check the Memory Database
                if db:
                    # If this ID is NOT in the database, it's a brand new room!
                    if not db.get(offer_id):
                        new_dortmund_room_found = True
                        
                        # Save it to the database, and tell it to expire in 172,800 seconds (48 hrs)
                        db.setex(offer_id, 172800, "seen")
                        print(f"✅ New Dortmund room saved to memory: {offer_id}")
                        break # Stop looking, we found a new one!
                    else:
                        print(f"🔁 Duplicate Dortmund room ignored: {offer_id}")
                else:
                    # If Redis isn't configured, default to old behavior
                    new_dortmund_room_found = True
                    break

        if new_dortmund_room_found:
            print("✨ NEW DORTMUND OFFER DETECTED!")
            msg = f"🏠 <b>NEW DORTMUND HOUSING ALERT!</b>\n\nA brand new offer appeared in Dortmund! Check immediately:\n{URL}"
            send_telegram_msg(msg)
        else:
            print("🔍 Checked all cards. No *new* Dortmund offers right now.")
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")

if __name__ == "__main__":
    check_once()
