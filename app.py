"""
KTC 凱旋交易社 - WhatsApp 審核機器人
主應用程式
"""

import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import json
from datetime import datetime

# 因為檔案都在同一層，所以把 src. 拿掉了
from bitunix_client import BitunixClient
from google_sheets_client import GoogleSheetsClient
from whatsapp_client import WhatsAppClient
from bot_logic import AuditBot
from audit_logger import AuditLogger

# 加載環境變數
load_dotenv()

# 配置日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 初始化 Flask 應用
app = Flask(__name__)

# 初始化各個客戶端
bitunix_client = BitunixClient(
    api_key=os.getenv('BITUNIX_API_KEY'),
    api_secret=os.getenv('BITUNIX_API_SECRET')
)

sheets_client = GoogleSheetsClient(
    spreadsheet_url=os.getenv('GOOGLE_SHEETS_URL')
)

whatsapp_client = WhatsAppClient(
    phone_number_id=os.getenv('WHATSAPP_PHONE_NUMBER_ID'),
    access_token=os.getenv('WHATSAPP_ACCESS_TOKEN'),
    business_account_id=os.getenv('WHATSAPP_BUSINESS_ACCOUNT_ID')
)

# 初始化審核日誌記錄器
audit_logger = AuditLogger()

# 初始化審核機器人
audit_bot = AuditBot(
    bitunix_client=bitunix_client,
    sheets_client=sheets_client,
    whatsapp_client=whatsapp_client,
    discussion_group_link=os.getenv('DISCUSSION_GROUP_LINK'),
    helper_phone=os.getenv('HELPER_PHONE')
)

# 驗證令牌（用於 Webhook 驗證）
VERIFY_TOKEN = os.getenv('WHATSAPP_VERIFY_TOKEN', 'ktc_audit_bot_2024')


@app.route('/webhook', methods=['GET'])
def webhook_verify():
    """
    驗證 WhatsApp Webhook
    當 WhatsApp 設定 Webhook 時會呼叫此端點
    """
    try:
        mode = request.args.get('hub.mode')
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        
        logger.info(f"Webhook verification request: mode={mode}, token={token}")
        
        if mode == 'subscribe' and token == VERIFY_TOKEN:
            logger.info("Webhook verified successfully")
            return challenge, 200
        else:
            logger.warning("Webhook verification failed")
            return 'Forbidden', 403
            
    except Exception as e:
        logger.error(f"Webhook verification error: {str(e)}")
        return 'Error', 500


@app.route('/webhook', methods=['POST'])
def webhook_receive():
    """
    接收 WhatsApp 訊息
    """
    try:
        data = request.get_json()
        logger.info(f"Received webhook data: {json.dumps(data, indent=2)}")
        
        # 驗證訊息格式
        if not data or 'entry' not in data:
            return jsonify({'status': 'ok'}), 200
        
        # 處理訊息
        for entry in data.get('entry', []):
            for change in entry.get('changes', []):
                value = change.get('value', {})
                
                # 檢查是否有訊息
                messages = value.get('messages', [])
                for message in messages:
                    logger.info(f"Processing message: {json.dumps(message, indent=2)}")
                    
                    # 使用機器人邏輯處理訊息
                    result = audit_bot.handle_message(message)
                    
                    if result:
                        to_phone, reply_message = result
                        
                        # 發送回覆訊息
                        logger.info(f"Sending reply to {to_phone}")
                        success = whatsapp_client.send_text_message(to_phone, reply_message)
                        
                        if success:
                            logger.info(f"Reply sent successfully to {to_phone}")
                        else:
                            logger.error(f"Failed to send reply to {to_phone}")
        
        # 返回 200 OK 以確認接收
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        logger.error(f"Webhook receive error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """
    健康檢查端點
    """
    stats = audit_logger.get_audit_stats()
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'KTC WhatsApp Audit Bot',
        'audit_stats': stats
    }), 200


@app.route('/test-audit', methods=['POST'])
def test_audit():
    """
    測試審核功能
    """
    try:
        data = request.get_json()
        uid = data.get('uid')
        phone = data.get('phone')
        
        if not uid or not phone:
            return jsonify({'error': 'Missing uid or phone'}), 400
        
        logger.info(f"Testing audit for UID: {uid}, Phone: {phone}")
        
        passed, message = audit_bot.audit_user(uid, phone)
        
        return jsonify({
            'uid': uid,
            'phone': phone,
            'passed': passed,
            'message': message
        }), 200
        
    except Exception as e:
        logger.error(f"Test audit error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/test-sheets', methods=['GET'])
def test_sheets():
    """
    測試 Google Sheets 連線
    """
    try:
        logger.info("Testing Google Sheets connection...")
        sheets_client.open_spreadsheet()
        test_uid = "test_12345"
        exists = sheets_client.check_uid_exists(test_uid)
        
        return jsonify({
            'status': 'ok',
            'message': 'Google Sheets connection successful',
            'test_uid': test_uid,
            'uid_exists': exists
        }), 200
        
    except Exception as e:
        logger.error(f"Sheets test error: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/test-bitunix', methods=['POST'])
def test_bitunix():
    """
    測試 Bitunix API 連線
    """
    try:
        data = request.get_json()
        uid = data.get('uid')
        
        if not uid:
            return jsonify({'error': 'Missing uid'}), 400
        
        logger.info(f"Testing Bitunix validation for UID: {uid}")
        success, result = bitunix_client.validate_user(uid)
        
        return jsonify({
            'uid': uid,
            'success': success,
            'result': result
        }), 200
        
    except Exception as e:
        logger.error(f"Bitunix test error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.route('/audit-stats', methods=['GET'])
def get_audit_stats():
    try:
        stats = audit_logger.get_audit_stats()
        return jsonify(stats), 200
    except Exception as e:
        logger.error(f"Error getting audit stats: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/audit-history/<uid>', methods=['GET'])
def get_user_history(uid):
    try:
        history = audit_logger.get_user_audit_history(uid)
        return jsonify({
            'uid': uid,
            'history': history,
            'total_attempts': len(history)
        }), 200
    except Exception as e:
        logger.error(f"Error getting user history: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/failed-audits', methods=['GET'])
def get_failed_audits():
    try:
        limit = request.args.get('limit', default=10, type=int)
        failed = audit_logger.get_failed_audits(limit)
        return jsonify({
            'failed_count': len(failed),
            'records': failed
        }), 200
    except Exception as e:
        logger.error(f"Error getting failed audits: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting KTC WhatsApp Audit Bot on port {port}")
    app.run(host='0.0.0.0', port=port, debug=debug)
