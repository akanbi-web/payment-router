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
    # Minimum deposit
    if amount < 100:
        return {"error": "Minimum deposit is ₦100"}

    unique_ref = f"txn_{uuid.uuid4().hex[:10]}"

    # ---- PAYSTACK ----
    try:
        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {PAYSTACK_KEY}",
            "Content-Type": "application/json"
        }
        payload = {"email": email, "amount": amount * 100}  # Paystack expects kobo
        res = requests.post(url, json=payload, headers=headers)
        data = res.json()
        if res.status_code == 200 and data.get("status"):
            return {"gateway": "Paystack", "link": data["data"]["authorization_url"], "reference": unique_ref}
    except:
        pass

    # ---- FLUTTERWAVE ----
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
            "customer": {"email": email, "name": "Ahmed Ridwan"}
        }
        res = requests.post(url, json=payload, headers=headers)
        data = res.json()
        if res.status_code == 200 and data.get("status") == "success":
            return {"gateway": "Flutterwave", "link": data["data"]["link"], "reference": unique_ref}
    except:
        pass

    return {"error": "All gateways failed"}

# ---- Flask endpoint ----
@app.route("/pay", methods=["POST"])
def pay():
    data = request.json
    amount = data.get("amount")
    email = data.get("email") or CUSTOMER_EMAIL

    if not amount:
        return jsonify({"error": "Missing amount"}), 400
    try:
        amount = int(amount)
    except:
        return jsonify({"error": "Amount must be a number"}), 400

    result = smart_router(amount, email)
    return jsonify(result)

# ---- Run server ----
app.run(host="0.0.0.0", port=5000)
