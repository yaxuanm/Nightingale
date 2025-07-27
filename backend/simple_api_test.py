#!/usr/bin/env python3
"""
简单的API测试脚本
"""

import requests
import json

def test_inspiration_chips():
    """测试inspiration chips端点"""
    print("🧪 测试 /api/generate-inspiration-chips 端点")
    print("=" * 50)
    
    url = "http://127.0.0.1:8000/api/generate-inspiration-chips"
    
    # 测试数据
    test_data = {
        "mode": "default",
        "user_input": ""
    }
    
    try:
        print(f"发送请求到: {url}")
        print(f"请求数据: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"响应数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                
                # 检查响应格式
                if "chips" in data:
                    chips = data["chips"]
                    if isinstance(chips, list):
                        print(f"✅ 响应格式正确，找到 {len(chips)} 个chips")
                        for i, chip in enumerate(chips):
                            print(f"   {i+1}. {chip}")
                    else:
                        print("❌ chips不是数组格式")
                else:
                    print("❌ 响应中没有chips字段")
                    
            except json.JSONDecodeError as e:
                print(f"❌ JSON解析错误: {e}")
                print(f"原始响应: {response.text}")
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            print(f"错误响应: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求异常: {e}")
    except Exception as e:
        print(f"❌ 其他错误: {e}")

def test_root_endpoint():
    """测试根端点"""
    print("\n🧪 测试根端点")
    print("=" * 50)
    
    try:
        response = requests.get("http://127.0.0.1:8000/", timeout=10)
        print(f"状态码: {response.status_code}")
        print(f"响应: {response.text}")
    except Exception as e:
        print(f"❌ 错误: {e}")

def main():
    """主函数"""
    print("🚀 简单API测试")
    print("=" * 50)
    
    # 测试根端点
    test_root_endpoint()
    
    # 测试inspiration chips端点
    test_inspiration_chips()
    
    print("\n" + "=" * 50)
    print("🎉 测试完成！")

if __name__ == "__main__":
    main() 