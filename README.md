# Nightingale

Nightingale is a modern, cross-platform audio processing and mixing toolkit, featuring a web frontend and a Python FastAPI backend. The project is designed for real-time audio playback, visualization, mixing, and AI-powered features. (Note: Native mobile app is not yet developed.)

## Features
- Audio playback and control
- Real-time audio visualization
- Multi-track audio mixing
- Audio effects (reverb, delay, filters, etc.)
- Audio recording and file management
- AI-powered chat and audio features
- Export and share audio files
- Web frontend and backend API

## Tech Stack
- React 18 (Web)
- TypeScript
- Python 3, FastAPI (Backend)
- Web Audio API
- CSS Grid & Flexbox
- Modern responsive design

## Project Structure
```
ambiance-weaver-react/      # Web frontend (React)
  └── src/
      ├── components/       # Main UI components (Player, ChatScreen, Overview, etc.)
      ├── utils/            # Utility functions and context
      ├── theme/            # Theming and styles
      └── ...               # Other app files

backend/                    # Backend API (Python FastAPI)
  └── app/
      ├── main.py           # Main FastAPI app entry
      ├── services/         # Audio, image, and AI services
      ├── models/           # (Reserved for future data models)
      ├── utils/            # (Reserved for future utility functions)
      └── ...               # Other backend files
```

## Getting Started

**Web Frontend**
```bash
cd ambiance-weaver-react
npm install
npm start
```

**Backend API**
```bash
cd backend
pip install -r requirements.txt
python run.py
```

## Contribution

Contributions are welcome! Feel free to open issues or submit pull requests for bug fixes, new features, or documentation improvements.

## License

MIT 