#!/usr/bin/env python3
"""
在客戶表單中添加內聯新增 KYC 記錄功能
"""

from pathlib import Path

def update_customer_admin_with_inline_add():
    """更新客戶 Admin，支援內聯新增 KYC 記錄"""
    
    print("🔧 更新 customers/admin.py 支援內聯新增 KYC...")
    
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
        fields = '__all__'
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
    
    def get_formset(self, request, obj=None, **kwargs):
        """自定義表單集，設置初始值"""
        formset = super().get_formset(request, obj, **kwargs)
        
        # 保存 request 到 formset，以便在保存時使用
        formset.request = request
        return formset
    
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
    
    def save_model(self, request, obj, form, change):
        """保存 KYC 記錄時設置上傳者"""
        if not change:  # 新增時
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)
    
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
        """保存表單集時設置上傳者"""
        instances = formset.save(commit=False)
        
        for instance in instances:
            # 如果是新的 KYC 記錄，設置上傳者
            if not instance.pk and hasattr(instance, 'uploaded_by'):
                instance.uploaded_by = request.user
            instance.save()
        
        # 刪除標記為刪除的實例
        formset.save_m2m()
        for obj in formset.deleted_objects:
            obj.delete()
    
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
    print("✅ 更新 customers/admin.py")

def update_custom_css():
    """更新自定義 CSS，優化內聯表單樣式"""
    
    print("🎨 更新自定義 CSS...")
    
    # 確保目錄存在
    static_dir = Path("static") / "admin" / "css"
    static_dir.mkdir(parents=True, exist_ok=True)
    
    css_content = '''/* 客戶管理自定義 CSS */

/* 統一 KYC 內聯表格字體大小 */
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

/* 客戶表單的文字框調整 */
.form-row .field-notes textarea,
.form-row .field-verified_accounts textarea {
    width: 400px !important;
    max-width: 400px !important;
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

/* Placeholder 樣式 */
.tabular input::placeholder {
    color: #999;
    font-style: italic;
}

/* 必填欄位標記 */
.tabular .required label:after {
    content: " *";
    color: #e74c3c;
    font-weight: bold;
}

/* 錯誤訊息樣式 */
.tabular .errorlist {
    background-color: #f8d7da;
    border: 1px solid #f5c6cb;
    color: #721c24;
    padding: 4px 8px;
    border-radius: 3px;
    font-size: 12px;
    margin-top: 2px;
}

/* 幫助文字樣式 */
.tabular .help {
    font-size: 11px;
    color: #666;
    font-style: italic;
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
    
    .tabular .field-file input[type="file"] {
        width: 120px;
    }
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
'''
    
    css_file = static_dir / "custom_customer_admin.css"
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content)
    print("✅ 更新自定義 CSS")

def create_inline_js():
    """創建 JavaScript 增強內聯表單體驗"""
    
    print("📝 創建 JavaScript 增強功能...")
    
    # 確保目錄存在
    js_dir = Path("static") / "admin" / "js"
    js_dir.mkdir(parents=True, exist_ok=True)
    
    js_content = '''// KYC 內聯表單增強 JavaScript

(function($) {
    $(document).ready(function() {
        
        // 檔案上傳預覽功能
        function setupFilePreview() {
            $('.field-file input[type="file"]').change(function() {
                var input = this;
                var previewCell = $(input).closest('tr').find('.field-get_file_preview');
                
                if (input.files && input.files[0]) {
                    var file = input.files[0];
                    var fileName = file.name;
                    var fileSize = (file.size / 1024 / 1024).toFixed(2); // MB
                    
                    // 檢查檔案大小（100MB 限制）
                    if (file.size > 100 * 1024 * 1024) {
                        alert('檔案大小不能超過 100MB。當前檔案：' + fileSize + 'MB');
                        $(input).val('');
                        return;
                    }
                    
                    // 顯示檔案資訊
                    var fileInfo = '<div style="font-size: 11px; color: #666;">';
                    fileInfo += '<strong>' + fileName.substring(0, 15) + (fileName.length > 15 ? '...' : '') + '</strong><br>';
                    fileInfo += fileSize + ' MB';
                    fileInfo += '</div>';
                    
                    // 如果是圖片，顯示預覽
                    if (file.type.startsWith('image/')) {
                        var reader = new FileReader();
                        reader.onload = function(e) {
                            var preview = '<img src="' + e.target.result + '" style="max-width: 50px; max-height: 50px; border-radius: 3px; border: 1px solid #ddd;" /><br>';
                            previewCell.html(preview + fileInfo);
                        };
                        reader.readAsDataURL(file);
                    } else {
                        // 非圖片檔案顯示圖示
                        var icon = '📄';
                        if (file.type.startsWith('video/')) icon = '🎥';
                        
                        var preview = '<div style="text-align: center; font-size: 20px;">' + icon + '</div>';
                        previewCell.html(preview + fileInfo);
                    }
                }
            });
        }
        
        // 自動填充功能
        function setupAutoFill() {
            $('.field-bank_code input').on('input', function() {
                var bankCode = $(this).val();
                var row = $(this).closest('tr');
                var descField = row.find('.field-file_description input');
                
                // 常見銀行代碼自動提示
                var bankNames = {
                    '004': '台灣銀行',
                    '005': '土地銀行',
                    '006': '合作金庫',
                    '007': '第一銀行',
                    '008': '華南銀行',
                    '009': '彰化銀行',
                    '011': '上海銀行',
                    '012': '台北富邦',
                    '013': '國泰世華',
                    '017': '兆豐銀行'
                };
                
                if (bankNames[bankCode] && !descField.val()) {
                    descField.attr('placeholder', bankNames[bankCode] + ' 相關文件');
                }
            });
        }
        
        // 表單驗證
        function setupValidation() {
            $('form').submit(function() {
                var hasError = false;
                
                // 檢查每個 KYC 記錄行
                $('.tabular tbody tr:not(.add-row, .empty-form)').each(function() {
                    var row = $(this);
                    var bankCode = row.find('.field-bank_code input').val();
                    var verifyAccount = row.find('.field-verification_account input').val();
                    var fileInput = row.find('.field-file input[type="file"]');
                    var hasFile = fileInput[0] && fileInput[0].files.length > 0;
                    var isDelete = row.find('.delete input[type="checkbox"]').prop('checked');
                    
                    // 跳過標記為刪除的行
                    if (isDelete) return;
                    
                    // 如果有任何欄位填寫，至少要有銀行代碼或檔案
                    if ((bankCode || verifyAccount || hasFile) && !bankCode && !hasFile) {
                        alert('請至少填寫銀行代碼或上傳檔案');
                        hasError = true;
                        return false;
                    }
                    
                    // 銀行代碼格式檢查
                    if (bankCode && !/^\\d{3}$/.test(bankCode)) {
                        alert('銀行代碼必須是3位數字');
                        hasError = true;
                        return false;
                    }
                    
                    // 驗證帳戶格式檢查
                    if (verifyAccount && !/^\\d+$/.test(verifyAccount)) {
                        alert('驗證帳戶只能包含數字');
                        hasError = true;
                        return false;
                    }
                });
                
                return !hasError;
            });
        }
        
        // 初始化所有功能
        setupFilePreview();
        setupAutoFill();
        setupValidation();
        
        // 當新增行時重新初始化
        $(document).on('formset:added', function() {
            setupFilePreview();
            setupAutoFill();
        });
        
        // 美化新增按鈕
        $('.add-row a').html('➕ 新增 KYC 記錄').css({
            'background': '#007cba',
            'color': 'white',
            'padding': '5px 10px',
            'border-radius': '3px',
            'text-decoration': 'none',
            'font-size': '12px'
        });
        
    });
})(django.jQuery);
'''
    
    js_file = js_dir / "kyc_inline.js"
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print("✅ 創建 JavaScript 增強功能")

def main():
    """主函數"""
    print("➕ 添加客戶表單內聯新增 KYC 記錄功能")
    print("=" * 40)
    
    # 檢查是否在正確的目錄
    if not Path("manage.py").exists():
        print("❌ 錯誤：請在 Django 項目根目錄執行此腳本")
        return
    
    try:
        # 更新文件
        update_customer_admin_with_inline_add()
        update_custom_css()
        create_inline_js()
        
        print("\n✅ 內聯新增功能設置完成！")
        print("\n🎯 新功能：")
        print("- ✅ 在客戶表單底部可直接新增 KYC 記錄")
        print("- ✅ 支援檔案上傳和即時預覽")
        print("- ✅ 自動設置上傳者為當前登入用戶")
        print("- ✅ 銀行代碼自動提示功能")
        print("- ✅ 表單驗證和錯誤提示")
        print("- ✅ 檔案大小檢查（100MB 限制）")
        print("- ✅ 支援編輯和刪除現有記錄")
        
        print("\n📋 使用方式：")
        print("1. 進入客戶編輯頁面")
        print("2. 滾動到底部的「KYC 記錄」區塊")
        print("3. 在空白行填寫新的 KYC 資料")
        print("4. 點擊「保存」即可同時保存客戶和 KYC 資料")
        
        print("\n🔧 接下來請執行：")
        print("git add .")
        print("git commit -m '添加客戶表單內聯新增 KYC 記錄功能'")
        print("git push origin main")
        
    except Exception as e:
        print(f"❌ 設置過程中出現錯誤：{e}")

if __name__ == "__main__":
    main()