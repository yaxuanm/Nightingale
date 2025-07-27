import re

def test_regex():
    pattern = r'```json\n([\s\S]*?)\n```'
    test_text = '```json\n["test"]\n```'
    
    print("测试正则表达式修复:")
    print(f"模式: {pattern}")
    print(f"测试文本: {test_text}")
    
    match = re.search(pattern, test_text)
    if match:
        print(f"✓ 匹配成功! 提取的内容: {match.group(1)}")
    else:
        print("✗ 匹配失败")

if __name__ == "__main__":
    test_regex() 