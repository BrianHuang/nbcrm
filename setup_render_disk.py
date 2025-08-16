#!/usr/bin/env python3
"""
設置 Render Disk 持久化媒體存儲
用於安全存儲 KYC 等隱私敏感文件
"""

from pathlib import Path

def update_settings_for_render_disk():
    """更新 settings.py 配置 Render Disk"""
    
    print("⚙️ 更新 settings.py 支援 Render Disk...")
    
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

# 媒體文件設定 - Render Disk 持久化存儲
if not DEBUG:
    # 生產環境：使用 Render Disk 掛載的目錄
    MEDIA_ROOT = '/opt/render/project/media'
    # 確保媒體目錄存在
    os.makedirs(MEDIA_ROOT, exist_ok=True)
else:
    # 開發環境：使用本地目錄
    MEDIA_ROOT = BASE_DIR / 'media'
    MEDIA_ROOT.mkdir(exist_ok=True)

MEDIA_URL = '/media/'

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
    
    # 額外安全設定為隱私文件
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# 日誌設定
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
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
        'nbcrm.media': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# 媒體文件訪問日誌（用於安全審計）
MEDIA_ACCESS_LOG = config('MEDIA_ACCESS_LOG', default=True, cast=bool)
'''
    
    settings_path = Path("nbcrm") / "settings.py"
    with open(settings_path, 'w', encoding='utf-8') as f:
        f.write(settings_content)
    print("✅ 更新 settings.py")

def update_urls_for_security():
    """更新 URLs 配置，增加安全檢查"""
    
    print("🔒 更新 URLs 配置，增加安全檢查...")
    
    urls_content = '''from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from django.http import Http404, HttpResponse
from django.views.static import serve
from django.utils.encoding import escape_uri_path
from django.contrib.auth.decorators import login_required
import os
import mimetypes
import logging

# 設置管理後台標題
admin.site.site_header = '小商人客戶管理系統'
admin.site.site_title = '小商人CRM'
admin.site.index_title = '系統管理'

# 媒體文件訪問日誌
media_logger = logging.getLogger('nbcrm.media')

def redirect_to_admin(request):
    """根路徑重定向到 admin"""
    return redirect('/admin/')

@login_required
def serve_secure_media(request, path):
    """安全地提供媒體文件服務（需要登入）"""
    try:
        # 記錄訪問日誌
        if settings.MEDIA_ACCESS_LOG:
            media_logger.info(f"用戶 {request.user.username} 訪問媒體文件: {path}")
        
        # 建構完整文件路徑
        document_root = settings.MEDIA_ROOT
        full_path = os.path.join(document_root, path)
        
        # 安全檢查：確保路徑在允許範圍內
        real_path = os.path.realpath(full_path)
        real_document_root = os.path.realpath(document_root)
        
        if not real_path.startswith(real_document_root + os.sep) and real_path != real_document_root:
            media_logger.warning(f"用戶 {request.user.username} 嘗試訪問不安全路徑: {path}")
            raise Http404("路徑不安全")
        
        # 檢查文件是否存在
        if not os.path.exists(full_path) or not os.path.isfile(full_path):
            media_logger.warning(f"用戶 {request.user.username} 訪問不存在的文件: {path}")
            raise Http404(f"文件不存在: {path}")
        
        # 額外權限檢查：只有登入用戶可以訪問
        if not request.user.is_authenticated:
            media_logger.warning(f"未登入用戶嘗試訪問媒體文件: {path}")
            raise Http404("需要登入")
        
        # 使用 Django 的 serve 函數
        response = serve(request, path, document_root=document_root)
        
        # 添加安全標頭
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['Cache-Control'] = 'private, no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        # 添加正確的 Content-Type
        content_type, encoding = mimetypes.guess_type(full_path)
        if content_type:
            response['Content-Type'] = content_type
        
        # 支援中文檔名
        filename = os.path.basename(full_path)
        response['Content-Disposition'] = f'inline; filename*=UTF-8\'\'{escape_uri_path(filename)}'
        
        media_logger.info(f"成功提供文件給用戶 {request.user.username}: {path}")
        return response
        
    except Exception as e:
        media_logger.error(f"媒體文件服務錯誤 (用戶: {request.user.username if request.user.is_authenticated else '未登入'}): {e}")
        raise Http404(f"無法提供文件: {path}")

urlpatterns = [
    path('', redirect_to_admin),
    path('admin/', admin.site.urls),
]

# 安全的媒體文件路由 - 需要登入才能訪問
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve_secure_media, name='serve_secure_media'),
]

# 開發環境的靜態文件服務
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
'''
    
    urls_path = Path("nbcrm") / "urls.py"
    with open(urls_path, 'w', encoding='utf-8') as f:
        f.write(urls_content)
    print("✅ 更新 URLs 配置")

def create_render_disk_guide():
    """創建 Render Disk 設置指南"""
    
    print("📋 創建 Render Disk 設置指南...")
    
    guide_content = '''# 🔒 Render Disk 設置指南

## 🎯 為什麼選擇 Render Disk

對於 KYC 等高度隱私敏感資料，Render Disk 提供：
- ✅ **數據主權**：資料完全在你控制範圍內
- ✅ **隱私保護**：不經過第三方雲服務
- ✅ **持久化存儲**：重新部署後文件不消失
- ✅ **高安全性**：只有登入用戶可訪問媒體文件

## 📋 設置步驟

### 1. 在 Render Dashboard 創建 Disk

1. **登入 Render Dashboard**
   - 前往 https://dashboard.render.com/
   - 選擇你的 Web Service

2. **添加 Disk**
   - 點擊左側 "Disks" 標籤
   - 點擊 "Add Disk"
   - 填寫設定：
     ```
     Name: media-storage
     Mount Path: /opt/render/project/media
     Size: 20GB (根據需求調整)
     ```
   - 點擊 "Create Disk"

3. **等待 Disk 創建完成**
   - 通常需要 2-5 分鐘
   - 狀態變為 "Available" 即可

### 2. 重新部署應用

創建 Disk 後需要重新部署：
- Render 會自動觸發重新部署
- 或手動點擊 "Deploy Latest Commit"

### 3. 驗證設置

部署完成後：
1. **上傳測試文件**
   - 登入 Admin 後台
   - 新增一個 KYC 記錄並上傳文件

2. **檢查文件路徑**
   - 文件應該存儲在 `/opt/render/project/media/` 下
   - URL 格式：`https://your-app.onrender.com/media/kyc/1/filename.jpg`

3. **測試持久性**
   - 觸發重新部署
   - 確認文件仍然存在且可訪問

## 💰 費用說明

Render Disk 定價（美金/月）：
- **20GB**: $7/月
- **50GB**: $15/月  
- **100GB**: $25/月

對於中小型 KYC 系統，20GB 通常足夠使用。

## 🔒 安全特性

### 已實施的安全措施

1. **登入驗證**：只有登入用戶可訪問媒體文件
2. **路徑檢查**：防止目錄遍歷攻擊
3. **訪問日誌**：記錄所有媒體文件訪問
4. **安全標頭**：防止快取和嵌入
5. **HTTPS 強制**：生產環境強制使用 HTTPS

### 訪問日誌範例
```
INFO 用戶 admin 訪問媒體文件: kyc/1/身分證.jpg
WARNING 用戶 cs001 嘗試訪問不安全路徑: ../../../etc/passwd
```

## 🔧 故障排除

### 問題：文件上傳後找不到
**解決方案**：
1. 檢查 Disk 是否正確掛載到 `/opt/render/project/media`
2. 檢查服務日誌是否有錯誤
3. 確認文件權限正確

### 問題：重新部署後文件消失
**解決方案**：
1. 確認 Disk 狀態為 "Available"
2. 檢查 Mount Path 是否正確
3. 聯繫 Render 支援檢查 Disk 健康狀態

### 問題：無法訪問媒體文件
**解決方案**：
1. 確認已登入 Admin 後台
2. 檢查文件路徑是否正確
3. 查看服務日誌中的錯誤訊息

## 📊 監控建議

### 定期檢查項目
- **存儲空間使用量**：避免超出 Disk 容量
- **訪問日誌**：監控異常訪問行為
- **文件完整性**：定期檢查重要文件是否存在

### 備份建議
- **重要文件**：定期下載重要 KYC 文件到本地備份
- **資料庫**：確保資料庫定期備份（文件路徑資訊）

## 🎉 完成！

設置完成後，你的 KYC 文件將：
- ✅ 安全存儲在 Render Disk 中
- ✅ 重新部署後仍然存在
- ✅ 只有授權用戶可以訪問
- ✅ 所有訪問都有日誌記錄
'''
    
    with open("RENDER_DISK_SETUP.md", 'w', encoding='utf-8') as f:
        f.write(guide_content)
    print("✅ 創建設置指南")

def create_security_check_script():
    """創建安全檢查腳本"""
    
    print("🔐 創建安全檢查腳本...")
    
    security_script = '''#!/usr/bin/env python3
"""
媒體文件安全檢查腳本
檢查 Render Disk 配置和安全設定
"""

import os
import sys
import django
from pathlib import Path

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nbcrm.settings')
django.setup()

from django.conf import settings
from kyc.models import KYCRecord

def check_media_security():
    """檢查媒體文件安全配置"""
    
    print("🔍 媒體文件安全檢查")
    print("=" * 40)
    
    # 基本配置檢查
    print(f"MEDIA_URL: {settings.MEDIA_URL}")
    print(f"MEDIA_ROOT: {settings.MEDIA_ROOT}")
    print(f"DEBUG 模式: {settings.DEBUG}")
    
    # 檢查媒體目錄
    media_exists = os.path.exists(settings.MEDIA_ROOT)
    print(f"媒體目錄存在: {media_exists}")
    
    if media_exists:
        media_writable = os.access(settings.MEDIA_ROOT, os.W_OK)
        print(f"媒體目錄可寫: {media_writable}")
        
        # 統計文件
        total_files = 0
        total_size = 0
        
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            for file in files:
                file_path = os.path.join(root, file)
                total_files += 1
                total_size += os.path.getsize(file_path)
        
        print(f"總文件數: {total_files}")
        print(f"總大小: {total_size / (1024*1024):.2f} MB")
    
    # 檢查 KYC 記錄
    kyc_records = KYCRecord.objects.filter(file__isnull=False)
    print(f"\\nKYC 文件記錄數: {kyc_records.count()}")
    
    # 檢查文件完整性
    missing_files = 0
    for kyc in kyc_records:
        file_path = os.path.join(settings.MEDIA_ROOT, kyc.file.name)
        if not os.path.exists(file_path):
            missing_files += 1
            print(f"❌ 缺失文件: {kyc.file.name}")
    
    if missing_files == 0:
        print("✅ 所有 KYC 文件完整")
    else:
        print(f"⚠️ 有 {missing_files} 個文件缺失")
    
    # 安全設定檢查
    print("\\n🔒 安全設定檢查")
    print("-" * 20)
    
    if not settings.DEBUG:
        security_checks = {
            'SECURE_SSL_REDIRECT': getattr(settings, 'SECURE_SSL_REDIRECT', False),
            'SECURE_HSTS_SECONDS': getattr(settings, 'SECURE_HSTS_SECONDS', 0) > 0,
            'X_FRAME_OPTIONS': getattr(settings, 'X_FRAME_OPTIONS', '') == 'DENY',
            'SECURE_CONTENT_TYPE_NOSNIFF': getattr(settings, 'SECURE_CONTENT_TYPE_NOSNIFF', False),
        }
        
        for setting, enabled in security_checks.items():
            status = "✅" if enabled else "⚠️"
            print(f"{status} {setting}: {enabled}")
    else:
        print("⚠️ 開發模式：安全設定未啟用")
    
    print("\\n✅ 安全檢查完成")

if __name__ == "__main__":
    check_media_security()
'''
    
    with open("check_media_security.py", 'w', encoding='utf-8') as f:
        f.write(security_script)
    print("✅ 創建安全檢查腳本")

def main():
    """主函數"""
    print("🔒 設置 Render Disk 持久化存儲")
    print("=" * 40)
    
    # 檢查是否在正確的目錄
    if not Path("manage.py").exists():
        print("❌ 錯誤：請在 Django 項目根目錄執行此腳本")
        return
    
    try:
        # 更新配置文件
        update_settings_for_render_disk()
        update_urls_for_security()
        create_render_disk_guide()
        create_security_check_script()
        
        print("\n✅ Render Disk 設置完成！")
        print("\n🔒 安全特性：")
        print("- 只有登入用戶可訪問媒體文件")
        print("- 路徑安全檢查防止目錄遍歷")
        print("- 詳細的訪問日誌記錄")
        print("- HTTPS 強制和安全標頭")
        
        print("\n📋 下一步操作：")
        print("\n1. 🏗️ 在 Render Dashboard 創建 Disk：")
        print("   - 前往你的 Web Service")
        print("   - 點擊 'Disks' → 'Add Disk'")
        print("   - Mount Path: /opt/render/project/media")
        print("   - Size: 20GB (建議)")
        
        print("\n2. 🚀 部署更新：")
        print("   git add .")
        print("   git commit -m '設置 Render Disk 安全媒體存儲'")
        print("   git push origin main")
        
        print("\n3. 🧪 測試：")
        print("   python check_media_security.py")
        
        print("\n📖 詳細指南：RENDER_DISK_SETUP.md")
        print("💰 預估費用：$7/月 (20GB)")
        
    except Exception as e:
        print(f"❌ 設置過程中出現錯誤：{e}")

if __name__ == "__main__":
    main()