#!/usr/bin/env python3
"""
队列功能测试脚本
"""

import requests
import time
import json

# 服务器地址
BASE_URL = "http://localhost:8000"

def test_queue_audio_generation():
    """测试音频生成队列"""
    print("=== 测试音频生成队列 ===")
    
    # 1. 提交任务
    payload = {
        "description": "A peaceful forest with gentle rain and distant bird songs",
        "duration": 20,
        "mode": "relax"
    }
    
    response = requests.post(f"{BASE_URL}/api/queue/audio-generation", json=payload)
    print(f"提交任务响应: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    if response.status_code == 200:
        task_id = response.json().get("task_id")
        print(f"任务ID: {task_id}")
        
        # 2. 轮询任务状态
        for i in range(30):  # 最多等待30次
            time.sleep(2)
            status_response = requests.get(f"{BASE_URL}/api/queue/status/{task_id}")
            
            if status_response.status_code == 200:
                status_data = status_response.json()
                print(f"任务状态: {status_data.get('status')}, 进度: {status_data.get('progress')}%")
                
                if status_data.get("status") == "completed":
                    print("任务完成!")
                    print(f"结果: {status_data.get('result')}")
                    break
                elif status_data.get("status") == "failed":
                    print(f"任务失败: {status_data.get('error')}")
                    break
            else:
                print(f"获取状态失败: {status_response.status_code}")
                break
    else:
        print("提交任务失败")

def test_queue_stats():
    """测试队列统计"""
    print("\n=== 测试队列统计 ===")
    
    response = requests.get(f"{BASE_URL}/api/queue/stats")
    if response.status_code == 200:
        stats = response.json()
        print(f"队列统计: {stats}")
    else:
        print(f"获取统计失败: {response.status_code}")

def test_cancel_task():
    """测试取消任务"""
    print("\n=== 测试取消任务 ===")
    
    # 1. 提交一个任务
    payload = {
        "description": "A busy coffee shop with people talking and coffee machine sounds",
        "duration": 10,
        "mode": "focus"
    }
    
    response = requests.post(f"{BASE_URL}/api/queue/audio-generation", json=payload)
    if response.status_code == 200:
        task_id = response.json().get("task_id")
        print(f"提交任务: {task_id}")
        
        # 2. 等待一下让任务开始
        time.sleep(3)
        
        # 3. 取消任务
        cancel_response = requests.delete(f"{BASE_URL}/api/queue/cancel/{task_id}")
        if cancel_response.status_code == 200:
            cancel_result = cancel_response.json()
            print(f"取消结果: {cancel_result}")
        else:
            print(f"取消失败: {cancel_response.status_code}")

def main():
    """主测试函数"""
    print("开始测试队列功能...")
    
    try:
        # 测试队列统计
        test_queue_stats()
        
        # 测试音频生成队列
        test_queue_audio_generation()
        
        # 测试取消任务
        test_cancel_task()
        
        print("\n测试完成!")
        
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器，请确保服务器正在运行")
    except Exception as e:
        print(f"测试过程中出现错误: {e}")

if __name__ == "__main__":
    main() 