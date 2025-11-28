"""
MODULE: Infrastructure Audit Protocol (Internal)
VERSION: 2.2-H200-Target
TYPE: Proprietary / Educational Proof-of-Concept
NOTE: Codebase defaults to 'Simulation Mode' if backend authorization keys are missing.
"""

import requests
import json
import os
from datetime import datetime

# --- SECURE CONFIGURATION ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TARGET_ENDPOINT = os.environ.get("SECRET_MARKET_URL") 

# BENCHMARK PRICE (RunPod H200)
BENCHMARK_PRICE = 3.39

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload)
    except: pass

def get_market_data():
    if not TARGET_ENDPOINT:
        print("\n⚠️  SECURITY ALERT: Authorized Endpoint Key missing.")
        print("🔄  System switching to: DEMO / SIMULATION MODE.")
        return None, None

    # H200 Audit parameters (Filters for GPUs > 100GB RAM)
    query_params = {
        "rentable": {"eq": True},
        "gpu_ram": {"gt": 100000}, 
        "type": "on-demand"
    }
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"}

    try:
        current_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
        print(f"[{current_time}] 📡 Targeting H200 Asset Class (High-Spec Audit)...")
        
        response = requests.get(TARGET_ENDPOINT, params={"q": json.dumps(query_params)}, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            offers = data.get('offers', [])
            
            if offers:
                relevant_prices = []
                for o in offers:
                    name = o.get('gpu_name', '')
                    price = float(o.get('dph_total', 0))
                    
                    if "H200" in name and price > 0.1: relevant_prices.append(price)
                
                if relevant_prices:
                    min_price = min(relevant_prices)
                    print(f"✅ H200 Units Detected: {len(relevant_prices)} active nodes.")
                    return min_price, current_time
    except Exception as e:
        print(f"Connection Error: {e}")
    return None, None

def main():
    print("--- Market Hawk: H200 Audit ---")
    price, timestamp = get_market_data()
    
    if price:
        print(f"💎 H200 SPOT PRICE: ${price:.4f}")
        print(f"🕒 Timestamp: {timestamp}")
        savings = (1 - (price / BENCHMARK_PRICE)) * 100
        print(f"📉 Discount vs Benchmark ($3.39): {savings:.1f}%")

        if price < BENCHMARK_PRICE:
            msg = (f"🚨 *H200 FOUND* 🚨\n\n"
                   f"Spot Price: *${price:.4f}/hr*\n"
                   f"Benchmark: ${BENCHMARK_PRICE}\n"
                   f"Arbitrage: {savings:.1f}%\n"
                   f"Time: {timestamp}")
            send_telegram(msg)
    else:
        print(">> System Idle or Data Unavailable.")

if __name__ == "__main__":
    main()
