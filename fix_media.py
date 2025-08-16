#!/usr/bin/env python3
"""
修復 KYC admin.py 語法錯誤
"""

from pathlib import Path

def fix_kyc_admin_syntax():
    """修復 KYC admin.py 語法錯誤"""
    
    print("🔧 修復 KYC admin.py 語法錯誤...")
    
    kyc_admin_content = '''from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import KYCRecord
from customers.models import Customer
import os

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
                        'description': '檔案上傳為選填，可只填寫銀行資訊，支援最大100MB檔案'
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
        """顯示檔案預覽 - 生產環境優化版本"""
        if not obj.file:
            return "無檔案"
        
        try:
            file_url = obj.file.url
            file_name = os.path.basename(obj.file.name)
            
            # 安全地獲取檔案資訊
            if obj.is_image():
                return format_html(
                    '<div style="text-align: center;">'
                    '<img src="{}" style="max-width: 100px; max-height: 100px; border-radius: 5px;" '
                    'onerror="this.style.display=\'none\'; this.nextElementSibling.style.display=\'block\';" />'
                    '<div style="display: none; padding: 20px; background: #f0f0f0; border-radius: 5px;">'
                    '<i style="font-size: 24px;">🖼️</i><br><small>圖片載入失敗</small>'
                    '</div><br>'
                    '<small><a href="{}" target="_blank">🖼️ {}</a></small>'
                    '</div>',
                    file_url, file_url, file_name
                )
            elif obj.is_video():
                return format_html(
                    '<div style="text-align: center;">'
                    '<video width="100" height="60" controls style="border-radius: 5px;" '
                    'onerror="this.style.display=\'none\'; this.nextElementSibling.style.display=\'block\';">'
                    '<source src="{}" type="video/mp4">'
                    '您的瀏覽器不支援影片標籤。'
                    '</video>'
                    '<div style="display: none; padding: 20px; background: #f0f0f0; border-radius: 5px;">'
                    '<i style="font-size: 24px;">🎥</i><br><small>影片載入失敗</small>'
                    '</div><br>'
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
        except Exception as e:
            return format_html(
                '<div style="text-align: center; color: #dc3545;">'
                '<i style="font-size: 24px;">⚠️</i><br>'
                '<small>檔案載入失敗</small>'
                '</div>'
            )
    
    get_file_preview.short_description = '檔案預覽'
    
    def get_file_info(self, obj):
        """顯示檔案詳細資訊"""
        if obj.file:
            try:
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
                    file_type, obj.get_file_size_display(), os.path.basename(obj.file.name)
                )
            except Exception:
                return '檔案資訊載入失敗'
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
'''
    
    kyc_admin_path = Path("kyc") / "admin.py"
    with open(kyc_admin_path, 'w', encoding='utf-8') as f:
        f.write(kyc_admin_content)
    print("✅ 修復 kyc/admin.py 語法錯誤")

def fix_urls_syntax():
    """修復 URLs 語法錯誤"""
    
    print("🔧 修復 nbcrm/urls.py...")
    
    urls_content = '''from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.http import Http404, FileResponse
from django.views.static import serve
import os

# 設置管理後台標題
admin.site.site_header = '小商人客戶管理系統'
admin.site.site_title = '小商人CRM'
admin.site.index_title = '系統管理'

def redirect_to_admin(request):
    """根路徑重定向到 admin"""
    return redirect('/admin/')

def serve_media(request, path):
    """在生產環境中服務媒體文件"""
    try:
        # 構建完整的文件路徑
        file_path = os.path.join(settings.MEDIA_ROOT, path)
        
        # 檢查文件是否存在
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return serve(request, path, document_root=settings.MEDIA_ROOT)
        else:
            raise Http404("媒體文件不存在")
    except Exception as e:
        raise Http404(f"無法訪問媒體文件: {str(e)}")

urlpatterns = [
    path('', redirect_to_admin),
    path('admin/', admin.site.urls),
    # 在生產環境中也服務媒體文件
    re_path(r'^media/(?P<path>.*)$', serve_media, name='media'),
]

# 開發環境的靜態文件服務
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    # 開發環境也保留原始的媒體文件服務
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
'''
    
    urls_path = Path("nbcrm") / "urls.py"
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(urls_content)
    print("✅ 修復 nbcrm/urls.py")

def main():
    """主函數"""
    print("🛠️ 修復語法錯誤")
    print("=" * 30)
    
    # 檢查是否在正確的目錄
    if not Path("manage.py").exists():
        print("❌ 錯誤：請在 Django 項目根目錄執行此腳本")
        return
    
    try:
        # 修復語法錯誤
        fix_kyc_admin_syntax()
        fix_urls_syntax()
        
        print("\n✅ 語法錯誤修復完成！")
        print("\n📋 接下來請執行：")
        print("git add .")
        print("git commit -m '修復語法錯誤'")
        print("git push origin main")
        
    except Exception as e:
        print(f"❌ 修復過程中出現錯誤：{e}")

if __name__ == "__main__":
    main()