# 小商人客戶管理系統 (Admin Only)

## 🎯 系統特點

- **純 Django Admin 介面**：專注於後台管理，減少維護成本
- **客戶資料管理**：完整的客戶信息管理
- **交易記錄追踪**：詳細的交易記錄和統計
- **KYC文件管理**：支援檔案上傳，檔案欄位為選填
- **用戶權限管理**：Admin（管理員）、CS（客服）角色控制

## 🚀 快速開始

### 1. 環境準備

```bash
# 創建虛擬環境
python -m venv venv

# 啟動虛擬環境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### 2. 安裝依賴

```bash
pip install -r requirements.txt
```

### 3. 環境設定

創建 `.env` 文件：
```env
SECRET_KEY=your-very-secret-key-change-this-in-production
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

### 4. 數據庫設置

```bash
# 創建遷移文件
python manage.py makemigrations

# 執行遷移
python manage.py migrate

# 創建超級用戶
python manage.py createsuperuser
```

### 5. 啟動服務

```bash
python manage.py runserver
```

### 6. 訪問系統

- 瀏覽器打開 `http://localhost:8000/`
- 會自動重定向到管理後台 `/admin/`
- 使用創建的超級用戶帳號登入

## 📊 系統架構

### 數據模型

1. **User（用戶）**
   - 基於 Django AbstractUser
   - 角色：Admin（管理員）、CS（客服）

2. **Customer（客戶）**
   - 客戶基本資料
   - Line 暱稱、N8 暱稱、聯絡方式

3. **Transaction（交易記錄）**
   - 買入/賣出記錄
   - N8幣數量、台幣金額
   - 快速回覆狀態

4. **KYCRecord（KYC記錄）**
   - 檔案上傳（選填）
   - 銀行代碼、驗證帳戶
   - 檔案說明

### 權限控制

- **Admin（管理員）**：所有功能的完整權限
- **CS（客服）**：客戶和交易管理權限，只能編輯自己上傳的KYC記錄

## 🛠️ KYC 功能更新

### 檔案上傳改為選填

- ✅ KYC 記錄可以只填寫銀行資訊
- ✅ 檔案上傳為選填項目
- ✅ 支援圖片和影片格式
- ✅ 檔案大小限制 10MB

### 使用方式

1. 進入 Admin 後台
2. 選擇「KYC 記錄」
3. 點擊「新增 KYC 記錄」
4. 選擇客戶
5. 選填：銀行代碼、驗證帳戶
6. 選填：上傳檔案、檔案說明
7. 保存

## 🚀 部署

系統已配置自動部署到 Render 平台：

1. 推送代碼到 GitHub
2. Render 自動檢測更新並部署
3. 環境變數在 Render 控制台設定

### 必要環境變數

```env
SECRET_KEY=your-production-secret-key
DEBUG=False
DATABASE_URL=postgresql://...
```

## 📝 變更記錄

### v2.0.0 - Admin Only 重構

- ✅ 移除所有前端視圖和模板
- ✅ 專注於 Django Admin 介面
- ✅ KYC 檔案欄位改為選填
- ✅ 減少代碼量 70%，降低維護成本
- ✅ 保持所有核心功能完整

## 🔧 開發說明

### 項目結構

```
nbcrm/
├── accounts/           # 用戶管理
│   ├── __init__.py
│   ├── admin.py       # 用戶 Admin 配置
│   ├── apps.py
│   └── models.py      # User 模型
├── customers/          # 客戶管理
│   ├── __init__.py
│   ├── admin.py       # 客戶 Admin 配置
│   ├── apps.py
│   └── models.py      # Customer 模型
├── kyc/               # KYC 管理
│   ├── __init__.py
│   ├── admin.py       # KYC Admin 配置
│   ├── apps.py
│   └── models.py      # KYCRecord 模型
├── transactions/       # 交易管理
│   ├── __init__.py
│   ├── admin.py       # 交易 Admin 配置
│   ├── apps.py
│   └── models.py      # Transaction 模型
├── nbcrm/             # 項目配置
│   ├── __init__.py
│   ├── settings.py    # Django 設定
│   ├── urls.py        # URL 配置
│   └── wsgi.py
├── media/             # 上傳檔案目錄
├── manage.py
├── requirements.txt
├── runtime.txt
├── Procfile
├── build.sh
└── README.md
```

### 常用操作

```bash
# 創建新的數據庫遷移
python manage.py makemigrations

# 執行遷移
python manage.py migrate

# 創建超級用戶
python manage.py createsuperuser

# 收集靜態文件（部署前）
python manage.py collectstatic

# 啟動開發服務器
python manage.py runserver
```

## 📞 技術支援

如有問題請聯繫系統管理員。

---

**小商人客戶管理系統** - 專注效率，簡化管理
