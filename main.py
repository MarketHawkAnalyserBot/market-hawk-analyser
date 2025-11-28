import requests
import json
import os
import sys

# --- CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

TARGET_GPU = "H100 PCIe"
API_URL = "https://console.vast.ai/api/v0/bundles/"

# THRESHOLDS
WARNING_PRICE = 2.20
DANGER_PRICE = 1.80

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Telegram Keys missing! Skipping alert.")
        return
        
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Telegram Error: {e}")

def get_market_price():
    # SEARCH QUERY
    query_params = {
        "verified": {"eq": True},
        "rentable": {"eq": True},
        "gpu_name": {"eq": TARGET_GPU},
        "type": "on-demand"
    }
    
    # THE MASK (User-Agent) - Tricks the server into thinking we are a browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        print(f"📡 Connecting to Vast.ai for {TARGET_GPU}...")
        response = requests.get(
            API_URL, 
            params={"q": json.dumps(query_params)}, 
            headers=headers, 
            timeout=30
        )
        
        # DEBUGGING INFO
        print(f"Server Response Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            offers = data.get('offers', [])
            print(f"Offers found: {len(offers)}")
            
            if offers:
                prices = [float(o['dph_total']) for o in offers]
                return min(prices)
            else:
                print("⚠️ No offers found for this GPU type right now.")
                return None
        else:
            print(f"❌ Server Error: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    return None

def main():
    print("--- Market Hawk Activated ---")
    current_price = get_market_price()
    
    if current_price is None:
        print("❌ CRITICAL: Could not read data.")
        # We do not exit here, so we can see the logs
        return
        
    print(f"✅ MARKET PRICE DETECTED: ${current_price:.4f}")

    # LOGIC
    if current_price <= DANGER_PRICE:
        msg = (f"🚨 *TITANIC MODE ACTIVATED* 🚨\n\n"
               f"H100 Price Drop: *${current_price}/hr*\n"
               f"Critical Limit ({DANGER_PRICE}$) breached.\n"
               f"EXECUTE STRATEGY NOW!")
        send_telegram(msg)
        print(">> Red Alert Sent.")
        
    elif current_price <= WARNING_PRICE:
        msg = (f"⚠️ *Market Hawk Alert* ⚠️\n\n"
               f"H100 Price Dip: *${current_price}/hr*\n"
               f"Approaching impact zone.")
        send_telegram(msg)
        print(">> Warning Alert Sent.")
        
    else:
        print(">> Price is STABLE (Above thresholds). No alert needed.")

if __name__ == "__main__":
    main()
