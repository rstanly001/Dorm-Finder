import requests
from bs4 import BeautifulSoup
import smtplib
import time
from email.message import EmailMessage
import os

# --- CONFIGURATION ---
URL = "https://www.stwdo.de/wohnen/aktuelle-wohnangebote"
EMAIL_ADDRESS = "rohitstanly123@gmail.com"
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")

def send_notification():
    msg = EmailMessage()
    msg.set_content(f"🚨 HOUSING ALERT: An offer has likely appeared! Check immediately: {URL}")
    msg["Subject"] = "🏠 STWDO Housing Opening Detected!"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = EMAIL_ADDRESS

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)
        print(f"[{time.strftime('%H:%M:%S')}] Email notification sent.")
    except Exception as e:
        print(f"Error sending email: {e}")

def monitor():
    print("🚀 Monitoring started. Checking every 10 minutes...")
    print("Targeting: STWDO Aktuelle Wohnangebote")
    
    while True:
        try:
            # Using headers to mimic a real browser session
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(URL, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()

            # Logic: If the 'No Offers' text is missing, trigger the alert
            if "leider" not in text:
                print("✨ CHANGE DETECTED! The 'No Offers' message is gone.")
                send_notification()
            else:
                print(f"[{time.strftime('%H:%M:%S')}] No offers yet. Checking again in 10 minutes...")
            
        except Exception as e:
            print(f"Connection Error: {e}")
        
        # Sleep for 10 minutes (600 seconds)
        time.sleep(600)

if __name__ == "__main__":
    monitor()
