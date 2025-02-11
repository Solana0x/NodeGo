import datetime
import sys
from colorama import init, Fore, Style
from curl_cffi import requests
import concurrent.futures
import time

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

TASKS_INFO = {
    "T001": "Verify Email ✅",
    "T005": "Follow Twitter ✅",
    "T006": "Rate us ✅",
    "T009": "Join Discord ✅",
    "T011": "share Refer ✅",
    "T012": "Retweet ✅",
    "T014": "Comment ✅",
    "T100": "Invite 1 friend ✅",
    "T101": "Invite 3 friends ✅",
    "T102": "Invite 5 friends ✅",
    "T103": "Invite 10 Friends ✅"
}

def run_tasks_for_token(index, token, proxy_line):
    proxies = {
        "http": proxy_line,
        "https": proxy_line
    }

    print(f"\n{Fore.BLUE}{get_timestamp()} [INFO] Token #{index+1}, using proxy: {proxy_line}{Style.RESET_ALL}")

    headers = {
        "accept": "application/json, text/plain, */*",
        "content-type": "application/json",
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
    for task_id, task_desc in TASKS_INFO.items():
        task_success = False

        for attempt in range(1, 4):
            try:
                response = requests.post(
                    "https://nodego.ai/api/user/task",
                    headers=headers,
                    json={"taskId": task_id},
                    proxies=proxies,
                    impersonate="chrome110",
                    timeout=30
                )

                if response.status_code in [200, 201]:
                    print(
                        f"{Fore.GREEN}{get_timestamp()} [SUCCESS] "
                        f"{task_id} -> {task_desc} for token #{index+1}{Style.RESET_ALL}"
                    )
                    task_success = True
                    break
                else:
                    print(
                        f"{Fore.RED}{get_timestamp()} [ERROR] Attempt {attempt}/3 for {task_id} "
                        f"(token #{index+1}): status {response.status_code}, resp: {response.text}{Style.RESET_ALL}"
                    )

            except Exception as e:
                print(
                    f"{Fore.RED}{get_timestamp()} [EXCEPTION] Attempt {attempt}/3 for {task_id} "
                    f"(token #{index+1}) - {e}{Style.RESET_ALL}"
                )
            if attempt < 3:
                print(f"{Fore.YELLOW}{get_timestamp()} [RETRY] Retrying {task_id} for token #{index+1}{Style.RESET_ALL}")
                time.sleep(1)

        if not task_success:
            print(
                f"{Fore.RED}{get_timestamp()} [FAIL] {task_id} could not be completed after 3 attempts "
                f"(token #{index+1}){Style.RESET_ALL}"
            )

    print(
        f"{Fore.MAGENTA}{get_timestamp()} [INFO] All selected tasks finished for token #{index+1}{Style.RESET_ALL}"
    )


def main():
    tokens = load_lines("accessToken.txt")
    proxies_list = load_lines("proxy.txt")

    total = min(len(tokens), len(proxies_list))
    if total == 0:
        print(f"{Fore.RED}[ERROR] No tokens or no proxies available.{Style.RESET_ALL}")
        return

    print(f"{Fore.CYAN}{get_timestamp()} [INFO] Starting tasks for {total} tokens...{Style.RESET_ALL}")
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        futures = []
        for i in range(total):
            token = tokens[i]
            proxy_line = proxies_list[i]
            future = executor.submit(run_tasks_for_token, i, token, proxy_line)
            futures.append(future)

        concurrent.futures.wait(futures)

    print(f"\n{Fore.CYAN}{get_timestamp()} [INFO] All done! Processed {total} tokens.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()
