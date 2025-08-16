#!/usr/bin/env python3
"""
調整客戶資料表單版面配置
"""

from pathlib import Path

def update_customer_admin_layout():
    """更新客戶 Admin 版面配置"""
    
    print("🎨 更新客戶資料表單版面配置...")
    
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
            'name': forms.TextInput(attrs={'style': 'width: 120px;'}),  # 縮短姓名欄位
            'line_nickname': forms.TextInput(attrs={'style': 'width: 120px;'}),  # 縮短Line暱稱
            'n8_nickname': forms.TextInput(attrs={'style': 'width: 120px;'}),  # 縮短N8暱稱
            'n8_phone': forms.TextInput(attrs={'style': 'width: 150px;'}),  # N8電話欄位
            'n8_email': forms.EmailInput(attrs={'style': 'width: 200px;'}),  # N8信箱欄位
            'notes': forms.Textarea(attrs={'rows': 3, 'cols': 50, 'style': 'width: 400px;'}),
            'verified_accounts': forms.Textarea(attrs={'rows': 3, 'cols': 50, 'style': 'width: 400px;'}),
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
    
    # 調整版面配置的 fieldsets
    fieldsets = (
        (None, {
            'fields': (
                ('name', 'line_nickname', 'n8_nickname'),  # 三個欄位同一列
                ('n8_email', 'n8_phone'),  # N8信箱和電話同一列  
                ('notes', 'verified_accounts'),  # 備註和驗證帳戶同一列
                ('created_at', 'updated_at')  # 系統資訊同一列
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
            'all': ('admin/css/custom_customer_layout.css',)
        }
        js = ('admin/js/kyc_inline.js',)
'''
    
    customer_admin_path = Path("customers") / "admin.py"
    with open(customer_admin_path, 'w', encoding='utf-8') as f:
        f.write(customer_admin_content)
    print("✅ 更新客戶 Admin 版面配置")

def create_custom_layout_css():
    """創建自定義版面 CSS"""
    
    print("🎨 創建自定義版面 CSS...")
    
    # 確保目錄存在
    static_dir = Path("static") / "admin" / "css"
    static_dir.mkdir(parents=True, exist_ok=True)
    
    css_content = '''/* 客戶資料表單版面自定義 CSS */

/* 表單行的版面配置 */
.form-row {
    margin-bottom: 10px;
    display: flex;
    align-items: flex-start;
    gap: 15px;
}

/* 三欄位同一列的樣式 */
.form-row .field-name,
.form-row .field-line_nickname,
.form-row .field-n8_nickname {
    flex: 0 0 auto;
    margin-right: 15px;
}

.form-row .field-name input,
.form-row .field-line_nickname input,
.form-row .field-n8_nickname input {
    width: 120px !important;
    max-width: 120px !important;
}

/* 兩欄位同一列的樣式 */
.form-row .field-n8_email,
.form-row .field-n8_phone {
    flex: 0 0 auto;
    margin-right: 15px;
}

.form-row .field-n8_email input {
    width: 200px !important;
    max-width: 200px !important;
}

.form-row .field-n8_phone input {
    width: 150px !important;
    max-width: 150px !important;
}

/* 備註和驗證帳戶同一列 */
.form-row .field-notes,
.form-row .field-verified_accounts {
    flex: 0 0 auto;
    margin-right: 15px;
}

.form-row .field-notes textarea,
.form-row .field-verified_accounts textarea {
    width: 400px !important;
    max-width: 400px !important;
    height: 80px !important;
    resize: vertical;
}

/* 系統資訊欄位 */
.form-row .field-created_at,
.form-row .field-updated_at {
    flex: 0 0 auto;
    margin-right: 15px;
}

/* 欄位標籤樣式 */
.form-row label {
    display: block;
    margin-bottom: 3px;
    font-weight: bold;
    font-size: 12px;
    color: #333;
    min-width: fit-content;
}

/* 輸入框通用樣式 */
.form-row input[type="text"],
.form-row input[type="email"],
.form-row textarea {
    padding: 6px 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 13px;
    font-family: inherit;
}

.form-row input[type="text"]:focus,
.form-row input[type="email"]:focus,
.form-row textarea:focus {
    border-color: #007cba;
    outline: none;
    box-shadow: 0 0 3px rgba(0, 124, 186, 0.3);
}

/* KYC 內聯表格字體大小統一 */
.tabular table {
    font-size: 13px !important;
}

.tabular table th,
.tabular table td {
    font-size: 13px !important;
    padding: 8px 6px !important;
}

/* KYC 內聯表格欄位寬度 */
.tabular .field-bank_code {
    width: 90px !important;
}

.tabular .field-verification_account {
    width: 130px !important;
}

.tabular .field-file {
    width: 150px !important;
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

/* 檔案上傳欄位樣式 */
.tabular .field-file input[type="file"] {
    font-size: 12px;
    width: 140px;
}

/* 檔案預覽樣式 */
.tabular .field-get_file_preview img {
    border: 1px solid #ddd;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* 新增行的樣式 */
.tabular .add-row {
    background-color: #f8f9fa !important;
}

.tabular .add-row td {
    border-top: 2px solid #007cba !important;
}

/* 改善內聯表格的可讀性 */
.tabular tr.has_original {
    background: #f9f9f9;
}

.tabular tr.has_original:hover {
    background: #f0f8ff;
}

/* 刪除按鈕樣式 */
.tabular .delete {
    text-align: center;
    width: 60px;
}

.tabular .delete input[type="checkbox"] {
    transform: scale(1.2);
}

/* 表格標題樣式 */
.tabular thead th {
    font-size: 13px !important;
    font-weight: bold;
    background-color: #f1f1f1;
}

/* 輸入框樣式統一 */
.tabular input[type="text"],
.tabular textarea,
.tabular select {
    font-size: 13px !important;
    padding: 4px;
    border: 1px solid #ccc;
    border-radius: 3px;
}

/* 內聯表單標題樣式 */
.inline-group h2 {
    background: linear-gradient(90deg, #007cba, #005a8b);
    color: white;
    padding: 10px 15px;
    margin: 0;
    border-radius: 5px 5px 0 0;
    font-size: 14px;
}

.inline-group .tabular {
    border: 1px solid #007cba;
    border-radius: 0 0 5px 5px;
}

/* 響應式設計 */
@media (max-width: 1024px) {
    .form-row {
        flex-direction: column;
        gap: 10px;
    }
    
    .form-row .field-name input,
    .form-row .field-line_nickname input,
    .form-row .field-n8_nickname input {
        width: 200px !important;
    }
    
    .form-row .field-notes textarea,
    .form-row .field-verified_accounts textarea {
        width: 300px !important;
    }
}

@media (max-width: 768px) {
    .tabular .field-get_file_preview {
        width: 60px !important;
    }
    
    .tabular .field-get_file_preview img {
        max-width: 40px;
        max-height: 40px;
    }
    
    .tabular .field-file input[type="file"] {
        width: 120px;
    }
}
'''
    
    css_file = static_dir / "custom_customer_layout.css"
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content)
    print("✅ 創建自定義版面 CSS")

def main():
    """主函數"""
    print("🎨 調整客戶資料表單版面配置")
    print("=" * 40)
    
    # 檢查是否在正確的目錄
    if not Path("manage.py").exists():
        print("❌ 錯誤：請在 Django 項目根目錄執行此腳本")
        return
    
    try:
        # 更新客戶 Admin
        update_customer_admin_layout()
        
        # 創建自定義 CSS
        create_custom_layout_css()
        
        print("\n✅ 版面配置調整完成！")
        print("\n🎯 新的版面配置：")
        print("- 📝 第一列：姓名、Line暱稱、N8暱稱（各120px寬）")
        print("- 📧 第二列：N8信箱（200px）、N8電話（150px）")
        print("- 📋 第三列：備註、驗證帳戶（各400px寬，3行高）")
        print("- 🕐 第四列：建立時間、更新時間")
        
        print("\n📱 響應式設計：")
        print("- 在小螢幕上自動調整為垂直排列")
        print("- 保持良好的可讀性和使用體驗")
        
        print("\n🔧 接下來請執行：")
        print("git add .")
        print("git commit -m '調整客戶資料表單版面配置'")
        print("git push origin main")
        
    except Exception as e:
        print(f"❌ 調整過程中出現錯誤：{e}")

if __name__ == "__main__":
    main()