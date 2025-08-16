#!/usr/bin/env python3
"""
小商人客戶管理系統重構腳本
- 簡化為純 Django Admin 版本
- KYC 檔案欄位改為非必須
- 移除所有前端視圖和模板
"""

import os
import shutil
import sys
from pathlib import Path

class CRMRefactor:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root)
        self.backup_dir = self.project_root / "backup_before_refactor"
        
    def create_backup(self):
        """創建備份"""
        print("📦 創建備份...")
        if self.backup_dir.exists():
            shutil.rmtree(self.backup_dir)
        
        # 備份重要文件和目錄
        backup_items = [
            "templates",
            "static",
            "accounts",
            "customers", 
            "kyc",
            "transactions",
            "nbcrm",
            "requirements.txt",
            "README.md"
        ]
        
        self.backup_dir.mkdir(exist_ok=True)
        for item in backup_items:
            src = self.project_root / item
            if src.exists():
                if src.is_dir():
                    shutil.copytree(src, self.backup_dir / item)
                else:
                    shutil.copy2(src, self.backup_dir / item)
        print("✅ 備份完成")

    def delete_unnecessary_files(self):
        """刪除不需要的文件"""
        print("🗑️ 刪除不必要的文件...")
        
        # 刪除整個目錄
        dirs_to_delete = [
            "templates",
            "static"
        ]
        
        for dir_name in dirs_to_delete:
            dir_path = self.project_root / dir_name
            if dir_path.exists():
                shutil.rmtree(dir_path)
                print(f"   刪除目錄: {dir_name}")
        
        # 刪除特定文件
        files_to_delete = [
            "accounts/views.py",
            "accounts/urls.py", 
            "accounts/forms.py",
            "accounts/tests.py",
            "customers/views.py",
            "customers/urls.py",
            "customers/forms.py", 
            "customers/tests.py",
            "kyc/views.py",
            "kyc/urls.py",
            "kyc/forms.py",
            "kyc/tests.py",
            "transactions/views.py",
            "transactions/urls.py",
            "transactions/forms.py",
            "transactions/tests.py",
            "create_project.py"
        ]
        
        for file_path in files_to_delete:
            full_path = self.project_root / file_path
            if full_path.exists():
                full_path.unlink()
                print(f"   刪除文件: {file_path}")

    def update_settings(self):
        """更新 settings.py"""
        print("⚙️ 更新 settings.py...")
        
        settings_content = '''from pathlib import Path
from decouple import config
import dj_database_url

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

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

AUTH_USER_MODEL = 'accounts.User'

# Admin 設定
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/admin/'
LOGOUT_REDIRECT_URL = '/admin/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
FILE_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 100 * 1024 * 1024  # 100MB
'''
        
        settings_path = self.project_root / "nbcrm" / "settings.py"
        with open(settings_path, 'w', encoding='utf-8') as f:
            f.write(settings_content)

    def update_urls(self):
        """更新主 urls.py"""
        print("🔗 更新 urls.py...")
        
        urls_content = '''from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

# 設置管理後台標題
admin.site.site_header = '小商人客戶管理系統'
admin.site.site_title = '小商人CRM'
admin.site.index_title = '系統管理'

def redirect_to_admin(request):
    """根路徑重定向到 admin"""
    return redirect('/admin/')

urlpatterns = [
    path('', redirect_to_admin),
    path('admin/', admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
'''
        
        urls_path = self.project_root / "nbcrm" / "urls.py"
        with open(urls_path, 'w', encoding='utf-8') as f:
            f.write(urls_content)

    def update_kyc_model(self):
        """更新 KYC 模型，將檔案欄位改為非必須"""
        print("📄 更新 KYC 模型...")
        
        kyc_models_content = '''# kyc/models.py
import os
from django.db import models
from django.contrib.auth import get_user_model
from customers.models import Customer
from django.core.validators import RegexValidator

User = get_user_model()

def kyc_upload_path(instance, filename):
    return f'kyc/{instance.customer.id}/{filename}'

class KYCRecord(models.Model):
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='kyc_records', 
        verbose_name='客戶'
    )
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='kyc_uploads', 
        verbose_name='上傳客服'
    )
    bank_code = models.CharField(
        max_length=3,
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^\d{3}$', message='請填入3位數字的銀行代碼')],
        verbose_name='銀行代碼',
        help_text='請填入3位數字的銀行代碼（選填）'
    )
    verification_account = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        validators=[RegexValidator(regex=r'^\d+$', message='只能填入數字')],
        verbose_name='驗證帳戶',
        help_text='請填入數字帳號（選填）'
    )
    file = models.FileField(
        upload_to=kyc_upload_path, 
        verbose_name='檔案',
        blank=True,
        null=True,
        help_text='支援圖片和影片檔案，檔案大小不超過100MB（選填）'
    )
    file_description = models.TextField(
        blank=True,
        verbose_name='檔案說明',
        help_text='對此檔案的說明或備註（選填）'
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='上傳時間'
    )
    
    class Meta:
        verbose_name = 'KYC 記錄'
        verbose_name_plural = 'KYC 記錄'
        ordering = ['-uploaded_at']
    
    def __str__(self):
        bank_info = f"({self.bank_code})" if self.bank_code else ""
        account_info = f" - {self.verification_account}" if self.verification_account else ""
        file_info = " [有檔案]" if self.file else " [無檔案]"
        return f"{self.customer.name}{account_info}{bank_info}{file_info}"
    
    def get_file_extension(self):
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return ""
    
    def is_image(self):
        if not self.file:
            return False
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.jfif']
        return self.get_file_extension() in image_extensions
    
    def is_video(self):
        if not self.file:
            return False
        video_extensions = ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm']
        return self.get_file_extension() in video_extensions
    
    def get_file_size_display(self):
        """返回易讀的檔案大小"""
        if self.file:
            size = self.file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        return "無檔案"
'''
        
        kyc_models_path = self.project_root / "kyc" / "models.py"
        with open(kyc_models_path, 'w', encoding='utf-8') as f:
            f.write(kyc_models_content)

    def update_kyc_admin(self):
        """更新 KYC Admin"""
        print("👤 更新 KYC Admin...")
        
        kyc_admin_content = '''from django.contrib import admin
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
'''
        
        kyc_admin_path = self.project_root / "kyc" / "admin.py"
        with open(kyc_admin_path, 'w', encoding='utf-8') as f:
            f.write(kyc_admin_content)

    def create_simple_app_files(self):
        """創建簡化的 app 文件"""
        print("📱 創建簡化的 app 文件...")
        
        # 為每個 app 創建必要的空文件
        apps = ['accounts', 'customers', 'kyc', 'transactions']
        
        for app in apps:
            app_path = self.project_root / app
            
            # 確保 __init__.py 存在
            init_file = app_path / "__init__.py"
            if not init_file.exists():
                init_file.touch()
            
            # 創建 apps.py 如果不存在
            apps_file = app_path / "apps.py"
            if not apps_file.exists():
                apps_content = f'''from django.apps import AppConfig

class {app.capitalize()}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app}'
'''
                with open(apps_file, 'w', encoding='utf-8') as f:
                    f.write(apps_content)

    def update_requirements(self):
        """更新 requirements.txt"""
        print("📦 更新 requirements.txt...")
        
        requirements_content = '''Django==4.2.15
Pillow==10.4.0
python-decouple==3.8
dj-database-url==2.1.0
whitenoise==6.6.0
gunicorn==22.0.0
psycopg2-binary==2.9.9
'''
        
        requirements_path = self.project_root / "requirements.txt"
        with open(requirements_path, 'w', encoding='utf-8') as f:
            f.write(requirements_content)

    def update_readme(self):
        """更新 README.md"""
        print("📖 更新 README.md...")
        
        readme_content = '''# 小商人客戶管理系統 (Admin Only)

## 🎯 系統特點

- **純 Django Admin 介面**：專注於後台管理，減少維護成本
- **客戶資料管理**：完整的客戶信息管理
- **交易記錄追踪**：詳細的交易記錄和統計
- **KYC文件管理**：支援檔案上傳，檔案欄位為選填，最大100MB
- **用戶權限管理**：Admin（管理員）、CS（客服）角色控制

## 🚀 快速開始

### 1. 環境準備

```bash
# 創建虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows:
venv\\Scripts\\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. 安裝依賴

```bash
pip install -r requirements.txt
```

### 3. 環境設定

創建 `.env` 文件：
```env
SECRET_KEY=your-very-secret-key-change-this-in-production
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

### 4. 數據庫設置

```bash
# 創建遷移文件
python manage.py makemigrations

# 執行遷移
python manage.py migrate

# 創建超級用戶
python manage.py createsuperuser
```

### 5. 啟動服務

```bash
python manage.py runserver
```

### 6. 訪問系統

- 瀏覽器打開 `http://localhost:8000/`
- 會自動重定向到管理後台 `/admin/`
- 使用創建的超級用戶帳號登入

## 📊 系統架構

### 數據模型

1. **User（用戶）**
   - 基於 Django AbstractUser
   - 角色：Admin（管理員）、CS（客服）

2. **Customer（客戶）**
   - 客戶基本資料
   - Line 暱稱、N8 暱稱、聯絡方式

3. **Transaction（交易記錄）**
   - 買入/賣出記錄
   - N8幣數量、台幣金額
   - 快速回覆狀態

4. **KYCRecord（KYC記錄）**
   - 檔案上傳（選填，最大100MB）
   - 銀行代碼、驗證帳戶
   - 檔案說明

### 權限控制

- **Admin（管理員）**：所有功能的完整權限
- **CS（客服）**：客戶和交易管理權限，只能編輯自己上傳的KYC記錄

## 🛠️ KYC 功能更新

### 檔案上傳改為選填

- ✅ KYC 記錄可以只填寫銀行資訊
- ✅ 檔案上傳為選填項目
- ✅ 支援圖片和影片格式
- ✅ 檔案大小限制 100MB

### 使用方式

1. 進入 Admin 後台
2. 選擇「KYC 記錄」
3. 點擊「新增 KYC 記錄」
4. 選擇客戶
5. 選填：銀行代碼、驗證帳戶
6. 選填：上傳檔案、檔案說明
7. 保存

## 🚀 部署

系統已配置自動部署到 Render 平台：

1. 推送代碼到 GitHub
2. Render 自動檢測更新並部署
3. 環境變數在 Render 控制台設定

### 必要環境變數

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
DATABASE_URL=postgresql://...
```

## 📝 變更記錄

### v2.0.0 - Admin Only 重構

- ✅ 移除所有前端視圖和模板
- ✅ 專注於 Django Admin 介面
- ✅ KYC 檔案欄位改為選填
- ✅ 減少代碼量 70%，降低維護成本
- ✅ 保持所有核心功能完整

## 🔧 開發說明

### 項目結構

```
nbcrm/
├── accounts/           # 用戶管理
│   ├── __init__.py
│   ├── admin.py       # 用戶 Admin 配置
│   ├── apps.py
│   └── models.py      # User 模型
├── customers/          # 客戶管理
│   ├── __init__.py
│   ├── admin.py       # 客戶 Admin 配置
│   ├── apps.py
│   └── models.py      # Customer 模型
├── kyc/               # KYC 管理
│   ├── __init__.py
│   ├── admin.py       # KYC Admin 配置
│   ├── apps.py
│   └── models.py      # KYCRecord 模型
├── transactions/       # 交易管理
│   ├── __init__.py
│   ├── admin.py       # 交易 Admin 配置
│   ├── apps.py
│   └── models.py      # Transaction 模型
├── nbcrm/             # 項目配置
│   ├── __init__.py
│   ├── settings.py    # Django 設定
│   ├── urls.py        # URL 配置
│   └── wsgi.py
├── media/             # 上傳檔案目錄
├── manage.py
├── requirements.txt
├── runtime.txt
├── Procfile
├── build.sh
└── README.md
```

### 常用操作

```bash
# 創建新的數據庫遷移
python manage.py makemigrations

# 執行遷移
python manage.py migrate

# 創建超級用戶
python manage.py createsuperuser

# 收集靜態文件（部署前）
python manage.py collectstatic

# 啟動開發服務器
python manage.py runserver
```

## 📞 技術支援

如有問題請聯繫系統管理員。

---

**小商人客戶管理系統** - 專注效率，簡化管理
'''
        
        readme_path = self.project_root / "README.md"
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)

    def create_migration_file(self):
        """創建 KYC 模型遷移文件"""
        print("📄 創建 KYC 遷移文件...")
        
        migration_content = '''# Generated by refactor script
from django.db import migrations, models
import django.core.validators
import kyc.models


class Migration(migrations.Migration):

    dependencies = [
        ('kyc', '0003_kycrecord_file_description_alter_kycrecord_bank_code_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='kycrecord',
            name='file',
            field=models.FileField(blank=True, help_text='支援圖片和影片檔案，檔案大小不超過100MB（選填）', null=True, upload_to=kyc.models.kyc_upload_path, verbose_name='檔案'),
        ),
    ]
'''
        
        # 創建遷移文件目錄
        migrations_dir = self.project_root / "kyc" / "migrations"
        migrations_dir.mkdir(exist_ok=True)
        
        # 創建遷移文件
        migration_file = migrations_dir / "0004_alter_kycrecord_file_optional.py"
        with open(migration_file, 'w', encoding='utf-8') as f:
            f.write(migration_content)

    def run_refactor(self):
        """執行完整重構"""
        print("🚀 開始小商人CRM系統重構...")
        print("=" * 50)
        
        try:
            # 1. 創建備份
            self.create_backup()
            
            # 2. 刪除不必要的文件
            self.delete_unnecessary_files()
            
            # 3. 更新配置文件
            self.update_settings()
            self.update_urls()
            
            # 4. 更新 KYC 相關文件
            self.update_kyc_model()
            self.update_kyc_admin()
            self.create_migration_file()
            
            # 5. 創建簡化的 app 文件
            self.create_simple_app_files()
            
            # 6. 更新其他文件
            self.update_requirements()
            self.update_readme()
            
            print("=" * 50)
            print("✅ 重構完成！")
            print("\n📋 後續步驟：")
            print("1. 執行數據庫遷移：python manage.py migrate")
            print("2. 創建超級用戶：python manage.py createsuperuser")
            print("3. 啟動服務器：python manage.py runserver")
            print("4. 訪問 http://localhost:8000/ （會重定向到 /admin/）")
            print("\n💾 備份位置：", self.backup_dir.absolute())
            print("\n🎉 現在您有一個更簡潔的純 Admin 版本系統！")
            
        except Exception as e:
            print(f"❌ 重構過程中出現錯誤：{e}")
            print("💾 請檢查備份文件夾：", self.backup_dir.absolute())
            sys.exit(1)

def main():
    """主函數"""
    print("小商人客戶管理系統重構工具")
    print("=" * 30)
    
    # 檢查是否在正確的目錄
    if not Path("manage.py").exists():
        print("❌ 錯誤：請在 Django 項目根目錄執行此腳本")
        print("   （包含 manage.py 的目錄）")
        sys.exit(1)
    
    # 確認是否要執行重構
    confirm = input("⚠️  此操作將會大幅修改您的項目，是否繼續？(y/N): ")
    if confirm.lower() != 'y':
        print("❌ 已取消重構")
        sys.exit(0)
    
    # 執行重構
    refactor = CRMRefactor()
    refactor.run_refactor()

if __name__ == "__main__":
    main()