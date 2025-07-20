# Stability AI 主要服务 + Gemini Fallback 机制

## 概述

这个项目现在支持双图片生成服务：
1. **Stability AI** (主要) - 优先使用的图片生成服务
2. **Gemini** (备用) - 当Stability AI失败时自动切换

## 设置步骤

### 1. 获取 Stability AI API Key

1. 访问 [Stability AI Platform](https://platform.stability.ai/)
2. 注册账户并登录
3. 进入 [API Keys 页面](https://platform.stability.ai/account/keys)
4. 创建新的 API Key

### 2. 配置 API Key

#### 方法一：使用设置脚本（推荐）
```bash
cd backend
python set_stability_key.py
```

#### 方法二：手动编辑 .env 文件
在项目根目录的 `.env` 文件中添加：
```
STABILITY_API_KEY=your_api_key_here
```

### 3. 测试配置

运行测试脚本验证配置：
```bash
cd backend
python test_stability_ai.py
```

## 工作原理

### Fallback 机制

1. **优先使用 Stability AI**：
   - 系统首先尝试使用 Stability AI 生成图片
   - 如果成功，直接返回结果

2. **自动切换到 Gemini**：
   - 当 Stability AI 失败时（包括余额不足、网络错误等）
   - 系统自动切换到 Gemini
   - 使用相同的描述生成图片

3. **错误处理**：
   - 如果两个服务都失败，返回 `None`
   - 详细的错误日志会显示在控制台

### 错误检测

系统会自动检测以下情况并触发 fallback：
- Stability AI 余额不足
- Stability AI 网络错误
- Stability AI 服务不可用
- Stability AI API 限制

## API 使用

### 图片生成接口

```python
from app.services.image_service import image_service

# 自动使用 Stability AI 优先策略
result = await image_service.generate_background("A peaceful forest scene")
```

### 直接使用 Stability AI

```python
from app.services.stability_image_service import stability_image_service

# 直接使用 Stability AI
result = await stability_image_service.generate_background("A peaceful forest scene")
```

## 配置参数

### Stability AI 参数

在 `stability_image_service.py` 中可以调整以下参数：

```python
data = {
    "text_prompts": [{"text": prompt, "weight": 1}],
    "cfg_scale": 7,        # 创意程度 (1-20)
    "height": 1024,        # 图片高度
    "width": 1024,         # 图片宽度
    "samples": 1,          # 生成数量
    "steps": 30,           # 生成步数
}
```

### 模型选择

当前使用 `stable-diffusion-xl-1024-v1-0` 模型，你也可以修改为其他模型：
- `stable-diffusion-v1-6`
- `stable-diffusion-xl-1024-v1-0`
- `stable-diffusion-xl-1024-v1-0-sdxl-turbo`

## 成本对比

| 服务 | 每张图片成本 | 质量 | 速度 | 优先级 |
|------|-------------|------|------|--------|
| Stability AI | ~$0.01 | 高 | 中等 | 主要 |
| Gemini | ~$0.02 | 高 | 快 | 备用 |

## 故障排除

### 常见问题

1. **API Key 未配置**
   ```
   [WARNING] STABILITY_API_KEY not found in environment variables
   ```
   解决：运行 `python set_stability_key.py`

2. **余额不足**
   ```
   [ERROR] Stability AI: Payment required - insufficient balance
   ```
   解决：在 Stability AI 平台充值

3. **网络错误**
   ```
   [ERROR] Network error calling Stability AI
   ```
   解决：检查网络连接和防火墙设置

### 调试模式

启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 更新日志

- **v1.0**: 初始实现，支持 Stability AI 主要服务 + Gemini fallback
- 自动错误检测和切换
- 完整的测试和配置脚本 