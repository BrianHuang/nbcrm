from django.contrib import admin
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
        response['Content-Disposition'] = f'inline; filename*=UTF-8''{escape_uri_path(filename)}'
        
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
