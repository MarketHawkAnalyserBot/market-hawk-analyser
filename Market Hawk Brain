import requests
import json
import os
import sys

# --- CONFIGURARE ---
# Citim cheile din seif
TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

TARGET_GPU = "H100 PCIe"
API_URL = "https://console.vast.ai/api/v0/bundles/"

# PRAGURILE DE SUPRAVIEȚUIRE ($)
WARNING_PRICE = 2.20  # Galben: Pregătește banii
DANGER_PRICE = 1.80   # Roșu: Bula s-a spart (Titanic)

def send_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Telegram status: {response.status_code}")
    except Exception as e:
        print(f"Eroare Telegram: {e}")

def get_market_price():
    query_params = {
        "verified": {"eq": True},
        "rentable": {"eq": True},
        "gpu_name": {"eq": TARGET_GPU},
        "type": "on-demand"
    }
    try:
        response = requests.get(API_URL, params={"q": json.dumps(query_params)}, timeout=30)
        if response.status_code == 200:
            data = response.json()
            offers = data.get('offers', [])
            if offers:
                prices = [float(o['dph_total']) for o in offers]
                return min(prices)
    except Exception as e:
        print(f"Eroare Vast: {e}")
    return None

def main():
    print("--- Market Hawk Activat ---")
    current_price = get_market_price()
    
    if current_price is None:
        print("Nu s-au putut citi datele.")
        sys.exit(0)
        
    print(f"PRET ACTUAL PIATA: ${current_price}")

    # LOGICA DE RAZBOI
    if current_price <= DANGER_PRICE:
        msg = (f"🚨 *TITANIC MODE ACTIVAT* 🚨\n\n"
               f"Prețul H100 a scăzut la: *${current_price}/oră*\n"
               f"Limita critică ({DANGER_PRICE}$) a fost atinsă.\n"
               f"Execută planul de investiții ACUM!")
        send_telegram(msg)
        
    elif current_price <= WARNING_PRICE:
        msg = (f"⚠️ *Atenție Market Hawk* ⚠️\n\n"
               f"Prețul H100 a coborât la: *${current_price}/oră*\n"
               f"Ne apropiem de zona de impact.")
        send_telegram(msg)
        
    else:
        print("Pretul e inca SUS (Bula rezista). Nu trimit alerta ca sa nu deranjez.")

if __name__ == "__main__":
    main()
