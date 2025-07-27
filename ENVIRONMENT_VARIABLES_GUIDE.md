# Nightingale 环境变量配置指南

## 📋 概述

Nightingale 项目支持通过环境变量配置 API 服务地址，实现灵活的部署配置。本文档详细说明如何配置和使用环境变量。

## 🎯 支持的组件

- **前端 React 应用** (`ambiance-weaver-react`)
- **Gemini API 服务** (端口 8000)
- **Stable Audio 服务** (端口 8001)

## 🔧 环境变量配置

### 必需的环境变量

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `REACT_APP_GEMINI_API_URL` | Gemini API 服务地址 | `http://localhost:8000` | `https://api.yourdomain.com:8000` |
| `REACT_APP_STABLE_AUDIO_API_URL` | Stable Audio 服务地址 | `http://localhost:8001` | `https://api.yourdomain.com:8001` |
| `REACT_APP_FRONTEND_URL` | 前端服务地址 | `http://localhost:3000` | `https://yourdomain.com` |

### 可选的环境变量

| 变量名 | 说明 | 默认值 | 示例 |
|--------|------|--------|------|
| `REACT_APP_ENV` | 环境标识 | `development` | `production` |
| `REACT_APP_DEBUG` | 调试模式 | `true` | `false` |

## 🚀 配置步骤

### 步骤1：创建环境变量文件

在 `ambiance-weaver-react` 目录下创建 `.env` 文件：

```bash
cd ambiance-weaver-react
copy env.example .env
```

### 步骤2：编辑环境变量

根据部署环境编辑 `.env` 文件：

#### 本地开发环境
```env
# 本地开发配置
REACT_APP_GEMINI_API_URL=http://localhost:8000
REACT_APP_STABLE_AUDIO_API_URL=http://localhost:8001
REACT_APP_FRONTEND_URL=http://localhost:3000
REACT_APP_ENV=development
REACT_APP_DEBUG=true
```

#### 生产环境
```env
# 生产环境配置
REACT_APP_GEMINI_API_URL=https://api.yourdomain.com:8000
REACT_APP_STABLE_AUDIO_API_URL=https://api.yourdomain.com:8001
REACT_APP_FRONTEND_URL=https://yourdomain.com
REACT_APP_ENV=production
REACT_APP_DEBUG=false
```

#### 测试环境
```env
# 测试环境配置
REACT_APP_GEMINI_API_URL=https://test-api.yourdomain.com:8000
REACT_APP_STABLE_AUDIO_API_URL=https://test-api.yourdomain.com:8001
REACT_APP_FRONTEND_URL=https://test.yourdomain.com
REACT_APP_ENV=staging
REACT_APP_DEBUG=true
```

### 步骤3：重启服务

修改环境变量后需要重启前端服务：

```bash
# 停止当前服务 (Ctrl+C)
# 重新启动
npm start
```

## 🔍 验证配置

### 方法1：浏览器控制台检查

打开浏览器开发者工具，在控制台运行：

```javascript
// 检查 API 地址配置
console.log('Gemini API:', process.env.REACT_APP_GEMINI_API_URL);
console.log('Stable Audio API:', process.env.REACT_APP_STABLE_AUDIO_API_URL);
console.log('Frontend URL:', process.env.REACT_APP_FRONTEND_URL);
console.log('Environment:', process.env.REACT_APP_ENV);
```

### 方法2：网络请求检查

在浏览器开发者工具的 Network 标签页中，查看 API 请求的 URL：

```
✅ 正确: https://api.yourdomain.com:8000/api/generate-inspiration-chips
❌ 错误: http://localhost:8000/api/generate-inspiration-chips
```

### 方法3：API 健康检查

```bash
# 检查 Gemini API
curl https://api.yourdomain.com:8000/health

# 检查 Stable Audio API
curl https://api.yourdomain.com:8001/health
```

## 📁 文件结构

```
ambiance-weaver-react/
├── .env                    # 环境变量文件 (不提交到 Git)
├── env.example            # 环境变量示例文件
├── src/
│   ├── config/
│   │   └── api.ts         # API 配置管理
│   └── components/
│       ├── MainScreen.tsx  # 使用 API_ENDPOINTS
│       ├── ChatScreen.tsx  # 使用 API_ENDPOINTS
│       ├── Player.tsx      # 使用 API_ENDPOINTS
│       └── SharePage.tsx   # 使用 API_ENDPOINTS
└── package.json
```

## 🔧 API 配置管理

### 配置文件位置
`ambiance-weaver-react/src/config/api.ts`

### 配置内容
```typescript
export const API_CONFIG = {
  GEMINI_API_BASE_URL: process.env.REACT_APP_GEMINI_API_URL || 'http://localhost:8000',
  STABLE_AUDIO_API_BASE_URL: process.env.REACT_APP_STABLE_AUDIO_API_URL || 'http://localhost:8001',
  FRONTEND_BASE_URL: process.env.REACT_APP_FRONTEND_URL || 'http://localhost:3000',
};

export const API_ENDPOINTS = {
  GENERATE_INSPIRATION_CHIPS: `${API_CONFIG.GEMINI_API_BASE_URL}/api/generate-inspiration-chips`,
  GENERATE_SCENE: `${API_CONFIG.GEMINI_API_BASE_URL}/api/generate-scene`,
  // ... 更多端点
};
```

### 使用方式
```typescript
import { API_ENDPOINTS } from '../config/api';

// 在组件中使用
const response = await fetch(API_ENDPOINTS.GENERATE_INSPIRATION_CHIPS, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(data),
});
```

## 🌍 不同环境配置示例

### 本地开发
```env
REACT_APP_GEMINI_API_URL=http://localhost:8000
REACT_APP_STABLE_AUDIO_API_URL=http://localhost:8001
REACT_APP_FRONTEND_URL=http://localhost:3000
```

### Docker 容器
```env
REACT_APP_GEMINI_API_URL=http://backend:8000
REACT_APP_STABLE_AUDIO_API_URL=http://backend:8001
REACT_APP_FRONTEND_URL=http://localhost:3000
```

### 云服务器
```env
REACT_APP_GEMINI_API_URL=https://your-server.com:8000
REACT_APP_STABLE_AUDIO_API_URL=https://your-server.com:8001
REACT_APP_FRONTEND_URL=https://your-server.com
```

### 负载均衡器
```env
REACT_APP_GEMINI_API_URL=https://api.yourdomain.com:8000
REACT_APP_STABLE_AUDIO_API_URL=https://api.yourdomain.com:8001
REACT_APP_FRONTEND_URL=https://app.yourdomain.com
```

## ⚠️ 注意事项

### 1. React 环境变量规则
- **必须以 `REACT_APP_` 开头**
- **修改后需要重启开发服务器**
- **生产环境需要重新构建**

### 2. 安全考虑
```env
# ✅ 正确：使用 HTTPS
REACT_APP_GEMINI_API_URL=https://api.yourdomain.com:8000

# ❌ 错误：生产环境使用 HTTP
REACT_APP_GEMINI_API_URL=http://api.yourdomain.com:8000
```

### 3. 端口配置
```env
# ✅ 正确：指定端口
REACT_APP_GEMINI_API_URL=https://api.yourdomain.com:8000

# ❌ 错误：使用默认端口 80/443
REACT_APP_GEMINI_API_URL=https://api.yourdomain.com
```

### 4. 构建和部署
```bash
# 开发环境
npm start

# 生产环境构建
npm run build

# 部署构建产物
npm run deploy
```

## 🚨 故障排除

### 问题1：环境变量不生效
```bash
# 解决方案
npm start
# 或者
npm run build
```

### 问题2：API 调用失败
```bash
# 检查网络连接
curl https://api.yourdomain.com:8000/health

# 检查 CORS 配置
# 确保后端允许前端域名访问
```

### 问题3：HTTPS 证书问题
```bash
# 开发环境可以使用 HTTP
REACT_APP_GEMINI_API_URL=http://localhost:8000

# 生产环境必须使用 HTTPS
REACT_APP_GEMINI_API_URL=https://api.yourdomain.com:8000
```

### 问题4：端口被占用
```bash
# 检查端口占用
netstat -ano | findstr :8000
netstat -ano | findstr :8001

# 结束占用进程
taskkill /PID {进程ID} /F
```

## 📝 最佳实践

### 1. 环境分离
```bash
# 开发环境
.env.development

# 生产环境
.env.production

# 测试环境
.env.staging
```

### 2. 版本控制
```bash
# 提交示例文件
git add env.example

# 不提交实际配置
echo ".env" >> .gitignore
```

### 3. 配置验证
```typescript
// 在应用启动时验证配置
if (!process.env.REACT_APP_GEMINI_API_URL) {
  console.error('Missing REACT_APP_GEMINI_API_URL');
}
```

### 4. 错误处理
```typescript
// API 调用错误处理
try {
  const response = await fetch(API_ENDPOINTS.GENERATE_INSPIRATION_CHIPS, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  
  if (!response.ok) {
    throw new Error(`API call failed: ${response.status}`);
  }
  
  return await response.json();
} catch (error) {
  console.error('API Error:', error);
  // 显示用户友好的错误信息
}
```

## 📞 技术支持

如果遇到环境变量配置问题：

1. **检查文件路径**：确保 `.env` 文件在正确位置
2. **检查变量名**：确保以 `REACT_APP_` 开头
3. **重启服务**：修改后必须重启开发服务器
4. **查看控制台**：检查浏览器控制台错误信息

---

**文档版本**: v1.0  
**最后更新**: 2025-01-21  
**适用版本**: Nightingale 1.0+ 