from django.contrib import admin
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
