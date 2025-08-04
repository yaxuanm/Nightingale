# Nightingale - Let Sound Touch the Soul

> AI-powered ambient sound generation platform that creates immersive audio experiences

## 🌟 Overview

Nightingale is an innovative AI-powered platform that generates ambient soundscapes based on user descriptions. Using advanced AI models including Gemini and Stable Audio, it creates immersive audio experiences that can help with relaxation, focus, and meditation.

## ✨ Features

- **AI-Powered Generation**: Uses Gemini AI for prompt understanding and Stable Audio for high-quality sound generation
- **Multiple Modes**: Support for different generation modes including story, focus, and ambient
- **Real-time Processing**: Fast audio generation with progress tracking
- **Interactive UI**: Modern React-based interface with intuitive controls
- **Audio Player**: Built-in player with background image support
- **Sharing**: Easy sharing of generated soundscapes
- **Cross-platform**: Web-based application accessible from any device

## 🏗️ Architecture

```
Nightingale/
├── ambiance-weaver-react/     # Frontend React application
├── backend/                   # Python FastAPI backend
│   ├── app/                  # Main application code
│   ├── scripts/              # Utility scripts
│   └── venv_gemini/         # Python virtual environment
├── docs/                     # Documentation
└── scripts/                  # Project scripts
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 (required, not compatible with 3.12 or 3.13)
- Node.js 16+
- FFmpeg installed and in PATH

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yaxuanm/Nightingale.git
   cd Nightingale
   ```

2. **Set up backend environment**
   ```bash
   cd backend
   python -m venv venv_gemini
   .\venv_gemini\Scripts\activate
   pip install -r requirements-gemini-working.txt
   ```

3. **Set up Stable Audio environment**
   ```bash
   python -m venv venv_stableaudio
   .\venv_stableaudio\Scripts\activate
   pip install -r requirements-stable-audio.txt
   python scripts/stable_audio_fix.py
   ```

4. **Set up frontend**
   ```bash
   cd ../ambiance-weaver-react
   npm install
   ```

5. **Configure environment variables**
   ```bash
   # Copy and edit environment files
   cp backend/env.example backend/.env
   cp ambiance-weaver-react/env.example ambiance-weaver-react/.env
   ```

### Running the Application

1. **Start backend services**
   ```bash
   # Terminal 1: Gemini API (port 8000)
   cd backend
   .\venv_gemini\Scripts\activate
   python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

   # Terminal 2: Stable Audio (port 8001)
   cd backend
   .\venv_stableaudio\Scripts\activate
   python -m uvicorn app.main_stable_audio:app --host 0.0.0.0 --port 8001
   ```

2. **Start frontend**
   ```bash
   cd ambiance-weaver-react
   npm start
   ```

3. **Access the application**
   - Frontend: http://localhost:3000
   - Gemini API: http://localhost:8000
   - Stable Audio: http://localhost:8001

## 🔧 Configuration

### Environment Variables

Create `.env` files in both `backend/` and `ambiance-weaver-react/` directories:

**Backend (.env)**
```env
GOOGLE_API_KEY=your-google-api-key
STABILITY_API_KEY=your-stability-api-key
HF_TOKEN=your-hugging-face-token
FFMPEG_PATH=C:\ffmpeg\bin
```

**Frontend (.env)**
```env
REACT_APP_GEMINI_API_URL=http://localhost:8000
REACT_APP_STABLE_AUDIO_API_URL=http://localhost:8001
REACT_APP_FRONTEND_URL=http://localhost:3000
```

## 📚 Documentation

- [Deployment Guide](DEPLOYMENT.md) - Complete deployment instructions
- [Start Instructions](start_instructions.txt) - Detailed setup guide
- [Environment Setup](backend/README_ENVIRONMENTS.md) - Environment configuration

## 🛠️ Development

### Project Structure

- **Frontend**: React with TypeScript, Material-UI components
- **Backend**: FastAPI with async/await support
- **AI Services**: Gemini for text processing, Stable Audio for sound generation
- **Storage**: Supabase for cloud storage

### Key Components

- `ChatScreen.tsx` - Main interaction interface
- `Player.tsx` - Audio playback component
- `main.py` - Primary API endpoints
- `main_stable_audio.py` - Stable Audio service
- `ai_service.py` - AI integration layer

## 🚀 Deployment

For production deployment, see [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions including:

- Environment setup
- Service configuration
- Performance optimization
- Troubleshooting guide

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License for the application code.

**AI Model Licenses:**
- **Stable Audio**: Uses Stability AI Community License Agreement
  - Free for research, non-commercial, and limited commercial use (organizations with <$1M annual revenue)
  - Commercial licensing required for organizations with >$1M annual revenue
  - See [Stability AI License](https://huggingface.co/stabilityai/stable-audio-open-small/blob/main/LICENSE) for full terms

- **Google Gemini**: Subject to Google's API Terms of Service
  - Requires valid Google API key
  - Usage subject to Google's rate limits and terms

## 🙏 Acknowledgments

- [Google Gemini AI](https://ai.google.dev/) for text processing
- [Stability AI](https://stability.ai/) for audio generation
- React and FastAPI communities
- All contributors and testers

---

**Nightingale** - Let sound touch the soul 🎵 