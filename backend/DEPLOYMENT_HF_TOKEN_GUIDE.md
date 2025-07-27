# Hugging Face Token 部署指南

## 为什么需要 Hugging Face Token？

Stable Audio 模型 (`stabilityai/stable-audio-open-small`) 是一个受限的模型，需要 Hugging Face 认证才能访问。每个部署环境都需要设置 token。

## 快速设置步骤

### 1. 获取 Hugging Face Token

1. 访问 https://huggingface.co/settings/tokens
2. 登录或注册 Hugging Face 账户
3. 点击 "New token"
4. 选择 "Read" 权限
5. 复制生成的 token

### 2. 设置 Token

#### 方法一：使用脚本（推荐）
```bash
cd backend
python scripts/set_hf_token.py
```

#### 方法二：手动设置环境变量
```bash
# Windows
set HF_TOKEN=your_token_here

# Linux/Mac
export HF_TOKEN=your_token_here
```

### 3. 验证设置
```bash
python scripts/test_hf_token.py
```

## 部署检查清单

- [ ] 获取 Hugging Face token
- [ ] 设置环境变量
- [ ] 验证 token 有效性
- [ ] 测试模型访问权限

## 常见问题

### Q: 为什么需要 token？
A: Stable Audio 模型是受限的，需要认证才能下载和使用。

### Q: 每个用户都需要自己的 token 吗？
A: 是的，每个部署环境都需要独立的 token。

### Q: token 会过期吗？
A: 默认不会过期，但建议定期检查。

### Q: 如何检查 token 是否有效？
A: 运行 `python scripts/test_hf_token.py`

## 自动化部署脚本

可以创建一个批处理脚本来自动化这个过程：

```bash
# setup_deployment.bat (Windows)
@echo off
echo 正在设置 Hugging Face Token...
python scripts/set_hf_token.py
if %errorlevel% neq 0 (
    echo Token 设置失败
    pause
    exit /b 1
)
echo Token 设置成功！
python scripts/test_hf_token.py
pause
```

## 安全注意事项

1. **不要将 token 提交到代码仓库**
2. **使用环境变量而不是硬编码**
3. **定期轮换 token**
4. **限制 token 权限为只读** 