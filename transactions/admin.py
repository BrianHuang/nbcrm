from django.contrib import admin
from django import forms
from .models import Transaction
from customers.models import Customer
from accounts.models import User

class TransactionAdminForm(forms.ModelForm):
    """自定義交易表單"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['customer'].queryset = Customer.objects.all().order_by('name')
        self.fields['customer'].empty_label = "請選擇客戶"
    
    class Meta:
        model = Transaction
        fields = '__all__'

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    form = TransactionAdminForm
    
    list_display = ('get_customer_display', 'transaction_type', 'n8_amount', 'twd_amount', 'get_cs_user_display', 'quick_reply', 'created_at')
    list_filter = ('transaction_type', 'quick_reply', 'created_at', 'cs_user')
    search_fields = (
        'customer__name', 
        'customer__n8_nickname', 
        'cs_user__username',
        'cs_user__first_name',
        'cs_user__last_name'
    )
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
    
    def get_cs_user_display(self, obj):
        """顯示客服的名字(使用者名稱)"""
        return obj.cs_user.get_display_name()
    get_cs_user_display.short_description = '客服'
    get_cs_user_display.admin_order_field = 'cs_user__first_name'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """自定義外鍵欄位顯示"""
        if db_field.name == "customer":
            kwargs["queryset"] = Customer.objects.all().order_by('name')
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: obj.get_display_name()
            return formfield
        elif db_field.name == "cs_user":
            kwargs["queryset"] = User.objects.filter(role__in=['admin', 'cs']).order_by('first_name', 'username')
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: obj.get_display_name()
            return formfield
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def save_model(self, request, obj, form, change):
        if not change:  # 新增時
            obj.cs_user = request.user
        super().save_model(request, obj, form, change)