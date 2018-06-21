import requests

from MedicalDispenser.settings import INSTA_MOJO_API_KEY, \
    INSTA_MOJO_AUTH_TOKEN

webhook_url = 'https://imed.iqube.io/users/api/v1/payment_webhook'


def create_payment_request(purpose, amount, phone, buyer_name=None, email=None):
    headers = {"X-Api-Key": INSTA_MOJO_API_KEY, "X-Auth-Token": INSTA_MOJO_AUTH_TOKEN}
    payload = {
        'purpose': purpose,
        'amount': amount,
        'phone': phone,
        # 'redirect_url': 'https://imed.iqube.io',
        'send_email': 'False',
        'send_sms': 'True',
        'webhook': webhook_url,
        # 'expires_at': expiry_string,
        'allow_repeated_payments': 'True',
    }
    if buyer_name:
        payload['buyer_name'] = buyer_name
    if email:
        payload['email'] = email
        payload['send_email'] = True
    response = requests.post("https://www.instamojo.com/api/1.1/payment-requests/", data=payload, headers=headers)
    if response.json().get("success"):
        return response.json().get("payment_request")
    else:
        return False


def check_payment(payment_id):
    headers = {"X-Api-Key": INSTA_MOJO_API_KEY, "X-Auth-Token": INSTA_MOJO_AUTH_TOKEN}
    response = requests.get(
        "https://www.instamojo.com/api/1.1/payment-requests/" + payment_id + "/",
        headers=headers)
    print(response.text)
