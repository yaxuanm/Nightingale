# Ambiance Waver

Ambiance Waver 是一个强大的音频处理和混合工具，基于 Web Audio API 和 React 构建。

## 功能特点

- 音频播放和控制
- 实时音频可视化
- 多轨音频混合
- 音频效果处理（混响、延迟、滤波器等）
- 音频录制
- 音频文件管理
- 音频导出

## 技术栈

- React 18
- Web Audio API
- CSS Grid & Flexbox
- 响应式设计

## 开始使用

### 安装依赖

```bash
npm install
```

### 开发模式运行

```bash
npm start
```

### 构建生产版本

```bash
npm run build
```

## 项目结构

```
src/
  ├── components/          # React 组件
  │   ├── AudioControls.js
  │   ├── AudioVisualizer.js
  │   ├── AudioMixer.js
  │   ├── AudioEffects.js
  │   ├── AudioRecorder.js
  │   ├── AudioPlayer.js
  │   ├── AudioSettings.js
  │   ├── AudioLibrary.js
  │   └── AudioExport.js
  ├── App.js              # 主应用组件
  ├── App.css             # 应用样式
  ├── index.js            # 应用入口
  └── index.css           # 全局样式
```

## 浏览器支持

- Chrome (推荐)
- Firefox
- Safari
- Edge

## 注意事项

- 使用 Chrome 浏览器可以获得最佳性能
- 需要现代浏览器支持 Web Audio API
- 音频处理可能需要较高的系统资源

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT 