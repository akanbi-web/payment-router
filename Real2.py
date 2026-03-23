from flask import Flask, request, jsonify
import requests
import uuid

app = Flask(__name__)

# 🔒 Your actual test keys
PAYSTACK_KEY = "sk_test_5eadb3c1f2a7cf879f5609d20c7418d4f71d59bb"
FLUTTERWAVE_KEY = "FLWSECK_TEST-af44efeba76ef235866efd3b99cfc4df-X"

# 🔹 Your email
CUSTOMER_EMAIL = "Ahmedridwan794@gmail.com"


def smart_router(amount, email):
    if amount < 100:
        return {"error": "Minimum deposit is ₦100"}

    unique_ref = f"txn_{uuid.uuid4().hex[:10]}"

    # -------- TRY PAYSTACK --------
    try:
        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {PAYSTACK_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"email": email, "amount": amount * 100}

        res = requests.post(url, json=payload, headers=headers, timeout=5)
        data = res.json()

        if res.status_code == 200 and data.get("status"):
            print("✅ Paystack success")
            return {
                "gateway": "Paystack",
                "link": data["data"]["authorization_url"],
                "reference": unique_ref
            }
        else:
            print("⚠️ Paystack failed:", data)

    except requests.exceptions.RequestException as e:
        print("❌ Paystack error:", str(e))

    # -------- FALLBACK TO FLUTTERWAVE --------
    try:
        url = "https://api.flutterwave.com/v3/payments"
        headers = {
            "Authorization": f"Bearer {FLUTTERWAVE_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "tx_ref": unique_ref,
            "amount": amount,
            "currency": "NGN",
            "redirect_url": "https://example.com",
            "customer": {
                "email": email,
                "name": "Ahmed Ridwan"
            }
        }

        res = requests.post(url, json=payload, headers=headers, timeout=5)
        data = res.json()

        if res.status_code == 200 and data.get("status") == "success":
            print("✅ Flutterwave success")
            return {
                "gateway": "Flutterwave",
                "link": data["data"]["link"],
                "reference": unique_ref
            }
        else:
            print("⚠️ Flutterwave failed:", data)

    except requests.exceptions.RequestException as e:
        print("❌ Flutterwave error:", str(e))
