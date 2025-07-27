#!/usr/bin/env python3
"""
修复AI服务中的正则表达式问题
"""

def fix_regex():
    """修复正则表达式"""
    
    # 读取文件
    with open('app/services/ai_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复所有有问题的正则表达式
    content = content.replace(
        "r'```json\\\\n([\\\\s\\\\S]*?)\\\\n```'",
        "r'```json\\n([\\s\\S]*?)\\n```'"
    )
    
    # 写回文件
    with open('app/services/ai_service.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ 正则表达式已修复")

if __name__ == "__main__":
    fix_regex() 