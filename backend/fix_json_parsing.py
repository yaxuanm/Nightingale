#!/usr/bin/env python3
"""
修复AI服务中的JSON解析正则表达式问题
"""

import re

def fix_json_parsing():
    """修复JSON解析正则表达式"""
    
    # 读取文件
    with open('app/services/ai_service.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复正则表达式 - 将 \\n 改为 \n
    old_pattern = r"```json\\n\(\[\\s\\S\]\*\?\)\\n```"
    new_pattern = r"```json\n([\s\S]*?)\n```"
    
    # 替换所有匹配项
    fixed_content = re.sub(old_pattern, new_pattern, content)
    
    # 写回文件
    with open('app/services/ai_service.py', 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("✅ JSON解析正则表达式已修复")
    print("修复内容:")
    print("- 将 r'```json\\\\n([\\s\\S]*?)\\\\n```' 改为 r'```json\\n([\\s\\S]*?)\\n```'")

if __name__ == "__main__":
    fix_json_parsing() 