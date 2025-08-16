#!/usr/bin/env python3
"""
更新客戶管理 Admin，添加 KYC 記錄內聯顯示
"""

from pathlib import Path

def update_customer_admin():
    """更新 customers/admin.py"""
    
    print("🔧 更新 customers/admin.py...")
    
    customer_admin_content = '''from django.contrib import admin
from django.utils.html import format_html
from .models import Customer
import os

class KYCRecordInline(admin.TabularInline):
    """KYC 記錄內聯顯示"""
    from kyc.models import KYCRecord
    model = KYCRecord
    extra = 0  # 不顯示額外的空表單
    can_delete = False  # 不允許在此處刪除
    
    fields = ('bank_code', 'verification_account', 'get_file_preview', 'file_description', 'get_uploaded_by_display', 'uploaded_at')
    readonly_fields = ('get_file_preview', 'get_uploaded_by_display', 'uploaded_at')
    
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
    list_display = ('get_display_name', 'line_nickname', 'n8_phone', 'n8_email', 'get_kyc_count', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('name', 'line_nickname', 'n8_nickname', 'n8_phone', 'n8_email', 'notes', 'verified_accounts')
    readonly_fields = ('created_at', 'updated_at', 'get_kyc_summary')
    
    # 添加 KYC 記錄內聯
    inlines = [KYCRecordInline]
    
    fieldsets = (
        ('基本資料', {
            'fields': ('name', 'line_nickname', 'n8_nickname', 'n8_phone', 'n8_email')
        }),
        ('詳細資訊', {
            'fields': ('notes', 'verified_accounts')
        }),
        ('KYC 概況', {
            'fields': ('get_kyc_summary',),
            'classes': ('collapse',),
            'description': '此客戶的 KYC 記錄概況，詳細記錄請查看下方 KYC 記錄區塊'
        }),
        ('系統資訊', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
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
    
    def get_kyc_summary(self, obj):
        """顯示 KYC 記錄摘要"""
        kyc_records = obj.kyc_records.all()
        
        if not kyc_records:
            return format_html(
                '<div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">'
                '<i style="color: #6c757d;">此客戶尚無 KYC 記錄</i><br>'
                '<small><a href="/admin/kyc/kycrecord/add/?customer={}" target="_blank">➕ 新增 KYC 記錄</a></small>'
                '</div>',
                obj.id
            )
        
        summary_html = f'<div style="padding: 10px; background: #e7f3ff; border-radius: 5px;">'
        summary_html += f'<strong>📊 KYC 記錄摘要</strong><br>'
        summary_html += f'<small>總記錄數：{kyc_records.count()}</small><br><br>'
        
        # 統計檔案類型
        image_count = sum(1 for kyc in kyc_records if kyc.file and kyc.is_image())
        video_count = sum(1 for kyc in kyc_records if kyc.file and kyc.is_video())
        other_count = sum(1 for kyc in kyc_records if kyc.file and not kyc.is_image() and not kyc.is_video())
        no_file_count = sum(1 for kyc in kyc_records if not kyc.file)
        
        if image_count > 0:
            summary_html += f'🖼️ 圖片檔案：{image_count} 個<br>'
        if video_count > 0:
            summary_html += f'🎥 影片檔案：{video_count} 個<br>'
        if other_count > 0:
            summary_html += f'📄 其他檔案：{other_count} 個<br>'
        if no_file_count > 0:
            summary_html += f'📝 純資料記錄：{no_file_count} 個<br>'
        
        # 最近記錄
        latest_kyc = kyc_records.first()
        if latest_kyc:
            summary_html += f'<br><small>最近記錄：{latest_kyc.uploaded_at.strftime("%Y-%m-%d %H:%M")}</small><br>'
            summary_html += f'<small>上傳客服：{latest_kyc.uploaded_by.username}</small>'
        
        summary_html += '<br><br><small><a href="/admin/kyc/kycrecord/?customer__id__exact={}" target="_blank">🔍 查看所有 KYC 記錄</a></small>'.format(obj.id)
        summary_html += '</div>'
        
        return format_html(summary_html)
    
    get_kyc_summary.short_description = 'KYC 記錄摘要'
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # 編輯時
            return self.readonly_fields
        return ('created_at', 'updated_at', 'get_kyc_summary')
'''
    
    customer_admin_path = Path("customers") / "admin.py"
    with open(customer_admin_path, 'w', encoding='utf-8') as f:
        f.write(customer_admin_content)
    print("✅ 更新 customers/admin.py")

def create_custom_css():
    """創建自定義 CSS（可選）"""
    
    print("🎨 創建自定義 CSS...")
    
    # 創建 static 目錄結構
    static_dir = Path("static") / "admin" / "css"
    static_dir.mkdir(parents=True, exist_ok=True)
    
    css_content = '''/* 自定義 Admin CSS */

/* KYC 內聯表格樣式 */
.tabular .kyc-file-preview {
    text-align: center;
    width: 80px;
}

.tabular .kyc-file-preview img {
    border: 1px solid #ddd;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

/* KYC 摘要區塊樣式 */
.kyc-summary {
    background: #f8f9fa;
    border-left: 4px solid #007cba;
    padding: 15px;
    margin: 10px 0;
}

/* 改善內聯表格的可讀性 */
.tabular tr.has_original {
    background: #f9f9f9;
}

.tabular tr.has_original:hover {
    background: #f0f8ff;
}

/* 響應式改善 */
@media (max-width: 768px) {
    .tabular .kyc-file-preview {
        width: 60px;
    }
    
    .tabular .kyc-file-preview img {
        max-width: 40px;
        max-height: 40px;
    }
}
'''
    
    css_file = static_dir / "custom_admin.css"
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content)
    print("✅ 創建自定義 CSS")

def main():
    """主函數"""
    print("🔧 更新客戶管理 Admin")
    print("=" * 30)
    
    # 檢查是否在正確的目錄
    if not Path("manage.py").exists():
        print("❌ 錯誤：請在 Django 項目根目錄執行此腳本")
        return
    
    try:
        # 更新客戶 Admin
        update_customer_admin()
        
        # 創建自定義 CSS（可選）
        create_custom_css()
        
        print("\n✅ 更新完成！")
        print("\n🎯 新功能：")
        print("- 客戶列表頁面顯示 KYC 記錄數量")
        print("- 客戶詳情頁面顯示 KYC 記錄摘要")
        print("- 客戶編輯頁面底部顯示所有 KYC 記錄")
        print("- KYC 記錄包含檔案預覽、銀行資訊等")
        print("- 可直接從客戶頁面查看或跳轉到 KYC 管理")
        
        print("\n📋 接下來請執行：")
        print("git add .")
        print("git commit -m '新增客戶頁面 KYC 記錄顯示功能'")
        print("git push origin main")
        
    except Exception as e:
        print(f"❌ 更新過程中出現錯誤：{e}")

if __name__ == "__main__":
    main()