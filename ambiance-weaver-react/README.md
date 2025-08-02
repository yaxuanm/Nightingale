# Nightingale - AI音效生成平台

Nightingale是一个基于AI的音效生成平台，能够将用户的文字描述转换为沉浸式的音频体验。该平台集成了多种AI模型，支持音效生成、音乐创作、TTS语音合成等功能。

## 功能特色

- **智能音效生成**：将自然语言描述转换为高质量的环境音效
- **多模态AI集成**：结合Stable Audio、MusicGen、AudioGen等多种AI模型
- **沉浸式体验**：支持背景图片生成，创造完整的视听体验
- **多场景适配**：支持专注、放松、故事、音乐等多种使用模式
- **实时生成**：快速响应用户需求，支持实时音频生成和播放

## 技术栈

- **前端**：React 18 + TypeScript + Material-UI
- **后端**：FastAPI + Google Gemini AI + Stable Audio Tools
- **AI模型**：Stable Audio、MusicGen、AudioGen、Edge TTS

## 快速开始

### 安装依赖
```bash
npm install
```

### 启动开发服务器
```bash
npm start
```

应用将在 [http://localhost:3000](http://localhost:3000) 启动。

### 构建生产版本
```bash
npm run build
```

## 项目结构

```
src/
├── components/          # React组件
├── theme/              # 主题配置
├── utils/              # 工具函数
└── config/             # 配置文件
```

## 部署

项目支持多种部署方式：
- 静态文件部署
- Docker容器化部署
- 云平台部署

## 贡献

欢迎提交Issue和Pull Request来改进项目。

---

*Nightingale - 让AI为您的音频内容创作赋能*
