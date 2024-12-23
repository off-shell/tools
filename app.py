from flask import Flask, request, render_template
import requests
import logging
import time

# Setup logging to display in the console
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Variabel global untuk Custom HTTP Client
request_headers = None
response_data = None
response_headers = None

@app.route("/")
def home():
    logging.info('Home page accessed')
    return render_template("index.html")

@app.route("/http-client", methods=["GET", "POST"])
def http_client():
    logging.info('HTTP client page accessed')
    global request_headers, response_data, response_headers
    return render_template("http_client.html",
                           request_headers=request_headers,
                           response=response_data,
                           response_headers=response_headers)

@app.route("/http-client/send_request", methods=["POST"])
def send_request():
    global request_headers, response_data, response_headers
    url = request.form.get("url")

    logging.info(f'Received POST request to {url}')

    try:
        response = requests.get(url)
        request_headers = "\n".join(f"{key}: {value}" for key, value in response.request.headers.items())
        response_data = response.text
        response_headers = "\n".join(f"{key}: {value}" for key, value in response.headers.items())

        logging.info(f'Response received for {url} with status code {response.status_code}')
    except Exception as e:
        response_data = f"Error: {str(e)}"
        response_headers = ""
        request_headers = ""
        logging.error(f'Error fetching URL {url}: {str(e)}')

    return http_client()

@app.route("/dirbuster", methods=["GET", "POST"])
def dirbuster():
    results = []  # Menyimpan hasil fuzzing

    if request.method == "POST":
        target_url = request.form.get("target_url")
        wordlist_url = request.form.get("wordlist_url")
        user_agent = request.form.get("user_agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36")
        delay = float(request.form.get("delay", 1.0))  # Delay in seconds

        logging.info(f'Fuzzing target {target_url} with wordlist {wordlist_url}, User-Agent: {user_agent}, Delay: {delay} seconds')

        try:
            wordlist_response = requests.get(wordlist_url)
            wordlist = wordlist_response.text.splitlines()  # Memisahkan wordlist menjadi daftar kata

            for word in wordlist:
                fuzz_url = f"{target_url.rstrip('/')}/{word}"
                headers = {
                    'User-Agent': user_agent
                }
                try:
                    response = requests.get(fuzz_url, headers=headers)
                    results.append({
                        "url": fuzz_url,
                        "status": response.status_code,
                        "size": len(response.content),
                    })
                    logging.info(f'Checked {fuzz_url} with status {response.status_code}')
                except Exception as e:
                    results.append({
                        "url": fuzz_url,
                        "status": "Error",
                        "size": str(e),
                    })
                    logging.error(f'Error accessing {fuzz_url}: {str(e)}')

                time.sleep(delay)  # Menambahkan delay antara request
        except Exception as e:
            results.append({
                "url": wordlist_url,
                "status": "Error",
                "size": str(e),
            })
            logging.error(f'Error fetching wordlist from {wordlist_url}: {str(e)}')

        if request.is_xhr:  # Periksa apakah permintaan datang melalui AJAX
            return render_template("dirbuster.html", results=results)

    return render_template("dirbuster.html", results=results)
if __name__ == "__main__":
    logging.info('Starting Flask application')
    app.run(host="0.0.0.0", port=5000)