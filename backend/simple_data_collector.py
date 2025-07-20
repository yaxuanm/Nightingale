#!/usr/bin/env python3
"""
简单的数据收集服务
- 接收前端提交的评测数据
- 保存到本地文件
- 提供简单的 API 接口
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from datetime import datetime
from pathlib import Path

app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 数据保存目录
DATA_DIR = Path("collected_data")
DATA_DIR.mkdir(exist_ok=True)

@app.route('/api/submit-evaluation', methods=['POST'])
def submit_evaluation():
    """接收评测数据"""
    try:
        data = request.json
        
        # 生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_{timestamp}.json"
        filepath = DATA_DIR / filename
        
        # 保存数据
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 收到评测数据: {filename}")
        
        return jsonify({
            "success": True,
            "message": "数据提交成功",
            "filename": filename
        })
        
    except Exception as e:
        print(f"❌ 数据提交失败: {e}")
        return jsonify({
            "success": False,
            "message": f"数据提交失败: {str(e)}"
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    print("🚀 启动数据收集服务...")
    print("📊 数据将保存到:", DATA_DIR)
    print("🌐 服务地址: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True) 