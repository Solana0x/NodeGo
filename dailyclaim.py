import datetime
import sys
from colorama import init, Fore, Style
from curl_cffi import requests
import concurrent.futures

init(autoreset=True)


def load_lines(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{Fore.RED}[FATAL] {filename} not found. Please create it.{Style.RESET_ALL}")
        sys.exit(1)


def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def daily_claim_worker(index, token, proxy_line):
    proxies = {
        "http": proxy_line,
        "https": proxy_line
    }
    print(f"\n{Fore.BLUE}{get_timestamp()} [INFO] Token #{index+1}, using proxy: {proxy_line}{Style.RESET_ALL}")

    headers = {
        "accept": "application/json, text/plain, */*",
        "authorization": f"Bearer {token}",
        "priority": "u=1, i",
        "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "Referer": "https://app.nodego.ai/",
        "Referrer-Policy": "strict-origin-when-cross-origin"
    }

    daily_url = "https://nodego.ai/api/daily-earnings"
    max_retries = 3
    success = False

    for attempt in range(1, max_retries + 1):
        try:
            response = requests.get(
                daily_url,
                headers=headers,
                proxies=proxies,
                impersonate="chrome110",
                timeout=30
            )

            if response.status_code in [200, 201]:
                print(f"{Fore.GREEN}{get_timestamp()} [SUCCESS] Daily claim ✅ for token #{index+1}{Style.RESET_ALL}")
                success = True
                break
            else:
                print(
                    f"{Fore.RED}{get_timestamp()} [ERROR] Attempt {attempt}/{max_retries} for token #{index+1} "
                    f"status: {response.status_code}, resp: {response.text}{Style.RESET_ALL}"
                )
        except Exception as e:
            print(f"{Fore.RED}{get_timestamp()} [EXCEPTION] Attempt {attempt}/{max_retries} for token #{index+1} - {e}{Style.RESET_ALL}")
        if not success and attempt < max_retries:
            print(f"{Fore.YELLOW}{get_timestamp()} [RETRY] Retrying daily claim for token #{index+1}{Style.RESET_ALL}")

    if not success:
        print(f"{Fore.RED}{get_timestamp()} [FAIL] Could not complete daily claim after {max_retries} attempts for token #{index+1}{Style.RESET_ALL}")


def main():
    tokens = load_lines("accessToken.txt")
    proxies_list = load_lines("proxy.txt")
    total = min(len(tokens), len(proxies_list))
    if total == 0:
        print(f"{Fore.RED}[ERROR] No tokens or proxies found.{Style.RESET_ALL}")
        return
    print(f"{Fore.CYAN}{get_timestamp()} [INFO] Starting daily claim for {total} tokens...{Style.RESET_ALL}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for i in range(total):
            token = tokens[i]
            proxy_line = proxies_list[i]
            futures.append(executor.submit(daily_claim_worker, i, token, proxy_line))
        concurrent.futures.wait(futures)

    print(f"\n{Fore.CYAN}{get_timestamp()} [INFO] All done! Processed {total} tokens.{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
