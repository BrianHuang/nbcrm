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
            'notes': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
            'verified_accounts': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
        }

class KYCRecordInlineForm(forms.ModelForm):
    """自定義 KYC 內聯表單"""
    
    class Meta:
        from kyc.models import KYCRecord
        model = KYCRecord
        fields = '__all__'
        widgets = {
            'bank_code': forms.TextInput(attrs={'size': 8, 'placeholder': '3位數字'}),
            'verification_account': forms.TextInput(attrs={'size': 15, 'placeholder': '帳號數字'}),
            'file_description': forms.TextInput(attrs={'size': 30, 'placeholder': '檔案說明（選填）'}),
        }

class KYCRecordInline(admin.TabularInline):
    """KYC 記錄內聯顯示 - 支援新增和編輯"""
    from kyc.models import KYCRecord
    model = KYCRecord
    form = KYCRecordInlineForm
    extra = 1  # 顯示 1 個空表單供新增
    can_delete = True  # 允許刪除
    
    fields = ('bank_code', 'verification_account', 'file', 'get_file_preview', 'file_description', 'get_uploaded_by_display', 'uploaded_at')
    readonly_fields = ('get_file_preview', 'get_uploaded_by_display', 'uploaded_at')
    
    def get_formset(self, request, obj=None, **kwargs):
        """自定義表單集，設置初始值"""
        formset = super().get_formset(request, obj, **kwargs)
        
        # 保存 request 到 formset，以便在保存時使用
        formset.request = request
        return formset
    
    def get_file_preview(self, obj):
        """顯示檔案預覽（簡化版）"""
        if not obj or not obj.file:
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
    
    get_file_preview.short_description = '檔案預覽'
    
    def get_uploaded_by_display(self, obj):
        """顯示上傳者"""
        if not obj or not obj.uploaded_by:
            return "新記錄"
        
        if hasattr(obj.uploaded_by, 'get_display_name'):
            return obj.uploaded_by.get_display_name()
        else:
            full_name = obj.uploaded_by.get_full_name().strip()
            if full_name:
                return f"{full_name}({obj.uploaded_by.username})"
            else:
                return obj.uploaded_by.username
    
    get_uploaded_by_display.short_description = '上傳客服'
    
    def save_model(self, request, obj, form, change):
        """保存 KYC 記錄時設置上傳者"""
        if not change:  # 新增時
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
    
    def has_add_permission(self, request, obj=None):
        """允許新增 KYC 記錄"""
        return True
    
    def has_change_permission(self, request, obj=None):
        """允許編輯 KYC 記錄"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """根據用戶角色決定刪除權限"""
        if obj and hasattr(obj, 'uploaded_by'):
            # 管理員可以刪除所有記錄，一般用戶只能刪除自己上傳的
            if request.user.is_admin():
                return True
            elif hasattr(obj, 'uploaded_by'):
                return obj.uploaded_by == request.user
        return request.user.is_admin()

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    form = CustomerAdminForm
    
    list_display = ('get_display_name', 'line_nickname', 'n8_phone', 'n8_email', 'get_kyc_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'line_nickname', 'n8_nickname', 'n8_phone', 'n8_email', 'notes', 'verified_accounts')
    readonly_fields = ('created_at', 'updated_at')
    
    # 添加 KYC 記錄內聯
    inlines = [KYCRecordInline]
    
    # 簡化的 fieldsets
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
    
    def save_formset(self, request, form, formset, change):
        """保存表單集時設置上傳者"""
        instances = formset.save(commit=False)
        
        for instance in instances:
            # 如果是新的 KYC 記錄，設置上傳者
            if not instance.pk and hasattr(instance, 'uploaded_by'):
                instance.uploaded_by = request.user
            instance.save()
        
        # 刪除標記為刪除的實例
        formset.save_m2m()
        for obj in formset.deleted_objects:
            obj.delete()
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # 編輯時
            return self.readonly_fields
        return ('created_at', 'updated_at')
    
    class Media:
        css = {
            'all': ('admin/css/custom_customer_admin.css',)
        }
        js = ('admin/js/kyc_inline.js',)
