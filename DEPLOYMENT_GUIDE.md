# KTC 凱旋交易社 - WhatsApp 審核機器人部署指南

## 目錄
1. [系統需求](#系統需求)
2. [本地開發環境設定](#本地開發環境設定)
3. [配置環境變數](#配置環境變數)
4. [本地測試](#本地測試)
5. [部署到 Render](#部署到-render)
6. [WhatsApp Webhook 設定](#whatsapp-webhook-設定)
7. [故障排除](#故障排除)

---

## 系統需求

- Python 3.8 或更高版本
- Git（用於版本控制和部署）
- GitHub 帳戶（用於部署）
- WhatsApp Business Account
- Meta Developer Account

---

## 本地開發環境設定

### 步驟 1: 克隆或下載專案

```bash
# 如果使用 Git
git clone <your-repo-url> ktc_whatsapp_bot
cd ktc_whatsapp_bot

# 或直接下載並解壓縮
cd ktc_whatsapp_bot
```

### 步驟 2: 建立虛擬環境

```bash
# 在 macOS/Linux
python3 -m venv venv
source venv/bin/activate

# 在 Windows
python -m venv venv
venv\Scripts\activate
```

### 步驟 3: 安裝依賴

```bash
pip install -r requirements.txt
```

---

## 配置環境變數

### 步驟 1: 複製環境變數範本

```bash
cp .env.example .env
```

### 步驟 2: 編輯 `.env` 檔案

使用文本編輯器打開 `.env` 檔案，填入以下信息：

#### Bitunix API 設定
```
BITUNIX_API_KEY=rmnyJHEiRTRMVUWkyCORwqBDwKCkFlixZRMttrmKjPfOMFHUEQIVmAZVaDhMPrBU
BITUNIX_API_SECRET=SmedJkpWDNnwalqfzrozJNnWsrFpxvsGXXHTfFCsUJBFduHixEDpYDwqLeCPGRTz
```

#### Google Sheets 設定
```
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/1Glo7fq0q2NjTd2_9ik6TZjX_tvxQbg6KGVNytmU6weE/edit?usp=drivesdk
```

#### WhatsApp 設定
```
WHATSAPP_PHONE_NUMBER_ID=886917823381
WHATSAPP_ACCESS_TOKEN=<從 Meta Developer 取得>
WHATSAPP_BUSINESS_ACCOUNT_ID=<你的商業帳戶 ID>
WHATSAPP_VERIFY_TOKEN=ktc_audit_bot_2024
```

#### 群組與聯繫信息
```
DISCUSSION_GROUP_LINK=https://chat.whatsapp.com/FDb7BvDd0nX90qpQ35ojo2?mode=gi_t
HELPER_PHONE=+886 912 255 937
```

---

## 本地測試

### 運行測試腳本

```bash
python test_local.py
```

這個腳本會測試：
- ✓ 環境變數是否正確設定
- ✓ UID 提取功能
- ✓ Google Sheets 連線
- ✓ Bitunix API 連線

### 測試 Flask 應用

```bash
# 啟動本地開發伺服器
python -m src.app

# 應該看到類似的輸出:
# WARNING in app.run()
#  * Running on http://127.0.0.1:5000
```

### 測試 API 端點

在另一個終端中運行：

```bash
# 健康檢查
curl http://localhost:5000/health

# 測試 Bitunix 驗證
curl -X POST http://localhost:5000/test-bitunix \
  -H "Content-Type: application/json" \
  -d '{"uid": "12345678"}'

# 測試 Google Sheets
curl http://localhost:5000/test-sheets

# 測試審核流程
curl -X POST http://localhost:5000/test-audit \
  -H "Content-Type: application/json" \
  -d '{"uid": "12345678", "phone": "886912345678"}'
```

---

## 部署到 Render

### 步驟 1: 上傳到 GitHub

```bash
# 初始化 Git 倉庫（如果還沒有）
git init
git add .
git commit -m "Initial commit: WhatsApp audit bot"

# 推送到 GitHub
git remote add origin https://github.com/your-username/ktc_whatsapp_bot.git
git branch -M main
git push -u origin main
```

### 步驟 2: 在 Render 上建立新服務

1. 訪問 [render.com](https://render.com)
2. 登入或註冊帳戶
3. 點擊「New +」→「Web Service」
4. 選擇「Connect a repository」
5. 授權 GitHub 並選擇 `ktc_whatsapp_bot` 倉庫
6. 填入以下設定：
   - **Name**: `ktc-whatsapp-bot`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT src.app:app`
   - **Plan**: 選擇「Free」或「Starter」

### 步驟 3: 設定環境變數

在 Render 控制面板中：
1. 進入你的服務
2. 點擊「Environment」
3. 添加所有在 `.env` 中的環境變數

**重要**: 不要在 GitHub 上提交 `.env` 檔案！

### 步驟 4: 部署

1. 點擊「Deploy」
2. 等待部署完成（通常需要 2-5 分鐘）
3. 你會獲得一個公開 URL，例如: `https://ktc-whatsapp-bot.onrender.com`

### 驗證部署

```bash
# 測試健康檢查
curl https://ktc-whatsapp-bot.onrender.com/health

# 應該返回:
# {"status":"healthy","timestamp":"2024-01-15T10:30:45.123456","service":"KTC WhatsApp Audit Bot"}
```

---

## WhatsApp Webhook 設定

### 步驟 1: 取得 Webhook URL

你的 Webhook URL 應該是：
```
https://ktc-whatsapp-bot.onrender.com/webhook
```

### 步驟 2: 在 Meta Developer 中設定

1. 訪問 [developers.facebook.com](https://developers.facebook.com)
2. 進入你的應用
3. 選擇「WhatsApp」→「Configuration」
4. 在「Webhook URL」中填入上面的 URL
5. 在「Verify Token」中填入: `ktc_audit_bot_2024`（或你在 `.env` 中設定的值）
6. 點擊「Verify and Save」

### 步驟 3: 訂閱 Webhook 事件

在 Meta Developer 中：
1. 進入「Webhooks」設定
2. 訂閱以下事件：
   - `messages`
   - `message_template_status_update`
   - `message_status_update`

### 步驟 4: 測試 Webhook

```bash
# 使用 curl 測試 Webhook 驗證
curl "https://ktc-whatsapp-bot.onrender.com/webhook?hub.mode=subscribe&hub.verify_token=ktc_audit_bot_2024&hub.challenge=test_challenge"

# 應該返回: test_challenge
```

---

## 故障排除

### 問題 1: 機器人無法接收訊息

**可能原因:**
- Webhook URL 設定錯誤
- Verify Token 不匹配
- WhatsApp Business Account 未正確連接

**解決方案:**
1. 檢查 Render 應用日誌: `https://dashboard.render.com/web/your-service-id/logs`
2. 確認 Webhook URL 和 Verify Token 在 Meta Developer 中正確設定
3. 確認 WhatsApp 商業帳戶已連接到你的應用

### 問題 2: Bitunix API 驗證失敗

**可能原因:**
- API Key 或 Secret 不正確
- 時間戳超過 30 秒的偏差
- 網絡連接問題

**解決方案:**
1. 驗證 API Key 和 Secret 是否正確
2. 確認伺服器時間同步
3. 檢查網絡連接

### 問題 3: Google Sheets 無法讀取

**可能原因:**
- 試算表 URL 不正確
- 試算表權限設定不正確
- 試算表不是公開的

**解決方案:**
1. 確認試算表 URL 正確
2. 確認試算表權限設定為「知道連結的人皆可檢視」
3. 測試 URL 是否可以在瀏覽器中打開

### 問題 4: 應用頻繁崩潰

**可能原因:**
- 記憶體不足
- 依賴版本衝突
- 未捕獲的異常

**解決方案:**
1. 檢查 Render 日誌查看具體錯誤
2. 更新依賴: `pip install --upgrade -r requirements.txt`
3. 增加 Render 計劃等級

---

## 監控和維護

### 查看日誌

```bash
# 在 Render 中查看實時日誌
# 進入你的服務 → Logs 標籤

# 或使用 curl 查看應用日誌
curl https://ktc-whatsapp-bot.onrender.com/health
```

### 定期檢查

- 每週檢查一次審核日誌
- 監控 API 使用量
- 確認沒有頻繁的錯誤

### 更新應用

```bash
# 在本地進行更改
git add .
git commit -m "Update: description of changes"
git push origin main

# Render 會自動部署最新版本
```

---

## 聯繫支持

如有問題，請聯繫小幫手：**+886 912 255 937**

---

**最後更新**: 2024 年 1 月
**版本**: 1.0.0
