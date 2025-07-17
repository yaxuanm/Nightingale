# 音频测试脚本使用说明

## 概述

本项目包含两个独立的测试脚本，分别用于不同的环境：

1. **Prompt生成脚本** (`generate_prompts.py`) - 在Gemini环境中运行
2. **音频测试脚本** (`test_audio_generation.py`) - 在Stable Audio环境中运行

## 脚本1: Prompt生成器 (Gemini环境)

### 功能
- 调用Gemini API生成inspiration chips, atmosphere, elements
- 随机选择选项组合成prompt
- 保存prompt到JSON文件供测试脚本使用

### 使用方法

```bash
# 激活Gemini虚拟环境
cd backend
venv_gemini\Scripts\activate

# 运行prompt生成脚本
python scripts/generate_prompts.py
```

### 输出
- 在 `generated_prompts/` 目录下生成JSON文件
- 文件名格式: `generated_prompts_YYYYMMDD_HHMMSS.json`
- 包含4个测试用例: focus, relax, story, music模式

### 示例输出
```
🎵 Prompt生成器 - Gemini环境
============================================================
批量生成prompt供测试使用

🚀 开始批量生成prompt - 共 4 个测试用例
模式包括: focus, relax, story, music

[1/4] 生成prompt
🤖 生成prompt (模式: focus)...
  📝 生成inspiration chips...
    选中chip: cozy cafe
  🌍 生成atmosphere选项...
    选中atmosphere: cozy cafe environment
  🔊 生成elements选项...
    选中elements: ['ambient sound', 'coffee machine']
  🎯 最终prompt: cozy cafe environment with ambient sound, coffee machine
✓ 完成: cozy cafe environment with ambient sound, coffee machine

📁 Prompt已保存: generated_prompts/generated_prompts_20241201_143022.json
共生成 4 个prompt

📋 生成的prompt列表:
  1. [focus] cozy cafe environment with ambient sound, coffee machine
  2. [relax] forest environment with gentle wind, birds chirping
  3. [story] library environment with turning pages, distant footsteps
  4. [music] concert hall environment with orchestral music, applause
```

## 脚本2: 音频测试器 (Stable Audio环境)

### 功能
- 读取生成的prompt文件
- 生成音频并上传到Supabase
- 创建英文评估界面
- 生成测试报告

### 使用方法

```bash
# 激活Stable Audio虚拟环境
cd backend
venv_stableaudio\Scripts\activate

# 运行音频测试脚本
python scripts/test_audio_generation.py
```

### 输出
- 在 `audio_test_output/` 目录下生成测试结果
- 包含音频文件、报告和评估界面

### 目录结构
```
audio_test_output/
├── audio_files/          # 生成的音频文件
├── reports/             # 测试报告
│   ├── audio_test_results_YYYYMMDD_HHMMSS.json
│   ├── audio_test_results_YYYYMMDD_HHMMSS.csv
│   └── audio_test_report_YYYYMMDD_HHMMSS.json
└── evaluation/          # 评估界面
    └── human_evaluation.html
```

### 示例输出
```
🎵 音频生成测试工具
============================================================
读取prompt文件，生成音频，创建评估界面

📁 自动选择prompt文件: generated_prompts/generated_prompts_20241201_143022.json
✅ 成功加载 4 个prompt

🚀 开始批量测试 - 共 4 个prompt
流程: 加载prompt → 生成音频 → 上传云存储 → 测评

[1/4] 进度

=== 测试: test_1 ===
模式: focus
用户输入: cozy cafe
最终prompt: cozy cafe environment with ambient sound, coffee machine
🔄 正在生成音频...
☁️ 正在上传到 Supabase...
✅ 上传成功: https://supabase.com/storage/v1/object/public/audio/...
✓ 成功 (耗时: 12.34秒)
  文件大小: 1234567 bytes
  实际时长: 8.00秒

============================================================
✅ 测试完成!
总耗时: 45.67秒
成功: 4/4
失败: 0/4
平均生成时间: 11.42秒

📊 结果已保存:
  详细结果: audio_test_output/reports/audio_test_results_20241201_143522.json
  CSV数据: audio_test_output/reports/audio_test_results_20241201_143522.csv
  统计报告: audio_test_output/reports/audio_test_report_20241201_143522.json

📈 基础统计:
  成功率: 100.0%
  平均生成时间: 11.42秒
  平均时长: 8.00秒
  平均文件大小: 1234567 bytes

🎯 人工评估界面已生成: audio_test_output/evaluation/human_evaluation.html
请在浏览器中打开此文件进行人工评估
```

## 评估界面

### 功能
- 英文界面，支持音频播放
- 4个评估维度: Relevance, Audio Quality, Listening Enjoyment, Usability
- 支持详细评论
- 自动保存评估结果

### 评估维度说明
1. **Relevance (相关性)** - 音频内容与prompt的匹配程度
2. **Audio Quality (音频质量)** - 技术层面的音频质量
3. **Listening Enjoyment (听感享受)** - 主观的听觉体验
4. **Usability (可用性)** - 作为放松产品的实用性

### 使用方法
1. 打开生成的HTML文件
2. 播放每个音频样本
3. 为每个维度打分 (1-5分)
4. 填写详细评论
5. 点击"Save Evaluation Results"保存结果

## 环境要求

### Gemini环境
```bash
# 安装依赖
pip install -r requirements-gemini-utf8.txt

# 设置环境变量
set GOOGLE_API_KEY=your_gemini_api_key
```

### Stable Audio环境
```bash
# 安装依赖
pip install -r requirements-stable-audio.txt

# 设置环境变量
set SUPABASE_URL=your_supabase_url
set SUPABASE_KEY=your_supabase_key
set HUGGINGFACE_TOKEN=your_hf_token
```

## 故障排除

### 常见问题

1. **Gemini API错误**
   - 检查API密钥是否正确设置
   - 确认网络连接正常

2. **音频生成失败**
   - 确认Stable Audio环境已正确安装
   - 检查HuggingFace token是否有效

3. **Supabase上传失败**
   - 检查Supabase配置
   - 确认存储桶权限设置

4. **音频无法播放**
   - 检查网络连接
   - 确认Supabase URL可访问

### 调试模式
在脚本中添加更多调试信息：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 扩展功能

### 自定义测试用例
修改 `generate_prompts.py` 中的 `create_test_cases()` 方法：
```python
def create_test_cases(self) -> List[Dict[str, Any]]:
    return [
        {"id": "custom_1", "mode": "focus"},
        {"id": "custom_2", "mode": "relax"},
        # 添加更多测试用例
    ]
```

### 自定义评估维度
修改 `test_audio_generation.py` 中的HTML模板，添加新的评估维度。

### 批量处理
可以修改脚本支持批量处理多个prompt文件：
```python
# 处理所有prompt文件
prompt_files = list(Path("generated_prompts").glob("*.json"))
for prompt_file in prompt_files:
    results = await tester.run_batch_test(str(prompt_file))
``` 