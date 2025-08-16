# 🔒 Render Disk 設置指南

## 🎯 為什麼選擇 Render Disk

對於 KYC 等高度隱私敏感資料，Render Disk 提供：
- ✅ **數據主權**：資料完全在你控制範圍內
- ✅ **隱私保護**：不經過第三方雲服務
- ✅ **持久化存儲**：重新部署後文件不消失
- ✅ **高安全性**：只有登入用戶可訪問媒體文件

## 📋 設置步驟

### 1. 在 Render Dashboard 創建 Disk

1. **登入 Render Dashboard**
   - 前往 https://dashboard.render.com/
   - 選擇你的 Web Service

2. **添加 Disk**
   - 點擊左側 "Disks" 標籤
   - 點擊 "Add Disk"
   - 填寫設定：
     ```
     Name: media-storage
     Mount Path: /opt/render/project/media
     Size: 20GB (根據需求調整)
     ```
   - 點擊 "Create Disk"

3. **等待 Disk 創建完成**
   - 通常需要 2-5 分鐘
   - 狀態變為 "Available" 即可

### 2. 重新部署應用

創建 Disk 後需要重新部署：
- Render 會自動觸發重新部署
- 或手動點擊 "Deploy Latest Commit"

### 3. 驗證設置

部署完成後：
1. **上傳測試文件**
   - 登入 Admin 後台
   - 新增一個 KYC 記錄並上傳文件

2. **檢查文件路徑**
   - 文件應該存儲在 `/opt/render/project/media/` 下
   - URL 格式：`https://your-app.onrender.com/media/kyc/1/filename.jpg`

3. **測試持久性**
   - 觸發重新部署
   - 確認文件仍然存在且可訪問

## 💰 費用說明

Render Disk 定價（美金/月）：
- **20GB**: $7/月
- **50GB**: $15/月  
- **100GB**: $25/月

對於中小型 KYC 系統，20GB 通常足夠使用。

## 🔒 安全特性

### 已實施的安全措施

1. **登入驗證**：只有登入用戶可訪問媒體文件
2. **路徑檢查**：防止目錄遍歷攻擊
3. **訪問日誌**：記錄所有媒體文件訪問
4. **安全標頭**：防止快取和嵌入
5. **HTTPS 強制**：生產環境強制使用 HTTPS

### 訪問日誌範例
```
INFO 用戶 admin 訪問媒體文件: kyc/1/身分證.jpg
WARNING 用戶 cs001 嘗試訪問不安全路徑: ../../../etc/passwd
```

## 🔧 故障排除

### 問題：文件上傳後找不到
**解決方案**：
1. 檢查 Disk 是否正確掛載到 `/opt/render/project/media`
2. 檢查服務日誌是否有錯誤
3. 確認文件權限正確

### 問題：重新部署後文件消失
**解決方案**：
1. 確認 Disk 狀態為 "Available"
2. 檢查 Mount Path 是否正確
3. 聯繫 Render 支援檢查 Disk 健康狀態

### 問題：無法訪問媒體文件
**解決方案**：
1. 確認已登入 Admin 後台
2. 檢查文件路徑是否正確
3. 查看服務日誌中的錯誤訊息

## 📊 監控建議

### 定期檢查項目
- **存儲空間使用量**：避免超出 Disk 容量
- **訪問日誌**：監控異常訪問行為
- **文件完整性**：定期檢查重要文件是否存在

### 備份建議
- **重要文件**：定期下載重要 KYC 文件到本地備份
- **資料庫**：確保資料庫定期備份（文件路徑資訊）

## 🎉 完成！

設置完成後，你的 KYC 文件將：
- ✅ 安全存儲在 Render Disk 中
- ✅ 重新部署後仍然存在
- ✅ 只有授權用戶可以訪問
- ✅ 所有訪問都有日誌記錄
