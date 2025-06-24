# Nightingale

Nightingale is a modern, cross-platform audio processing and mixing toolkit, featuring a web frontend and a Python FastAPI backend. The project is designed for real-time audio playback, visualization, mixing, and advanced AI-powered features. **At its core, Nightingale leverages Meta's AudioCraft to enable state-of-the-art AI audio generation from text prompts.** (Note: Native mobile app is not yet developed.)

## Features
- Audio playback and control
- Real-time audio visualization
- Multi-track audio mixing
- Audio effects (reverb, delay, filters, etc.)
- Audio recording and file management
- **AI audio generation using Meta AudioCraft**
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

## Key Dependencies

### Web Frontend (ambiance-weaver-react)
- **react, react-dom**: Core UI library for building user interfaces.
- **@mui/material, @mui/icons-material**: Material UI component library and icons for modern, accessible design.
- **@emotion/react, @emotion/styled**: CSS-in-JS styling for React components.
- **framer-motion**: Animation and gesture library for React.
- **react-router-dom**: Declarative routing for React web apps.
- **typescript**: Type safety and modern JavaScript tooling.
- **@testing-library/react, @testing-library/jest-dom, @testing-library/user-event**: Testing utilities for React components.
- **web-vitals**: Measuring and reporting web performance metrics.

### Backend (backend/requirements.txt)
- **fastapi**: High-performance Python web framework for building APIs.
- **uvicorn**: ASGI server for running FastAPI applications.
- **google-generativeai**: Google Generative AI API client for advanced AI features.
- **pydub**: Audio manipulation and processing library.
- **python-multipart**: Parsing multipart/form-data (file uploads).
- **python-dotenv**: Loading environment variables from .env files.
- **pytest**: Testing framework for Python.
- **requests, httpx**: HTTP clients for making API requests.
- **numpy**: Numerical computing and array operations.
- **soundfile**: Reading and writing sound files.
- **audiocraft**: **Meta's state-of-the-art AI audio generation library, powering Nightingale's core sound synthesis features.**
- **accelerate**: Utilities for fast and distributed training (HuggingFace).
- **torch, torchaudio**: PyTorch and audio processing for deep learning.
- **transformers**: State-of-the-art machine learning models (HuggingFace Transformers).
- **protobuf**: Protocol Buffers for efficient data serialization.
- **supabase**: Python client for Supabase backend services.

> Note: Some dependencies are for development or testing only. See `package.json` and `requirements.txt` for the full list and version details.

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