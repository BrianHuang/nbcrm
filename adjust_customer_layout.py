#!/usr/bin/env python3
"""
調整客戶管理頁面版面配置
"""

from pathlib import Path

def update_customer_admin():
    """更新 customers/admin.py"""
    
    print("🔧 更新 customers/admin.py...")
    
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
            'notes': forms.Textarea(attrs={'rows': 3, 'cols': 50}),  # 一半高度
            'verified_accounts': forms.Textarea(attrs={'rows': 3, 'cols': 50}),  # 一半高度
        }

class KYCRecordInline(admin.TabularInline):
    """KYC 記錄內聯顯示"""
    from kyc.models import KYCRecord
    model = KYCRecord
    extra = 0  # 不顯示額外的空表單
    can_delete = False  # 不允許在此處刪除
    
    fields = ('bank_code', 'verification_account', 'get_file_preview', 'file_description', 'get_uploaded_by_display', 'uploaded_at')
    readonly_fields = ('get_file_preview', 'get_uploaded_by_display', 'uploaded_at')
    
    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """自定義表單欄位"""
        if db_field.name == 'bank_code':
            kwargs['widget'] = forms.TextInput(attrs={'size': 8})  # 縮短銀行代碼欄位
        elif db_field.name == 'verification_account':
            kwargs['widget'] = forms.TextInput(attrs={'size': 15})  # 縮短驗證帳戶欄位
        elif db_field.name == 'file_description':
            kwargs['widget'] = forms.TextInput(attrs={'size': 30})  # 檔案說明用一行
        return super().formfield_for_dbfield(db_field, request, **kwargs)
    
    def get_file_preview(self, obj):
        """顯示檔案預覽（簡化版）"""
        if not obj.file:
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
    
    get_file_preview.short_description = '檔案'
    
    def get_uploaded_by_display(self, obj):
        """顯示上傳者"""
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
        """不允許在此處新增"""
        return False

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    form = CustomerAdminForm
    
    list_display = ('get_display_name', 'line_nickname', 'n8_phone', 'n8_email', 'get_kyc_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'line_nickname', 'n8_nickname', 'n8_phone', 'n8_email', 'notes', 'verified_accounts')
    readonly_fields = ('created_at', 'updated_at')
    
    # 添加 KYC 記錄內聯
    inlines = [KYCRecordInline]
    
    # 簡化的 fieldsets，不分組
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
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # 編輯時
            return self.readonly_fields
        return ('created_at', 'updated_at')
    
    class Media:
        css = {
            'all': ('admin/css/custom_customer_admin.css',)
        }
'''
    
    customer_admin_path = Path("customers") / "admin.py"
    with open(customer_admin_path, 'w', encoding='utf-8') as f:
        f.write(customer_admin_content)
    print("✅ 更新 customers/admin.py")

def create_custom_css():
    """創建自定義 CSS"""
    
    print("🎨 創建自定義 CSS...")
    
    # 創建 static 目錄結構
    static_dir = Path("static") / "admin" / "css"
    static_dir.mkdir(parents=True, exist_ok=True)
    
    css_content = '''/* 客戶管理自定義 CSS */

/* 統一 KYC 內聯表格字體大小為正常大小 */
.tabular table {
    font-size: 13px !important;
}

.tabular table th,
.tabular table td {
    font-size: 13px !important;
    padding: 8px 6px !important;
}

/* KYC 內聯表格欄位寬度調整 */
.tabular .field-bank_code {
    width: 80px !important;
}

.tabular .field-verification_account {
    width: 120px !important;
}

.tabular .field-get_file_preview {
    width: 80px !important;
    text-align: center;
}

.tabular .field-file_description {
    width: 200px !important;
}

.tabular .field-get_uploaded_by_display {
    width: 120px !important;
}

.tabular .field-uploaded_at {
    width: 120px !important;
}

/* 檔案預覽樣式 */
.tabular .field-get_file_preview img {
    border: 1px solid #ddd;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* 客戶表單的備註和驗證帳戶欄位寬度調整 */
.form-row .field-notes textarea,
.form-row .field-verified_accounts textarea {
    width: 400px !important;  /* 一半寬度 */
    max-width: 400px !important;
}

/* 改善內聯表格的可讀性 */
.tabular tr.has_original {
    background: #f9f9f9;
}

.tabular tr.has_original:hover {
    background: #f0f8ff;
}

/* 確保表格標題也是正常字體大小 */
.tabular thead th {
    font-size: 13px !important;
    font-weight: bold;
}

/* KYC 內聯表格輸入框調整 */
.tabular input[type="text"] {
    font-size: 13px !important;
}

/* 響應式改善 */
@media (max-width: 768px) {
    .tabular .field-get_file_preview {
        width: 60px !important;
    }
    
    .tabular .field-get_file_preview img {
        max-width: 40px;
        max-height: 40px;
    }
    
    .form-row .field-notes textarea,
    .form-row .field-verified_accounts textarea {
        width: 300px !important;
    }
}
'''
    
    css_file = static_dir / "custom_customer_admin.css"
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content)
    print("✅ 創建自定義 CSS")

def main():
    """主函數"""
    print("🔧 調整客戶管理頁面版面")
    print("=" * 30)
    
    # 檢查是否在正確的目錄
    if not Path("manage.py").exists():
        print("❌ 錯誤：請在 Django 項目根目錄執行此腳本")
        return
    
    try:
        # 更新客戶 Admin
        update_customer_admin()
        
        # 創建自定義 CSS
        create_custom_css()
        
        print("\n✅ 調整完成！")
        print("\n🎯 版面調整：")
        print("- ✅ 移除基本資料和詳細資料分組")
        print("- ✅ 備註和驗證帳戶文字框調整為一半寬度和高度")
        print("- ✅ 移除 KYC 概況區塊")
        print("- ✅ KYC 記錄表格字體大小調整為正常")
        print("- ✅ 銀行代碼和驗證帳戶欄位寬度縮短")
        print("- ✅ 檔案說明改為一行輸入")
        
        print("\n📋 接下來請執行：")
        print("git add .")
        print("git commit -m '調整客戶管理頁面版面配置'")
        print("git push origin main")
        
    except Exception as e:
        print(f"❌ 更新過程中出現錯誤：{e}")

if __name__ == "__main__":
    main()