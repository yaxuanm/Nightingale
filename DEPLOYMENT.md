# Nightingale 部署说明

## 🎯 部署目标

将 Nightingale 项目部署到目标机器上，包括环境设置、模型下载和服务启动。

## 📋 系统要求

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

### 方案2：离线部署（无网络环境）

**适用场景**: 目标机器无法访问互联网或网络受限

#### 步骤1：准备离线包
在源机器上创建包含模型的完整包：

```bash
# 方式1：从 GitHub 克隆后准备
git clone https://github.com/your-username/Nightingale.git
cd Nightingale

# 方式2：如果已有项目，直接使用
# cd Nightingale

# 创建部署目录
mkdir Nightingale_Offline_Deploy
xcopy . Nightingale_Offline_Deploy\Nightingale /E /I /H

# 复制模型文件
mkdir Nightingale_Offline_Deploy\model_cache
xcopy "%USERPROFILE%\.cache\huggingface\hub\models--stabilityai--stable-audio-open-small" Nightingale_Offline_Deploy\model_cache\models--stabilityai--stable-audio-open-small /E /I /H

# 创建安装脚本
echo @echo off > Nightingale_Offline_Deploy\install.bat
echo echo 正在安装 Nightingale... >> Nightingale_Offline_Deploy\install.bat
echo mkdir "%USERPROFILE%\.cache\huggingface\hub" 2^>nul >> Nightingale_Offline_Deploy\install.bat
echo xcopy model_cache\* "%USERPROFILE%\.cache\huggingface\hub\" /E /I /H >> Nightingale_Offline_Deploy\install.bat
echo cd Nightingale >> Nightingale_Offline_Deploy\install.bat
echo start_clean_new.bat >> Nightingale_Offline_Deploy\install.bat
echo pause >> Nightingale_Offline_Deploy\install.bat

# 压缩部署包
powershell Compress-Archive -Path Nightingale_Offline_Deploy -DestinationPath Nightingale_Offline_Deploy.zip
```

#### 步骤2：在目标机器上安装
```bash
# 解压部署包（如果是 ZIP 文件）
# 或直接复制文件夹到目标机器
# 运行安装脚本
install.bat
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

# 可选的 API 密钥
STABILITY_API_KEY=your-stability-api-key-here
SUPABASE_URL=your-supabase-url-here
SUPABASE_ANON_KEY=your-supabase-anon-key-here
```

## 📊 部署检查清单

### 环境检查
- [ ] Git 2.0+ 已安装
- [ ] Python 3.11 已安装（必需）
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

#### 9. Python 3.12 兼容性错误
```bash
# 如果出现 "AttributeError: module 'pkgutil' has no attribute 'ImpImporter'" 错误
# 运行修复脚本
./backend/scripts/fix_python312_compatibility.bat

# 或者手动修复
cd backend
# 修复 venv_stableaudio
call venv_stableaudio\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel pkg_resources
pip install -r requirements-stable-audio.txt --no-cache-dir

# 修复 venv_gemini
call venv_gemini\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel pkg_resources
pip install -r requirements-gemini-utf8.txt --no-cache-dir

# 修复 venv_audio
call venv_audio\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel pkg_resources
pip install -r requirements-audio.txt --no-cache-dir
```

#### 10. Stable Audio Int32 溢出错误
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

#### 11. 模型下载失败
```bash
# 清理缓存重新下载
rmdir /s /q "%USERPROFILE%\.cache\huggingface\hub\models--stabilityai--stable-audio-open-small"
# 重新启动 Stable Audio 服务
```

#### 12. 端口被占用
```bash
# 检查端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :8001
netstat -ano | findstr :3000

# 结束占用进程
taskkill /PID {进程ID} /F
```

#### 13. 内存不足
```bash
# 关闭其他程序释放内存
# 或使用 CPU 模式（较慢但内存占用少）
```

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