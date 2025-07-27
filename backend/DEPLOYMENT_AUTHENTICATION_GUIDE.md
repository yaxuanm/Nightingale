# Nightingale 部署认证指南

## 🔐 认证概述

Nightingale 是一个**单用户应用**，不需要复杂的用户登录系统，但在部署到不同环境时需要配置相应的 API 密钥和认证信息。

## 📋 部署前检查清单

### 1. API 密钥配置

| 服务 | 必需性 | 获取地址 | 配置方法 |
|------|--------|----------|----------|
| **Hugging Face Token** | ✅ 必需 | https://huggingface.co/settings/tokens | `python scripts/set_hf_token.py` |
| **Google API Key** | ✅ 必需 | https://makersuite.google.com/app/apikey | 手动设置环境变量 |
| **Stability AI Key** | ⚪ 可选 | https://platform.stability.ai/account/keys | `python set_stability_key.py` |

### 2. 环境变量配置

创建 `.env` 文件（基于 `env.example`）：

```bash
cd backend
copy env.example .env
```

编辑 `.env` 文件：

```env
# 必需配置
GOOGLE_API_KEY=your-google-api-key-here
HF_TOKEN=your-huggingface-token-here

# 可选配置
STABILITY_API_KEY=your-stability-api-key-here
SUPABASE_URL=your-supabase-url-here
SUPABASE_ANON_KEY=your-supabase-anon-key-here

# 应用设置
SHARE_BASE_URL=http://localhost:3000
DEBUG=True
LOG_LEVEL=INFO

# 服务器设置
HOST=0.0.0.0
PORT=8000
RELOAD=True
```

## 🚀 快速部署脚本

### Windows 一键部署

```bash
# 运行部署向导
cd backend
scripts\setup_deployment.bat
```

### Linux/Mac 一键部署

```bash
# 运行部署向导
cd backend
chmod +x scripts/setup_deployment.sh
./scripts/setup_deployment.sh
```

## 🔧 手动配置步骤

### 步骤 1: 设置 Hugging Face Token

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

### 步骤 2: 设置 Google API Key

```bash
# 编辑 .env 文件
notepad .env  # Windows
nano .env     # Linux/Mac
```

添加：
```env
GOOGLE_API_KEY=your-google-api-key-here
```

### 步骤 3: 验证配置

```bash
# 测试 Hugging Face Token
python scripts/test_hf_token.py

# 测试 Google API
python scripts/test_gemini_api.py

# 测试完整服务
python scripts/test_all_services.py
```

## 🌐 多环境部署

### 开发环境
```env
REACT_APP_GEMINI_API_URL=http://localhost:8000
REACT_APP_STABLE_AUDIO_API_URL=http://localhost:8001
REACT_APP_FRONTEND_URL=http://localhost:3000
```

### 生产环境
```env
REACT_APP_GEMINI_API_URL=https://api.yourdomain.com:8000
REACT_APP_STABLE_AUDIO_API_URL=https://api.yourdomain.com:8001
REACT_APP_FRONTEND_URL=https://yourdomain.com
```

### 测试环境
```env
REACT_APP_GEMINI_API_URL=https://test-api.yourdomain.com:8000
REACT_APP_STABLE_AUDIO_API_URL=https://test-api.yourdomain.com:8001
REACT_APP_FRONTEND_URL=https://test.yourdomain.com
```

## 🔒 安全最佳实践

### 1. 环境变量管理
- ✅ 使用环境变量而不是硬编码
- ✅ 不要将 `.env` 文件提交到版本控制
- ✅ 定期轮换 API 密钥

### 2. 网络安全
- ✅ 使用 HTTPS 在生产环境
- ✅ 配置防火墙规则
- ✅ 限制 API 访问权限

### 3. 访问控制
- ✅ 限制 token 权限为只读
- ✅ 使用最小权限原则
- ✅ 监控 API 使用情况

## 🛠️ 故障排除

### 常见问题

#### 1. Hugging Face 认证失败
```
❌ 错误：未设置 Hugging Face Token
```
**解决方案：**
```bash
python scripts/set_hf_token.py
```

#### 2. Google API 认证失败
```
❌ 错误：Google API Key 未配置
```
**解决方案：**
```bash
# 编辑 .env 文件
echo GOOGLE_API_KEY=your-key-here >> .env
```

#### 3. 模型访问权限不足
```
❌ 错误：无法访问 stable-audio-open-small 模型
```
**解决方案：**
1. 确保 Hugging Face 账户有访问权限
2. 检查 token 是否有效
3. 重新生成 token

#### 4. 网络连接问题
```
❌ 错误：网络连接失败
```
**解决方案：**
1. 检查网络连接
2. 配置代理（如果需要）
3. 检查防火墙设置

## 📊 监控和日志

### 启用详细日志
```env
LOG_LEVEL=DEBUG
DEBUG=True
```

### 查看服务状态
```bash
# 检查服务运行状态
python scripts/check_services.py

# 查看日志
tail -f logs/app.log
```

## 🔄 更新和维护

### 定期维护任务
1. **每周**：检查 API 使用量
2. **每月**：轮换 API 密钥
3. **每季度**：更新依赖包
4. **每年**：安全审计

### 备份配置
```bash
# 备份环境配置
cp .env .env.backup.$(date +%Y%m%d)

# 恢复配置
cp .env.backup.20241201 .env
```

## 📞 技术支持

如果遇到问题，请：

1. 查看日志文件
2. 运行诊断脚本
3. 检查网络连接
4. 验证 API 密钥
5. 联系技术支持

---

**注意**：这个应用是单用户设计，不需要复杂的用户管理系统。主要认证需求是 API 服务的访问权限。 