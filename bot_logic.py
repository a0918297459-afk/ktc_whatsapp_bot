"""
WhatsApp 審核機器人核心邏輯
"""

import re
import logging
from datetime import datetime
from typing import Optional, Tuple, Dict
from src.bitunix_client import BitunixClient
from src.google_sheets_client import GoogleSheetsClient
from src.whatsapp_client import WhatsAppClient

logger = logging.getLogger(__name__)


class AuditBot:
    \"\"\"審核機器人核心邏輯\"\"\"
    
    def __init__(
        self,
        bitunix_client: BitunixClient,
        sheets_client: GoogleSheetsClient,
        whatsapp_client: WhatsAppClient,
        discussion_group_link: str,
        helper_phone: str
    ):
        \"\"\"
        初始化審核機器人
        
        Args:
            bitunix_client: Bitunix API 客戶端
            sheets_client: Google Sheets 客戶端
            whatsapp_client: WhatsApp API 客戶端
            discussion_group_link: 主討論區群組邀請連結
            helper_phone: 小幫手電話號碼
        \"\"\"
        self.bitunix_client = bitunix_client
        self.sheets_client = sheets_client
        self.whatsapp_client = whatsapp_client
        self.discussion_group_link = discussion_group_link
        self.helper_phone = helper_phone
    
    @staticmethod
    def extract_uid_from_message(message: str) -> Optional[str]:
        \"\"\"
        從訊息中提取 UID
        支持的格式:
        - UID: 12345678
        - UID:12345678
        - uid: 12345678
        - 12345678
        
        Args:
            message: 訊息內容
            
        Returns:
            提取的 UID 或 None
        \"\"\"
        # 移除空格
        message = message.strip()
        
        # 嘗試匹配 "UID: 數字" 或 "UID:數字" 的格式
        match = re.search(r'[Uu][Ii][Dd]\s*:\s*(\d+)', message)
        if match:
            return match.group(1)
        
        # 嘗試匹配純數字（假設是 UID）
        if message.isdigit() and len(message) >= 6:
            return message
        
        return None
    
    def audit_user(self, uid: str, sender_phone: str) -> Tuple[bool, str]:
        \"\"\"
        審核用戶
        
        Args:
            uid: Bitunix UID
            sender_phone: 發送者電話號碼
            
        Returns:
            (審核通過, 回覆訊息)
        \"\"\"
        try:
            logger.info(f"Starting audit for UID: {uid}, Phone: {sender_phone}")
            
            # 步驟 1: 檢查 UID 是否在 Google 表單中
            logger.info(f"Checking if UID {uid} exists in Google Sheets...")
            uid_in_sheets = self.sheets_client.check_uid_exists(uid)
            
            if not uid_in_sheets:
                logger.warning(f"UID {uid} not found in Google Sheets")
                return False, (
                    f"❌ 審核未通過\n\n"
                    f"我們在表單中找不到您的 UID: {uid}\n\n"
                    f"請確認：\n"
                    f"1️⃣ 已填寫完整的入群基本資料表單\n"
                    f"2️⃣ 使用的 UID 與表單填寫的相同\n\n"
                    f"如有疑問，請私訊聯繫小幫手：{self.helper_phone}"
                )
            
            # 步驟 2: 驗證 UID 是否為有效的 Bitunix 帳戶
            logger.info(f"Validating UID {uid} with Bitunix API...")
            success, result = self.bitunix_client.validate_user(uid)
            
            if not success:
                logger.error(f"Bitunix validation failed: {result}")
                return False, (
                    f"❌ 審核未通過\n\n"
                    f"無法驗證您的 Bitunix 帳戶\n\n"
                    f"可能原因：\n"
                    f"• UID 尚未在 Bitunix 完成註冊\n"
                    f"• 系統暫時無法連線\n\n"
                    f"請確認已透過推薦連結完成註冊，"
                    f"然後重新提交 UID。\n\n"
                    f"如有疑問，請私訊聯繫小幫手：{self.helper_phone}"
                )
            
            # 檢查是否為直接推薦
            is_direct_referral = result.get('result', False)
            
            if not is_direct_referral:
                logger.warning(f"UID {uid} is not a direct referral")
                return False, (
                    f"❌ 審核未通過\n\n"
                    f"您的帳戶未透過我們的推薦連結註冊\n\n"
                    f"請使用以下推薦連結重新註冊 Bitunix：\n"
                    f"https://www.bitunix.com/register?vipCode=4hry\n\n"
                    f"註冊完成後，重新提交您的 UID 進行審核。\n\n"
                    f"如有疑問，請私訊聯繫小幫手：{self.helper_phone}"
                )
            
            # 審核通過
            logger.info(f"UID {uid} passed audit")
            
            return True, (
                f"✅ 恭喜！審核通過\n\n"
                f"歡迎加入 KTC 凱旋交易社！\n\n"
                f"點擊下方連結進入主討論區：\n"
                f"{self.discussion_group_link}\n\n"
                f"在主討論區中，你可以：\n"
                f"• 參與實時盤面分析討論\n"
                f"• 學習交易技術分析\n"
                f"• 與其他交易者交流經驗\n\n"
                f"祝你交易順利！🚀"
            )
            
        except Exception as e:
            logger.error(f"Audit error: {str(e)}")
            return False, (
                f"❌ 審核系統暫時出錯\n\n"
                f"請稍後重試或聯繫小幫手：{self.helper_phone}"
            )
    
    def handle_message(self, message_data: Dict) -> Optional[Tuple[str, str]]:
        \"\"\"
        處理接收到的訊息
        
        Args:
            message_data: WhatsApp Webhook 訊息資料
            
        Returns:
            (收件人電話, 回覆訊息) 或 None
        \"\"\"
        try:
            # 提取訊息信息
            message_type = message_data.get('type', '')
            
            if message_type != 'text':
                logger.info(f"Ignoring non-text message: {message_type}")
                return None
            
            message_text = message_data.get('text', {}).get('body', '')
            sender_phone = message_data.get('from', '')
            message_id = message_data.get('id', '')
            
            logger.info(f"Received message from {sender_phone}: {message_text}")
            
            # 提取 UID
            uid = self.extract_uid_from_message(message_text)
            
            if not uid:
                logger.info(f"No UID found in message from {sender_phone}")
                return None
            
            # 標記訊息為已讀
            self.whatsapp_client.mark_message_as_read(message_id)
            
            # 進行審核
            passed, reply_message = self.audit_user(uid, sender_phone)
            
            # 記錄審核結果
            timestamp = datetime.now().isoformat()
            status = "passed" if passed else "failed"
            
            try:
                self.sheets_client.add_audit_record(uid, sender_phone, status, timestamp)
            except Exception as e:
                logger.error(f"Failed to add audit record: {str(e)}")
            
            return (sender_phone, reply_message)
            
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            return None


# 測試函數
if __name__ == "__main__":
    # 測試 UID 提取
    test_messages = [
        "UID: 12345678",
        "UID:12345678",
        "uid: 87654321",
        "我的 UID 是 11111111",
        "12345678",
        "沒有 UID 的訊息"
    ]
    
    for msg in test_messages:
        uid = AuditBot.extract_uid_from_message(msg)
        print(f"Message: '{msg}' -> UID: {uid}")
