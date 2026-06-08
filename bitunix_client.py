"""
Bitunix Partnership System API 客戶端
實作 API 簽名與 UID 驗證功能
"""

import requests
import hashlib
import time
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode
import logging

logger = logging.getLogger(__name__)


class BitunixClient:
    """Bitunix API 客戶端"""
    
    def __init__(self, api_key: str, api_secret: str):
        """
        初始化 Bitunix 客戶端
        
        Args:
            api_key: Bitunix API Key
            api_secret: Bitunix API Secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://partners.bitunix.com"
        self.timeout = 10
        
    @staticmethod
    def _get_parameter_type(s: str) -> int:
        """
        根據字符串首字符判斷類型
        1: 數字, 2: 小寫字母, 3: 其他
        """
        if s[0].isdigit():
            return 1
        elif s[0].islower():
            return 2
        return 3
    
    @staticmethod
    def _str_to_ascii_sum(s: str) -> int:
        """計算字符串所有字符的 ASCII 值之和"""
        return sum(ord(c) for c in s)
    
    def _sort_params(self, params: Dict) -> Dict:
        """
        按照 Bitunix 規則排序參數
        排序優先級: 數字 > 小寫字母 > 其他
        """
        sorted_keys = sorted(
            params.keys(),
            key=lambda k: (self._get_parameter_type(k), self._str_to_ascii_sum(k))
        )
        return {k: params[k] for k in sorted_keys}
    
    def _generate_signature(self, params: Dict) -> str:
        """
        生成 API 簽名
        
        Args:
            params: 請求參數字典
            
        Returns:
            SHA1 簽名字符串
        """
        sorted_params = self._sort_params(params)
        
        # 將參數值連接成字符串（不包括鍵名）
        value_strings = [str(v) for v in sorted_params.values()]
        concatenated_string = ''.join(value_strings)
        
        # 使用 SHA1 加密
        signature = hashlib.sha1(
            (concatenated_string + self.api_secret).encode('utf-8')
        ).hexdigest()
        
        return signature
    
    def validate_user(self, account: str) -> Tuple[bool, Optional[Dict]]:
        """
        驗證用戶是否為合作夥伴的直接推薦
        
        Args:
            account: UID 或 Email
            
        Returns:
            (成功標誌, 結果字典)
            結果字典包含:
            - result: bool, 是否為直接推薦
            - deposit_usdt_amount: str, USDT 存款金額
            - error: str, 錯誤信息（如果失敗）
        """
        try:
            # 構建請求參數
            params = {
                'timestamp': int(time.time()),
                'account': account
            }
            
            # 生成簽名
            signature = self._generate_signature(params)
            
            # 設置請求頭
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
                'apiKey': self.api_key,
                'signature': signature
            }
            
            # 發送 POST 請求
            url = f"{self.base_url}/partner/api/v2/openapi/validateUser"
            
            logger.info(f"Validating user: {account}")
            
            response = requests.post(
                url,
                data={'account': account},
                headers=headers,
                timeout=self.timeout,
                verify=False  # 禁用 SSL 驗證（生產環境應該啟用）
            )
            
            response.raise_for_status()
            
            # 解析回應
            result = response.json()
            
            if result.get('code') == '0':
                # 成功
                data = result.get('result', {})
                return True, {
                    'result': data.get('result', False),
                    'deposit_usdt_amount': data.get('deposit_usdt_amount', '0'),
                    'deposit_usdt_onchain': data.get('deposit_usdt_Onchain', '0'),
                    'deposit_usdt_otc': data.get('deposit_usdt_OTC', '0'),
                    'deposit_usdt_internal': data.get('deposit_usdt_Internal', '0')
                }
            else:
                # API 返回錯誤
                error_msg = result.get('msg', 'Unknown error')
                logger.error(f"Bitunix API error: {error_msg}")
                return False, {'error': error_msg}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {str(e)}")
            return False, {'error': f"Network error: {str(e)}"}
        except ValueError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            return False, {'error': f"Invalid response: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return False, {'error': f"Unexpected error: {str(e)}"}


# 測試函數
if __name__ == "__main__":
    import os
    
    # 從環境變數讀取 API 金鑰
    api_key = os.getenv('BITUNIX_API_KEY', 'rmnyJHEiRTRMVUWkyCORwqBDwKCkFlixZRMttrmKjPfOMFHUEQIVmAZVaDhMPrBU')
    api_secret = os.getenv('BITUNIX_API_SECRET', 'SmedJkpWDNnwalqfzrozJNnWsrFpxvsGXXHTfFCsUJBFduHixEDpYDwqLeCPGRTz')
    
    client = BitunixClient(api_key, api_secret)
    
    # 測試驗證
    success, result = client.validate_user('test_uid_12345')
    print(f"Success: {success}")
    print(f"Result: {result}")
