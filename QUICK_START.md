# 快速開始指南 - 5 分鐘上手

這份指南將幫助你在 5 分鐘內完成基本設定。

## 前置檢查清單

在開始前，請確保你已準備好以下信息：

- [ ] Bitunix API Key 和 Secret
- [ ] Google Sheets 試算表 URL（已設定為公開）
- [ ] WhatsApp 商業帳戶電話號碼
- [ ] Meta API Access Token
- [ ] GitHub 帳戶（用於部署）
- [ ] Render 帳戶（免費）

---

## 第 1 步: 本地設定（3 分鐘）

### 1.1 複製環境變數範本

```bash
cd ktc_whatsapp_bot
cp .env.example .env
```

### 1.2 編輯 `.env` 檔案

打開 `.env` 檔案，填入以下信息：

```env
# Bitunix
BITUNIX_API_KEY=rmnyJHEiRTRMVUWkyCORwqBDwKCkFlixZRMttrmKjPfOMFHUEQIVmAZVaDhMPrBU
BITUNIX_API_SECRET=SmedJkpWDNnwalqfzrozJNnWsrFpxvsGXXHTfFCsUJBFduHixEDpYDwqLeCPGRTz

# Google Sheets
GOOGLE_SHEETS_URL=https://docs.google.com/spreadsheets/d/1Glo7fq0q2NjTd2_9ik6TZjX_tvxQbg6KGVNytmU6weE/edit?usp=drivesdk

# WhatsApp（這些稍後從 Meta Developer 取得）
WHATSAPP_PHONE_NUMBER_ID=886917823381
WHATSAPP_ACCESS_TOKEN=<稍後填入>
WHATSAPP_BUSINESS_ACCOUNT_ID=<稍後填入>

# 群組連結
DISCUSSION_GROUP_LINK=https://chat.whatsapp.com/FDb7BvDd0nX90qpQ35ojo2?mode=gi_t
HELPER_PHONE=+886 912 255 937
```

---

## 第 2 步: 部署到 Render（2 分鐘）

### 2.1 上傳到 GitHub

```bash
# 初始化 Git（如果還沒有）
git init
git add .
git commit -m "Initial commit"

# 建立 GitHub 倉庫並推送
# 進入 https://github.com/new 建立新倉庫
# 然後執行:
git remote add origin https://github.com/your-username/ktc_whatsapp_bot.git
git branch -M main
git push -u origin main
```

### 2.2 在 Render 上部署

1. 進入 [render.com](https://render.com)
2. 點擊「New +」→「Web Service」
3. 連接你的 GitHub 倉庫
4. 填入以下設定：
   - **Name**: `ktc-whatsapp-bot`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn -w 4 -b 0.0.0.0:$PORT src.app:app`

### 2.3 添加環境變數

在 Render 中：
1. 進入你的服務 → Environment
2. 添加所有 `.env` 中的變數

部署會自動開始，等待 2-5 分鐘完成。

---

## 第 3 步: WhatsApp Webhook 設定

部署完成後，你會獲得一個 URL，例如：
```
https://ktc-whatsapp-bot.onrender.com
```

### 3.1 在 Meta Developer 中設定 Webhook

1. 進入 [developers.facebook.com](https://developers.facebook.com)
2. 選擇你的應用 → WhatsApp
3. 在「Webhook」部分：
   - **Callback URL**: `https://ktc-whatsapp-bot.onrender.com/webhook`
   - **Verify Token**: `ktc_audit_bot_2024`
4. 點擊「Verify and Save」

### 3.2 訂閱事件

在「Webhook」設定中，訂閱：
- `messages`
- `message_template_status_update`
- `message_status_update`

---

## 第 4 步: 測試機器人

### 4.1 健康檢查

```bash
curl https://ktc-whatsapp-bot.onrender.com/health
```

應該返回：
```json
{"status":"healthy","timestamp":"...","service":"KTC WhatsApp Audit Bot"}
```

### 4.2 在審核區群組中測試

1. 加入「新人審核區」WhatsApp 群組
2. 發送訊息：`UID: 12345678`
3. 機器人應該在幾秒內回覆

---

## 完成！🎉

你的 WhatsApp 審核機器人現在已上線！

### 接下來可以做什麼

- 📖 閱讀 [README.md](./README.md) 了解更多功能
- 🔧 查看 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) 了解詳細設定
- 🐛 如有問題，查看 [故障排除](./DEPLOYMENT_GUIDE.md#故障排除)

---

## 常見問題

### Q: 機器人無法接收訊息

**A:** 檢查以下項目：
1. Webhook URL 是否正確設定
2. Verify Token 是否匹配
3. 查看 Render 日誌查找錯誤

### Q: 審核總是失敗

**A:** 可能原因：
1. UID 不在 Google 試算表中
2. UID 未透過推薦連結註冊
3. Bitunix API 連線有問題

### Q: 如何查看日誌

**A:** 在 Render 中：
1. 進入你的服務
2. 點擊「Logs」標籤
3. 查看實時日誌

---

## 需要幫助？

- 📞 聯繫小幫手：+886 912 255 937
- 📧 查看詳細文件：[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- 🔗 WhatsApp 設定：[WHATSAPP_SETUP.md](./WHATSAPP_SETUP.md)

---

**預計時間**: 5 分鐘  
**難度**: ⭐ 簡單
