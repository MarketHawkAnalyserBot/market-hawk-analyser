import requests
import json
import os
import sys

# --- CONFIGURARE ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# Căutăm orice fel de H100 (SXM, PCIe, NVL)
TARGET_GPU_NAME = "H100" 
API_URL = "https://console.vast.ai/api/v0/bundles/"

# PRAGURILE ($)
WARNING_PRICE = 2.50
DANGER_PRICE = 2.00

def send_telegram(message):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("❌ Lipsesc cheile Telegram. Nu pot trimite alerta.")
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
        print(f"Eroare Telegram: {e}")

def get_market_price():
    # --- SCHIMBARE STRATEGIE: CĂUTARE LARGĂ ---
    # Nu mai cerem "Verified". Cerem tot ce e "Rentable" (închiriatibil).
    query_params = {
        "rentable": {"eq": True},
        "gpu_name": {"eq": TARGET_GPU_NAME},
        "type": "on-demand"
    }
    
    # Masca (Browser)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        print(f"📡 Scanez piața Vast.ai pentru ORICE '{TARGET_GPU_NAME}'...")
        response = requests.get(
            API_URL, 
            params={"q": json.dumps(query_params)}, 
            headers=headers, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            offers = data.get('offers', [])
            print(f"✅ Am găsit {len(offers)} oferte totale.")
            
            if offers:
                # Filtrăm și curățăm prețurile
                valid_prices = []
                for o in offers:
                    # Ne asigurăm că e un preț valid
                    if 'dph_total' in o:
                        price = float(o['dph_total'])
                        # Eliminăm erorile de preț (sub 10 cenți e imposibil)
                        if price > 0.1:
                            valid_prices.append(price)
                
                if valid_prices:
                    min_price = min(valid_prices)
                    # DEBUG: Arată-mi primele 3 prețuri găsite ca să fiu sigur
                    valid_prices.sort()
                    print(f"Top 3 cele mai mici prețuri găsite: {valid_prices[:3]}")
                    return min_price
                else:
                    print("⚠️ Ofertele există, dar nu au preț valid setat.")
                    return None
            else:
                print("⚠️ Zero oferte găsite. Piața e goală sau API-ul a schimbat numele.")
                return None
        else:
            print(f"❌ Serverul a refuzat cererea. Cod: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Eroare Conexiune: {e}")
    return None

def main():
    print("--- Market Hawk 2.0 (Wide Net) ---")
    current_price = get_market_price()
    
    if current_price is None:
        print("❌ CRITIC: Nu am putut stabili un preț de referință.")
        return
        
    print(f"\n💎 PRETUL PIETEI (FLOOR PRICE): ${current_price:.4f}")

    # LOGICA DE ALERTARE
    if current_price <= DANGER_PRICE:
        msg = (f"🚨 *TITANIC MODE ACTIVAT* 🚨\n\n"
               f"H100 la lichidare: *${current_price}/oră*\n"
               f"Sub pragul critic de ${DANGER_PRICE}.\n"
               f"Cumpără ACUM!")
        send_telegram(msg)
        print(">> Alarma Roșie trimisă!")
        
    elif current_price <= WARNING_PRICE:
        msg = (f"⚠️ *Market Hawk Alert* ⚠️\n\n"
               f"H100 a scăzut la: *${current_price}/oră*\n"
               f"Atenție, preț bun.")
        send_telegram(msg)
        print(">> Alarma Galbenă trimisă!")
        
    else:
        print(f">> Prețul (${current_price}) este stabil (peste ${WARNING_PRICE}).")

if __name__ == "__main__":
    main()
