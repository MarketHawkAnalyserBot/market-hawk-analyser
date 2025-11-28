"""
MODULE: Infrastructure Audit Protocol (Internal)
VERSION: 2.1-global
TYPE: Proprietary / Educational Proof-of-Concept
NOTE: Codebase defaults to 'Simulation Mode' if backend authorization keys are missing.
"""

import requests
import json
import os
import sys

# --- SECURE CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TARGET_ENDPOINT = os.environ.get("SECRET_MARKET_URL") 

# THRESHOLDS ($)
DANGER_PRICE = 1.50

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except:
        pass

def get_market_data():
    # --- SECURITY TRAP (SIMULATION MODE) ---
    if not TARGET_ENDPOINT:
        print("\n⚠️  SECURITY ALERT: Authorized Endpoint Key missing.")
        print("🔄  System switching to: DEMO / SIMULATION MODE.")
        print("    (No live data will be fetched. Exiting safely.)")
        return None

    # --- LIVE EXECUTION ---
    query_params = {
        "rentable": {"eq": True},
        "gpu_ram": {"gt": 75000}, 
        "type": "on-demand"
    }
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}

    try:
        print("📡 Authorized Source Detected. Initiating Encrypted Scan...")
        response = requests.get(TARGET_ENDPOINT, params={"q": json.dumps(query_params)}, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            offers = data.get('offers', [])
            
            if offers:
                relevant_prices = []
                for o in offers:
                    name = o.get('gpu_name', '')
                    price = float(o.get('dph_total', 0))
                    
                    if "H100" in name and price > 0.1:
                        relevant_prices.append(price)
                
                if relevant_prices:
                    min_price = min(relevant_prices)
                    print(f"✅ Live Telemetry Acquired: {len(relevant_prices)} active nodes.")
                    return min_price
    except Exception as e:
        print(f"Connection Error: {e}")
    return None

def main():
    print("--- Market Hawk System Boot ---")
    price = get_market_data()
    
    if price:
        print(f"💎 MARKET FLOOR PRICE: ${price:.4f}")
        
        if price <= DANGER_PRICE:
            msg = (f"🚨 *SIGNAL DETECTED* 🚨\n\n"
                   f"Asset Price: *${price:.4f}/hr*\n"
                   f"Threshold: ${DANGER_PRICE}\n"
                   f"Status: OPPORTUNITY")
            send_telegram(msg)
            print(">> Encrypted Signal sent to Analyst.")
    else:
        print(">> System Idle (Simulation or No Data).")

if __name__ == "__main__":
    main()
