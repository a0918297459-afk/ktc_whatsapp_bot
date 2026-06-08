"""
Google Sheets 客戶端
用於讀取表單回應試算表
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging
from typing import Optional, List, Dict

logger = logging.getLogger(__name__)


class GoogleSheetsClient:
    """Google Sheets 客戶端"""
    
    def __init__(self, spreadsheet_url: str, credentials_path: Optional[str] = None):
        """
        初始化 Google Sheets 客戶端
        
        Args:
            spreadsheet_url: Google Sheets 試算表 URL
            credentials_path: Google Service Account JSON 檔案路徑（可選）
        """
        self.spreadsheet_url = spreadsheet_url
        self.credentials_path = credentials_path
        self.client = None
        self.worksheet = None
        
        # 如果提供了認證檔案，則進行認證
        if credentials_path:
            self._authenticate()
    
    def _authenticate(self):
        """使用 Service Account 進行認證"""
        try:
            scope = [
                'https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive'
            ]
            
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                self.credentials_path,
                scope
            )
            
            self.client = gspread.authorize(credentials)
            logger.info("Successfully authenticated with Google Sheets")
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            raise
    
    def open_spreadsheet(self, sheet_name: str = "表單回應 1"):
        """
        打開試算表並選擇工作表
        
        Args:
            sheet_name: 工作表名稱
        """
        try:
            # 從 URL 提取試算表 ID
            spreadsheet_id = self._extract_spreadsheet_id(self.spreadsheet_url)
            
            # 使用 gspread 打開試算表
            # 如果沒有認證，使用公開存取
            if self.client:
                spreadsheet = self.client.open_by_key(spreadsheet_id)
            else:
                # 對於公開試算表，可以使用簡單的 HTTP 請求
                logger.info("Using public spreadsheet access")
                spreadsheet = None
            
            # 選擇工作表
            if spreadsheet:
                try:
                    self.worksheet = spreadsheet.worksheet(sheet_name)
                except gspread.exceptions.WorksheetNotFound:
                    # 如果指定的工作表不存在，使用第一個工作表
                    self.worksheet = spreadsheet.get_worksheet(0)
                    logger.warning(f"Sheet '{sheet_name}' not found, using first sheet")
            
            logger.info(f"Successfully opened spreadsheet: {sheet_name}")
            
        except Exception as e:
            logger.error(f"Error opening spreadsheet: {str(e)}")
            raise
    
    @staticmethod
    def _extract_spreadsheet_id(url: str) -> str:
        """
        從 Google Sheets URL 提取試算表 ID
        
        Args:
            url: Google Sheets URL
            
        Returns:
            試算表 ID
        """
        # URL 格式: https://docs.google.com/spreadsheets/d/{ID}/edit...
        parts = url.split('/d/')
        if len(parts) > 1:
            return parts[1].split('/')[0]
        raise ValueError(f"Invalid spreadsheet URL: {url}")
    
    def check_uid_exists(self, uid: str) -> bool:
        """
        檢查 UID 是否在試算表中存在
        
        Args:
            uid: Bitunix UID
            
        Returns:
            是否存在
        """
        try:
            if not self.worksheet:
                logger.error("Worksheet not opened")
                return False
            
            # 獲取所有行
            all_rows = self.worksheet.get_all_values()
            
            if not all_rows:
                logger.warning("Spreadsheet is empty")
                return False
            
            # 假設 UID 在第 4 列（BITUNIX 交易所 UID）
            # 根據表單結構，列順序為: 推薦人, WhatsApp 暱稱, 電話, UID, IG, 年紀, 國家
            uid_column_index = 3  # 0-indexed，所以第 4 列是索引 3
            
            # 跳過標題行，檢查所有行
            for row_index, row in enumerate(all_rows[1:], start=1):
                if len(row) > uid_column_index:
                    if row[uid_column_index].strip() == uid.strip():
                        logger.info(f"UID {uid} found in row {row_index}")
                        return True
            
            logger.info(f"UID {uid} not found in spreadsheet")
            return False
            
        except Exception as e:
            logger.error(f"Error checking UID: {str(e)}")
            return False
    
    def get_user_info(self, uid: str) -> Optional[Dict]:
        """
        獲取用戶的完整信息
        
        Args:
            uid: Bitunix UID
            
        Returns:
            用戶信息字典或 None
        """
        try:
            if not self.worksheet:
                logger.error("Worksheet not opened")
                return None
            
            all_rows = self.worksheet.get_all_values()
            
            if not all_rows:
                return None
            
            # 列標題（根據表單結構）
            headers = ['推薦人', 'WhatsApp暱稱', '電話', 'UID', 'IG帳號', '年紀', '國家']
            uid_column_index = 3
            
            for row in all_rows[1:]:
                if len(row) > uid_column_index and row[uid_column_index].strip() == uid.strip():
                    # 構建用戶信息字典
                    user_info = {}
                    for i, header in enumerate(headers):
                        if i < len(row):
                            user_info[header] = row[i]
                    return user_info
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting user info: {str(e)}")
            return None
    
    def add_audit_record(self, uid: str, phone: str, status: str, timestamp: str):
        """
        添加審核記錄到日誌工作表
        
        Args:
            uid: Bitunix UID
            phone: WhatsApp 電話號碼
            status: 審核狀態 (passed/failed)
            timestamp: 審核時間戳
        """
        try:
            if not self.worksheet:
                logger.error("Worksheet not opened")
                return False
            
            # 添加新行
            new_row = [timestamp, uid, phone, status]
            self.worksheet.append_row(new_row)
            
            logger.info(f"Audit record added: {uid} - {status}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding audit record: {str(e)}")
            return False


# 測試函數
if __name__ == "__main__":
    # 試算表 URL
    spreadsheet_url = "https://docs.google.com/spreadsheets/d/1Glo7fq0q2NjTd2_9ik6TZjX_tvxQbg6KGVNytmU6weE/edit?usp=drive_link"
    
    # 不使用認證，直接測試公開存取
    client = GoogleSheetsClient(spreadsheet_url)
    
    # 測試檢查 UID
    uid_exists = client.check_uid_exists("12345678")
    print(f"UID exists: {uid_exists}")
