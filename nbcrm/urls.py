# nbcrm/urls.py - 僅更新管理後台標題
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# 設置管理後台標題
admin.site.site_header = '小商人客戶管理系統'
admin.site.site_title = '小商人CRM'
admin.site.index_title = '系統管理'

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