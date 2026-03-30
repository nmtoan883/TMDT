from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
def checkout(request):
    data = request.data

    amount = float(data.get('amount', 0))
    location = data.get('location')
    payment_method = data.get('payment_method')

    # ===== phí ship =====
    if location == 'noi_thanh':
        shipping_fee = 30000
    elif location == 'ngoai_thanh':
        shipping_fee = 50000
    else:
        return Response({'error': 'Địa điểm không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)

    total = amount + shipping_fee

    # ===== thanh toán =====
    if payment_method == 'momo':
        payment_status = "Thanh toán qua MoMo"
    elif payment_method == 'zalopay':
        payment_status = "Thanh toán qua ZaloPay"
    elif payment_method == 'cod':
        payment_status = "Thanh toán khi nhận hàng"
    else:
        return Response({'error': 'Phương thức không hợp lệ'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({
        "amount": amount,
        "shipping_fee": shipping_fee,
        "total": total,
        "payment_method": payment_method,
        "payment_status": payment_status
    })