import os
from flask import Flask, request, jsonify
import requests
import uuid

app = Flask(__name__)

# 🔒 Keys (Uses Render Environment Variables first)
PAYSTACK_KEY = os.environ.get("PAYSTACK_KEY", "sk_test_5eadb3c1f2a7cf879f5609d20c7418d4f71d59bb")
FLUTTERWAVE_KEY = os.environ.get("FLUTTERWAVE_KEY", "FLWSECK_TEST-af44efeba76ef235866efd3b99cfc4df-X")
CUSTOMER_EMAIL = "Ahmedridwan794@gmail.com"

# 🏠 HOME ROUTE (For Cron-job to ping)
@app.route('/')
def home():
    return "Payment Router is Awake! 🚀", 200

def smart_router(amount, email):
    unique_ref = f"txn_{uuid.uuid4().hex[:10]}"

    # --- TRY PAYSTACK (3-SECOND LIMIT) ---
    try:
        url = "https://api.paystack.co"
        headers = {"Authorization": f"Bearer {PAYSTACK_KEY}"}
        payload = {"email": email, "amount": int(amount) * 100}

        # ⏱️ 3-second timeout
        res = requests.post(url, json=payload, headers=headers, timeout=3)
        data = res.json()

        if res.status_code == 200 and data.get("status"):
            return {"gateway": "Paystack", "link": data["data"]["authorization_url"], "ref": unique_ref}
    except:
        print("⚡ Paystack slow or failed. Switching to Flutterwave...")

    # --- FALLBACK TO FLUTTERWAVE ---
    try:
        url = "https://api.flutterwave.com"
        headers = {"Authorization": f"Bearer {FLUTTERWAVE_KEY}"}
        payload = {
            "tx_ref": unique_ref,
            "amount": amount,
            "currency": "NGN",
            "customer": {"email": email}
        }

        res = requests.post(url, json=payload, headers=headers, timeout=10)
        data = res.json()

        if res.status_code == 200 and data.get("status") == "success":
            return {"gateway": "Flutterwave", "link": data["data"]["link"], "ref": unique_ref}
    except Exception as e:
        return {"error": "Both failed", "details": str(e)}

    return {"error": "Payment failed"}

@app.route("/pay", methods=["POST"])
def pay():
    data = request.json or {}
    amount = data.get("amount")
    email = data.get("email") or CUSTOMER_EMAIL
    if not amount:
        return jsonify({"error": "No amount"}), 400
    return jsonify(smart_router(amount, email))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
