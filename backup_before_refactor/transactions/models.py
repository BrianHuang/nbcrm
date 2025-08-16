from django.db import models
from django.contrib.auth import get_user_model
from customers.models import Customer

User = get_user_model()

class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('sell', '賣出'),
        ('buy', '收購'),
    ]
    
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='transactions', verbose_name='客戶')
    cs_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions', verbose_name='客服')
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPE_CHOICES, verbose_name='交易類型')
    n8_amount = models.DecimalField(max_digits=20, decimal_places=8, verbose_name='N8幣數量')
    twd_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='台幣金額')
    quick_reply = models.BooleanField(default=True, verbose_name='客戶訊息是否有在三分鐘內回覆')
    no_reply_reason = models.TextField(blank=True, verbose_name='未快速回覆原因')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    
    class Meta:
        verbose_name = '交易記錄'
        verbose_name_plural = '交易記錄'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.customer.name} - {self.get_transaction_type_display()} - {self.n8_amount}"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.quick_reply and not self.no_reply_reason:
            raise ValidationError('未快速回覆時必須填寫原因')
