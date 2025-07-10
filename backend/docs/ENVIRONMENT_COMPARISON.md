# 环境依赖对比文档

## 环境概览

本项目使用多个虚拟环境来隔离不同功能的依赖，避免版本冲突。

### 1. API环境 (venv_api)
**文件**: `requirements-api.txt`
**用途**: 完整功能环境，包含所有服务
**特点**: 
- 包含Stable Audio、Gemini、图像生成等所有功能
- protobuf 3.19.6
- numpy 1.23.5 (修复int32溢出问题)
- 适合开发和测试

**主要依赖**:
- fastapi==0.115.14
- stable-audio-tools==0.0.19
- google-generativeai==0.8.5
- torch==2.7.1
- supabase==1.0.3

### 2. Stable Audio环境 (venv_stableaudio)
**文件**: `requirements-stable-audio.txt`
**用途**: 专注于音频生成功能
**特点**:
- 专门用于Stable Audio模型
- protobuf 3.19.6 (兼容Stable Audio)
- 更新的supabase版本 (2.16.0)
- 优化的音频处理依赖

**主要依赖**:
- stable-audio-tools==0.0.19
- torch==2.7.1
- protobuf==3.19.6
- supabase==2.16.0

### 3. Gemini环境 (venv_gemini)
**文件**: `requirements-gemini-utf8.txt`
**用途**: 专注于Gemini API功能
**特点**:
- 专门用于Google Generative AI
- protobuf 4.25.8 (Gemini兼容)
- 包含新旧两个Gemini客户端
- 轻量级音频处理

**主要依赖**:
- google-generativeai==0.8.5
- google-genai==1.24.0
- protobuf==4.25.8
- supabase==1.0.3

### 4. Audio环境 (venv_audio)
**文件**: `requirements-audio.txt`
**用途**: 音频处理工具环境
**特点**:
- 包含demucs、audiocraft等音频工具
- protobuf 5.29.5 (最新版本)
- 完整的音频处理生态
- 适合音频分离和处理

**主要依赖**:
- demucs==4.0.1
- audiocraft==1.0.0
- protobuf==5.29.5
- numpy==1.26.4

### 5. 主环境 (requirements.txt)
**用途**: 基础功能环境
**特点**:
- 最小化依赖
- 核心Web服务
- 基础音频处理
- 适合部署

## 版本冲突解决方案

### protobuf版本冲突
- **API环境**: protobuf 3.19.6 (兼容Stable Audio)
- **Stable Audio环境**: protobuf 3.19.6 (必需)
- **Gemini环境**: protobuf 4.25.8 (必需)
- **Audio环境**: protobuf 5.29.5 (最新)

### numpy版本冲突
- **API/Stable Audio环境**: numpy 1.23.5 (修复int32溢出)
- **Gemini环境**: numpy 2.2.6 (最新)
- **Audio环境**: numpy 1.26.4 (中间版本)

## 环境选择建议

1. **开发测试**: 使用API环境 (venv_api)
2. **音频生成**: 使用Stable Audio环境 (venv_stableaudio)
3. **图像生成**: 使用Gemini环境 (venv_gemini)
4. **音频处理**: 使用Audio环境 (venv_audio)
5. **生产部署**: 使用主环境 (requirements.txt)

## 安装说明

```bash
# 激活API环境
.\venv_api\Scripts\Activate.ps1
pip install -r requirements-api.txt

# 激活Stable Audio环境
.\venv_stableaudio\Scripts\Activate.ps1
pip install -r requirements-stable-audio.txt

# 激活Gemini环境
.\venv_gemini\Scripts\Activate.ps1
pip install -r requirements-gemini-utf8.txt

# 激活Audio环境
.\venv_audio\Scripts\Activate.ps1
pip install -r requirements-audio.txt
``` 