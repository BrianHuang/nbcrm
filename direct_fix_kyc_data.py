#!/usr/bin/env python3
"""
直接修復 KYC 記錄的 uploaded_by 問題（不使用 migration）
"""

import os
import django

# 設置 Django 環境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nbcrm.settings')
django.setup()

from kyc.models import KYCRecord
from django.contrib.auth import get_user_model

User = get_user_model()

def fix_kyc_uploaded_by():
    """直接修復 uploaded_by 為 null 的記錄"""
    
    print("🔧 修復 KYC 記錄的 uploaded_by 問題")
    print("=" * 40)
    
    # 檢查問題記錄
    null_records = KYCRecord.objects.filter(uploaded_by__isnull=True)
    null_count = null_records.count()
    
    print(f"需要修復的記錄數：{null_count}")
    
    if null_count == 0:
        print("✅ 沒有需要修復的記錄")
        return
    
    # 顯示問題記錄詳情
    print("\n❌ 問題記錄：")
    for record in null_records[:10]:  # 只顯示前10個
        print(f"  ID: {record.id}, 客戶: {record.customer.name}, 時間: {record.uploaded_at}")
    
    if null_count > 10:
        print(f"  ... 還有 {null_count - 10} 個記錄")
    
    # 找到一個管理員用戶
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if not admin_user:
        # 找 staff 用戶
        admin_user = User.objects.filter(is_staff=True).first()
    
    if not admin_user:
        print("\n❌ 沒有找到合適的用戶來設置為 uploaded_by")
        print("請先創建一個管理員用戶：")
        print("python manage.py createsuperuser")
        return
    
    print(f"\n將使用用戶：{admin_user.username} ({admin_user.get_full_name()})")
    
    # 確認操作
    confirm = input(f"\n確定要修復 {null_count} 個記錄嗎？(y/N): ")
    
    if confirm.lower() != 'y':
        print("❌ 取消修復")
        return
    
    # 執行修復
    try:
        updated_count = null_records.update(uploaded_by=admin_user)
        print(f"✅ 成功修復 {updated_count} 個記錄")
        
        # 驗證修復結果
        remaining_null = KYCRecord.objects.filter(uploaded_by__isnull=True).count()
        print(f"剩餘 null 記錄：{remaining_null}")
        
        if remaining_null == 0:
            print("🎉 所有問題都已修復！")
        
    except Exception as e:
        print(f"❌ 修復過程中出現錯誤：{e}")

if __name__ == "__main__":
    fix_kyc_uploaded_by()