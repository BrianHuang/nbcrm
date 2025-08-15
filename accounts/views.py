from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from customers.models import Customer
from transactions.models import Transaction
from kyc.models import KYCRecord

User = get_user_model()

@login_required
def dashboard(request):
    context = {
        'total_customers': Customer.objects.count(),
        'total_transactions': Transaction.objects.count(),
        'total_kyc_records': KYCRecord.objects.count(),
        'recent_transactions': Transaction.objects.select_related('customer', 'cs_user')[:5],
    }
    return render(request, 'accounts/dashboard.html', context)