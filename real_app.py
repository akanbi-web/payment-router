import os
import requests
import uuid
from flask import Flask, request, jsonify

app = Flask(__name__)

# 🔒 Keys (Uses Render Environment Variables first, then test keys as backup)
PAYSTACK_KEY = os.environ.get("PAYSTACK_KEY", "sk_test_5eadb3c1f2a7cf879f5609d20c7418d4f71d59bb")
FLUTTERWAVE_KEY = os.environ.get("FLUTTERWAVE_KEY", "FLWSECK_TEST-af44efeba76ef235866efd3b99cfc4df-X")
CUSTOMER_EMAIL = "Ahmedridwan794@gmail.com"

# 🏠 HOME ROUTE (This is what the Cron-job hits to keep the server awake)
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

        # ⏱️ The 3-second timer you requested
        res = requests.post(url, json=payload, headers=headers, timeout=3)
        data = res.json()

        if res.status_code == 200 and data.get("status"):
            return {"gateway": "Paystack", "link": data["data"]["authorization_url"], "ref": unique_ref}
    except Exception as e:
        print(f"⚡ Paystack slow or failed: {str(e)}")

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
        return {"error": "Both gateways failed", "details": str(e)}

    return {"error": "Payment initialization failed"}

@app.route("/pay", methods=["POST"])
def pay():
    data = request.json or {}
    amount = data.get("amount")
    email = data.get("email") or CUSTOMER_EMAIL
    
    if not amount:
        return jsonify({"error": "No amount provided"}), 400
        
    return jsonify(smart_router(amount, email))

if __name__ == "__main__":
    # Render requires host 0.0.0.0 and port 10000
    app.run(host="0.0.0.0", port=10000)
