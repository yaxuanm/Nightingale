#!/usr/bin/env python3
"""
固定音频Web评测服务
直接加载预先准备好的30个固定音频文件，无需重新生成
- /         : 前端评测页面
- /api/test-data : GET，获取测试数据
- /api/save-evaluation : POST，保存用户评测结果
"""

import os
import sys
import json
import time
import threading
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import webbrowser
from typing import Dict, Any

# 数据目录
DATA_DIR = Path("audio_test_output/fixed_web")
AUDIO_DIR = DATA_DIR / "audio_files"
WEB_DATA_FILE = DATA_DIR / "web_test_data.json"
EVALUATION_DIR = DATA_DIR / "evaluations"

# 创建必要的目录
DATA_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
EVALUATION_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Nightingale Fixed Audio Test", version="1.0.0")

# 添加CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载音频文件目录
app.mount("/audio_files", StaticFiles(directory=AUDIO_DIR), name="audio_files")

def load_test_data():
    """加载测试数据"""
    if not WEB_DATA_FILE.exists():
        print(f"错误：Web数据文件不存在: {WEB_DATA_FILE}")
        print("请先运行 prepare_fixed_audio_for_web.py 生成音频文件")
        return []
    
    with open(WEB_DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

@app.get("/", response_class=HTMLResponse)
async def index():
    """前端测试页面"""
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Nightingale 固定音频评测 - 30个音频样本</title>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0; 
            padding: 20px; 
            min-height: 100vh;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: rgba(255,255,255,0.95); 
            border-radius: 12px; 
            box-shadow: 0 8px 32px rgba(0,0,0,0.1); 
            padding: 32px; 
            backdrop-filter: blur(10px);
        }
        h1 { 
            color: #2c3e50; 
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
            font-weight: 300;
        }
        .subtitle {
            text-align: center;
            color: #7f8c8d;
            margin-bottom: 40px;
            font-size: 1.1em;
        }
        .test-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
            gap: 24px;
            margin-top: 30px;
        }
        .test-item { 
            background: #f8f9fa; 
            border-radius: 8px; 
            padding: 20px; 
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border: 1px solid #e9ecef;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .test-item:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        }
        .test-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .test-id {
            background: #3498db;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
        }
        .mode-tag {
            background: #e74c3c;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
        }
        .prompt-text {
            font-size: 1.1em;
            color: #2c3e50;
            margin-bottom: 15px;
            line-height: 1.4;
        }
        .description {
            color: #7f8c8d;
            font-style: italic;
            margin-bottom: 15px;
            font-size: 0.9em;
        }
        .audio-player { 
            margin: 15px 0; 
            width: 100%;
        }
        .audio-player audio {
            width: 100%;
            height: 40px;
        }
        .evaluation-form { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
            gap: 12px; 
            margin: 15px 0; 
        }
        .rating-group { 
            display: flex; 
            flex-direction: column; 
        }
        .rating-group label { 
            font-weight: 600; 
            margin-bottom: 4px; 
            color: #34495e;
            font-size: 0.9em;
        }
        .rating-group select { 
            padding: 8px; 
            border: 1px solid #ddd; 
            border-radius: 4px; 
            background: white;
            font-size: 0.9em;
        }
        .comments { 
            width: 100%; 
            height: 80px; 
            padding: 8px; 
            border: 1px solid #ddd; 
            border-radius: 4px; 
            resize: vertical; 
            font-family: inherit;
            margin-top: 10px;
        }
        .submit-btn { 
            background: linear-gradient(45deg, #27ae60, #2ecc71); 
            color: white; 
            padding: 12px 24px; 
            border: none; 
            border-radius: 6px; 
            cursor: pointer; 
            font-size: 16px; 
            font-weight: 600;
            transition: all 0.2s;
            margin-top: 10px;
        }
        .submit-btn:hover { 
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(39, 174, 96, 0.3);
        }
        .submit-btn:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        .loading {
            text-align: center;
            color: #7f8c8d;
            font-size: 1.1em;
            margin: 40px 0;
        }
        .error {
            color: #e74c3c;
            font-weight: bold;
            text-align: center;
            margin: 20px 0;
        }
        .stats {
            background: #ecf0f1;
            padding: 15px;
            border-radius: 6px;
            margin-bottom: 20px;
            text-align: center;
        }
        .stats h3 {
            margin: 0 0 10px 0;
            color: #2c3e50;
        }
        .stats p {
            margin: 5px 0;
            color: #7f8c8d;
        }
        .audio-error { 
            color: #e74c3c; 
            font-weight: bold; 
            font-size: 0.9em;
            margin-top: 5px;
        }
        .save-all-btn {
            background: linear-gradient(45deg, #9b59b6, #8e44ad);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 18px;
            font-weight: 600;
            margin: 30px auto;
            display: block;
            transition: all 0.2s;
        }
        .save-all-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(155, 89, 182, 0.3);
        }
        .save-all-btn:disabled {
            background: #bdc3c7;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>🎵 Nightingale 固定音频评测</h1>
    <div class="subtitle">请聆听以下30个AI生成的音频样本，并给出您的评价</div>
    
    <div class="stats">
        <h3>评测说明</h3>
        <p>• 每个音频样本都有对应的英文描述</p>
        <p>• 请仔细聆听每个音频，然后从4个维度进行评分</p>
        <p>• 评分完成后，点击"保存所有评价"按钮下载结果</p>
    </div>
    
    <div id="loading" class="loading">正在加载测试数据...</div>
    <div id="error" class="error" style="display:none;"></div>
    <div id="test-content" style="display:none;">
        <div id="test-grid" class="test-grid"></div>
        <button id="save-all-btn" class="save-all-btn" onclick="saveAllEvaluations()">💾 保存所有评价结果</button>
    </div>
</div>

<script>
let testData = [];
let evaluations = {};

async function loadTestData() {
    try {
        const response = await fetch('/api/test-data');
        if (!response.ok) {
            throw new Error('Failed to load test data');
        }
        testData = await response.json();
        showTestContent();
    } catch (error) {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('error').textContent = '加载测试数据失败: ' + error.message;
        document.getElementById('error').style.display = 'block';
    }
}

function showTestContent() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('test-content').style.display = 'block';
    
    const grid = document.getElementById('test-grid');
    let html = '';
    
    testData.forEach((item, index) => {
        const modeColors = {
            'focus': '#3498db',
            'relax': '#27ae60', 
            'story': '#e67e22',
            'music': '#9b59b6'
        };
        
        const modeColor = modeColors[item.mode] || '#95a5a6';
        
        html += `
        <div class="test-item">
            <div class="test-header">
                <span class="test-id">${item.id}</span>
                <span class="mode-tag" style="background: ${modeColor}">${item.mode}</span>
            </div>
            <div class="prompt-text">${item.prompt}</div>
            ${item.description ? `<div class="description">${item.description}</div>` : ''}
            <div class="audio-player">
                <audio controls style="width: 100%;" onerror="showAudioError(${index})">
                    <source src="${item.audio_url}" type="audio/wav">
                    您的浏览器不支持音频播放。
                </audio>
                <div class="audio-error" id="audio-error-${index}" style="display:none;">⚠️ 音频无法播放，请检查网络连接</div>
            </div>
            <form class="evaluation-form" id="form-${index}">
                <div class="rating-group">
                    <label for="relevance_${index}">相关性 (1-5):</label>
                    <select name="relevance_${index}" id="relevance_${index}" required onchange="updateEvaluation(${index})">
                        <option value="">请选择</option>
                        <option value="1">1 - 完全不相关</option>
                        <option value="2">2 - 部分相关</option>
                        <option value="3">3 - 中等相关</option>
                        <option value="4">4 - 高度相关</option>
                        <option value="5">5 - 完全相关</option>
                    </select>
                </div>
                <div class="rating-group">
                    <label for="quality_${index}">音频质量 (1-5):</label>
                    <select name="quality_${index}" id="quality_${index}" required onchange="updateEvaluation(${index})">
                        <option value="">请选择</option>
                        <option value="1">1 - 质量很差</option>
                        <option value="2">2 - 质量较差</option>
                        <option value="3">3 - 质量一般</option>
                        <option value="4">4 - 质量良好</option>
                        <option value="5">5 - 质量优秀</option>
                    </select>
                </div>
                <div class="rating-group">
                    <label for="enjoyment_${index}">聆听体验 (1-5):</label>
                    <select name="enjoyment_${index}" id="enjoyment_${index}" required onchange="updateEvaluation(${index})">
                        <option value="">请选择</option>
                        <option value="1">1 - 完全不享受</option>
                        <option value="2">2 - 稍微享受</option>
                        <option value="3">3 - 中等享受</option>
                        <option value="4">4 - 比较享受</option>
                        <option value="5">5 - 非常享受</option>
                    </select>
                </div>
                <div class="rating-group">
                    <label for="usability_${index}">实用性 (1-5):</label>
                    <select name="usability_${index}" id="usability_${index}" required onchange="updateEvaluation(${index})">
                        <option value="">请选择</option>
                        <option value="1">1 - 完全不可用</option>
                        <option value="2">2 - 基本不可用</option>
                        <option value="3">3 - 勉强可用</option>
                        <option value="4">4 - 比较可用</option>
                        <option value="5">5 - 高度可用</option>
                    </select>
                </div>
                <div style="grid-column: 1 / -1;">
                    <label for="comments_${index}">详细评价:</label>
                    <textarea name="comments_${index}" id="comments_${index}" class="comments" 
                              placeholder="请详细描述您的体验和建议..." onchange="updateEvaluation(${index})"></textarea>
                </div>
            </form>
        </div>`;
    });
    
    grid.innerHTML = html;
}

function showAudioError(index) {
    document.getElementById(`audio-error-${index}`).style.display = 'block';
}

function updateEvaluation(index) {
    const form = document.getElementById(`form-${index}`);
    const data = {
        id: testData[index].id,
        prompt: testData[index].prompt,
        mode: testData[index].mode,
        relevance: form.querySelector(`[name="relevance_${index}"]`).value,
        quality: form.querySelector(`[name="quality_${index}"]`).value,
        enjoyment: form.querySelector(`[name="enjoyment_${index}"]`).value,
        usability: form.querySelector(`[name="usability_${index}"]`).value,
        comments: form.querySelector(`[name="comments_${index}"]`).value,
        timestamp: new Date().toISOString()
    };
    
    evaluations[index] = data;
    updateSaveButton();
}

function updateSaveButton() {
    const saveBtn = document.getElementById('save-all-btn');
    const completedCount = Object.keys(evaluations).length;
    const totalCount = testData.length;
    
    if (completedCount === totalCount) {
        saveBtn.textContent = `💾 保存所有评价结果 (${completedCount}/${totalCount})`;
        saveBtn.disabled = false;
    } else {
        saveBtn.textContent = `💾 保存所有评价结果 (${completedCount}/${totalCount})`;
        saveBtn.disabled = true;
    }
}

function saveAllEvaluations() {
    if (Object.keys(evaluations).length === 0) {
        alert('请至少完成一个评价后再保存');
        return;
    }
    
    const data = {
        test_data: testData,
        evaluations: evaluations,
        timestamp: new Date().toISOString(),
        total_items: testData.length,
        completed_items: Object.keys(evaluations).length
    };
    
    const dataStr = JSON.stringify(data, null, 2);
    const blob = new Blob([dataStr], {type: 'application/json'});
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `nightingale_evaluation_${new Date().toISOString().slice(0,19).replace(/:/g,'-')}.json`;
    link.click();
    
    alert(`评价结果已保存！共完成 ${Object.keys(evaluations).length}/${testData.length} 个评价`);
}

// 页面加载时获取测试数据
document.addEventListener('DOMContentLoaded', loadTestData);
</script>
</body>
</html>
"""
    return HTMLResponse(html_content)

@app.get("/api/test-data")
async def api_test_data():
    """获取测试数据"""
    try:
        data = load_test_data()
        return JSONResponse(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load test data: {str(e)}")

@app.post("/api/save-evaluation")
async def api_save_evaluation(evaluation_data: Dict[str, Any]):
    """保存用户评价结果"""
    try:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"evaluation_{timestamp}.json"
        filepath = EVALUATION_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(evaluation_data, f, ensure_ascii=False, indent=2)
        
        return {"success": True, "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save evaluation: {str(e)}")

def open_browser():
    """打开浏览器"""
    url = "http://127.0.0.1:8013/"
    webbrowser.open(url)

def main():
    """启动服务"""
    print("=== Nightingale 固定音频评测服务 ===")
    print("服务地址: http://127.0.0.1:8013/")
    print("音频文件目录:", AUDIO_DIR)
    
    # 检查测试数据
    test_data = load_test_data()
    print(f"加载了 {len(test_data)} 个测试项目")
    
    # 检查音频文件
    audio_files = list(AUDIO_DIR.glob("*.wav"))
    print(f"找到 {len(audio_files)} 个音频文件")
    
    if len(audio_files) == 0:
        print("⚠️  警告：未找到音频文件，请先运行 prepare_fixed_audio_for_web.py 生成音频")
    
    # 启动服务
    threading.Timer(1.0, open_browser).start()
    uvicorn.run(app, host="0.0.0.0", port=8013, reload=False)

if __name__ == "__main__":
    main() 