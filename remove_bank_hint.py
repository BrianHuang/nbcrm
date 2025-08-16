#!/usr/bin/env python3
"""
移除銀行代碼自動提示功能
"""

from pathlib import Path

def update_inline_js_remove_bank_hint():
    """更新 JavaScript，移除銀行代碼提示"""
    
    print("📝 更新 JavaScript，移除銀行代碼提示...")
    
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
        setupValidation();
        
        // 當新增行時重新初始化
        $(document).on('formset:added', function() {
            setupFilePreview();
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
    
    js_dir = Path("static") / "admin" / "js"
    js_dir.mkdir(parents=True, exist_ok=True)
    
    js_file = js_dir / "kyc_inline.js"
    with open(js_file, 'w', encoding='utf-8') as f:
        f.write(js_content)
    print("✅ 更新 JavaScript 文件")

def main():
    """主函數"""
    print("🔧 移除銀行代碼自動提示功能")
    print("=" * 30)
    
    # 檢查是否在正確的目錄
    if not Path("manage.py").exists():
        print("❌ 錯誤：請在 Django 項目根目錄執行此腳本")
        return
    
    try:
        # 更新 JavaScript
        update_inline_js_remove_bank_hint()
        
        print("\n✅ 移除銀行代碼提示完成！")
        print("\n📋 保留的功能：")
        print("- ✅ 檔案上傳即時預覽")
        print("- ✅ 檔案大小檢查（100MB）")
        print("- ✅ 表單驗證和錯誤提示")
        print("- ✅ 銀行代碼格式驗證（3位數字）")
        print("- ✅ 驗證帳戶格式驗證（純數字）")
        
        print("\n🗑️ 移除的功能：")
        print("- ❌ 銀行代碼自動提示")
        print("- ❌ 銀行名稱顯示")
        
        print("\n🔧 接下來請執行：")
        print("git add .")
        print("git commit -m '移除銀行代碼自動提示功能'")
        print("git push origin main")
        
    except Exception as e:
        print(f"❌ 更新過程中出現錯誤：{e}")

if __name__ == "__main__":
    main()