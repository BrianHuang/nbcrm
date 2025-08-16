// KYC 內聯表單增強 JavaScript

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
                    if (bankCode && !/^\d{3}$/.test(bankCode)) {
                        alert('銀行代碼必須是3位數字');
                        hasError = true;
                        return false;
                    }
                    
                    // 驗證帳戶格式檢查
                    if (verifyAccount && !/^\d+$/.test(verifyAccount)) {
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
