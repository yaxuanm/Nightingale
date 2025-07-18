#!/usr/bin/env python3
"""
固定测试Web服务 - 加载预设的30个音频文件供用户测试
- /         : 前端测试页面
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
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--data_file', type=str, required=True)
parser.add_argument('--audio_dir', type=str, required=True)
parser.add_argument('--port', type=int, default=8010)
args = parser.parse_args()

AUDIO_DIR = Path(args.audio_dir)

# 数据目录
DATA_DIR = Path("audio_test_output/fixed_test")
WEB_DATA_FILE = DATA_DIR / "web_test_data.json"
EVALUATION_DIR = DATA_DIR / "evaluations"

# 创建必要的目录
DATA_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
EVALUATION_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Nightingale Fixed Test", version="1.0.0")

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
    """Load test data"""
    if not WEB_DATA_FILE.exists():
        # If web data file doesn't exist, try to create from fixed data
        try:
            from fixed_test_data import get_fixed_prompts
            prompts = get_fixed_prompts()
            
            # Create basic web data
            web_data = []
            for prompt in prompts:
                web_data.append({
                    "id": prompt["id"],
                    "prompt": prompt["prompt"],
                    "description": prompt["description"],
                    "category": prompt["category"],
                    "audio_url": f"/audio_files/{prompt['id']}.wav",
                    "local_file": str(AUDIO_DIR / f"{prompt['id']}.wav"),
                    "metrics": {
                        "duration": 0,
                        "file_size": 0
                    }
                })
            
            # Save web data
            with open(WEB_DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump(web_data, f, ensure_ascii=False, indent=2)
            
            return web_data
        except Exception as e:
            print(f"Failed to load test data: {e}")
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
    <title>Nightingale Fixed Test - 30 Audio Samples</title>
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
        .category-tag {
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
    <h1>🎵 Nightingale Audio Evaluation</h1>
    <div class="subtitle">Please listen to the following 30 AI-generated audio samples and provide your evaluation.</div>
    
    <div class="stats">
        <h3>Instructions</h3>
        <p>• Each audio sample has a corresponding English description.</p>
        <p>• Please listen carefully to each audio and rate it on 4 dimensions.</p>
        <p>• You can save your evaluations at any time - just complete at least one item and click "Save Evaluations".</p>
    </div>
    
    <div id="loading" class="loading">Loading test data...</div>
    <div id="error" class="error" style="display:none;"></div>
    <div id="test-content" style="display:none;">
        <div id="test-grid" class="test-grid"></div>
        <button id="save-all-btn" class="save-all-btn" onclick="saveAllEvaluations()">💾 Save Evaluations</button>
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
        document.getElementById('error').textContent = 'Failed to load test data: ' + error.message;
        document.getElementById('error').style.display = 'block';
    }
}

function showTestContent() {
    document.getElementById('loading').style.display = 'none';
    document.getElementById('test-content').style.display = 'block';
    
    const grid = document.getElementById('test-grid');
    let html = '';
    
    testData.forEach((item, index) => {
        const categoryColors = {
            'nature': '#27ae60',
            'urban': '#3498db', 
            'weather': '#e67e22',
            'meditation': '#9b59b6',
            'home': '#f39c12',
            'music': '#e74c3c'
        };
        
        const categoryColor = categoryColors[item.category] || '#95a5a6';
        
        html += `
        <div class="test-item">
            <div class="test-header">
                <span class="test-id">${item.id}</span>
            </div>
            <div class="prompt-text">${item.prompt}</div>
            ${item.description ? `<div class="description">${item.description}</div>` : ''}
            <div class="audio-player">
                <audio controls style="width: 100%;" onerror="showAudioError(${index})">
                    <source src="${item.audio_url}" type="audio/wav">
                    Your browser does not support audio playback.
                </audio>
                <div class="audio-error" id="audio-error-${index}" style="display:none;">⚠️ Audio cannot be played, please check your network connection.</div>
            </div>
            <form class="evaluation-form" id="form-${index}">
                <div class="rating-group">
                    <label for="relevance_${index}">Relevance (1-5):</label>
                    <select name="relevance_${index}" id="relevance_${index}" required onchange="updateEvaluation(${index})">
                        <option value="">Please select</option>
                        <option value="1">1 - Not relevant at all</option>
                        <option value="2">2 - Slightly relevant</option>
                        <option value="3">3 - Moderately relevant</option>
                        <option value="4">4 - Highly relevant</option>
                        <option value="5">5 - Perfectly relevant</option>
                    </select>
                </div>
                <div class="rating-group">
                    <label for="quality_${index}">Audio Quality (1-5):</label>
                    <select name="quality_${index}" id="quality_${index}" required onchange="updateEvaluation(${index})">
                        <option value="">Please select</option>
                        <option value="1">1 - Very poor</option>
                        <option value="2">2 - Poor</option>
                        <option value="3">3 - Average</option>
                        <option value="4">4 - Good</option>
                        <option value="5">5 - Excellent</option>
                    </select>
                </div>
                <div class="rating-group">
                    <label for="relaxation_${index}">Relaxation Effectiveness (1-5):</label>
                    <select name="relaxation_${index}" id="relaxation_${index}" required onchange="updateEvaluation(${index})">
                        <option value="">Please select</option>
                        <option value="1">1 - Not relaxing at all</option>
                        <option value="2">2 - Slightly relaxing</option>
                        <option value="3">3 - Moderately relaxing</option>
                        <option value="4">4 - Quite relaxing</option>
                        <option value="5">5 - Extremely relaxing</option>
                    </select>
                </div>
                <div class="rating-group">
                    <label for="immersiveness_${index}">Immersiveness (1-5):</label>
                    <select name="immersiveness_${index}" id="immersiveness_${index}" required onchange="updateEvaluation(${index})">
                        <option value="">Please select</option>
                        <option value="1">1 - Not immersive at all</option>
                        <option value="2">2 - Slightly immersive</option>
                        <option value="3">3 - Moderately immersive</option>
                        <option value="4">4 - Quite immersive</option>
                        <option value="5">5 - Extremely immersive</option>
                    </select>
                </div>
                <div style="grid-column: 1 / -1;">
                    <label for="comments_${index}">General Comments/Feedback:</label>
                    <textarea name="comments_${index}" id="comments_${index}" class="comments" 
                              placeholder="Your comments or suggestions (optional)" onchange="updateEvaluation(${index})"></textarea>
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
        relevance: form.querySelector(`[name="relevance_${index}"]`).value,
        quality: form.querySelector(`[name="quality_${index}"]`).value,
        relaxation: form.querySelector(`[name="relaxation_${index}"]`).value,
        immersiveness: form.querySelector(`[name="immersiveness_${index}"]`).value,
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
    
    // 只要有一道题完成就可以保存
    if (completedCount > 0) {
        saveBtn.textContent = `💾 Save Evaluations (${completedCount}/${totalCount})`;
        saveBtn.disabled = false;
    } else {
        saveBtn.textContent = `💾 Save Evaluations (0/${totalCount})`;
        saveBtn.disabled = true;
    }
}

function saveAllEvaluations() {
    if (Object.keys(evaluations).length === 0) {
        alert('Please complete at least one evaluation before saving.');
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
    
    alert(`Evaluation results saved! You can continue evaluating more items. Completed ${Object.keys(evaluations).length}/${testData.length} evaluations.`);
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
    """Get test data"""
    try:
        data = load_test_data()
        return JSONResponse(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load test data: {str(e)}")

@app.post("/api/save-evaluation")
async def api_save_evaluation(evaluation_data: Dict[str, Any]):
    """Save user evaluation results"""
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
    """Open browser"""
    url = f"http://127.0.0.1:{args.port}/"
    webbrowser.open(url)

def main():
    """Start service"""
    print("=== Nightingale Fixed Test Service ===")
    print(f"Service URL: http://127.0.0.1:{args.port}/")
    print("Audio files directory:", AUDIO_DIR)
    
    # Check test data
    test_data = load_test_data()
    print(f"Loaded {len(test_data)} test items")
    
    # Check audio files
    audio_files = list(AUDIO_DIR.glob("*.wav"))
    print(f"Found {len(audio_files)} audio files")
    
    if len(audio_files) == 0:
        print("⚠️  Warning: No audio files found, please run generate_fixed_audio.py first")
    
    # Start service
    threading.Timer(1.0, open_browser).start()
    uvicorn.run(app, host="0.0.0.0", port=args.port)

if __name__ == "__main__":
    main() 