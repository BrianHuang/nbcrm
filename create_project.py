#!/usr/bin/env python3
"""
N8幣客戶管理系統項目自動創建腳本
運行此腳本會自動創建完整的Django項目結構和所有必要文件
"""

import os
import sys

def create_directory(path):
    """創建目錄"""
    os.makedirs(path, exist_ok=True)
    print(f"Created directory: {path}")

def create_file(path, content):
    """創建文件"""
    directory = os.path.dirname(path)
    if directory:  # 只有當目錄不為空時才創建
        os.makedirs(directory, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created file: {path}")

def main():
    """主函數"""
    print("開始創建N8幣客戶管理系統...")
    
    # 創建基礎目錄結構
    directories = [
        'nbcrm',
        'accounts',
        'customers', 
        'kyc',
        'transactions',
        'templates/accounts',
        'templates/customers',
        'templates/kyc', 
        'templates/transactions',
        'static/css',
        'static/js',
        'media'
    ]
    
    for directory in directories:
        create_directory(directory)
    
    # requirements.txt
    requirements_content = """Django==4.2.7
Pillow==10.1.0
python-decouple==3.8
dj-database-url==2.1.0
whitenoise==6.6.0
gunicorn==21.2.0
psycopg2-binary==2.9.9
django-crispy-forms==2.1
crispy-bootstrap5==0.7
django-extensions==3.2.3
"""
    create_file('requirements.txt', requirements_content)
    
    # .env文件
    env_content = """SECRET_KEY=your-very-secret-key-change-this-in-production
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
"""
    create_file('.env', env_content)
    
    # .gitignore
    gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Django
*.log
local_settings.py
db.sqlite3
db.sqlite3-journal
media/

# Environment
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# macOS
.DS_Store
"""
    create_file('.gitignore', gitignore_content)
    
    # manage.py
    manage_content = """#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nbcrm.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
"""
    create_file('manage.py', manage_content)
    
    # nbcrm/__init__.py
    create_file('nbcrm/__init__.py', '')
    
    # nbcrm/settings.py
    settings_content = """from pathlib import Path
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
    'crispy_forms',
    'crispy_bootstrap5',
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
        'DIRS': [BASE_DIR / 'templates'],
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
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'zh-hant'
TIME_ZONE = 'Asia/Taipei'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
"""
    create_file('nbcrm/settings.py', settings_content)
    
    # nbcrm/urls.py
    urls_content = """from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('customers/', include('customers.urls')),
    path('kyc/', include('kyc.urls')),
    path('transactions/', include('transactions.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
"""
    create_file('nbcrm/urls.py', urls_content)
    
    # nbcrm/wsgi.py
    wsgi_content = """import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nbcrm.settings')
application = get_wsgi_application()
"""
    create_file('nbcrm/wsgi.py', wsgi_content)
    
    # accounts app
    create_file('accounts/__init__.py', '')
    create_file('accounts/apps.py', """from django.apps import AppConfig

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'
""")
    
    # accounts/models.py
    accounts_models = """from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', '管理員'),
        ('cs', '客服'),
    ]
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='cs', verbose_name='角色')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='建立時間')
    
    class Meta:
        verbose_name = '使用者'
        verbose_name_plural = '使用者'
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'admin'
"""
    create_file('accounts/models.py', accounts_models)
    
    # 創建其他必要的空文件
    for app in ['accounts', 'customers', 'kyc', 'transactions']:
        create_file(f'{app}/admin.py', 'from django.contrib import admin\n')
        create_file(f'{app}/views.py', 'from django.shortcuts import render\n')
        create_file(f'{app}/urls.py', 'from django.urls import path\nfrom . import views\n\napp_name = "{}"\nurlpatterns = []\n'.format(app))
        create_file(f'{app}/forms.py', 'from django import forms\n')
        create_file(f'{app}/tests.py', 'from django.test import TestCase\n')
    
    # README.md
    readme_content = """# N8幣客戶管理系統

## 功能特點
- 客戶資料管理
- 交易記錄追踪
- KYC文件上傳
- 用戶權限管理
- 報表生成

## 安裝步驟

1. 創建虛擬環境：
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
```

2. 安裝依賴：
```bash
pip install -r requirements.txt
```

3. 數據庫遷移：
```bash
python manage.py makemigrations
python manage.py migrate
```

4. 創建超級用戶：
```bash
python manage.py createsuperuser
```

5. 運行服務器：
```bash
python manage.py runserver
```

## 部署到Render

1. 創建GitHub儲存庫
2. 在Render創建Web Service
3. 設置環境變數
4. 自動部署

## 系統角色

- **Admin（管理員）**：所有權限
- **CS（客服）**：客戶和交易管理權限
"""
    create_file('README.md', readme_content)
    
    print("\n✅ 項目創建完成！")
    print("\n接下來的步驟：")
    print("1. cd 到項目目錄")
    print("2. python -m venv venv")
    print("3. source venv/bin/activate (或 Windows: venv\\Scripts\\activate)")
    print("4. pip install -r requirements.txt")
    print("5. python manage.py makemigrations")
    print("6. python manage.py migrate")
    print("7. python manage.py createsuperuser")
    print("8. python manage.py runserver")

if __name__ == '__main__':
    main()