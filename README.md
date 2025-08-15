# N8幣客戶管理系統

## 功能特點
- 客戶資料管理
- 交易記錄追踪
- KYC文件上傳
- 用戶權限管理
- 報表生成

## 安裝步驟

1. 創建虛擬環境：
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. 安裝依賴：
```bash
pip install -r requirements.txt
```

3. 數據庫遷移：
```bash
python manage.py makemigrations
python manage.py migrate
```

4. 創建超級用戶：
```bash
python manage.py createsuperuser
```

5. 運行服務器：
```bash
python manage.py runserver
```

## 部署到Render

1. 創建GitHub儲存庫
2. 在Render創建Web Service
3. 設置環境變數
4. 自動部署

## 系統角色

- **Admin（管理員）**：所有權限
- **CS（客服）**：客戶和交易管理權限
