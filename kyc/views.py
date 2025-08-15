# kyc/views.py - 更新視圖，讓所有人都能查看所有KYC記錄
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import Http404
from customers.models import Customer
from .models import KYCRecord
from .forms import KYCRecordForm

@login_required
def kyc_list(request):
    # 所有登入用戶都可以查看所有KYC記錄
    kyc_records = KYCRecord.objects.select_related('customer', 'uploaded_by').order_by('-uploaded_at')
    
    # 搜尋功能
    search_query = request.GET.get('search', '')
    if search_query:
        kyc_records = kyc_records.filter(
            customer__name__icontains=search_query
        ) | kyc_records.filter(
            bank_code__icontains=search_query
        ) | kyc_records.filter(
            verification_account__icontains=search_query
        ) | kyc_records.filter(
            file_description__icontains=search_query
        ) | kyc_records.filter(
            uploaded_by__username__icontains=search_query
        )
    
    paginator = Paginator(kyc_records, 20)
    page = request.GET.get('page')
    kyc_records = paginator.get_page(page)
    
    return render(request, 'kyc/kyc_list.html', {
        'kyc_records': kyc_records,
        'search_query': search_query
    })

@login_required
def kyc_upload(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        form = KYCRecordForm(request.POST, request.FILES)
        if form.is_valid():
            kyc_record = form.save(commit=False)
            kyc_record.customer = customer
            kyc_record.uploaded_by = request.user
            kyc_record.save()
            messages.success(request, 'KYC 檔案上傳成功！')
            return redirect('customers:customer_detail', customer_id=customer.id)
    else:
        form = KYCRecordForm()
    
    return render(request, 'kyc/kyc_upload.html', {
        'form': form,
        'customer': customer
    })

@login_required
def kyc_detail(request, kyc_id):
    # 所有登入用戶都可以查看任何KYC記錄的詳情
    kyc_record = get_object_or_404(KYCRecord, id=kyc_id)
    
    return render(request, 'kyc/kyc_detail.html', {'kyc_record': kyc_record})