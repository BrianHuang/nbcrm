"""
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
        response['Content-Disposition'] = f'inline; filename*=UTF-8''{escape_uri_path(filename)}'
        
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
