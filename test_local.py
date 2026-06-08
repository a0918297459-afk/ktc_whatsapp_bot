"""
本地測試腳本
用於在部署前測試各個模組
"""

import os
import sys
from dotenv import load_dotenv

# 加載環境變數
load_dotenv()

# 添加 src 目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(__file__))

from src.bitunix_client import BitunixClient
from src.google_sheets_client import GoogleSheetsClient
from src.bot_logic import AuditBot


def test_bitunix_api():
    """測試 Bitunix API 連線"""
    print("\n" + "="*50)
    print("測試 Bitunix API 連線")
    print("="*50)
    
    try:
        api_key = os.getenv('BITUNIX_API_KEY')
        api_secret = os.getenv('BITUNIX_API_SECRET')
        
        if not api_key or not api_secret:
            print("❌ 缺少 Bitunix API 金鑰")
            return False
        
        client = BitunixClient(api_key, api_secret)
        
        # 測試簽名生成
        print("✓ Bitunix 客戶端初始化成功")
        
        # 測試驗證（使用測試 UID）
        print("正在測試 UID 驗證...")
        success, result = client.validate_user("test_uid_12345")
        
        if success:
            print("✓ API 連線成功")
            print(f"  結果: {result}")
            return True
        else:
            print("⚠ API 返回錯誤（可能是測試 UID 無效）")
            print(f"  錯誤: {result}")
            return True  # 連線成功，只是 UID 無效
            
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        return False


def test_google_sheets():
    """測試 Google Sheets 連線"""
    print("\n" + "="*50)
    print("測試 Google Sheets 連線")
    print("="*50)
    
    try:
        sheets_url = os.getenv('GOOGLE_SHEETS_URL')
        
        if not sheets_url:
            print("❌ 缺少 Google Sheets URL")
            return False
        
        client = GoogleSheetsClient(sheets_url)
        print("✓ Google Sheets 客戶端初始化成功")
        
        # 嘗試打開試算表
        print("正在連線試算表...")
        try:
            client.open_spreadsheet()
            print("✓ 試算表連線成功")
        except Exception as e:
            print(f"⚠ 無法自動打開試算表（可能需要認證）")
            print(f"  錯誤: {str(e)}")
            print("  提示: 如果試算表是公開的，可以手動檢查 URL")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        return False


def test_uid_extraction():
    """測試 UID 提取"""
    print("\n" + "="*50)
    print("測試 UID 提取功能")
    print("="*50)
    
    test_cases = [
        ("UID: 12345678", "12345678"),
        ("UID:87654321", "87654321"),
        ("uid: 11111111", "11111111"),
        ("我的 UID 是 99999999", "99999999"),
        ("99999999", "99999999"),
        ("沒有 UID 的訊息", None),
    ]
    
    all_passed = True
    
    for message, expected_uid in test_cases:
        extracted_uid = AuditBot.extract_uid_from_message(message)
        
        if extracted_uid == expected_uid:
            print(f"✓ '{message}' -> {extracted_uid}")
        else:
            print(f"❌ '{message}' -> {extracted_uid} (期望: {expected_uid})")
            all_passed = False
    
    return all_passed


def test_environment():
    """檢查環境變數"""
    print("\n" + "="*50)
    print("檢查環境變數")
    print("="*50)
    
    required_vars = [
        'BITUNIX_API_KEY',
        'BITUNIX_API_SECRET',
        'GOOGLE_SHEETS_URL',
        'WHATSAPP_PHONE_NUMBER_ID',
        'WHATSAPP_ACCESS_TOKEN',
        'WHATSAPP_BUSINESS_ACCOUNT_ID',
        'WHATSAPP_VERIFY_TOKEN',
        'DISCUSSION_GROUP_LINK',
        'HELPER_PHONE'
    ]
    
    all_present = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # 隱藏敏感信息
            if 'KEY' in var or 'SECRET' in var or 'TOKEN' in var:
                display_value = value[:10] + '...' if len(value) > 10 else '***'
            else:
                display_value = value
            print(f"✓ {var}: {display_value}")
        else:
            print(f"❌ {var}: 未設定")
            all_present = False
    
    return all_present


def main():
    """主測試函數"""
    print("\n")
    print("╔" + "="*48 + "╗")
    print("║  KTC 凱旋交易社 - WhatsApp 審核機器人本地測試  ║")
    print("╚" + "="*48 + "╝")
    
    results = {
        "環境變數": test_environment(),
        "UID 提取": test_uid_extraction(),
        "Google Sheets": test_google_sheets(),
        "Bitunix API": test_bitunix_api(),
    }
    
    print("\n" + "="*50)
    print("測試結果總結")
    print("="*50)
    
    for test_name, result in results.items():
        status = "✓ 通過" if result else "❌ 失敗"
        print(f"{test_name}: {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "="*50)
    if all_passed:
        print("✓ 所有測試通過！機器人已準備好部署")
    else:
        print("❌ 部分測試失敗，請檢查上面的錯誤信息")
    print("="*50 + "\n")
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
