#!/usr/bin/env python3
"""
修復客戶表單中 KYC 記錄 uploaded_by 空值錯誤
"""

from pathlib import Path

def fix_customer_admin_uploaded_by():
    """修復 customers/admin.py 中的 uploaded_by 問題"""
    
    print("🔧 修復 customers/admin.py 中的 uploaded_by 錯誤...")
    
    customer_admin_content = '''from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import Customer
import os

class CustomerAdminForm(forms.ModelForm):
    """自定義客戶表單"""
    
    class Meta:
        model = Customer
        fields = '__all__'
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
            'verified_accounts': forms.Textarea(attrs={'rows': 3, 'cols': 50}),
        }

class KYCRecordInlineForm(forms.ModelForm):
    """自定義 KYC 內聯表單"""
    
    class Meta:
        from kyc.models import KYCRecord
        model = KYCRecord
        fields = ['bank_code', 'verification_account', 'file', 'file_description']  # 排除 uploaded_by
        widgets = {
            'bank_code': forms.TextInput(attrs={'size': 8, 'placeholder': '3位數字'}),
            'verification_account': forms.TextInput(attrs={'size': 15, 'placeholder': '帳號數字'}),
            'file_description': forms.TextInput(attrs={'size': 30, 'placeholder': '檔案說明（選填）'}),
        }

class KYCRecordInline(admin.TabularInline):
    """KYC 記錄內聯顯示 - 支援新增和編輯"""
    from kyc.models import KYCRecord
    model = KYCRecord
    form = KYCRecordInlineForm
    extra = 1  # 顯示 1 個空表單供新增
    can_delete = True  # 允許刪除
    
    fields = ('bank_code', 'verification_account', 'file', 'get_file_preview', 'file_description', 'get_uploaded_by_display', 'uploaded_at')
    readonly_fields = ('get_file_preview', 'get_uploaded_by_display', 'uploaded_at')
    
    def get_file_preview(self, obj):
        """顯示檔案預覽（簡化版）"""
        if not obj or not obj.file:
            return "無檔案"
        
        try:
            file_url = obj.file.url
            file_name = os.path.basename(obj.file.name)
            
            if obj.is_image():
                return format_html(
                    '<img src="{}" style="max-width: 50px; max-height: 50px; border-radius: 3px;" /><br>'
                    '<small><a href="{}" target="_blank">{}</a></small>',
                    file_url, file_url, file_name[:20] + "..." if len(file_name) > 20 else file_name
                )
            elif obj.is_video():
                return format_html(
                    '<div style="text-align: center;">'
                    '<i style="font-size: 20px;">🎥</i><br>'
                    '<small><a href="{}" target="_blank">{}</a></small>'
                    '</div>',
                    file_url, file_name[:20] + "..." if len(file_name) > 20 else file_name
                )
            else:
                return format_html(
                    '<div style="text-align: center;">'
                    '<i style="font-size: 20px;">📄</i><br>'
                    '<small><a href="{}" target="_blank">{}</a></small>'
                    '</div>',
                    file_url, file_name[:20] + "..." if len(file_name) > 20 else file_name
                )
        except Exception:
            return format_html('<span style="color: #dc3545;">載入失敗</span>')
    
    get_file_preview.short_description = '檔案預覽'
    
    def get_uploaded_by_display(self, obj):
        """顯示上傳者"""
        if not obj or not obj.uploaded_by:
            return "新記錄"
        
        if hasattr(obj.uploaded_by, 'get_display_name'):
            return obj.uploaded_by.get_display_name()
        else:
            full_name = obj.uploaded_by.get_full_name().strip()
            if full_name:
                return f"{full_name}({obj.uploaded_by.username})"
            else:
                return obj.uploaded_by.username
    
    get_uploaded_by_display.short_description = '上傳客服'
    
    def has_add_permission(self, request, obj=None):
        """允許新增 KYC 記錄"""
        return True
    
    def has_change_permission(self, request, obj=None):
        """允許編輯 KYC 記錄"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """根據用戶角色決定刪除權限"""
        if obj and hasattr(obj, 'uploaded_by'):
            # 管理員可以刪除所有記錄，一般用戶只能刪除自己上傳的
            if request.user.is_admin():
                return True
            elif hasattr(obj, 'uploaded_by'):
                return obj.uploaded_by == request.user
        return request.user.is_admin()

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    form = CustomerAdminForm
    
    list_display = ('get_display_name', 'line_nickname', 'n8_phone', 'n8_email', 'get_kyc_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'line_nickname', 'n8_nickname', 'n8_phone', 'n8_email', 'notes', 'verified_accounts')
    readonly_fields = ('created_at', 'updated_at')
    
    # 添加 KYC 記錄內聯
    inlines = [KYCRecordInline]
    
    # 簡化的 fieldsets
    fieldsets = (
        (None, {
            'fields': (
                ('name', 'line_nickname'),
                ('n8_nickname', 'n8_phone'), 
                'n8_email',
                'notes',
                'verified_accounts',
                ('created_at', 'updated_at')
            )
        }),
    )
    
    def get_display_name(self, obj):
        return obj.get_display_name()
    get_display_name.short_description = '客戶姓名'
    get_display_name.admin_order_field = 'name'
    
    def get_kyc_count(self, obj):
        """顯示 KYC 記錄數量"""
        count = obj.kyc_records.count()
        if count > 0:
            return format_html(
                '<span style="background: #28a745; color: white; padding: 2px 6px; border-radius: 3px;">{}</span>',
                count
            )
        else:
            return format_html(
                '<span style="background: #6c757d; color: white; padding: 2px 6px; border-radius: 3px;">0</span>'
            )
    get_kyc_count.short_description = 'KYC 記錄'
    
    def save_formset(self, request, form, formset, change):
        """保存表單集時設置上傳者 - 修復版本"""
        # 先保存表單集，但不提交到資料庫
        instances = formset.save(commit=False)
        
        # 處理新增和修改的實例
        for instance in instances:
            # 如果是新的 KYC 記錄且沒有設置 uploaded_by，設置為當前用戶
            if not instance.pk:  # 新記錄
                instance.uploaded_by = request.user
            # 如果 uploaded_by 為空（可能因為某種原因），也設置為當前用戶
            elif not instance.uploaded_by:
                instance.uploaded_by = request.user
            
            # 保存實例
            instance.save()
        
        # 處理標記為刪除的實例
        for obj in formset.deleted_objects:
            obj.delete()
        
        # 保存多對多關係
        formset.save_m2m()
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # 編輯時
            return self.readonly_fields
        return ('created_at', 'updated_at')
    
    class Media:
        css = {
            'all': ('admin/css/custom_customer_admin.css',)
        }
        js = ('admin/js/kyc_inline.js',)
'''
    
    customer_admin_path = Path("customers") / "admin.py"
    with open(customer_admin_path, 'w', encoding='utf-8') as f:
        f.write(customer_admin_content)
    print("✅ 修復 customers/admin.py")

def create_migration_fix():
    """創建修復現有 null 值的 migration"""
    
    print("🔧 創建修復現有 null 值的 migration...")
    
    migration_content = '''# Generated to fix existing null uploaded_by values
from django.db import migrations
from django.contrib.auth import get_user_model

def fix_null_uploaded_by(apps, schema_editor):
    """修復現有的 null uploaded_by 值"""
    KYCRecord = apps.get_model('kyc', 'KYCRecord')
    User = get_user_model()
    
    # 找到一個管理員用戶作為預設值
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        # 如果沒有超級用戶，創建一個系統用戶
        admin_user = User.objects.create_user(
            username='system',
            email='system@nbcrm.local',
            first_name='系統',
            last_name='管理員',
            is_staff=True,
            is_superuser=True
        )
    
    # 更新所有 uploaded_by 為 null 的記錄
    null_records = KYCRecord.objects.filter(uploaded_by__isnull=True)
    updated_count = null_records.update(uploaded_by=admin_user)
    
    print(f"修復了 {updated_count} 個 KYC 記錄的 uploaded_by 欄位")

def reverse_fix_null_uploaded_by(apps, schema_editor):
    """回滾操作（不執行任何操作）"""
    pass

class Migration(migrations.Migration):

    dependencies = [
        ('kyc', '0005_update_file_size_limit_100mb'),  # 請根據實際情況調整
    ]

    operations = [
        migrations.RunPython(fix_null_uploaded_by, reverse_fix_null_uploaded_by),
    ]
'''
    
    # 創建 migration 目錄
    migrations_dir = Path("kyc") / "migrations"
    migrations_dir.mkdir(exist_ok=True)
    
    migration_file = migrations_dir / "0006_fix_null_uploaded_by.py"
    with open(migration_file, 'w', encoding='utf-8') as f:
        f.write(migration_content)
    print("✅ 創建修復 migration")

def main():
    """主函數"""
    print("🔧 修復 KYC 記錄 uploaded_by 空值錯誤")
    print("=" * 40)
    
    # 檢查是否在正確的目錄
    if not Path("manage.py").exists():
        print("❌ 錯誤：請在 Django 項目根目錄執行此腳本")
        return
    
    try:
        # 修復代碼
        fix_customer_admin_uploaded_by()
        create_migration_fix()
        
        print("\n✅ 修復完成！")
        print("\n🔧 主要修復：")
        print("- ✅ 修正 save_formset 方法，確保 uploaded_by 不為空")
        print("- ✅ 從內聯表單中排除 uploaded_by 欄位")
        print("- ✅ 加強新記錄的 uploaded_by 設置邏輯")
        print("- ✅ 創建修復現有 null 值的 migration")
        
        print("\n📋 下一步操作：")
        print("1. python manage.py makemigrations")
        print("2. python manage.py migrate")
        print("3. git add .")
        print("4. git commit -m '修復 KYC 記錄 uploaded_by 空值錯誤'")
        print("5. git push origin main")
        
    except Exception as e:
        print(f"❌ 修復過程中出現錯誤：{e}")

if __name__ == "__main__":
    main()