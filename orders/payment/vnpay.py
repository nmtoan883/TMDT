import hashlib
import hmac
import urllib.parse
from datetime import datetime


class VNPay:
    def __init__(self):
        # Thông tin test (sandbox)
        self.vnp_TmnCode = "TESTCODE"
        self.vnp_HashSecret = "SECRETKEY"

        # Link thanh toán sandbox
        self.vnp_Url = "https://sandbox.vnpayment.vn/paymentv2/vpcpay.html"

        # URL nhận kết quả sau khi thanh toán
        self.vnp_ReturnUrl = "http://127.0.0.1:8000/payment_return"

    def create_payment_url(self, order_id, amount):
        # Các tham số gửi sang VNPay
        vnp_Params = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": self.vnp_TmnCode,
            "vnp_Amount": str(amount * 100),
            "vnp_CreateDate": datetime.now().strftime("%Y%m%d%H%M%S"),
            "vnp_CurrCode": "VND",
            "vnp_IpAddr": "127.0.0.1",
            "vnp_Locale": "vn",
            "vnp_OrderInfo": f"Thanh toan don hang {order_id}",
            "vnp_OrderType": "billpayment",
            "vnp_ReturnUrl": self.vnp_ReturnUrl,
            "vnp_TxnRef": str(order_id),
        }

        # Sắp xếp tham số theo alphabet
        sorted_params = sorted(vnp_Params.items())

        # Tạo query string
        query_string = urllib.parse.urlencode(sorted_params)

        # Tạo hash bảo mật
        hash_value = hmac.new(
            self.vnp_HashSecret.encode(),
            query_string.encode(),
            hashlib.sha512
        ).hexdigest()

        # Tạo URL thanh toán
        payment_url = (
            f"{self.vnp_Url}?{query_string}"
            f"&vnp_SecureHash={hash_value}"
        )

        return payment_url