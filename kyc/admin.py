# kyc/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import KYCRecord

@admin.register(KYCRecord)
class KYCRecordAdmin(admin.ModelAdmin):
    list_display = (
        'customer', 
        'bank_code',
        'verification_account', 
        'get_file_preview',
        'file_description',
        'uploaded_by', 
        'uploaded_at'
    )
    list_filter = ('uploaded_at', 'uploaded_by', 'bank_code')
    search_fields = (
        'customer__name', 
        'bank_code',
        'verification_account', 
        'file_description',
        'uploaded_by__username'
    )
    readonly_fields = ('uploaded_at', 'get_file_preview', 'get_file_info')
    list_per_page = 25
    
    fieldsets = (
        ('客戶資訊', {
            'fields': ('customer',)
        }),
        ('銀行資訊 (選填)', {
            'fields': ('bank_code', 'verification_account'),
            'description': '銀行代碼和驗證帳戶為選填欄位'
        }),
        ('檔案資訊', {
            'fields': ('file', 'get_file_preview', 'file_description', 'get_file_info'),
        }),
        ('上傳資訊', {
            'fields': ('uploaded_by', 'uploaded_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_file_preview(self, obj):
        """顯示檔案預覽"""
        if not obj.file:
            return "無檔案"
        
        file_url = obj.file.url
        file_name = obj.file.name.split('/')[-1]
        
        if obj.is_image():
            # 圖片預覽
            return format_html(
                '<div style="text-align: center;">'
                '<img src="{}" style="max-width: 100px; max-height: 100px; border-radius: 5px;" /><br>'
                '<small><a href="{}" target="_blank">🖼️ {}</a></small>'
                '</div>',
                file_url, file_url, file_name
            )
        elif obj.is_video():
            # 影片預覽
            return format_html(
                '<div style="text-align: center;">'
                '<video width="100" height="60" controls style="border-radius: 5px;">'
                '<source src="{}" type="video/mp4">'
                '您的瀏覽器不支援影片標籤。'
                '</video><br>'
                '<small><a href="{}" target="_blank">🎥 {}</a></small>'
                '</div>',
                file_url, file_url, file_name
            )
        else:
            # 其他檔案類型
            return format_html(
                '<div style="text-align: center;">'
                '<div style="padding: 20px; background: #f0f0f0; border-radius: 5px; margin: 10px 0;">'
                '<i style="font-size: 24px;">📄</i><br>'
                '<small><a href="{}" target="_blank">{}</a></small>'
                '</div></div>',
                file_url, file_name
            )
    
    get_file_preview.short_description = '檔案預覽'
    get_file_preview.allow_tags = True
    
    def get_file_info(self, obj):
        """顯示檔案詳細資訊"""
        if obj.file:
            file_type = ''
            if obj.is_image():
                file_type = '🖼️ 圖片檔案'
            elif obj.is_video():
                file_type = '🎥 影片檔案'
            else:
                file_type = '📄 一般檔案'
            
            return format_html(
                '<strong>類型：</strong>{}<br>'
                '<strong>大小：</strong>{}<br>'
                '<strong>檔名：</strong>{}',
                file_type, obj.get_file_size_display(), obj.file.name.split('/')[-1]
            )
        return '無檔案'
    get_file_info.short_description = '檔案資訊'
    get_file_info.allow_tags = True
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # 新增時
            form.base_fields['uploaded_by'].initial = request.user
        
        # 自定義客戶選項顯示格式
        from customers.models import Customer
        if 'customer' in form.base_fields:
            customers = Customer.objects.all().order_by('name')
            choices = [(customer.id, customer.get_display_name()) for customer in customers]
            form.base_fields['customer'].choices = [('', '請選擇客戶')] + choices
        
        # 設置幫助文字
        if 'bank_code' in form.base_fields:
            form.base_fields['bank_code'].help_text = '選填：3位數字的銀行代碼，例如：004、012、822'
        if 'verification_account' in form.base_fields:
            form.base_fields['verification_account'].help_text = '選填：數字帳戶號碼'
        
        return form
    
    def save_model(self, request, obj, form, change):
        if not change:  # 新增時
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # 編輯時
            return self.readonly_fields + ('uploaded_by',)
        return self.readonly_fields
    
    class Media:
        css = {
            'all': ('admin/css/kyc_preview.css',)
        }