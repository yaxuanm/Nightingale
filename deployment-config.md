# Nightingale 云端部署配置

## 1. 当前分享功能分析

### 现有架构
- ✅ **音频存储**: 使用 Supabase Storage 存储音频文件
- ✅ **图片存储**: 使用 Supabase Storage 存储背景图片  
- ✅ **云存储URL**: 音频和图片都有永久的云存储URL
- ✅ **分享API**: 后端已实现分享创建和获取API

### 分享链接格式
```
https://your-domain.com/share/{share_id}
```

## 2. 部署到云端的步骤

### 2.1 前端部署 (React App)

#### 选项A: Vercel (推荐)
```bash
# 安装 Vercel CLI
npm i -g vercel

# 在 ambiance-weaver-react 目录下
cd ambiance-weaver-react
vercel

# 配置环境变量
vercel env add REACT_APP_API_URL https://your-backend-domain.com
```

#### 选项B: Netlify
```bash
# 构建项目
npm run build

# 部署到 Netlify
# 上传 build 文件夹到 Netlify
```

### 2.2 后端部署 (FastAPI)

#### 选项A: Railway
```bash
# 创建 Railway 项目
# 上传 backend 文件夹
# 配置环境变量
```

#### 选项B: Heroku
```bash
# 创建 Procfile
echo "web: uvicorn app.main:app --host 0.0.0.0 --port \$PORT" > Procfile

# 部署
heroku create your-app-name
git push heroku main
```

#### 选项C: DigitalOcean App Platform
- 上传 backend 文件夹
- 配置环境变量
- 设置启动命令: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 2.3 环境变量配置

#### 前端环境变量 (.env)
```env
REACT_APP_API_URL=https://your-backend-domain.com
REACT_APP_SUPABASE_URL=https://your-project.supabase.co
REACT_APP_SUPABASE_KEY=your-anon-key
```

#### 后端环境变量
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
GOOGLE_API_KEY=your-google-api-key
STABILITY_API_KEY=your-stability-api-key
```

## 3. 分享功能配置

### 3.1 更新分享URL生成

在 `backend/app/main.py` 中更新分享URL：

```python
# 根据实际部署域名更新
SHARE_BASE_URL = os.getenv("SHARE_BASE_URL", "https://your-domain.com")

@app.post("/api/create-share")
async def create_share(request: dict):
    # ... existing code ...
    
    # 使用环境变量中的域名
    share_url = f"{SHARE_BASE_URL}/share/{share_id}"
    
    return {
        "share_id": share_id,
        "share_url": share_url,
        "message": "Share created successfully"
    }
```

### 3.2 前端API配置

在 `ambiance-weaver-react/src/components/Player.tsx` 中：

```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const handleShare = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/api/create-share`, {
      // ... existing code ...
    });
  } catch (error) {
    // ... error handling ...
  }
};
```

## 4. 分享功能特性

### 4.1 分享链接包含的数据
```json
{
  "id": "uuid-share-id",
  "audio_url": "https://supabase.co/storage/v1/object/public/audio-files/file.wav",
  "background_url": "https://supabase.co/storage/v1/object/public/images/file.png",
  "description": "A cozy café on a rainy afternoon",
  "title": "My Nightingale Soundscape",
  "created_at": "2024-01-01T12:00:00",
  "views": 42
}
```

### 4.2 分享页面功能
- ✅ **音频播放**: 直接播放分享的音频
- ✅ **背景图片**: 显示原始背景图片
- ✅ **描述信息**: 显示音频描述
- ✅ **访问统计**: 记录查看次数
- ✅ **再次分享**: 可以重新分享链接
- ✅ **收藏功能**: 可以收藏分享的内容

### 4.3 分享链接示例
```
https://nightingale-app.vercel.app/share/550e8400-e29b-41d4-a716-446655440000
```

## 5. 部署检查清单

### 5.1 前端部署
- [ ] 构建 React 应用 (`npm run build`)
- [ ] 配置环境变量
- [ ] 部署到 Vercel/Netlify
- [ ] 测试分享功能

### 5.2 后端部署
- [ ] 配置环境变量
- [ ] 部署到 Railway/Heroku/DigitalOcean
- [ ] 测试 API 端点
- [ ] 验证音频上传功能

### 5.3 数据库配置
- [ ] 配置 Supabase 项目
- [ ] 设置存储桶权限
- [ ] 测试音频和图片上传

### 5.4 域名配置
- [ ] 配置自定义域名
- [ ] 设置 SSL 证书
- [ ] 更新分享URL生成逻辑

## 6. 测试分享功能

### 6.1 本地测试
```bash
# 启动后端
cd backend
uvicorn app.main:app --reload

# 启动前端
cd ambiance-weaver-react
npm start

# 测试分享功能
# 1. 生成音频
# 2. 点击分享按钮
# 3. 复制分享链接
# 4. 在新窗口打开分享链接
```

### 6.2 云端测试
- [ ] 部署完成后测试分享功能
- [ ] 验证音频播放
- [ ] 检查背景图片显示
- [ ] 测试访问统计

## 7. 优化建议

### 7.1 性能优化
- 使用 CDN 加速音频和图片加载
- 实现音频预加载
- 添加加载动画

### 7.2 功能增强
- 添加社交分享按钮 (Facebook, Twitter, WhatsApp)
- 实现分享密码保护
- 添加分享过期时间
- 实现分享评论功能

### 7.3 用户体验
- 添加分享成功提示
- 实现分享链接预览
- 添加分享统计面板 