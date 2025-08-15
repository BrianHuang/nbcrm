# customers/views.py - 修復版本
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Customer

@login_required
def customer_list(request):
    search_query = request.GET.get('search', '')
    customers = Customer.objects.all()
    
    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) |
            Q(line_nickname__icontains=search_query) |
            Q(n8_nickname__icontains=search_query) |
            Q(n8_phone__icontains=search_query) |
            Q(n8_email__icontains=search_query) |
            Q(notes__icontains=search_query) |
            Q(verified_accounts__icontains=search_query)
        )
    
    paginator = Paginator(customers, 20)
    page = request.GET.get('page')
    customers = paginator.get_page(page)
    
    return render(request, 'customers/customer_list.html', {
        'customers': customers,
        'search_query': search_query
    })

@login_required
def customer_detail(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    
    # 取得相關記錄，使用 try-except 避免模型不存在的錯誤
    transactions = []
    kyc_records = []
    
    try:
        transactions = customer.transactions.select_related('cs_user').order_by('-created_at')[:10]
    except Exception:
        pass
    
    try:
        kyc_records = customer.kyc_records.select_related('uploaded_by').order_by('-uploaded_at')[:10]
    except Exception:
        pass
    
    return render(request, 'customers/customer_detail.html', {
        'customer': customer,
        'transactions': transactions,
        'kyc_records': kyc_records
    })