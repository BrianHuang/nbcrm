#!/usr/bin/env python3
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
    print(f"\nKYC 文件記錄數: {kyc_records.count()}")
    
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
    print("\n🔒 安全設定檢查")
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
    
    print("\n✅ 安全檢查完成")

if __name__ == "__main__":
    check_media_security()
