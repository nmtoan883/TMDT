class Sepay:
    def __init__(self):
        from django.conf import settings
        self.api_key = getattr(settings, 'SEPAY_API_KEY', '')
        self.account_number = getattr(settings, 'SEPAY_ACCOUNT_NUMBER', '')
        self.bank = getattr(settings, 'SEPAY_BANK', '')

    def get_qr_code_url(self, order_id, amount):
        # Tạo URL QR tĩnh của Sepay
        des = f"DH{order_id}"
        return f"https://qr.sepay.vn/img?acc={self.account_number}&bank={self.bank}&amount={int(amount)}&des={des}"

    def create_payment_url(self, order_id, amount, return_url=None):
        # Vì Sepay là QR cố định, không có trang cổng thanh toán riêng rẽ nên lấy chính nó làm payment_url
        return self.get_qr_code_url(order_id, amount)
