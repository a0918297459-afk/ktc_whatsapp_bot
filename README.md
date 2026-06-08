# KTC 凱旋交易社 - WhatsApp 入群審核機器人

一個自動化的 WhatsApp 社群入群審核系統，整合 Google 表單驗證、Bitunix UID 核實，並自動管理新人從審核區進入主討論區的流程。

## 功能特性

✨ **自動化審核流程**
- 自動提取 WhatsApp 訊息中的 Bitunix UID
- 驗證 UID 是否在 Google 表單中填寫
- 核實 UID 是否為有效的 Bitunix 帳戶
- 確認用戶是否透過推薦連結註冊

🔒 **安全可靠**
- 使用官方 Meta WhatsApp Cloud API
- SHA1 加密簽名驗證
- 環境變數管理敏感信息
- 完整的日誌記錄

📊 **易於監控**
- 實時日誌記錄
- 審核結果追蹤
- 健康檢查端點
- 詳細的錯誤信息

🚀 **快速部署**
- 一鍵部署到 Render
- 支持本地開發測試
- 完整的部署指南
- 自動化測試腳本

---

## 快速開始

### 前置要求

- Python 3.8+
- WhatsApp Business Account
- Meta Developer Account
- Google Sheets（用於表單回應）
- Bitunix API Key 和 Secret

### 安裝

```bash
# 1. 克隆或下載專案
git clone <repo-url>
cd ktc_whatsapp_bot

# 2. 建立虛擬環境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate     # Windows

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 配置環境變數
cp .env.example .env
# 編輯 .env 檔案，填入你的 API 金鑰和設定
```

### 本地測試

```bash
# 運行測試腳本
python test_local.py

# 啟動本地開發伺服器
python -m src.app

# 在另一個終端測試 API
curl http://localhost:5000/health
```

### 部署

詳見 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

---

## 系統架構

```
┌─────────────────────────────────────────────────────────────┐
│                     WhatsApp 新人審核區                      │
│                                                               │
│  新人輸入: "UID: 12345678"                                   │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │   Webhook 接收訊息         │
        │   (Flask /webhook POST)    │
        └────────────┬───────────────┘
                     │
                     ▼
        ┌────────────────────────────┐
        │   提取 UID                 │
        │   (正則表達式)             │
        └────────────┬───────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
    ┌─────────────┐          ┌──────────────────┐
    │ Google      │          │ Bitunix API      │
    │ Sheets      │          │ 驗證 UID         │
    │ 檢查 UID    │          │                  │
    └────┬────────┘          └────┬─────────────┘
         │                        │
         └────────┬───────────────┘
                  │
        ┌─────────▼──────────┐
        │  審核邏輯          │
        │  (bot_logic.py)    │
        └─────────┬──────────┘
                  │
        ┌─────────┴──────────┐
        │                    │
        ▼                    ▼
    ✅ 通過              ❌ 未通過
    │                    │
    ▼                    ▼
發送邀請連結          發送失敗原因
到主討論區            + 小幫手聯繫方式
```

---

## 檔案結構

```
ktc_whatsapp_bot/
├── src/
│   ├── __init__.py                 # 套件初始化
│   ├── app.py                      # Flask 主應用
│   ├── bot_logic.py                # 審核邏輯
│   ├── bitunix_client.py           # Bitunix API 客戶端
│   ├── google_sheets_client.py     # Google Sheets 客戶端
│   └── whatsapp_client.py          # WhatsApp API 客戶端
├── config/                         # 配置檔案目錄
├── logs/                           # 日誌檔案目錄
├── .env.example                    # 環境變數範本
├── .env                            # 環境變數（不提交到 Git）
├── requirements.txt                # Python 依賴
├── Procfile                        # Render 部署配置
├── render.yaml                     # Render 詳細配置
├── test_local.py                   # 本地測試腳本
├── README.md                       # 本檔案
└── DEPLOYMENT_GUIDE.md             # 部署指南
```

---

## 環境變數

詳見 `.env.example`。主要變數包括：

| 變數名 | 說明 | 範例 |
|--------|------|------|
| `BITUNIX_API_KEY` | Bitunix API Key | `rmnyJHEiRT...` |
| `BITUNIX_API_SECRET` | Bitunix API Secret | `SmedJkpWDN...` |
| `GOOGLE_SHEETS_URL` | Google Sheets 試算表 URL | `https://docs.google.com/...` |
| `WHATSAPP_PHONE_NUMBER_ID` | WhatsApp 電話號碼 ID | `886917823381` |
| `WHATSAPP_ACCESS_TOKEN` | Meta API 存取令牌 | `EAABs...` |
| `WHATSAPP_BUSINESS_ACCOUNT_ID` | WhatsApp 商業帳戶 ID | `123456789` |
| `DISCUSSION_GROUP_LINK` | 主討論區邀請連結 | `https://chat.whatsapp.com/...` |
| `HELPER_PHONE` | 小幫手電話號碼 | `+886 912 255 937` |

---

## API 端點

### 健康檢查
```
GET /health
```
返回應用狀態。

### Webhook 驗證
```
GET /webhook?hub.mode=subscribe&hub.verify_token=...&hub.challenge=...
```
WhatsApp 驗證 Webhook 時使用。

### Webhook 接收
```
POST /webhook
```
接收 WhatsApp 訊息。

### 測試審核
```
POST /test-audit
Content-Type: application/json

{
  "uid": "12345678",
  "phone": "886912345678"
}
```
測試審核流程。

### 測試 Google Sheets
```
GET /test-sheets
```
測試 Google Sheets 連線。

### 測試 Bitunix API
```
POST /test-bitunix
Content-Type: application/json

{
  "uid": "12345678"
}
```
測試 Bitunix API 連線。

---

## 審核流程

### 通過審核

1. 新人在審核區輸入: `UID: 12345678`
2. 機器人驗證：
   - ✓ UID 在 Google 表單中存在
   - ✓ UID 是有效的 Bitunix 帳戶
   - ✓ UID 透過推薦連結註冊
3. 機器人回覆：
   ```
   ✅ 恭喜！審核通過
   
   歡迎加入 KTC 凱旋交易社！
   
   點擊下方連結進入主討論區：
   https://chat.whatsapp.com/...
   ```

### 未通過審核

機器人會根據失敗原因回覆不同的信息，並提示用戶聯繫小幫手。

---

## 日誌

應用日誌保存在 `logs/bot.log`。包含：
- 接收的訊息
- API 呼叫
- 審核結果
- 錯誤信息

---

## 故障排除

### 機器人無法接收訊息

1. 檢查 Webhook URL 是否正確設定在 Meta Developer
2. 確認 Verify Token 匹配
3. 查看應用日誌查找具體錯誤

### Bitunix API 驗證失敗

1. 確認 API Key 和 Secret 正確
2. 檢查伺服器時間同步
3. 確認 UID 是有效的 Bitunix 帳戶

### Google Sheets 無法讀取

1. 確認試算表 URL 正確
2. 確認試算表權限設定為公開
3. 檢查試算表是否有資料

詳見 [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md#故障排除)

---

## 技術棧

- **後端框架**: Flask
- **Web 伺服器**: Gunicorn
- **API 整合**: requests
- **Google Sheets**: gspread
- **部署平台**: Render
- **版本控制**: Git

---

## 安全考量

- ✅ 所有 API 金鑰存儲在環境變數中
- ✅ 使用 SHA1 加密簽名驗證 Bitunix API 請求
- ✅ 完整的日誌記錄用於審計
- ✅ 錯誤信息不洩露敏感信息
- ✅ 支持 HTTPS（Render 自動提供）

---

## 許可證

MIT License

---

## 聯繫方式

如有問題或建議，請聯繫小幫手：**+886 912 255 937**

---

**版本**: 1.0.0  
**最後更新**: 2024 年 1 月  
**作者**: KTC Bot Team
