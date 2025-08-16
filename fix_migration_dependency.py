#!/usr/bin/env python3
"""
修復 Migration 依賴關係錯誤
"""

import os
from pathlib import Path

def check_existing_migrations():
    """檢查現有的 migration 文件"""
    
    print("🔍 檢查現有的 migration 文件...")
    
    kyc_migrations_dir = Path("kyc") / "migrations"
    
    if not kyc_migrations_dir.exists():
        print("❌ kyc/migrations 目錄不存在")
        return None
    
    # 列出所有 migration 文件
    migration_files = []
    for file in kyc_migrations_dir.glob("*.py"):
        if file.name != "__init__.py":
            migration_files.append(file.name)
    
    migration_files.sort()
    
    print("📋 現有的 migration 文件：")
    for i, file in enumerate(migration_files, 1):
        print(f"  {i}. {file}")
    
    if migration_files:
        # 返回最後一個 migration 文件名（不包含 .py）
        last_migration = migration_files[-1].replace('.py', '')
        print(f"\n✅ 最後一個 migration: {last_migration}")
        return last_migration
    else:
        print("\n⚠️ 沒有找到現有的 migration 文件")
        return None

def create_correct_migration():
    """創建正確的 migration 文件"""
    
    print("\n🔧 創建正確的 migration 文件...")
    
    # 檢查現有 migration
    last_migration = check_existing_migrations()
    
    if last_migration:
        dependencies_line = f"        ('{last_migration.split('_')[0]}', '{last_migration}'),"
    else:
        # 如果沒有找到，使用初始 migration
        dependencies_line = "        ('kyc', '__first__'),"
    
    migration_content = f'''# Generated to fix existing null uploaded_by values
from django.db import migrations
from django.contrib.auth import get_user_model

def fix_null_uploaded_by(apps, schema_editor):
    """修復現有的 null uploaded_by 值"""
    KYCRecord = apps.get_model('kyc', 'KYCRecord')
    User = get_user_model()
    
    # 找到一個管理員用戶作為預設值
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        # 如果沒有超級用戶，找一個 staff 用戶
        admin_user = User.objects.filter(is_staff=True).first()
    
    if not admin_user:
        # 如果都沒有，創建一個系統用戶
        admin_user = User.objects.create_user(
            username='system',
            email='system@nbcrm.local',
            first_name='系統',
            last_name='管理員',
            is_staff=True,
            is_superuser=True
        )
        print("創建了系統管理員用戶")
    
    # 更新所有 uploaded_by 為 null 的記錄
    null_records = KYCRecord.objects.filter(uploaded_by__isnull=True)
    updated_count = null_records.update(uploaded_by=admin_user)
    
    print(f"修復了 {{updated_count}} 個 KYC 記錄的 uploaded_by 欄位")

def reverse_fix_null_uploaded_by(apps, schema_editor):
    """回滾操作（不執行任何操作）"""
    pass

class Migration(migrations.Migration):

    dependencies = [
{dependencies_line}
    ]

    operations = [
        migrations.RunPython(fix_null_uploaded_by, reverse_fix_null_uploaded_by),
    ]
'''
    
    # 刪除舊的錯誤 migration 文件
    old_migration_file = Path("kyc") / "migrations" / "0006_fix_null_uploaded_by.py"
    if old_migration_file.exists():
        old_migration_file.unlink()
        print("✅ 刪除舊的錯誤 migration 文件")
    
    # 創建新的 migration 文件
    migrations_dir = Path("kyc") / "migrations"
    migrations_dir.mkdir(exist_ok=True)
    
    # 生成新的 migration 文件名
    import datetime
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    migration_file = migrations_dir / f"{timestamp}_fix_null_uploaded_by.py"
    
    with open(migration_file, 'w', encoding='utf-8') as f:
        f.write(migration_content)
    
    print(f"✅ 創建新的 migration 文件: {migration_file.name}")
    return migration_file.name

def create_simple_data_fix_script():
    """創建簡單的資料修復腳本（不使用 migration）"""
    
    print("\n📝 創建簡單資料修復腳本...")
    
    fix_script_content = '''#!/usr/bin/env python3
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
    
    # 找到一個管理員用戶
    admin_user = User.objects.filter(is_superuser=True).first()
    
    if not admin_user:
        # 找 staff 用戶
        admin_user = User.objects.filter(is_staff=True).first()
    
    if not admin_user:
        print("❌ 沒有找到合適的用戶來設置為 uploaded_by")
        print("請先創建一個管理員用戶：")
        print("python manage.py createsuperuser")
        return
    
    print(f"將使用用戶：{admin_user.username} ({admin_user.get_full_name()})")
    
    # 確認操作
    confirm = input(f"確定要修復 {null_count} 個記錄嗎？(y/N): ")
    
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
        
    except Exception as e:
        print(f"❌ 修復過程中出現錯誤：{e}")

if __name__ == "__main__":
    fix_kyc_uploaded_by()
'''
    
    with open("fix_kyc_data.py", 'w', encoding='utf-8') as f:
        f.write(fix_script_content)
    
    print("✅ 創建資料修復腳本: fix_kyc_data.py")

def main():
    """主函數"""
    print("🔧 修復 Migration 依賴關係錯誤")
    print("=" * 40)
    
    # 檢查是否在正確的目錄
    if not Path("manage.py").exists():
        print("❌ 錯誤：請在 Django 項目根目錄執行此腳本")
        return
    
    try:
        # 檢查現有 migrations
        last_migration = check_existing_migrations()
        
        if last_migration:
            # 創建正確的 migration
            new_migration = create_correct_migration()
            print(f"\n✅ 修復完成！新 migration: {new_migration}")
        else:
            print("\n⚠️ 沒有找到現有 migration，建議使用資料修復腳本")
        
        # 創建備用的資料修復腳本
        create_simple_data_fix_script()
        
        print("\n📋 解決方案：")
        print("\n方案一：使用 Migration（推薦）")
        print("1. python manage.py makemigrations")
        print("2. python manage.py migrate")
        
        print("\n方案二：直接修復資料")
        print("1. python fix_kyc_data.py")
        
        print("\n方案三：如果還有問題")
        print("1. 刪除 kyc/migrations/ 目錄下的錯誤文件")
        print("2. python manage.py makemigrations kyc")
        print("3. python manage.py migrate")
        print("4. python fix_kyc_data.py")
        
    except Exception as e:
        print(f"❌ 修復過程中出現錯誤：{e}")

if __name__ == "__main__":
    main()