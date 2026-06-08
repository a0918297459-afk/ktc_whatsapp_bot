# WhatsApp Business API 設定指南

本指南將逐步引導你設定 WhatsApp Business API，以便機器人能夠接收和發送訊息。

## 目錄
1. [建立 Meta Developer 帳戶](#建立-meta-developer-帳戶)
2. [建立應用](#建立應用)
3. [設定 WhatsApp 商業帳戶](#設定-whatsapp-商業帳戶)
4. [取得 API 金鑰](#取得-api-金鑰)
5. [設定 Webhook](#設定-webhook)
6. [測試連線](#測試連線)

---

## 建立 Meta Developer 帳戶

### 步驟 1: 訪問 Meta Developer

1. 進入 [developers.facebook.com](https://developers.facebook.com)
2. 點擊右上角「Get Started」
3. 使用 Facebook 帳戶登入或建立新帳戶

### 步驟 2: 完成帳戶驗證

1. 驗證你的電郵地址
2. 填寫基本信息
3. 同意開發者協議

---

## 建立應用

### 步驟 1: 建立新應用

1. 進入 [My Apps](https://developers.facebook.com/apps)
2. 點擊「Create App」
3. 選擇「Business」作為應用類型
4. 填入應用名稱，例如：`KTC WhatsApp Audit Bot`
5. 點擊「Create App」

### 步驟 2: 添加 WhatsApp 產品

1. 在應用儀表板中，點擊「Add Product」
2. 搜尋「WhatsApp」
3. 點擊「Set Up」

### 步驟 3: 選擇商業帳戶

1. 如果你已有 WhatsApp Business Account，選擇它
2. 如果沒有，點擊「Create New Business Account」
3. 填入必要信息

---

## 設定 WhatsApp 商業帳戶

### 步驟 1: 驗證電話號碼

1. 進入 WhatsApp 設定頁面
2. 在「Phone Number」部分，點擊「Add Phone Number」
3. 選擇你的國家（台灣）
4. 輸入你的電話號碼（例如：886917823381）
5. 選擇驗證方式（自動呼叫或 SMS）
6. 輸入驗證碼

### 步驟 2: 設定商業帳戶信息

1. 填入商業名稱：`KTC 凱旋交易社`
2. 填入商業描述
3. 上傳商業頭像（可選）

### 步驟 3: 添加管理員

1. 進入「Team」部分
2. 添加其他管理員（可選）

---

## 取得 API 金鑰

### 步驟 1: 取得 Access Token

1. 進入應用設定 → WhatsApp
2. 在「API Setup」部分，找到「Access Token」
3. 點擊「Generate Token」
4. 複製 Token（**保密！不要分享**）
5. 將其粘貼到 `.env` 檔案的 `WHATSAPP_ACCESS_TOKEN`

### 步驟 2: 取得 Phone Number ID

1. 在同一頁面，找到「Phone Number ID」
2. 複製 ID
3. 將其粘貼到 `.env` 檔案的 `WHATSAPP_PHONE_NUMBER_ID`

### 步驟 3: 取得 Business Account ID

1. 進入應用設定 → WhatsApp
2. 在「Business Account」部分，找到 Account ID
3. 複製 ID
4. 將其粘貼到 `.env` 檔案的 `WHATSAPP_BUSINESS_ACCOUNT_ID`

---

## 設定 Webhook

### 步驟 1: 部署應用

首先，確保你的應用已部署到 Render（或其他雲端平台）。

你的 Webhook URL 應該是：
```
https://ktc-whatsapp-bot.onrender.com/webhook
```

### 步驟 2: 在 Meta Developer 中設定 Webhook

1. 進入應用設定 → WhatsApp
2. 在「Webhook」部分，點擊「Edit」
3. 填入以下信息：
   - **Callback URL**: `https://ktc-whatsapp-bot.onrender.com/webhook`
   - **Verify Token**: `ktc_audit_bot_2024`（或你在 `.env` 中設定的值）
4. 點擊「Verify and Save」

Meta 會向你的 Webhook URL 發送驗證請求。如果設定正確，應該會看到「Webhook verified」的訊息。

### 步驟 3: 訂閱 Webhook 事件

1. 在「Webhook」設定中，找到「Webhook Fields」
2. 訂閱以下事件：
   - `messages` - 接收訊息
   - `message_template_status_update` - 範本狀態更新
   - `message_status_update` - 訊息狀態更新

### 步驟 4: 測試 Webhook

```bash
# 使用 curl 測試
curl "https://ktc-whatsapp-bot.onrender.com/webhook?hub.mode=subscribe&hub.verify_token=ktc_audit_bot_2024&hub.challenge=test_challenge"

# 應該返回: test_challenge
```

---

## 測試連線

### 步驟 1: 使用 Meta 的測試工具

1. 進入應用設定 → WhatsApp
2. 在「API Setup」部分，找到「Send Message」
3. 選擇你的電話號碼
4. 輸入收件人電話號碼
5. 點擊「Send Message」

### 步驟 2: 在審核區群組中測試

1. 加入你的「新人審核區」WhatsApp 群組
2. 發送一條訊息，例如：`UID: 12345678`
3. 機器人應該會在幾秒內回覆

### 步驟 3: 查看日誌

檢查應用日誌以確保訊息被正確接收和處理：

```bash
# 在 Render 中查看日誌
# 進入應用 → Logs 標籤
```

---

## 常見問題

### Q: Webhook 驗證失敗

**A:** 檢查以下項目：
- Callback URL 是否正確
- Verify Token 是否匹配
- 應用是否已部署且可公開訪問
- 防火牆是否允許 Meta 的 IP 地址

### Q: 無法發送訊息

**A:** 檢查以下項目：
- Access Token 是否正確
- Phone Number ID 是否正確
- 收件人電話號碼格式是否正確（應包含國家代碼）
- API 配額是否已超出

### Q: 訊息發送但未收到

**A:** 可能原因：
- 電話號碼未驗證
- 商業帳戶未激活
- 訊息內容違反 WhatsApp 政策

---

## 安全建議

1. **保護 Access Token**
   - 不要在程式碼中硬編碼 Token
   - 不要在 GitHub 上提交 Token
   - 定期更新 Token

2. **監控 API 使用**
   - 定期檢查 API 使用量
   - 設定使用警告

3. **備份配置**
   - 保存 API 金鑰的備份（安全位置）
   - 記錄所有設定

---

## 下一步

1. 完成 Webhook 設定後，回到 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
2. 部署應用到 Render
3. 在審核區群組中測試機器人

---

## 聯繫支持

如有問題，請聯繫：
- **Meta 支持**: [developers.facebook.com/support](https://developers.facebook.com/support)
- **小幫手**: +886 912 255 937

---

**最後更新**: 2024 年 1 月
