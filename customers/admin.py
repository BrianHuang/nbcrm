from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import Customer
import os

class CustomerAdminForm(forms.ModelForm):
    """自定義客戶表單"""
    
    class Meta:
        model = Customer
        fields = '__all__'
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'cols': 50}),  # 一半高度
            'verified_accounts': forms.Textarea(attrs={'rows': 3, 'cols': 50}),  # 一半高度
        }

class KYCRecordInline(admin.TabularInline):
    """KYC 記錄內聯顯示"""
    from kyc.models import KYCRecord
    model = KYCRecord
    extra = 0  # 不顯示額外的空表單
    can_delete = False  # 不允許在此處刪除
    
    fields = ('bank_code', 'verification_account', 'get_file_preview', 'file_description', 'get_uploaded_by_display', 'uploaded_at')
    readonly_fields = ('get_file_preview', 'get_uploaded_by_display', 'uploaded_at')
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """自定義表單欄位"""
        if db_field.name == 'bank_code':
            kwargs['widget'] = forms.TextInput(attrs={'size': 8})  # 縮短銀行代碼欄位
        elif db_field.name == 'verification_account':
            kwargs['widget'] = forms.TextInput(attrs={'size': 15})  # 縮短驗證帳戶欄位
        elif db_field.name == 'file_description':
            kwargs['widget'] = forms.TextInput(attrs={'size': 30})  # 檔案說明用一行
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
    def get_file_preview(self, obj):
        """顯示檔案預覽（簡化版）"""
        if not obj.file:
            return "無檔案"
        
        try:
            file_url = obj.file.url
            file_name = os.path.basename(obj.file.name)
            
            if obj.is_image():
                return format_html(
                    '<img src="{}" style="max-width: 50px; max-height: 50px; border-radius: 3px;" /><br>'
                    '<small><a href="{}" target="_blank">{}</a></small>',
                    file_url, file_url, file_name[:20] + "..." if len(file_name) > 20 else file_name
                )
            elif obj.is_video():
                return format_html(
                    '<div style="text-align: center;">'
                    '<i style="font-size: 20px;">🎥</i><br>'
                    '<small><a href="{}" target="_blank">{}</a></small>'
                    '</div>',
                    file_url, file_name[:20] + "..." if len(file_name) > 20 else file_name
                )
            else:
                return format_html(
                    '<div style="text-align: center;">'
                    '<i style="font-size: 20px;">📄</i><br>'
                    '<small><a href="{}" target="_blank">{}</a></small>'
                    '</div>',
                    file_url, file_name[:20] + "..." if len(file_name) > 20 else file_name
                )
        except Exception:
            return format_html('<span style="color: #dc3545;">載入失敗</span>')
    
    get_file_preview.short_description = '檔案'
    
    def get_uploaded_by_display(self, obj):
        """顯示上傳者"""
        if hasattr(obj.uploaded_by, 'get_display_name'):
            return obj.uploaded_by.get_display_name()
        else:
            full_name = obj.uploaded_by.get_full_name().strip()
            if full_name:
                return f"{full_name}({obj.uploaded_by.username})"
            else:
                return obj.uploaded_by.username
    
    get_uploaded_by_display.short_description = '上傳客服'
    
    def has_add_permission(self, request, obj=None):
        """不允許在此處新增"""
        return False

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    form = CustomerAdminForm
    
    list_display = ('get_display_name', 'line_nickname', 'n8_phone', 'n8_email', 'get_kyc_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'line_nickname', 'n8_nickname', 'n8_phone', 'n8_email', 'notes', 'verified_accounts')
    readonly_fields = ('created_at', 'updated_at')
    
    # 添加 KYC 記錄內聯
    inlines = [KYCRecordInline]
    
    # 簡化的 fieldsets，不分組
    fieldsets = (
        (None, {
            'fields': (
                ('name', 'line_nickname'),
                ('n8_nickname', 'n8_phone'), 
                'n8_email',
                'notes',
                'verified_accounts',
                ('created_at', 'updated_at')
            )
        }),
    )
    
    def get_display_name(self, obj):
        return obj.get_display_name()
    get_display_name.short_description = '客戶姓名'
    get_display_name.admin_order_field = 'name'
    
    def get_kyc_count(self, obj):
        """顯示 KYC 記錄數量"""
        count = obj.kyc_records.count()
        if count > 0:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
                count
            )
        else:
            return format_html(
                '<span style="background: #6c757d; color: white; padding: 2px 6px; border-radius: 3px;">0</span>'
            )
    get_kyc_count.short_description = 'KYC 記錄'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # 編輯時
            return self.readonly_fields
        return ('created_at', 'updated_at')
    
    class Media:
        css = {
            'all': ('admin/css/custom_customer_admin.css',)
        }
