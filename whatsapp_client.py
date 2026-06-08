"""
WhatsApp Business API 客戶端
用於發送訊息和管理群組
"""

import requests
import logging
from typing import Optional, Dict, List
import json

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """WhatsApp Business API 客戶端"""
    
    def __init__(self, phone_number_id: str, access_token: str, business_account_id: str):
        """
        初始化 WhatsApp 客戶端
        
        Args:
            phone_number_id: WhatsApp 商業帳戶的電話號碼 ID
            access_token: Meta API 存取令牌
            business_account_id: 商業帳戶 ID
        """
        self.phone_number_id = phone_number_id
        self.access_token = access_token
        self.business_account_id = business_account_id
        self.base_url = f"https://graph.instagram.com/v18.0"
        self.timeout = 10
    
    def _get_headers(self) -> Dict:
        """獲取 API 請求頭"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
    
    def send_text_message(self, to_phone: str, message: str) -> bool:
        """
        發送文本訊息
        
        Args:
            to_phone: 收件人電話號碼（格式: 886912345678）
            message: 訊息內容
            
        Returns:
            是否成功
        """
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_phone,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message
                }
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Message sent successfully to {to_phone}")
                return True
            else:
                logger.error(f"Failed to send message: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
    
    def send_template_message(self, to_phone: str, template_name: str, parameters: Optional[List] = None) -> bool:
        """
        發送範本訊息
        
        Args:
            to_phone: 收件人電話號碼
            template_name: 範本名稱
            parameters: 範本參數
            
        Returns:
            是否成功
        """
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to_phone,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": "zh_TW"
                    }
                }
            }
            
            if parameters:
                payload["template"]["components"] = [
                    {
                        "type": "body",
                        "parameters": [{"type": "text", "text": param} for param in parameters]
                    }
                ]
            
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Template message sent successfully to {to_phone}")
                return True
            else:
                logger.error(f"Failed to send template message: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending template message: {str(e)}")
            return False
    
    def send_group_message(self, group_id: str, message: str) -> bool:
        """
        發送群組訊息
        
        Args:
            group_id: WhatsApp 群組 ID
            message: 訊息內容
            
        Returns:
            是否成功
        """
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "group",
                "to": group_id,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": message
                }
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Group message sent successfully to {group_id}")
                return True
            else:
                logger.error(f"Failed to send group message: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending group message: {str(e)}")
            return False
    
    def send_interactive_message(self, to_phone: str, message_text: str, buttons: List[Dict]) -> bool:
        """
        發送互動式訊息（帶按鈕）
        
        Args:
            to_phone: 收件人電話號碼
            message_text: 訊息文本
            buttons: 按鈕列表，每個按鈕為 {"id": "...", "title": "..."}
            
        Returns:
            是否成功
        """
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            button_objects = [
                {
                    "type": "reply",
                    "reply": {
                        "id": btn["id"],
                        "title": btn["title"]
                    }
                }
                for btn in buttons
            ]
            
            payload = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": to_phone,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {
                        "text": message_text
                    },
                    "action": {
                        "buttons": button_objects
                    }
                }
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Interactive message sent successfully to {to_phone}")
                return True
            else:
                logger.error(f"Failed to send interactive message: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending interactive message: {str(e)}")
            return False
    
    def mark_message_as_read(self, message_id: str) -> bool:
        """
        標記訊息為已讀
        
        Args:
            message_id: 訊息 ID
            
        Returns:
            是否成功
        """
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }
            
            response = requests.post(
                url,
                json=payload,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            
            if response.status_code in [200, 201]:
                logger.info(f"Message {message_id} marked as read")
                return True
            else:
                logger.error(f"Failed to mark message as read: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error marking message as read: {str(e)}")
            return False


# 測試函數
if __name__ == "__main__":
    import os
    
    phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '')
    access_token = os.getenv('WHATSAPP_ACCESS_TOKEN', '')
    business_account_id = os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID', '')
    
    if phone_number_id and access_token:
        client = WhatsAppClient(phone_number_id, access_token, business_account_id)
        
        # 測試發送訊息
        success = client.send_text_message('886912345678', 'Test message')
        print(f"Send message success: {success}")
