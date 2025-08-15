from django.contrib import admin
from django import forms
from .models import Transaction
from customers.models import Customer

class TransactionAdminForm(forms.ModelForm):
    """自定義交易表單"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 自定義客戶欄位顯示
        self.fields['customer'].queryset = Customer.objects.all().order_by('name')
        self.fields['customer'].empty_label = "請選擇客戶"
    
    class Meta:
        model = Transaction
        fields = '__all__'

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    form = TransactionAdminForm
    
    list_display = ('get_customer_display', 'transaction_type', 'n8_amount', 'twd_amount', 'cs_user', 'quick_reply', 'created_at')
    list_filter = ('transaction_type', 'quick_reply', 'created_at', 'cs_user')
    search_fields = ('customer__name', 'customer__n8_nickname', 'cs_user__username')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('交易資訊', {
            'fields': ('customer', 'transaction_type', 'n8_amount', 'twd_amount')
        }),
        ('客服資訊', {
            'fields': ('cs_user', 'quick_reply', 'no_reply_reason')
        }),
        ('系統資訊', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_customer_display(self, obj):
        """在列表中顯示客戶名稱"""
        return obj.customer.get_display_name()
    get_customer_display.short_description = '客戶'
    get_customer_display.admin_order_field = 'customer__name'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """自定義外鍵欄位顯示"""
        if db_field.name == "customer":
            kwargs["queryset"] = Customer.objects.all().order_by('name')
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: obj.get_display_name()
            return formfield
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        if not change:  # 新增時
            obj.cs_user = request.user
        super().save_model(request, obj, form, change)