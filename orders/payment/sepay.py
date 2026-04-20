import hashlib
import hmac
import urllib.parse
from datetime import datetime


class Sepay:
    def __init__(self):
        self.merchant_code = "SEPAYTEST"
        self.secret_key = "SEPAYSECRET"
        self.endpoint = "https://sandbox.sepay.vn/payment"

    def _build_params(self, order_id, amount, return_url):
        return {
            "version": "1.0",
            "command": "pay",
            "merchant_code": self.merchant_code,
            "amount": str(int(amount * 100)),
            "currency": "VND",
            "order_id": str(order_id),
            "order_info": f"Thanh toan don hang {order_id}",
            "return_url": return_url,
            "timestamp": datetime.now().strftime("%Y%m%d%H%M%S"),
            "locale": "vn",
        }

    def _sign(self, params):
        sorted_items = sorted(params.items())
        raw_string = "&".join(f"{k}={v}" for k, v in sorted_items)
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            raw_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        return signature

    def create_payment_url(self, order_id, amount, return_url):
        params = self._build_params(order_id, amount, return_url)
        params["secure_hash"] = self._sign(params)
        query_string = urllib.parse.urlencode(params)
        return f"{self.endpoint}?{query_string}"

    def get_qr_code_url(self, payment_url, size="320x320"):
        encoded = urllib.parse.quote_plus(payment_url)
        return f"https://api.qrserver.com/v1/create-qr-code/?size={size}&data={encoded}&format=png&margin=10"
