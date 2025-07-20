# GitHub 上传指南

## 准备工作

### 1. 初始化Git仓库（如果还没有）
```bash
# 在项目根目录
git init
```

### 2. 添加所有文件到Git
```bash
# 添加所有文件（包括虚拟环境）
git add .

# 检查要提交的文件
git status
```

### 3. 创建初始提交
```bash
git commit -m "Initial commit: Nightingale audio processing app

- React frontend with Material-UI
- Python FastAPI backend
- AI audio generation with AudioCraft
- Share functionality with unique URLs
- Download audio and background images
- Virtual environments for different AI services
- Comprehensive documentation and setup guides"
```

## 上传到GitHub

### 1. 创建GitHub仓库
1. 访问 [GitHub](https://github.com)
2. 点击 "New repository"
3. 仓库名称：`Nightingale`
4. 描述：`Modern audio processing app with AI generation capabilities`
5. 选择 "Public" 或 "Private"
6. **不要** 初始化README（因为我们已经有了）
7. 点击 "Create repository"

### 2. 连接本地仓库到GitHub
```bash
# 添加远程仓库（替换yourusername为你的GitHub用户名）
git remote add origin https://github.com/yourusername/Nightingale.git

# 验证远程仓库
git remote -v
```

### 3. 推送到GitHub
```bash
# 推送主分支
git branch -M main
git push -u origin main
```

## 文件结构说明

### 包含的虚拟环境
- `venv_gemini/` - Google Generative AI开发环境
- `venv_stableaudio/` - Stable Audio AI开发环境

### 主要目录
```
Nightingale/
├── ambiance-weaver-react/     # React前端
├── backend/                   # Python FastAPI后端
├── ambiance-weaver-native/    # React Native应用（开发中）
├── docs/                     # 文档和测试文件
├── scripts/                  # 工具脚本
├── venv_gemini/             # Gemini虚拟环境
├── venv_stableaudio/        # Stable Audio虚拟环境
├── README.md                 # 项目说明
├── .gitignore               # Git忽略文件
└── background-image-prompt.md # 背景图片生成指南
```

## 重要文件说明

### 1. README.md
- 完整的项目介绍
- API keys设置说明
- 详细的安装和运行指南
- 虚拟环境说明

### 2. .gitignore
- 排除了不必要的文件
- **保留了虚拟环境** (`venv_gemini/`, `venv_stableaudio/`)
- 排除了大型音频/图片文件但保留了一些样本

### 3. backend/env.example
- 环境变量模板
- 包含所有需要的API keys说明

## 上传后的验证

### 1. 检查文件是否上传成功
```bash
# 在GitHub上检查以下文件是否存在：
- README.md
- .gitignore
- backend/env.example
- venv_gemini/ (文件夹)
- venv_stableaudio/ (文件夹)
- ambiance-weaver-react/ (文件夹)
- backend/ (文件夹)
```

### 2. 测试克隆
```bash
# 测试从GitHub克隆项目
git clone https://github.com/yourusername/Nightingale.git
cd Nightingale
ls -la
```

## 后续维护

### 1. 更新代码
```bash
# 修改代码后
git add .
git commit -m "描述你的更改"
git push origin main
```

### 2. 添加新功能
```bash
# 创建新分支
git checkout -b feature/new-feature
# 开发新功能
git add .
git commit -m "Add new feature"
git push origin feature/new-feature
# 在GitHub上创建Pull Request
```

### 3. 更新文档
```bash
# 更新README或其他文档
git add README.md
git commit -m "Update documentation"
git push origin main
```

## 注意事项

### 1. 虚拟环境
- 虚拟环境已经包含在仓库中
- 用户可以直接使用这些环境
- 如果需要重新创建环境，参考README中的说明

### 2. API Keys
- 不要将真实的API keys上传到GitHub
- 使用 `backend/env.example` 作为模板
- 用户需要自己创建 `.env` 文件并填入真实的API keys

### 3. 大文件
- 音频和图片文件被排除在Git之外
- 保留了一些样本文件用于测试
- 如果需要共享音频文件，考虑使用云存储

## 故障排除

### 1. 如果推送失败
```bash
# 检查网络连接
ping github.com

# 检查Git配置
git config --list

# 重新设置远程仓库
git remote remove origin
git remote add origin https://github.com/yourusername/Nightingale.git
```

### 2. 如果文件太大
```bash
# 检查大文件
git ls-files | xargs ls -lh | sort -k5 -hr | head -10

# 如果虚拟环境太大，可以考虑压缩
# 或者只上传requirements文件，让用户自己创建环境
```

### 3. 如果需要删除敏感信息
```bash
# 从Git历史中删除敏感文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch path/to/sensitive/file" \
  --prune-empty --tag-name-filter cat -- --all
```

## 完成！

上传成功后，你的项目将包含：
- ✅ 完整的React前端应用
- ✅ Python FastAPI后端
- ✅ 虚拟环境配置
- ✅ 详细的文档和设置指南
- ✅ API keys配置说明
- ✅ 背景图片生成指南

用户可以通过以下步骤快速开始：
1. 克隆仓库
2. 设置API keys
3. 启动后端和前端
4. 开始使用应用

🎉 恭喜！你的Nightingale项目已经成功上传到GitHub！ 