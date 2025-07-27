# Nightingale 快速部署指南

## 🚀 一键部署（推荐）

### Windows
```bash
cd backend
scripts\setup_deployment.bat
```

### Linux/Mac
```bash
cd backend
chmod +x scripts/setup_deployment.sh
./scripts/setup_deployment.sh
```

## 🔧 手动部署步骤

### 1. 设置 Hugging Face Token（必需）

```bash
cd backend
python scripts/set_hf_token.py
```

**或者手动设置：**
```bash
# Windows
set HF_TOKEN=your_token_here

# Linux/Mac  
export HF_TOKEN=your_token_here
```

### 2. 设置 Google API Key（必需）

编辑 `.env` 文件：
```env
GOOGLE_API_KEY=your-google-api-key-here
```

### 3. 验证配置

```bash
python scripts/test_hf_token.py
```

### 4. 修复 Stable Audio 兼容性问题（Windows 必需）

```bash
# 修复 stable-audio-tools 中的 int32 溢出问题
python scripts/stable_audio_fix.py
```

### 5. 启动服务

```bash
# 启动所有服务
./start_clean.bat  # Windows
./start_clean.sh   # Linux/Mac
```

## 📋 部署检查清单

- [ ] 获取 Hugging Face token
- [ ] 获取 Google API key  
- [ ] 设置环境变量
- [ ] 验证 token 有效性
- [ ] 修复 Stable Audio 兼容性问题（Windows 必需）
- [ ] 测试服务启动

## 🆘 常见问题

### Q: 提示"未设置 Hugging Face Token"
**A:** 运行 `python scripts/set_hf_token.py`

### Q: 提示"无法访问模型"
**A:** 确保 Hugging Face 账户有访问 `stable-audio-open-small` 的权限

### Q: 网络连接失败
**A:** 检查网络连接和防火墙设置

### Q: Stable Audio 服务启动失败
**A:** 运行 `python scripts/stable_audio_fix.py` 修复兼容性问题

## 📞 获取 API Keys

1. **Hugging Face Token**: https://huggingface.co/settings/tokens
2. **Google API Key**: https://makersuite.google.com/app/apikey

---

**注意**: 每个部署环境都需要独立的 API keys，不能共享使用。 