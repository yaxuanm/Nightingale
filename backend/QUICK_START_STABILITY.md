# 🚀 Stability AI Fallback 快速开始

## 一键设置

运行以下命令完成所有配置：

```bash
cd backend
python setup_stability_fallback.py
```

这个脚本会：
1. ✅ 检查Python依赖
2. 🔧 设置 Stability AI API Key
3. 🧪 测试 Stability AI 集成
4. 🔄 测试 fallback 机制
5. 🎉 完成配置

## 手动设置（如果一键设置失败）

### 1. 获取 API Key
访问 [Stability AI Platform](https://platform.stability.ai/account/keys) 获取 API Key

### 2. 设置 API Key
```bash
python set_stability_key.py
```

### 3. 测试配置
```bash
python test_stability_ai.py
```

## 使用方法

### 启动服务
```bash
uvicorn app.main:app --reload --port 8000
```

### 图片生成会自动使用 fallback 机制：
- 🎯 **优先使用 Gemini**
- 🔄 **Gemini 失败时自动切换到 Stability AI**
- ❌ **两个服务都失败时返回 None**

## 查看日志

在控制台日志中，你可以看到：
- `[IMAGE] [GENAI]` - 使用 Gemini 生成
- `[FALLBACK]` - 切换到 Stability AI
- `[IMAGE] [STABILITY]` - 使用 Stability AI 生成

## 故障排除

### 常见问题

1. **API Key 未配置**
   ```
   [WARNING] STABILITY_API_KEY not found
   ```
   **解决**: 运行 `python set_stability_key.py`

2. **余额不足**
   ```
   [ERROR] Stability AI: Payment required
   ```
   **解决**: 在 Stability AI 平台充值

3. **网络错误**
   ```
   [ERROR] Network error calling Stability AI
   ```
   **解决**: 检查网络连接

### 测试命令

```bash
# 测试 Stability AI 直接调用
python test_stability_ai.py

# 测试 fallback 机制
python start_with_stability.py

# 详细测试
python -c "
import asyncio
from app.services.image_service import image_service
result = asyncio.run(image_service.generate_background('test'))
print(f'Result: {result}')
"
```

## 配置参数

在 `stability_image_service.py` 中可以调整：

```python
data = {
    "cfg_scale": 7,        # 创意程度 (1-20)
    "height": 1024,        # 图片高度
    "width": 1024,         # 图片宽度
    "steps": 30,           # 生成步数
}
```

## 成本对比

| 服务 | 每张图片 | 质量 | 速度 |
|------|---------|------|------|
| Gemini | ~$0.02 | 高 | 快 |
| Stability AI | ~$0.01 | 高 | 中等 |

---

🎉 **现在你的系统已经支持智能 fallback 机制了！** 