# Nightingale

Nightingale is a modern, cross-platform audio generation and mixing toolkit, featuring a web frontend, a React Native mobile app, and a Python FastAPI backend. It supports real-time audio playback, AI-powered sound generation (using Stability AI Stable Audio), and sharing features.

## Features
- Real-time audio playback and mixing
- **AI-powered audio generation (text-to-audio via Stability AI Stable Audio)**
- Audio effects and visualization
- Multi-platform: Web, Native (React Native), Backend API
- Share and export audio and images
- Modern, responsive UI

## Tech Stack
- **Web**: React 18, TypeScript, Material-UI, Framer Motion
- **Native**: React Native, Expo, TypeScript
- **Backend**: Python 3, FastAPI, Uvicorn, HuggingFace, Google Generative AI, **Stability AI Stable Audio**

## Project Structure
```
Nightingale/
├── ambiance-weaver-react/        # Web frontend (React)
│   ├── src/
│   │   ├── components/           # UI components (Player, Chat, etc.)
│   │   ├── utils/                # Utilities and context
│   │   ├── theme/                # Theming and styles
│   │   └── ...
│   ├── public/                   # Static assets
│   └── package.json
│
├── ambiance-weaver-native/       # React Native app (mobile)
│   ├── app/                      # App entry and navigation
│   │   ├── (tabs)/               # Tab pages (explore, main, etc.)
│   │   └── _layout.tsx, +not-found.tsx
│   ├── components/               # Shared and UI components
│   │   └── ui/                   # Icon, TabBar, etc.
│   ├── assets/                   # Images, fonts
│   ├── hooks/                    # Custom hooks
│   ├── constants/                # Color and config
│   ├── src/
│   │   ├── screens/              # MainScreen, PlayerScreen, etc.
│   │   └── services/             # AudioService, NotificationService
│   ├── ambiance-weaver-native-new/ # (Experimental new structure)
│   └── package.json
│
├── backend/                      # Backend API (Python FastAPI)
│   ├── app/
│   │   ├── main.py               # Main FastAPI app
│   │   ├── services/             # Audio, image, AI services
│   │   └── ...
│   ├── requirements.txt          # Python dependencies
│   ├── scripts/                  # Batch/test/utility scripts
│   └── .env.example              # Environment variable template
│
├── docs/                         # Documentation
├── scripts/                      # Project-level scripts
└── start_instructions.txt        # Full environment & startup guide (see below)
```

## Environment Setup & Startup

**All environment setup and startup instructions are now maintained in [`start_instructions.txt`](./start_instructions.txt).**

- Includes one-click setup, service startup, troubleshooting, and batch testing guides.
- Please refer to that file for the latest and most accurate instructions for Windows/PowerShell and cross-platform usage.

## Quick Start (Summary)
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/Nightingale.git
   cd Nightingale
   ```
2. Follow the steps in `start_instructions.txt` for environment setup and running the app.

## Contribution
Contributions are welcome! Please open issues or submit pull requests for bug fixes, new features, or documentation improvements.

## License
MIT 