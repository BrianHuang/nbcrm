from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import KYCRecord
from customers.models import Customer

class KYCRecordAdminForm(forms.ModelForm):
    """自定義KYC表單"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 自定義客戶欄位顯示
        self.fields['customer'].queryset = Customer.objects.all().order_by('name')
        self.fields['customer'].empty_label = "請選擇客戶"
    
    class Meta:
        model = KYCRecord
        fields = '__all__'

@admin.register(KYCRecord)
class KYCRecordAdmin(admin.ModelAdmin):
    form = KYCRecordAdminForm
    
    list_display = (
        'get_customer_display', 
        'bank_code',
        'verification_account', 
        'get_file_preview',
        'file_description',
        'get_uploaded_by_display',
        'uploaded_at'
    )
    list_filter = ('uploaded_at', 'uploaded_by', 'bank_code')
    search_fields = (
        'customer__name', 
        'customer__n8_nickname',
        'bank_code',
        'verification_account', 
        'file_description',
        'uploaded_by__username'
    )
    readonly_fields = ('uploaded_at', 'get_file_preview', 'get_file_info')
    list_per_page = 25
    
    def get_fieldsets(self, request, obj=None):
        """根據用戶角色和操作類型動態設置fieldsets"""
        if obj:  # 編輯現有記錄
            if request.user.is_admin():
                return (
                    ('客戶資訊', {
                        'fields': ('customer',)
                    }),
                    ('銀行資訊 (選填)', {
                        'fields': ('bank_code', 'verification_account'),
                        'description': '銀行代碼和驗證帳戶為選填欄位'
                    }),
                    ('檔案資訊 (選填)', {
                        'fields': ('file', 'get_file_preview', 'file_description', 'get_file_info'),
                        'description': '檔案上傳為選填，可只填寫銀行資訊，支援最大100MB檔案'
                    }),
                    ('上傳資訊', {
                        'fields': ('uploaded_by', 'uploaded_at'),
                        'classes': ('collapse',)
                    }),
                )
            else:
                return (
                    ('客戶資訊', {
                        'fields': ('customer',)
                    }),
                    ('銀行資訊 (選填)', {
                        'fields': ('bank_code', 'verification_account'),
                        'description': '銀行代碼和驗證帳戶為選填欄位'
                    }),
                    ('檔案資訊 (選填)', {
                        'fields': ('file', 'get_file_preview', 'file_description', 'get_file_info'),
                        'description': '檔案上傳為選填，可只填寫銀行資訊，支援最大100MB檔案'
                    }),
                    ('上傳資訊', {
                        'fields': ('uploaded_at',),
                        'classes': ('collapse',)
                    }),
                )
        else:  # 新增記錄
            if request.user.is_admin():
                return (
                    ('客戶資訊', {
                        'fields': ('customer',)
                    }),
                    ('銀行資訊 (選填)', {
                        'fields': ('bank_code', 'verification_account'),
                        'description': '銀行代碼和驗證帳戶為選填欄位'
                    }),
                    ('檔案資訊 (選填)', {
                        'fields': ('file', 'file_description'),
                        'description': '檔案上傳為選填，可只填寫銀行資訊，支援最大100MB檔案'
                    }),
                    ('上傳資訊', {
                        'fields': ('uploaded_by',),
                        'description': '預設為目前登入帳號'
                    }),
                )
            else:
                return (
                    ('客戶資訊', {
                        'fields': ('customer',)
                    }),
                    ('銀行資訊 (選填)', {
                        'fields': ('bank_code', 'verification_account'),
                        'description': '銀行代碼和驗證帳戶為選填欄位'
                    }),
                    ('檔案資訊 (選填)', {
                        'fields': ('file', 'file_description'),
                        'description': '檔案上傳為選填，可只填寫銀行資訊'
                    }),
                )
    
    def get_customer_display(self, obj):
        """在列表中顯示客戶名稱"""
        return obj.customer.get_display_name()
    get_customer_display.short_description = '客戶'
    get_customer_display.admin_order_field = 'customer__name'
    
    def get_uploaded_by_display(self, obj):
        """在列表中顯示上傳客服名稱"""
        if hasattr(obj.uploaded_by, 'get_display_name'):
            return obj.uploaded_by.get_display_name()
        else:
            full_name = obj.uploaded_by.get_full_name().strip()
            if full_name:
                return f"{full_name}({obj.uploaded_by.username})"
            else:
                return obj.uploaded_by.username
    get_uploaded_by_display.short_description = '上傳客服'
    get_uploaded_by_display.admin_order_field = 'uploaded_by__first_name'
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """自定義外鍵欄位顯示"""
        if db_field.name == "customer":
            kwargs["queryset"] = Customer.objects.all().order_by('name')
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            formfield.label_from_instance = lambda obj: obj.get_display_name()
            return formfield
        elif db_field.name == "uploaded_by":
            from accounts.models import User
            kwargs["initial"] = request.user
            if not request.user.is_admin():
                kwargs["queryset"] = User.objects.filter(id=request.user.id)
            else:
                kwargs["queryset"] = User.objects.filter(role__in=['admin', 'cs']).order_by('first_name', 'username')
            formfield = super().formfield_for_foreignkey(db_field, request, **kwargs)
            def safe_label_from_instance(obj):
                if hasattr(obj, 'get_display_name'):
                    return obj.get_display_name()
                else:
                    full_name = obj.get_full_name().strip()
                    if full_name:
                        return f"{full_name}({obj.username})"
                    else:
                        return obj.username
            formfield.label_from_instance = safe_label_from_instance
            return formfield
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    def get_file_preview(self, obj):
        """顯示檔案預覽"""
        if not obj.file:
            return "無檔案"
        
        file_url = obj.file.url
        file_name = obj.file.name.split('/')[-1]
        
        if obj.is_image():
            return format_html(
                '<div style="text-align: center;">'
                '<img src="{}" style="max-width: 100px; max-height: 100px; border-radius: 5px;" /><br>'
                '<small><a href="{}" target="_blank">🖼️ {}</a></small>'
                '</div>',
                file_url, file_url, file_name
            )
        elif obj.is_video():
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
            return format_html(
                '<div style="text-align: center;">'
                '<div style="padding: 20px; background: #f0f0f0; border-radius: 5px; margin: 10px 0;">'
                '<i style="font-size: 24px;">📄</i><br>'
                '<small><a href="{}" target="_blank">{}</a></small>'
                '</div></div>',
                file_url, file_name
            )
    
    get_file_preview.short_description = '檔案預覽'
    
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
    
    def save_model(self, request, obj, form, change):
        """保存模型時的處理"""
        if not change:  # 新增時
            obj.uploaded_by = request.user
        elif not request.user.is_admin():
            obj.uploaded_by = obj.uploaded_by
        super().save_model(request, obj, form, change)
    
    def get_readonly_fields(self, request, obj=None):
        """根據用戶角色動態設置唯讀欄位"""
        base_readonly = ['uploaded_at', 'get_file_preview', 'get_file_info']
        
        if obj and not request.user.is_admin():
            return base_readonly + ['uploaded_by']
        elif not obj and not request.user.is_admin():
            return base_readonly
        else:
            return base_readonly
    
    def has_change_permission(self, request, obj=None):
        """檢查編輯權限"""
        if obj and not request.user.is_admin():
            return obj.uploaded_by == request.user
        return super().has_change_permission(request, obj)
    
    def has_delete_permission(self, request, obj=None):
        """檢查刪除權限"""
        if obj and not request.user.is_admin():
            return obj.uploaded_by == request.user
        return super().has_delete_permission(request, obj)
