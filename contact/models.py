from django.db import models

class Contact(models.Model):
    SUBJECT_CHOICES = [
        ('support', 'Hỗ trợ đơn hàng'),
        ('consult', 'Tư vấn sản phẩm'),
        ('feedback', 'Góp ý'),
        ('complaint', 'Khiếu nại'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='support')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name