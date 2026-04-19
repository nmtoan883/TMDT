from django.urls import path
from . import views

app_name = 'dasher_admin'

urlpatterns = [
    path('', views.index, name='index'),
]
