import requests
import json
import os

# --- CONFIGURARE ---
API_URL = "https://console.vast.ai/api/v0/bundles/"

def spy_on_market():
    # STRATEGIA: Cautam dupa MEMORIE (RAM), nu dupa nume.
    # H100 are 80GB RAM. Cerem tot ce are peste 75GB RAM.
    # Asta include A100 si H100.
    query_params = {
        "rentable": {"eq": True},
        "gpu_ram": {"gt": 75000}  # Mai mult de 75.000 MB
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        print("📡 SONDA ACTIVATĂ: Caut monștrii cu >80GB RAM...")
        response = requests.get(
            API_URL, 
            params={"q": json.dumps(query_params)}, 
            headers=headers, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            offers = data.get('offers', [])
            print(f"✅ Sonda a găsit {len(offers)} servere grele.")
            
            if offers:
                # Facem un recensământ al numelor
                nume_gasite = set()
                h100_gasiti = 0
                cel_mai_mic_pret = 100.0
                
                print("\n--- CE AM GĂSIT ÎN BULETIN ---")
                for o in offers:
                    nume = o.get('gpu_name', 'Necunoscut')
                    pret = float(o.get('dph_total', 0))
                    
                    # Adăugăm numele în lista unică
                    nume_gasite.add(nume)
                    
                    # Căutăm manual textul "H100" în nume
                    if "H100" in nume:
                        h100_gasiti += 1
                        if pret < cel_mai_mic_pret:
                            cel_mai_mic_pret = pret

                # Afișăm catalogul exact
                for n in nume_gasite:
                    print(f"👉 Nume Oficial: '{n}'")
                
                print("-" * 30)
                if h100_gasiti > 0:
                    print(f"💎 VICTORIE: Am identificat {h100_gasiti} unități H100!")
                    print(f"💰 Cel mai mic preț H100: ${cel_mai_mic_pret:.4f}")
                else:
                    print("⚠️ Am găsit servere puternice (A100 probabil), dar niciunul nu conține textul 'H100'.")
            else:
                print("⚠️ Niciun server 'greu' disponibil. Ciudat.")
        else:
            print(f"❌ Serverul ne-a refuzat. Cod: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Eroare: {e}")

if __name__ == "__main__":
    spy_on_market()
