from django.urls import path
from . import views

app_name = 'kyc'

urlpatterns = [
    path('', views.kyc_list, name='kyc_list'),
]
