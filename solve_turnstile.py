import requests
import time

def solve_turnstile(api_key, sitekey, page_url):
    try:
        in_url = "http://2captcha.com/in.php"
        payload = {
            "key": api_key,
            "method": "turnstile",
            "sitekey": sitekey,
            "pageurl": page_url,
            "json": 1
        }
        in_res = requests.post(in_url, data=payload)
        in_data = in_res.json()

        if in_data.get("status") != 1:
            raise Exception(f"2Captcha error: {in_data.get('request')}")
        request_id = in_data.get("request")
        res_url = "http://2captcha.com/res.php"
        captcha_token = None
        for _ in range(24):
            time.sleep(5)
            check_params = {
                "key": api_key,
                "action": "get",
                "id": request_id,
                "json": 1
            }
            res_check = requests.get(res_url, params=check_params)
            res_data = res_check.json()

            if res_data.get("status") == 1:
                captcha_token = res_data.get("request")
                break
            else:
                if res_data.get("request") != "CAPCHA_NOT_READY":
                    raise Exception(f"2Captcha error: {res_data.get('request')}")
        if not captcha_token:
            raise TimeoutError("Timed out waiting for 2Captcha to solve Turnstile.")
        return captcha_token
    except Exception as exc:
        raise exc
