from django.urls import path
from . import views

app_name = 'legal'

urlpatterns = [
    path('chinh-sach/<slug:slug>/', views.policy_detail, name='policy_detail'),
    path('giay-phep-kinh-doanh/', views.business_license_detail, name='business_license'),
]