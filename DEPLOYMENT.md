# Nightingale 部署说明

## 🎯 部署目标

将 Nightingale 项目部署到目标机器上，包括环境设置、模型下载和服务启动。项目专注于Web平台，提供AI驱动的音频生成和批量测试功能。

## 📋 系统要求

### 项目架构
```
Nightingale/
├── ambiance-weaver-react/        # Web 前端 (React)
│   ├── src/components/           # UI 组件 (Player, Chat, 等)
│   ├── src/utils/                # 工具和上下文
│   ├── src/theme/                # 主题和样式
│   ├── public/                   # 静态资源
│   └── package.json
│
├── backend/                      # 后端 API (Python FastAPI)
│   ├── app/main.py               # 主 FastAPI 应用
│   ├── app/services/             # 音频、图像、AI 服务
│   ├── requirements.txt          # Python 依赖
│   ├── scripts/                  # 批处理/测试/工具脚本
│   └── .env.example              # 环境变量模板
│
├── docs/                         # 文档和测试页面
├── scripts/                      # 项目级脚本
├── DEPLOYMENT.md                 # 部署说明文档
├── start_clean_new.bat           # 一键启动脚本
└── start_instructions.txt        # 完整环境和启动指南
```

### 技术栈
- **前端**: React 18, TypeScript, Material-UI, Framer Motion
- **后端**: Python 3.11, FastAPI, Uvicorn, HuggingFace, Google Generative AI, Stability AI Stable Audio
- **部署**: 支持本地部署和虚拟机部署

### 最低要求
- **操作系统**: Windows 10/11
- **Python**: 3.11（必需，不支持3.12或3.13）
- **Node.js**: 18.0+
- **npm**: 8.0+
- **Git**: 2.0+（用于克隆项目）
- **内存**: 8GB RAM
- **存储**: 10GB 可用空间
- **网络**: 稳定的网络连接（首次下载模型）

### 推荐配置
- **内存**: 16GB RAM
- **存储**: 20GB SSD
- **GPU**: 支持 CUDA 的 GPU（可选，用于加速）

## 🚀 部署方案

### 方案1：自动部署（推荐）

**适用场景**: 目标机器有网络连接，可以自动下载模型

#### 步骤1：获取项目

**方式1：从 GitHub 克隆（推荐）**
```bash
# 克隆项目仓库
git clone https://github.com/your-username/Nightingale.git
cd Nightingale
```

**方式2：使用 Git 指定分支**
```bash
# 克隆特定分支
git clone -b main https://github.com/your-username/Nightingale.git
cd Nightingale

# 或克隆最新版本
git clone --depth 1 https://github.com/your-username/Nightingale.git
cd Nightingale
```

**方式3：下载压缩包（备选）**
```bash
# 从 GitHub 下载 ZIP 文件
# 访问: https://github.com/your-username/Nightingale
# 点击 "Code" -> "Download ZIP"
# 解压到目标目录
cd Nightingale
```

#### 步骤2：环境设置
```bash
# 运行环境设置脚本
./start_clean_new.bat
# 选择 5 (Setup Environment)
# 等待环境设置完成（约5-10分钟）
```

#### 步骤3：修复 Stable Audio 兼容性问题
```bash
# 修复 stable-audio-tools 中的 int32 溢出问题（Windows 64位系统必需）
cd backend
.\venv_stableaudio\Scripts\activate
python scripts/stable_audio_fix.py
```

#### 步骤4：启动服务
```bash
# 启动 Stable Audio 服务（首次运行会下载模型）
./start_clean_new.bat
# 选择 2 (Start Stable Audio Service)
# 等待模型下载完成（约5-15分钟，取决于网络速度）
```

#### 步骤5：启动所有服务
```bash
# 启动所有服务
./start_clean_new.bat
# 选择 4 (Start All Services)
```

### 方案3：分步部署（适合调试）

#### 步骤1：获取项目并检查系统要求

**获取项目**：
```bash
# 从 GitHub 克隆项目
git clone https://github.com/your-username/Nightingale.git
cd Nightingale
```

**检查系统要求**：
```bash
# 检查 Python 版本（必须是3.11）
python --version

# 检查 Node.js 版本
node --version

# 检查 npm 版本
npm --version

# 检查 Git 版本
git --version
```

#### 步骤2：环境设置
```bash
cd backend
python scripts/setup_environments.bat
```

#### 步骤3：修复 Stable Audio 兼容性问题
```bash
# 修复 stable-audio-tools 中的 int32 溢出问题（Windows 64位系统必需）
cd backend
.\venv_stableaudio\Scripts\activate
python scripts/stable_audio_fix.py
```

#### 步骤4：手动下载模型
```bash
# 激活 Stable Audio 环境
venv_stableaudio\Scripts\activate

# 下载模型
python -c "from stable_audio_tools import get_pretrained_model; model, config = get_pretrained_model('stabilityai/stable-audio-open-small'); print('模型下载完成')"

# 退出环境
deactivate
```

#### 步骤5：启动服务
```bash
# 启动 Gemini API 服务
./start_clean_new.bat
# 选择 1

# 启动 Stable Audio 服务
./start_clean_new.bat
# 选择 2

# 启动前端服务
./start_clean_new.bat
# 选择 3
```

## 🔧 服务配置

### 服务端口
- **Gemini API**: http://127.0.0.1:8000
- **Stable Audio**: http://127.0.0.1:8001
- **前端**: http://localhost:3000
- **批量测试**: http://127.0.0.1:8010

### API 密钥配置
在 `backend/.env` 文件中配置：

```env
# 必需的 API 密钥
GOOGLE_API_KEY=your-google-api-key-here
STABILITY_API_KEY=your-stability-api-key-here
SUPABASE_URL=your-supabase-url-here
SUPABASE_ANON_KEY=your-supabase-anon-key-here
HF_TOKEN=your-hugging-face-token
```

## 📊 部署检查清单

### 环境检查
- [ ] Git 2.0+ 已安装
- [ ] Python 3.11 已安装
- [ ] Node.js 18.0+ 已安装
- [ ] npm 8.0+ 已安装
- [ ] 项目克隆成功
- [ ] 虚拟环境创建成功
- [ ] 依赖包安装完成

### 模型检查
- [ ] Stable Audio 模型已下载
- [ ] 模型文件位于: `%USERPROFILE%\.cache\huggingface\hub\models--stabilityai--stable-audio-open-small`
- [ ] 模型大小约 1-2GB

### 服务检查
- [ ] Gemini API 服务启动成功
- [ ] Stable Audio 服务启动成功
- [ ] 前端服务启动成功
- [ ] 所有端口可访问

### 功能检查
- [ ] 音频生成功能正常
- [ ] 批量测试功能正常
- [ ] Web 界面可访问
- [ ] API 文档可访问

## 🚨 故障排除

### 常见问题

#### 1. Python 版本错误
```bash
# 检查 Python 版本
python --version

# 如果版本不是 3.11，请安装 Python 3.11
# 下载地址：https://www.python.org/downloads/release/python-3119/
```

#### 2. 项目克隆失败
```bash
# 检查网络连接
ping github.com

# 重新克隆
rmdir /s /q Nightingale
git clone https://github.com/your-username/Nightingale.git
```

#### 3. 环境设置失败
```bash
# 解决方案
rmdir /s /q venv_*
./start_clean_new.bat
# 选择 5 重新设置环境
```

#### 4. 脚本路径错误
```bash
# 如果出现 "not recognized as an internal or external command" 错误
# 检查文件路径是否正确
dir backend\scripts\setup_environments.bat

# 如果文件不存在，重新下载项目
git clone https://github.com/your-username/Nightingale.git
```

#### 5. 虚拟环境创建失败
```bash
# 如果出现 "The system cannot find the path specified" 错误
# 清理现有环境重新创建
rmdir /s /q venv_*
python -m venv venv_stableaudio
python -m venv venv_gemini

# 手动激活并安装依赖
call venv_stableaudio\Scripts\activate.bat
pip install -r requirements-stable-audio.txt
call venv_stableaudio\Scripts\deactivate.bat

call venv_gemini\Scripts\activate.bat
pip install -r requirements-gemini-utf8.txt
call venv_gemini\Scripts\deactivate.bat
```

#### 6. NVM 路径提示（可忽略）
```bash
# 如果出现 "Enter the absolute path where the nvm-windows zip file" 提示
# 这是系统安装程序的提示，与项目无关
# 直接按 Ctrl+C 取消，然后重新运行环境设置
```

#### 7. NVM 持续干扰（推荐使用专用脚本）
```bash
# 如果 NVM 提示持续出现，使用专用部署脚本
./deploy_without_nvm.bat

# 或者手动临时禁用 NVM
ren "%APPDATA%\nvm" "nvm_backup"
# 运行环境设置
./start_clean_new.bat
# 完成后恢复
ren "%APPDATA%\nvm_backup" "nvm"
```

#### 8. setuptools 安装错误
```bash
# 如果出现 "Cannot import 'setuptools.build_meta'" 错误
# 运行修复脚本
./backend/scripts/fix_setuptools.bat

# 或者手动修复
cd backend
call venv_stableaudio\Scripts\activate.bat
python -m pip install --upgrade setuptools wheel
pip install -r requirements-stable-audio.txt

call venv_gemini\Scripts\activate.bat
python -m pip install --upgrade setuptools wheel
pip install -r requirements-gemini-utf8.txt
```

#### 9. Stable Audio Int32 溢出错误
```bash
# 如果出现 "OverflowError: Python int too large to convert to C long" 错误
# 运行修复脚本
cd backend
.\venv_stableaudio\Scripts\activate
python scripts/stable_audio_fix.py

# 修复完成后重新启动 Stable Audio 服务
./start_clean_new.bat
# 选择 2 (Start Stable Audio Service)
```

#### 10. 模型下载失败
```bash
# 清理缓存重新下载
rmdir /s /q "%USERPROFILE%\.cache\huggingface\hub\models--stabilityai--stable-audio-open-small"
# 重新启动 Stable Audio 服务
```

#### 11. 端口被占用
```bash
# 检查端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :8001
netstat -ano | findstr :3000

# 结束占用进程
taskkill /PID {进程ID} /F
```

#### 12. 内存不足
```bash
# 关闭其他程序释放内存
# 或使用 CPU 模式（较慢但内存占用少）
```

#### 13. 500 Internal Server Error - FFmpeg 路径问题
```bash
# 如果出现 500 Internal Server Error，可能是 FFmpeg 路径问题
# 在虚拟环境中设置 FFmpeg 路径

# 对于 Stable Audio 环境
cd backend
.\venv_stableaudio\Scripts\activate
set PATH=%PATH%;C:\ffmpeg\bin
# 或者将 FFmpeg 添加到系统 PATH

# 对于 Gemini 环境
cd backend
.\venv_gemini\Scripts\activate
set PATH=%PATH%;C:\ffmpeg\bin

# 验证 FFmpeg 是否可用
ffmpeg -version

# 如果 FFmpeg 未安装，下载并安装：
# 1. 访问 https://ffmpeg.org/download.html
# 2. 下载 Windows 版本
# 3. 解压到 C:\ffmpeg
# 4. 将 C:\ffmpeg\bin 添加到系统 PATH
```

#### 14. 500 Internal Server Error - 代码级 FFmpeg 解决方案
如果上述方法仍然无法解决 500 错误，可以在代码中直接设置 FFmpeg 路径：

**在 main.py 文件开头添加以下代码：**
```python
import os
import warnings
from dotenv import load_dotenv

# 设置 FFmpeg PATH - 确保 pydub 能找到 FFmpeg
ffmpeg_path = r"C:\ffmpeg\ffmpeg-master-latest-win64-gpl-shared\bin"
if ffmpeg_path not in os.environ["PATH"]:
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ["PATH"]

# 忽略 ffmpeg 警告
warnings.filterwarnings("ignore", message="Couldn't find ffprobe or avprobe")
```

**或者创建环境变量文件 (.env)：**
```bash
# .env 文件内容
FFMPEG_PATH=C:\ffmpeg\ffmpeg-master-latest-win64-gpl-shared\bin
```

**然后在代码中读取：**
```python
import os
from dotenv import load_dotenv

load_dotenv()  # 加载 .env 文件

# 从环境变量读取 FFmpeg 路径
ffmpeg_path = os.getenv('FFMPEG_PATH', r"C:\ffmpeg\ffmpeg-master-latest-win64-gpl-shared\bin")
if ffmpeg_path not in os.environ["PATH"]:
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ["PATH"]
```

**注意事项：**
- 确保 FFmpeg 路径正确
- 路径中不要有中文字符
- 重启服务后生效
- 这种方法可以解决 pydub 找不到 FFmpeg 的问题

### 调试模式

启用详细日志：
```bash
# 设置环境变量
set DEBUG=True
set LOG_LEVEL=DEBUG

# 重新启动服务
```

## 📝 版本说明

### 当前版本要求
- **Python**: 3.11（必需，不支持3.12或3.13）
- **Node.js**: 18.0+
- **npm**: 8.0+
- **Git**: 2.0+

### 兼容性说明
- 不支持 Python 3.12 或 3.13（存在兼容性问题）
- 推荐使用 Python 3.11.9
- 如果使用其他版本，请降级到 Python 3.11

## 🔄 Git 同步说明

### 同步到 GitHub
```bash
# 添加所有更改
git add .

# 提交更改
git commit -m "Update deployment instructions and Python version requirements"

# 推送到远程仓库
git push origin main
```

### 从 GitHub 同步
```bash
# 拉取最新更改
git pull origin main

# 如果有冲突，解决冲突后重新提交
git add .
git commit -m "Resolve merge conflicts"
git push origin main
```

### 注意事项
- 同步时会保留本地更改
- 删除的文件不会自动删除（需要手动处理）
- 建议在同步前备份重要文件 