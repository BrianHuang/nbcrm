#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
客戶表單布局升級腳本 (修正 Windows 編碼問題版本)
自動修改 Django Admin 客戶表單，改善標籤與欄位的距離問題
"""

import os
import shutil
from pathlib import Path
import re
import sys

# 設置 stdout 編碼為 UTF-8 (解決 Windows 顯示問題)
if sys.platform.startswith('win'):
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def create_backup(file_path):
    """建立檔案備份"""
    if os.path.exists(file_path):
        backup_path = f"{file_path}.backup"
        shutil.copy2(file_path, backup_path)
        print(f"[備份] 已備份: {file_path} -> {backup_path}")
        return True
    return False

def create_css_file():
    """建立自定義 CSS 檔案"""
    css_content = """/* 客戶表單緊密布局樣式 */

/* 緊密組合布局 */
.compact-customer-form .form-row {
    display: flex;
    flex-direction: column;
    margin-bottom: 20px;
    max-width: 400px;
}

.compact-customer-form .form-row label {
    margin-bottom: 6px;
    font-weight: 600;
    color: #2c3e50;
    font-size: 14px;
}

.compact-customer-form .form-row input,
.compact-customer-form .form-row textarea,
.compact-customer-form .form-row select {
    padding: 10px;
    border: 2px solid #ddd;
    border-radius: 6px;
    font-size: 14px;
    transition: all 0.3s ease;
    width: 100%;
}

.compact-customer-form .form-row input:focus,
.compact-customer-form .form-row textarea:focus,
.compact-customer-form .form-row select:focus {
    outline: none;
    border-color: #3498db;
    box-shadow: 0 0 0 3px rgba(52, 152, 219, 0.1);
}

/* 時間欄位保持水平排列 */
.compact-customer-form .form-row:has(input[readonly]) {
    flex-direction: row;
    gap: 15px;
    align-items: center;
}

.compact-customer-form .form-row:has(input[readonly]) label {
    margin-bottom: 0;
    min-width: 80px;
}

/* 備註欄位特殊樣式 */
.compact-customer-form .form-row textarea {
    min-height: 80px;
    resize: vertical;
}

/* 改善 KYC 內聯表單 */
.kyc-inline-form {
    margin-top: 30px;
    border-top: 2px solid #3498db;
    padding-top: 20px;
}

.kyc-inline-form h2 {
    color: #3498db;
    margin-bottom: 15px;
}

/* 響應式設計 */
@media (max-width: 768px) {
    .compact-customer-form .form-row {
        max-width: 100%;
    }
    
    .compact-customer-form .form-row:has(input[readonly]) {
        flex-direction: column;
        align-items: stretch;
    }
    
    .compact-customer-form .form-row:has(input[readonly]) label {
        min-width: auto;
        margin-bottom: 6px;
    }
}

/* 改善按鈕區域 */
.submit-row {
    margin-top: 30px;
    padding-top: 20px;
    border-top: 1px solid #eee;
}

.submit-row input[type="submit"] {
    background: #3498db;
    color: white;
    padding: 12px 24px;
    border: none;
    border-radius: 6px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
}

.submit-row input[type="submit"]:hover {
    background: #2980b9;
    transform: translateY(-1px);
}

/* 表單區段美化 */
.fieldset {
    background: #fafafa;
    border-radius: 8px;
    padding: 20px;
    margin-bottom: 20px;
    border: 1px solid #e0e0e0;
}

.fieldset h2 {
    color: #2c3e50;
    border-bottom: 2px solid #3498db;
    padding-bottom: 10px;
    margin-bottom: 20px;
}
"""
    
    # 建立目錄結構
    css_dir = Path("static/admin/css")
    css_dir.mkdir(parents=True, exist_ok=True)
    
    # 寫入 CSS 檔案
    css_file = css_dir / "custom_customer_layout.css"
    css_file.write_text(css_content, encoding='utf-8')
    
    print(f"[CSS] 已建立 CSS 檔案: {css_file}")
    return css_file

def update_admin_py():
    """更新 customers/admin.py 檔案"""
    admin_file = Path("customers/admin.py")
    
    if not admin_file.exists():
        print(f"[錯誤] 找不到檔案: {admin_file}")
        return False
    
    # 備份原檔案
    create_backup(admin_file)
    
    # 讀取原檔案內容
    content = admin_file.read_text(encoding='utf-8')
    
    # 修改 fieldsets 配置
    fieldsets_pattern = r'fieldsets\s*=\s*\([^)]*\([^)]*\{[^}]*\'fields\'[^}]*\}[^)]*\)[^)]*\)'
    new_fieldsets = """fieldsets = (
        (None, {
            'fields': (
                'name',           # 每個欄位獨立一行，確保標籤貼近
                'n8_nickname',    
                'line_nickname',
                'n8_phone',
                'n8_email',
                'notes',
                'verified_accounts',
                ('created_at', 'updated_at')  # 只有時間欄位保持在同一行
            ),
            'classes': ('compact-customer-form',),  # 自定義 CSS class
        }),
    )"""
    
    # 替換 fieldsets
    if re.search(fieldsets_pattern, content, flags=re.DOTALL):
        content = re.sub(fieldsets_pattern, new_fieldsets, content, flags=re.DOTALL)
        print("[Admin] 已更新 fieldsets 配置")
    else:
        print("[警告] 無法自動替換 fieldsets，請手動修改")
    
    # 確保 Media 類別包含新的 CSS
    if 'class Media:' in content:
        # 更新現有的 Media 類別
        media_pattern = r'class Media:(.*?)(?=\n    [^\s]|\n@|\nclass|\Z)'
        new_media = """class Media:
        css = {
            'all': ('admin/css/custom_customer_layout.css',)
        }
        js = ('admin/js/kyc_inline.js',)"""
        
        if re.search(media_pattern, content, flags=re.DOTALL):
            content = re.sub(media_pattern, new_media, content, flags=re.DOTALL)
            print("[Admin] 已更新 Media 類別")
    else:
        # 在檔案末尾添加 Media 類別
        if 'CustomerAdmin' in content:
            # 找到 CustomerAdmin 類別的最後一行
            lines = content.split('\n')
            insert_index = -1
            in_customer_admin = False
            
            for i, line in enumerate(lines):
                if 'class CustomerAdmin' in line:
                    in_customer_admin = True
                elif in_customer_admin and (line.startswith('class ') or line.startswith('@')):
                    insert_index = i
                    break
            
            if insert_index == -1:
                insert_index = len(lines)
            
            # 插入 Media 類別
            media_lines = [
                "",
                "    class Media:",
                "        css = {",
                "            'all': ('admin/css/custom_customer_layout.css',)",
                "        }",
                "        js = ('admin/js/kyc_inline.js',)",
                ""
            ]
            
            for j, media_line in enumerate(media_lines):
                lines.insert(insert_index + j, media_line)
            
            content = '\n'.join(lines)
            print("[Admin] 已添加 Media 類別")
    
    # 寫回檔案
    admin_file.write_text(content, encoding='utf-8')
    
    print(f"[Admin] 已更新: {admin_file}")
    return True

def update_settings_py():
    """確保 settings.py 包含靜態檔案配置"""
    settings_file = Path("nbcrm/settings.py")
    
    if not settings_file.exists():
        print(f"[警告] 找不到檔案: {settings_file}")
        return False
    
    content = settings_file.read_text(encoding='utf-8')
    
    # 檢查是否已有正確的靜態檔案配置
    if 'STATICFILES_DIRS' in content and 'BASE_DIR / \'static\'' in content:
        print("[設定] 靜態檔案配置已存在")
        return True
    
    # 如果沒有，提醒用戶檢查
    print("[提醒] 請確認 settings.py 中有以下配置:")
    print("STATICFILES_DIRS = [")
    print("    BASE_DIR / 'static',")
    print("]")
    return True

def create_collectstatic_script():
    """建立收集靜態檔案的腳本"""
    script_content = """@echo off
chcp 65001 >nul
echo [收集] 開始收集靜態檔案...
python manage.py collectstatic --noinput

echo [完成] 靜態檔案收集完成!
echo [提示] 請重新啟動開發伺服器:
echo    python manage.py runserver
pause
"""
    
    # Windows 批次檔
    script_file = Path("collect_static.bat")
    script_file.write_text(script_content, encoding='utf-8')
    
    print(f"[腳本] 已建立腳本: {script_file}")
    return script_file

def main():
    """主要執行函數"""
    print("客戶表單布局升級腳本")
    print("=" * 50)
    
    try:
        # 檢查是否在 Django 專案根目錄
        if not Path("manage.py").exists():
            print("[錯誤] 請在 Django 專案根目錄執行此腳本")
            return False
        
        print("步驟 1: 建立自定義 CSS 檔案...")
        create_css_file()
        
        print("\n步驟 2: 更新 customers/admin.py...")
        update_admin_py()
        
        print("\n步驟 3: 檢查 settings.py 配置...")
        update_settings_py()
        
        print("\n步驟 4: 建立靜態檔案收集腳本...")
        create_collectstatic_script()
        
        print("\n" + "=" * 50)
        print("[完成] 升級完成!")
        print("\n後續步驟:")
        print("1. 執行: python manage.py collectstatic")
        print("2. 重新啟動伺服器: python manage.py runserver")
        print("3. 訪問客戶管理頁面查看效果")
        print("4. 如有問題，可以使用 .backup 檔案還原")
        
        return True
        
    except Exception as e:
        print(f"[錯誤] 執行過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
    input("\n按 Enter 鍵結束...")  # 防止視窗關閉