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
- **Share functionality with unique URLs**
- **Download audio and background images**
- **Modern UI with Material-UI components**

## Tech Stack
- React 18 (Web)
- TypeScript
- Python 3, FastAPI (Backend)
- Web Audio API
- CSS Grid & Flexbox
- Modern responsive design
- **Supabase for cloud storage**
- **Google Generative AI for text processing**

## Required API Keys

### 1. Google Generative AI API Key
- **Purpose**: Text processing and AI chat features
- **Setup**: 
  ```bash
  # Set environment variable
  export GOOGLE_API_KEY="your-google-api-key"
  ```
- **Get it from**: [Google AI Studio](https://makersuite.google.com/app/apikey)

### 2. Stability AI API Key (Optional)
- **Purpose**: High-quality image generation for backgrounds
- **Setup**:
  ```bash
  # Set environment variable
  export STABILITY_API_KEY="your-stability-api-key"
  ```
- **Get it from**: [Stability AI Platform](https://platform.stability.ai/)

### 3. Supabase Configuration (Optional)
- **Purpose**: Cloud storage for audio and image files
- **Setup**:
  ```bash
  # Set environment variables
  export SUPABASE_URL="your-supabase-url"
  export SUPABASE_ANON_KEY="your-supabase-anon-key"
  export SUPABASE_SERVICE_ROLE_KEY="your-supabase-service-role-key"
  ```
- **Get it from**: [Supabase Dashboard](https://supabase.com/)

### 4. Hugging Face Token (Optional)
- **Purpose**: Access to Hugging Face models
- **Setup**:
  ```bash
  # Set environment variable
  export HF_TOKEN="your-huggingface-token"
  ```
- **Get it from**: [Hugging Face Settings](https://huggingface.co/settings/tokens)

## Environment Setup

### Create Environment File
```bash
# Create .env file in backend directory
cd backend
touch .env
```

### Add API Keys to .env
```env
# Required
GOOGLE_API_KEY=your-google-api-key

# Optional
STABILITY_API_KEY=your-stability-api-key
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-supabase-service-role-key
HF_TOKEN=your-huggingface-token
SHARE_BASE_URL=http://localhost:3000
```

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
Nightingale/
├── ambiance-weaver-react/      # Web frontend (React)
│   ├── src/
│   │   ├── components/         # Main UI components (Player, ChatScreen, Overview, etc.)
│   │   ├── utils/              # Utility functions and context
│   │   ├── theme/              # Theming and styles
│   │   └── ...                 # Other app files
│   ├── public/                 # Static assets
│   └── package.json
├── backend/                    # Backend API (Python FastAPI)
│   ├── app/
│   │   ├── main.py             # Main FastAPI app entry
│   │   ├── services/           # Audio, image, and AI services
│   │   ├── models/             # (Reserved for future data models)
│   │   ├── utils/              # (Reserved for future utility functions)
│   │   └── ...                 # Other backend files
│   ├── requirements.txt
│   └── .env                    # Environment variables (create this)
├── ambiance-weaver-native/     # React Native app (in development)
├── venv_gemini/               # Python virtual environment for Gemini
├── venv_stableaudio/          # Python virtual environment for Stable Audio
├── docs/                      # Documentation and test files
├── scripts/                   # Utility scripts
└── README.md
```

## Getting Started

### Prerequisites
- Node.js 16+ and npm
- Python 3.8+
- Git

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/Nightingale.git
cd Nightingale
```

### 2. Set Up API Keys
```bash
# Copy the environment template
cp backend/.env.example backend/.env

# Edit the .env file with your API keys
nano backend/.env
```

### 3. Start the Backend
```bash
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Start the Frontend
```bash
cd ambiance-weaver-react

# Install dependencies
npm install

# Start the development server
npm start
```

### 5. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Virtual Environments

This project includes pre-configured virtual environments:

### venv_gemini/
- **Purpose**: Google Generative AI development
- **Activation**: `source venv_gemini/bin/activate` (Linux/Mac) or `venv_gemini\Scripts\activate` (Windows)
- **Dependencies**: `requirements-gemini-utf8.txt`

### venv_stableaudio/
- **Purpose**: Stable Audio AI development
- **Activation**: `source venv_stableaudio/bin/activate` (Linux/Mac) or `venv_stableaudio\Scripts\activate` (Windows)
- **Dependencies**: `requirements-stable-audio.txt`

## Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd ambiance-weaver-react
npm test
```

## Deployment

### Frontend Deployment
```bash
cd ambiance-weaver-react
npm run build
# Deploy the build/ folder to your hosting service
```

### Backend Deployment
```bash
cd backend
# Use uvicorn or gunicorn for production
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Contribution

Contributions are welcome! Feel free to open issues or submit pull requests for bug fixes, new features, or documentation improvements.

## License

MIT 