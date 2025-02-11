import sys
import json
import traceback
import random
import datetime
import threading
from colorama import init, Fore, Style
from curl_cffi import requests
from solve_turnstile import solve_turnstile

init(autoreset=True)
REFERRAL_CODES = [
    "NODED6D5AFD7BEF4",
    "NODEE5FB06CA2299",
    # Add your referal code here
]

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def log_info(message):
    print(f"{Fore.CYAN}{get_timestamp()} [INFO]{Style.RESET_ALL} {message}")

def log_warn(message):
    print(f"{Fore.YELLOW}{get_timestamp()} [WARN]{Style.RESET_ALL} {message}")

def log_error(message):
    print(f"{Fore.RED}{get_timestamp()} [ERROR]{Style.RESET_ALL} {message}")

def load_lines(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        log_error(f"'{filename}' not found. Please create it and add required data.")
        sys.exit(1)

def worker_register():
    proxy_lines = load_lines("proxy.txt")
    username_lines = load_lines("username.txt")
    account_lines = load_lines("accounts.txt")
    if not proxy_lines:
        log_error("No proxies found in 'proxy.txt'.")
        return
    if not username_lines:
        log_error("No usernames found in 'username.txt'.")
        return
    if not account_lines:
        log_error("No accounts found in 'accounts.txt'.")
        return

    total = min(len(proxy_lines), len(username_lines), len(account_lines))
    if total == 0:
        log_error("Mismatch or no data in proxy/username/accounts. Exiting...")
        return

    log_info(f"Starting registration for {total} accounts...")

    for i in range(total):
        proxy_line = proxy_lines[i]
        username = username_lines[i]
        account_parts = account_lines[i].split(":", 1)
        if len(account_parts) < 2:
            log_warn(f"Invalid account format at line {i+1} in 'accounts.txt'. Skipping...")
            continue

        email, password = account_parts[0], account_parts[1]
        proxies = {
            "http": proxy_line,
            "https": proxy_line
        }
        success = False
        for attempt in range(1, 4):
            log_info(f"Attempting registration #{i+1} with proxy: {proxy_line} (Attempt {attempt}/3)")
            try:
                CAPTCHA_SITE_KEY = "0x4AAAAAAA4zgfgCoYChIZf4"
                PAGE_URL         = "https://app.nodego.ai"
                TWO_CAPTCHA_API  = "YOUR2CaptchaKEy"

                captcha_solution = solve_turnstile(
                    TWO_CAPTCHA_API,
                    CAPTCHA_SITE_KEY,
                    PAGE_URL
                )

                log_info(f"Captcha solved! token: {captcha_solution}")
                ref_code = random.choice(REFERRAL_CODES)
                url = "https://nodego.ai/api/auth/register"
                headers = {
                    "accept": "application/json, text/plain, */*",
                    "content-type": "application/json"
                }
                payload = {
                    "username": username,
                    "email": email,
                    "password": password,
                    "refBy": ref_code,
                    "captcha": captcha_solution
                }

                response = requests.post(
                    url,
                    headers=headers,
                    json=payload,
                    proxies=proxies,
                    impersonate="chrome110",
                    timeout=30
                )

                if response.status_code not in [200, 201]:
                    raise Exception(f"Registration failed: {response.status_code} - {response.text}")
                data = response.json()
                log_info(f"Registration response: {data}")
                access_token = None
                if "metadata" in data and "accessToken" in data["metadata"]:
                    access_token = data["metadata"]["accessToken"]

                if not access_token:
                    log_warn(f"No access token found for {email}.")
                    break
                log_info(f"AccessToken for {email}: {access_token}")
                with open("accessToken.txt", "a", encoding="utf-8") as out_file:
                    out_file.write(access_token + "\n")
                me_url = "https://nodego.ai/api/user/me"
                me_headers = {
                    "accept": "application/json, text/plain, */*",
                    "accept-language": "en-US,en;q=0.9",
                    "authorization": f"Bearer {access_token}",
                    "if-none-match": 'W/"255-Jn4vhkHxPsnpjuk3W/ksa8vukGE"',
                    "priority": "u=1, i",
                    "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "sec-fetch-dest": "empty",
                    "sec-fetch-mode": "cors",
                    "sec-fetch-site": "same-site"
                }

                me_response = requests.get(
                    me_url,
                    headers=me_headers,
                    proxies=proxies,
                    impersonate="chrome110",
                    timeout=30
                )
                if me_response.status_code not in [200, 304]:
                    log_warn(f"/me request returned status {me_response.status_code}: {me_response.text}")

                me_data = me_response.json()
                with open("refer.txt", "a", encoding="utf-8") as ref_file:
                    ref_file.write(json.dumps(me_data) + "\n")

                log_info("refer code saved ✅")

                success = True
                break  

            except Exception as ex:
                log_error(f"Error on attempt {attempt}/3 for proxy '{proxy_line}': {ex}")
                traceback.print_exc()
                if attempt < 3:
                    log_info("Retrying...")

        if not success:
            log_error(f"Failed to register after 3 attempts for {email} with proxy {proxy_line}")

    log_info("Registration process completed.")

def main():
    t = threading.Thread(target=worker_register)
    t.start()
    t.join()

if __name__ == "__main__":
    main()
