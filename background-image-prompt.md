# 背景图片生成指南

## Gemini Prompt

```
请为我生成一张高质量的网页背景图片，要求如下：

**技术规格：**
- 分辨率：1920x1080 像素（16:9比例）
- 格式：PNG，支持透明背景
- 质量：高清，适合网页显示
- 文件大小：优化后不超过2MB

**设计风格：**
- 主题：自然、解压、宁静
- 色调：温暖的绿色和蓝色渐变，带有金色点缀
- 风格：现代简约，高级感
- 氛围：让人感到放松、平静、专注

**具体元素：**
- 背景：柔和的自然渐变，从深绿色到浅蓝色
- 纹理：微妙的自然纹理，如树叶、水波纹或云彩
- 光效：柔和的光晕和光影效果
- 装饰：极简的几何形状或自然元素（如叶子、花瓣）
- 深度：营造层次感和空间感

**色彩要求：**
- 主色调：#2d9c93（你的品牌绿色）
- 辅助色：#1a5f5a（深绿色）
- 点缀色：#f4d03f（温暖金色）
- 背景色：#0c1a1a（深色背景）

**特殊要求：**
- 适合作为网页背景，不会干扰文字阅读
- 具有现代感和高级感
- 符合"解压、自然"的应用调性
- 与现有的UI设计风格协调
- 可以添加微妙的动画效果（如果需要）

**参考风格：**
- 类似高端Spa或冥想应用的设计
- 自然元素与现代设计的结合
- 温暖而专业的色调
- 简约而不失精致

请生成一张符合以上要求的背景图片，确保图片质量高，适合网页使用。
```

## 当前背景图片位置

### 主要背景图片
```
ambiance-weaver-react/public/cover.png  (1.7MB)
```

### 其他背景图片
```
ambiance-weaver-react/public/forest.png  (2.5MB)
ambiance-weaver-react/public/coffee.png  (2.8MB)
```

## 更换背景图片的步骤

### 1. 生成新背景图片

1. **使用Gemini生成图片**
   - 复制上面的prompt到Gemini
   - 生成多张候选图片
   - 选择最符合要求的一张

2. **图片优化**
   - 确保分辨率是1920x1080
   - 压缩文件大小到2MB以下
   - 保存为PNG格式

### 2. 替换现有背景图片

#### 方法一：直接替换主背景图片

1. **替换主背景**
   ```bash
   # 将新生成的图片重命名为cover.png
   # 替换到以下位置：
   ambiance-weaver-react/public/cover.png
   ```

2. **备份原文件（可选）**
   ```bash
   # 备份原背景图片
   cp ambiance-weaver-react/public/cover.png ambiance-weaver-react/public/cover-backup.png
   ```

#### 方法二：创建新的背景图片

1. **创建新的背景图片**
   ```bash
   # 将新图片放到public文件夹
   ambiance-weaver-react/public/new-background.png
   ```

2. **更新代码引用**
   ```javascript
   // 在PageLayout.tsx中更新背景图片路径
   background: showBackground !== false ? `url(${backgroundImageUrl || `${process.env.PUBLIC_URL}/new-background.png`}) no-repeat center center fixed` : 'transparent',
   ```

### 3. 测试新背景

1. **启动应用**
   ```bash
   cd ambiance-weaver-react
   npm start
   ```

2. **检查效果**
   - 访问 `http://localhost:3000/chat`
   - 生成音频和背景图片
   - 进入Player页面查看新背景效果
   - 检查SharePage的背景显示

3. **调整CSS（如果需要）**
   ```css
   /* 如果需要调整背景显示效果 */
   .background-image {
     background-size: cover;
     background-position: center;
     background-repeat: no-repeat;
     filter: brightness(0.8) contrast(1.1);
   }
   ```

## 代码中的背景图片引用

### 主要引用位置
- `ambiance-weaver-react/src/components/PageLayout.tsx` - 主要背景图片组件
- `ambiance-weaver-react/src/components/AllScreensShowcase.tsx` - 展示页面背景
- `ambiance-weaver-react/src/components/DemoOverview.tsx` - 演示概览背景
- `ambiance-weaver-react/src/components/Overview.tsx` - 概览页面背景

### 当前使用的背景图片
```javascript
// 在PageLayout.tsx中
background: showBackground !== false ? `url(${backgroundImageUrl || `${process.env.PUBLIC_URL}/cover.png`}) no-repeat center center fixed` : 'transparent',
```

## 推荐的背景图片位置

### 本地存储
```
ambiance-weaver-react/public/
├── cover.png              # 主背景图片（当前使用）
├── new-background.png     # 新背景图片（建议）
├── forest.png             # 森林主题背景
└── coffee.png             # 咖啡主题背景
```

### 云端存储
```
https://your-supabase-bucket.supabase.co/storage/v1/object/public/backgrounds/
├── main-background.png
├── mobile-background.png
└── dark-background.png
```

## 背景图片优化建议

### 1. 响应式设计
- **桌面端**: 1920x1080
- **平板端**: 1024x768
- **手机端**: 375x667

### 2. 性能优化
- 使用WebP格式（如果支持）
- 压缩图片文件大小
- 使用CDN加速

### 3. 主题适配
- **浅色主题**: 明亮、清新的背景
- **深色主题**: 深沉、宁静的背景
- **自动切换**: 根据系统主题自动切换

## 快速替换步骤

### 最简单的替换方法

1. **生成新背景图片**
   - 使用上面的Gemini prompt
   - 生成高质量的背景图片

2. **直接替换**
   ```bash
   # 将新图片重命名为cover.png
   # 替换到以下位置：
   ambiance-weaver-react/public/cover.png
   ```

3. **测试效果**
   ```bash
   cd ambiance-weaver-react
   npm start
   # 访问 http://localhost:3000/chat
   ```

## 测试清单

- [ ] 新背景图片生成完成
- [ ] 图片分辨率符合要求（1920x1080）
- [ ] 文件大小优化（<2MB）
- [ ] 替换到正确位置（`public/cover.png`）
- [ ] 在桌面端测试显示效果
- [ ] 在移动端测试显示效果
- [ ] 检查与UI元素的协调性
- [ ] 验证在不同页面的一致性
- [ ] 测试加载速度
- [ ] 确认符合品牌调性

## 备用方案

如果Gemini生成的图片不满意，可以考虑：

1. **使用其他AI工具**
   - DALL-E 3
   - Midjourney
   - Stable Diffusion

2. **使用现成的背景**
   - Unsplash
   - Pexels
   - Pixabay

3. **手动设计**
   - 使用Figma或Sketch
   - 参考高端应用的设计风格

## 当前背景图片分析

### cover.png (1.7MB)
- **用途**: 主要背景图片
- **位置**: `ambiance-weaver-react/public/cover.png`
- **引用**: 在PageLayout.tsx中被引用
- **状态**: 需要替换为更高质量的背景

### forest.png (2.5MB) 和 coffee.png (2.8MB)
- **用途**: 主题背景图片
- **位置**: `ambiance-weaver-react/public/`
- **状态**: 可以保留作为主题选项

记住，背景图片应该与你的应用"解压、自然"的调性完美契合，同时保持现代感和高级感！🎨 