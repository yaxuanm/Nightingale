import os
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

class StabilityKeyManager:
    """Stability AI API Key 管理器，支持自动切换"""
    
    def __init__(self):
        # 加载环境变量
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.env')
        if os.path.exists(env_path):
            load_dotenv(env_path)
        
        self.primary_key = os.getenv('STABILITY_API_KEY')
        self.backup_key = os.getenv('STABILITY_API_KEY_BACKUP')
        self.current_key = self.primary_key
        self.key_usage = {'primary': 0, 'backup': 0}
        
        print(f"[KEY_MANAGER] 初始化完成")
        print(f"[KEY_MANAGER] 主 key: {'已设置' if self.primary_key else '未设置'}")
        print(f"[KEY_MANAGER] 备用 key: {'已设置' if self.backup_key else '未设置'}")
    
    def get_current_key(self) -> Optional[str]:
        """获取当前可用的 key"""
        return self.current_key
    
    def test_key(self, key: str) -> Dict[str, Any]:
        """测试 key 是否有效"""
        try:
            headers = {"Authorization": f"Bearer {key}"}
            response = requests.get("https://api.stability.ai/v1/user/balance", headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'valid': True,
                    'credits': data.get('credits', 0),
                    'balance': data
                }
            else:
                return {
                    'valid': False,
                    'error': f"HTTP {response.status_code}",
                    'response': response.text
                }
        except Exception as e:
            return {
                'valid': False,
                'error': str(e)
            }
    
    def switch_to_backup(self) -> bool:
        """切换到备用 key"""
        if self.backup_key and self.backup_key != self.current_key:
            print(f"[KEY_MANAGER] 切换到备用 key")
            self.current_key = self.backup_key
            return True
        else:
            print(f"[KEY_MANAGER] 没有可用的备用 key")
            return False
    
    def switch_to_primary(self) -> bool:
        """切换回主 key"""
        if self.primary_key and self.primary_key != self.current_key:
            print(f"[KEY_MANAGER] 切换回主 key")
            self.current_key = self.primary_key
            return True
        return False
    
    def handle_api_error(self, error_response: Dict[str, Any]) -> bool:
        """处理 API 错误，决定是否切换 key"""
        error_text = str(error_response).lower()
        
        # 检查是否是 credit 不足或 key 无效的错误
        credit_errors = ['insufficient', 'credit', 'quota', 'limit', 'balance']
        key_errors = ['invalid', 'unauthorized', 'forbidden', '401', '403']
        
        if any(err in error_text for err in credit_errors):
            print(f"[KEY_MANAGER] 检测到 credit 不足，尝试切换 key")
            return self.switch_to_backup()
        elif any(err in error_text for err in key_errors):
            print(f"[KEY_MANAGER] 检测到 key 无效，尝试切换 key")
            return self.switch_to_backup()
        
        return False
    
    def get_key_status(self) -> Dict[str, Any]:
        """获取所有 keys 的状态"""
        status = {
            'primary': {'key': self.primary_key, 'status': 'unknown'},
            'backup': {'key': self.backup_key, 'status': 'unknown'},
            'current': self.current_key
        }
        
        # 测试主 key
        if self.primary_key:
            primary_test = self.test_key(self.primary_key)
            status['primary']['status'] = 'valid' if primary_test['valid'] else 'invalid'
            status['primary']['credits'] = primary_test.get('credits', 0)
        
        # 测试备用 key
        if self.backup_key:
            backup_test = self.test_key(self.backup_key)
            status['backup']['status'] = 'valid' if backup_test['valid'] else 'invalid'
            status['backup']['credits'] = backup_test.get('credits', 0)
        
        return status
    
    def log_usage(self, key_type: str = 'current'):
        """记录 key 使用情况"""
        if key_type == 'primary' and self.current_key == self.primary_key:
            self.key_usage['primary'] += 1
        elif key_type == 'backup' and self.current_key == self.backup_key:
            self.key_usage['backup'] += 1
        else:
            # 根据当前 key 判断类型
            if self.current_key == self.primary_key:
                self.key_usage['primary'] += 1
            elif self.current_key == self.backup_key:
                self.key_usage['backup'] += 1

# 全局实例
stability_key_manager = StabilityKeyManager() 