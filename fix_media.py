#!/usr/bin/env python3
"""
Render 媒體文件問題解決腳本
解決生產環境中 /media/ 文件無法訪問的問題
"""

import os
from pathlib import Path

def fix_render_media_issue():
    """修復 Render 媒體文件訪問問題"""
    
    print("🔧 修復 Render 媒體文件訪問問題...")
    
    # 1. 更新 urls.py 添加媒體文件服務
    update_main_urls()
    
    # 2. 更新 settings.py 媒體文件設定
    update_settings_for_production()
    
    # 3. 創建媒體文件服務視圖
    create_media_serve_view()
    
    # 4. 更新 KYC Admin 顯示邏輯
    update_kyc_admin_for_production()
    
    print("✅ 修復完成！")
    print("\n📋 接下來需要：")
    print("1. git add .")
    print("2. git commit -m '修復生產環境媒體文件訪問問題'")
    print("3. git push origin main")
    print("4. 等待 Render 重新部署")

def update_main_urls():
    """更新主 URLs 配置"""
    
    urls_content = '''from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.http import HttpResponse, Http404
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
    print("✅ 更新 nbcrm/urls.py")

def update_settings_for_production():
    """更新 settings.py 生產環境媒體設定"""
    
    settings_content = '''from pathlib import Path
from decouple import config
import dj_database_url
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'customers',
    'kyc',
    'transactions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'nbcrm.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'nbcrm.wsgi.application'

DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3')
    )
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'zh-hant'
TIME_ZONE = 'Asia/Taipei'
USE_I18N = True
USE_TZ = True

# 靜態文件設定
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# 媒體文件設定 - 生產環境優化
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 確保媒體目錄存在
os.makedirs(MEDIA_ROOT, exist_ok=True)

# Admin 設定
AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/admin/'

# 文件上傳設定
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB

# 安全設定（生產環境）
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'

# 日誌設定
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
'''
    
    settings_path = Path("nbcrm") / "settings.py"
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(settings_content)
    print("✅ 更新 nbcrm/settings.py")

def create_media_serve_view():
    """創建媒體文件服務視圖"""
    
    # 創建 utils 目錄
    utils_dir = Path("nbcrm") / "utils"
    utils_dir.mkdir(exist_ok=True)
    
    # 創建 __init__.py
    init_file = utils_dir / "__init__.py"
    init_file.touch()
    
    # 創建媒體服務工具
    media_utils_content = '''"""
媒體文件服務工具
用於在生產環境中正確服務媒體文件
"""

import os
import mimetypes
from django.http import HttpResponse, Http404, FileResponse
from django.conf import settings
from django.utils.encoding import escape_uri_path

def serve_protected_media(request, path):
    """
    安全地服務媒體文件
    支援中文檔名和特殊字符
    """
    try:
        # 構建完整的文件路徑
        file_path = os.path.join(settings.MEDIA_ROOT, path)
        
        # 安全檢查：確保路徑在 MEDIA_ROOT 內
        real_path = os.path.realpath(file_path)
        real_media_root = os.path.realpath(settings.MEDIA_ROOT)
        
        if not real_path.startswith(real_media_root):
            raise Http404("無效的文件路徑")
        
        # 檢查文件是否存在
        if not os.path.exists(file_path) or not os.path.isfile(file_path):
            raise Http404("文件不存在")
        
        # 獲取文件 MIME 類型
        content_type, _ = mimetypes.guess_type(file_path)
        if content_type is None:
            content_type = 'application/octet-stream'
        
        # 返回文件響應
        response = FileResponse(
            open(file_path, 'rb'),
            content_type=content_type
        )
        
        # 設置文件名（支援中文）
        filename = os.path.basename(file_path)
        response['Content-Disposition'] = f'inline; filename*=UTF-8\'\'{escape_uri_path(filename)}'
        
        return response
        
    except Exception as e:
        raise Http404(f"無法訪問文件: {str(e)}")

def get_media_url(file_field):
    """
    安全地獲取媒體文件 URL
    處理中文檔名和特殊字符
    """
    if not file_field:
        return None
    
    try:
        # 使用 Django 的內建 URL 生成
        return file_field.url
    except Exception:
        # 如果出錯，返回空
        return None
'''
    
    media_utils_path = utils_dir / "media_utils.py"
    with open(media_utils_path, 'w', encoding='utf-8') as f:
        f.write(media_utils_content)
    print("✅ 創建媒體服務工具")

def update_kyc_admin_for_production():
    """更新 KYC Admin 以處理生產環境媒體文件"""
    
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
    print("✅ 更新 kyc/admin.py")

def main():
    """主函數"""
    print("🔧 Render 媒體文件問題修復工具")
    print("=" * 40)
    
    # 檢查是否在正確的目錄
    if not Path("manage.py").exists():
        print("❌ 錯誤：請在 Django 項目根目錄執行此腳本")
        return
    
    try:
        fix_render_media_issue()
        
        print("\n🎯 問題原因：")
        print("- Render 等生產環境不會自動服務 /media/ 文件")
        print("- 需要手動配置媒體文件路由")
        print("- 中文檔名需要特殊處理")
        
        print("\n✨ 解決方案：")
        print("- 添加自定義媒體文件服務路由")
        print("- 改善錯誤處理和安全檢查")
        print("- 支援中文檔名和特殊字符")
        
    except Exception as e:
        print(f"❌ 修復過程中出現錯誤：{e}")

if __name__ == "__main__":
    main()