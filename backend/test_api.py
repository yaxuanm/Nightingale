import requests
import json
import sys

def test_audio_generation():
    url = "http://127.0.0.1:8000/api/generate-audio"
    payload = {
        "description": "A peaceful forest with birds chirping and gentle wind",
        "duration": 15
    }
    
    print("正在发送请求...")
    try:
        # 设置较长的超时时间（5分钟）
        response = requests.post(url, json=payload, timeout=300)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except requests.exceptions.Timeout:
        print("请求超时 - 服务器响应时间过长")
    except requests.exceptions.ConnectionError:
        print("连接错误 - 请确保服务器正在运行")
    except Exception as e:
        print(f"发生错误: {str(e)}")

if __name__ == "__main__":
    print("开始测试音频生成 API...")
    test_audio_generation()
    print("测试完成") 