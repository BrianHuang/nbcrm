from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Transaction

@login_required
def transaction_list(request):
    transactions = Transaction.objects.select_related('customer', 'cs_user').order_by('-created_at')
    
    search_query = request.GET.get('search', '')
    if search_query:
        transactions = transactions.filter(
            Q(customer__name__icontains=search_query) |
            Q(cs_user__username__icontains=search_query)
        )
    
    paginator = Paginator(transactions, 20)
    page = request.GET.get('page')
    transactions = paginator.get_page(page)
    
    return render(request, 'transactions/transaction_list.html', {
        'transactions': transactions,
        'search_query': search_query
    })