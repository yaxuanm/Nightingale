# Stable Audio Open Small 模型测试

本目录包含针对 Stable Audio Open Small 模型的测试文件。

## 文件说明

### 测试文件
- `test_stable_audio_model.py` - 完整的模型测试套件
- `test_model_comparison.py` - 模型对比和性能测试
- `test_audio_generation.py` - 原有音频生成测试
- `test_audio_service.py` - 原有音频服务测试
- `test_frontend_integration.py` - 前端集成测试

### 运行脚本
- `run_stable_audio_tests.py` - 完整的测试运行脚本
- `test_stable_audio_simple.py` - 简单测试脚本

## 环境要求

### Python 版本
- Python 3.8 或更高版本

### 依赖包
```bash
pip install stable-audio-tools einops psutil pytest requests
```

### 系统要求
- 至少 4GB RAM
- 推荐使用 GPU (CUDA 支持)
- 至少 2GB 可用磁盘空间

## 快速开始

### 1. 安装依赖
```bash
cd backend
pip install -r requirements.txt
```

### 2. 运行简单测试
```bash
python test_stable_audio_simple.py
```

### 3. 运行完整测试
```bash
python run_stable_audio_tests.py
```

### 4. 运行 pytest 测试
```bash
# 运行所有测试
pytest tests/ -v

# 运行特定测试
pytest tests/test_stable_audio_model.py -v

# 运行性能测试
pytest tests/test_model_comparison.py -v
```

## 测试内容

### 基础功能测试
- 模型初始化
- 模型加载
- 音频生成
- 文件格式验证
- 时长限制检查

### 性能测试
- 模型加载时间
- 音频生成速度
- 内存使用情况
- CPU 使用情况
- 文件大小分析

### 质量测试
- 音频质量指标
- 采样率验证
- 声道数检查
- 振幅分析
- 比特率计算

### 集成测试
- API 端点测试
- 前端集成测试
- 错误处理测试
- 参数验证测试

## API 端点

### 生成音频
```http
POST /api/generate-stable-audio
Content-Type: application/json

{
  "prompt": "128 BPM tech house drum loop",
  "duration": 5.0,
  "steps": 8,
  "cfg_scale": 1.0,
  "sampler_type": "pingpong"
}
```

### 获取模型信息
```http
GET /api/stable-audio-info
```

## 测试结果

测试结果将保存在以下位置：
- 音频文件：`backend/audio_output/`
- 测试报告：`backend/tests/comparison_results/`

### 结果文件格式
- `loading_time_YYYYMMDD_HHMMSS.json` - 加载时间测试结果
- `generation_speed_YYYYMMDD_HHMMSS.json` - 生成速度测试结果
- `audio_quality_YYYYMMDD_HHMMSS.json` - 音频质量测试结果
- `resource_usage_YYYYMMDD_HHMMSS.json` - 资源使用测试结果

## 故障排除

### 常见问题

1. **导入错误**
   ```
   ImportError: No module named 'stable_audio_tools'
   ```
   解决方案：`pip install stable-audio-tools`

2. **CUDA 错误**
   ```
   RuntimeError: CUDA out of memory
   ```
   解决方案：减少 batch size 或使用 CPU

3. **模型下载失败**
   ```
   ConnectionError: Failed to download model
   ```
   解决方案：检查网络连接，或手动下载模型

4. **内存不足**
   ```
   MemoryError: Not enough memory
   ```
   解决方案：关闭其他程序，或使用更小的模型

### 调试模式

启用详细日志：
```bash
export PYTHONPATH=.
python -u test_stable_audio_simple.py
```

## 性能基准

### 预期性能指标

| 指标 | 预期值 | 说明 |
|------|--------|------|
| 模型加载时间 | < 30秒 | 首次加载 |
| 音频生成时间 | < 10秒/3秒音频 | 3秒音频生成 |
| 内存使用 | < 4GB | 模型加载后 |
| 文件大小 | ~500KB/3秒 | 44.1kHz 立体声 |

### 硬件要求

| 硬件 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 4核心 | 8核心 |
| RAM | 8GB | 16GB |
| GPU | 可选 | RTX 3060+ |
| 存储 | 10GB | 20GB SSD |

## 贡献

欢迎提交测试改进和新的测试用例！

### 添加新测试
1. 在 `tests/` 目录下创建新的测试文件
2. 遵循现有的命名约定
3. 添加适当的文档说明
4. 确保测试可以独立运行

### 报告问题
请包含以下信息：
- Python 版本
- 操作系统
- 错误日志
- 复现步骤 