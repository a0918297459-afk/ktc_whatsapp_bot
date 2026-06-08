"""
審核日誌管理模組
記錄所有審核活動到本地檔案和 Google Sheets
"""

import logging
import json
import os
from datetime import datetime
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger(__name__)


class AuditLogger:
    """審核日誌記錄器"""
    
    def __init__(self, log_dir: str = "logs"):
        """
        初始化審核日誌記錄器
        
        Args:
            log_dir: 日誌目錄
        """
        self.log_dir = log_dir
        self.audit_log_file = os.path.join(log_dir, "audit.log")
        self.json_log_file = os.path.join(log_dir, "audit.json")
        
        # 確保日誌目錄存在
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # 初始化 JSON 日誌檔案
        if not os.path.exists(self.json_log_file):
            with open(self.json_log_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def log_audit(
        self,
        uid: str,
        phone: str,
        passed: bool,
        reason: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> bool:
        """
        記錄審核結果
        
        Args:
            uid: Bitunix UID
            phone: WhatsApp 電話號碼
            passed: 是否通過審核
            reason: 失敗原因（如果未通過）
            metadata: 額外的元數據
            
        Returns:
            是否成功記錄
        """
        try:
            timestamp = datetime.now()
            timestamp_str = timestamp.isoformat()
            
            # 構建日誌記錄
            record = {
                'timestamp': timestamp_str,
                'uid': uid,
                'phone': phone,
                'passed': passed,
                'reason': reason,
                'metadata': metadata or {}
            }
            
            # 寫入文本日誌
            self._write_text_log(record, timestamp)
            
            # 寫入 JSON 日誌
            self._write_json_log(record)
            
            logger.info(f"Audit logged: UID={uid}, Phone={phone}, Passed={passed}")
            return True
            
        except Exception as e:
            logger.error(f"Error logging audit: {str(e)}")
            return False
    
    def _write_text_log(self, record: Dict, timestamp: datetime) -> None:
        """
        寫入文本格式的日誌
        
        Args:
            record: 日誌記錄
            timestamp: 時間戳
        """
        try:
            with open(self.audit_log_file, 'a', encoding='utf-8') as f:
                # 格式化日誌行
                status = "✅ PASSED" if record['passed'] else "❌ FAILED"
                log_line = (
                    f"[{timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {status} | "
                    f"UID: {record['uid']} | "
                    f"Phone: {record['phone']}"
                )
                
                if record['reason']:
                    log_line += f" | Reason: {record['reason']}"
                
                f.write(log_line + '\n')
                
        except Exception as e:
            logger.error(f"Error writing text log: {str(e)}")
    
    def _write_json_log(self, record: Dict) -> None:
        """
        寫入 JSON 格式的日誌
        
        Args:
            record: 日誌記錄
        """
        try:
            # 讀取現有日誌
            with open(self.json_log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            # 添加新記錄
            logs.append(record)
            
            # 寫回檔案
            with open(self.json_log_file, 'w', encoding='utf-8') as f:
                json.dump(logs, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            logger.error(f"Error writing JSON log: {str(e)}")
    
    def get_audit_stats(self) -> Dict:
        """
        獲取審核統計信息
        
        Returns:
            統計字典，包含:
            - total: 總審核數
            - passed: 通過數
            - failed: 失敗數
            - pass_rate: 通過率（百分比）
            - today_total: 今日審核數
            - today_passed: 今日通過數
        """
        try:
            with open(self.json_log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            if not logs:
                return {
                    'total': 0,
                    'passed': 0,
                    'failed': 0,
                    'pass_rate': 0,
                    'today_total': 0,
                    'today_passed': 0
                }
            
            # 計算總統計
            total = len(logs)
            passed = sum(1 for log in logs if log.get('passed', False))
            failed = total - passed
            pass_rate = (passed / total * 100) if total > 0 else 0
            
            # 計算今日統計
            today = datetime.now().date()
            today_logs = [
                log for log in logs
                if datetime.fromisoformat(log['timestamp']).date() == today
            ]
            today_total = len(today_logs)
            today_passed = sum(1 for log in today_logs if log.get('passed', False))
            
            return {
                'total': total,
                'passed': passed,
                'failed': failed,
                'pass_rate': round(pass_rate, 2),
                'today_total': today_total,
                'today_passed': today_passed
            }
            
        except Exception as e:
            logger.error(f"Error getting audit stats: {str(e)}")
            return {}
    
    def get_failed_audits(self, limit: int = 10) -> list:
        """
        獲取最近失敗的審核記錄
        
        Args:
            limit: 返回的記錄數量
            
        Returns:
            失敗記錄列表
        """
        try:
            with open(self.json_log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            # 篩選失敗的記錄並按時間倒序排列
            failed_logs = [log for log in logs if not log.get('passed', False)]
            failed_logs.reverse()
            
            return failed_logs[:limit]
            
        except Exception as e:
            logger.error(f"Error getting failed audits: {str(e)}")
            return []
    
    def get_user_audit_history(self, uid: str) -> list:
        """
        獲取特定用戶的審核歷史
        
        Args:
            uid: Bitunix UID
            
        Returns:
            該用戶的審核記錄列表
        """
        try:
            with open(self.json_log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            # 篩選該用戶的記錄
            user_logs = [log for log in logs if log.get('uid') == uid]
            user_logs.reverse()  # 按時間倒序
            
            return user_logs
            
        except Exception as e:
            logger.error(f"Error getting user audit history: {str(e)}")
            return []
    
    def export_audit_report(self, output_file: str) -> bool:
        """
        匯出審核報告
        
        Args:
            output_file: 輸出檔案路徑
            
        Returns:
            是否成功
        """
        try:
            with open(self.json_log_file, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            # 生成報告
            report = {
                'generated_at': datetime.now().isoformat(),
                'statistics': self.get_audit_stats(),
                'total_records': len(logs),
                'records': logs
            }
            
            # 寫入報告
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Audit report exported to {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting audit report: {str(e)}")
            return False


# 測試函數
if __name__ == "__main__":
    # 建立日誌記錄器
    audit_logger = AuditLogger()
    
    # 測試記錄
    print("記錄審核結果...")
    audit_logger.log_audit(
        uid="12345678",
        phone="886912345678",
        passed=True,
        metadata={'source': 'test'}
    )
    
    audit_logger.log_audit(
        uid="87654321",
        phone="886987654321",
        passed=False,
        reason="UID not found in spreadsheet"
    )
    
    # 獲取統計
    print("\n審核統計:")
    stats = audit_logger.get_audit_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # 獲取失敗的審核
    print("\n最近失敗的審核:")
    failed = audit_logger.get_failed_audits()
    for log in failed:
        print(f"  UID: {log['uid']}, 原因: {log['reason']}")
    
    # 匯出報告
    print("\n匯出報告...")
    audit_logger.export_audit_report("audit_report.json")
    print("報告已匯出到 audit_report.json")
