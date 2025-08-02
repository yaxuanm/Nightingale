# Queue Integration Guide

## 概述

队列功能已经成功集成到前端应用中，提供了两种音频生成模式：

1. **Fast Mode (快速模式)** - 传统的同步生成
2. **Queue Mode (队列模式)** - 异步队列生成，支持多用户并发

### 多用户队列系统特性

- ✅ **并发控制** - 最多同时运行3个任务
- ✅ **队列管理** - 最多50个任务排队
- ✅ **用户隔离** - 每个用户只能访问自己的任务
- ✅ **优先级支持** - 支持低、普通、高、紧急优先级
- ✅ **实时统计** - 队列大小、等待时间、运行状态
- ✅ **公平排队** - 先进先出，按优先级排序

## 功能特性

### 队列模式优势
- ✅ **非阻塞** - 不会阻塞用户界面
- ✅ **实时进度** - 显示生成进度百分比
- ✅ **可取消** - 用户可以随时取消任务
- ✅ **状态跟踪** - 实时显示任务状态
- ✅ **错误处理** - 完善的错误处理机制

### 状态指示
- 🔄 **Pending** - 任务已排队
- ⏳ **Running** - 正在生成音频
- ✅ **Completed** - 生成完成
- ❌ **Failed** - 生成失败
- 🚫 **Cancelled** - 任务已取消

## 使用方法

### 1. 在主界面使用

1. 打开主界面 (`/main`)
2. 在工具栏中选择模式：
   - **Fast Mode** - 快速生成（传统方式）
   - **Queue Mode** - 队列生成（推荐）
3. 输入描述文本
4. 点击 "Start with [Mode]" 按钮
5. 如果选择队列模式，会显示队列生成器界面

### 2. 队列生成器界面

队列生成器提供以下功能：
- **任务创建** - 自动创建队列任务
- **进度显示** - 实时显示生成进度
- **状态更新** - 显示当前任务状态
- **取消功能** - 可以随时取消任务
- **完成处理** - 完成后自动跳转到播放器

### 3. 测试页面

访问 `/queue-test` 可以测试队列功能：
- 预设的测试描述
- 完整的队列流程测试
- 错误处理测试

## API 端点

### 队列相关端点
- `POST /api/queue/audio-generation` - 创建音频生成任务
- `GET /api/queue/status/{task_id}` - 获取任务状态
- `DELETE /api/queue/cancel/{task_id}` - 取消任务
- `GET /api/queue/stats` - 获取队列统计

### 请求示例
```javascript
// 创建任务
const response = await fetch('http://localhost:8000/api/queue/audio-generation', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    description: "森林中的鸟叫声",
    duration: 20,
    mode: "default"
  })
});

// 查询状态
const statusResponse = await fetch(`http://localhost:8000/api/queue/status/${taskId}`);
```

## 组件说明

### QueueAudioGenerator
主要的队列生成组件，提供：
- 任务创建和管理
- 状态轮询和更新
- 进度显示
- 错误处理
- 取消功能

### MainScreen 集成
在主界面中添加了：
- 模式切换按钮（Fast/Queue）
- 队列生成器集成
- 完成后的导航处理

## 技术实现

### 轮询机制
- 每2秒轮询一次任务状态
- 自动清理轮询定时器
- 支持任务完成、失败、取消状态

### 状态管理
- 使用 React hooks 管理状态
- 实时更新任务进度
- 错误状态处理

### UI/UX
- 使用 Material-UI 组件
- 动画效果（Framer Motion）
- 响应式设计
- 主题集成

## 部署说明

### 后端要求
确保后端服务运行在正确的端口：
- Gemini服务：`http://localhost:8000`（包含队列功能）
- Stable Audio服务：`http://localhost:8001`（纯音频生成）

### 前端启动
```bash
cd ambiance-weaver-react
npm start
```

### 测试
1. 访问 `http://localhost:3000/main`
2. 选择 "Queue Mode"
3. 输入描述并开始生成
4. 观察队列进度和状态

## 故障排除

### 常见问题
1. **连接错误** - 确保后端服务正在运行
2. **任务超时** - 检查网络连接和服务器状态
3. **进度不更新** - 检查轮询是否正常工作

### 调试
- 打开浏览器开发者工具
- 查看 Network 标签页的API请求
- 检查 Console 中的错误信息

## 未来改进

- [ ] 添加批量任务支持
- [ ] 实现任务优先级
- [ ] 添加任务历史记录
- [ ] 支持更多音频参数
- [ ] 添加语音/图片输入支持 