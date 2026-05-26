# Nightingale Frontend

This directory contains the React portfolio app for Nightingale, an AI
soundscape product that turns emotional prompts into immersive audio scenes.

Live build: https://yaxuanm.github.io/Nightingale/

## Stack

- React 18
- TypeScript
- Material UI
- Framer Motion
- React Router

## Local Development

```bash
npm install
npm start
```

The local app runs at `http://localhost:3000`.

## Environment

Create `.env` from `env.example` when connecting to local or hosted APIs:

```env
REACT_APP_GEMINI_API_URL=http://localhost:8000
REACT_APP_STABLE_AUDIO_API_URL=http://localhost:8001
REACT_APP_FRONTEND_URL=http://localhost:3000
```

For the GitHub Pages portfolio build, the app is configured with the repository
homepage `/Nightingale/`.

## Quality Checks

```bash
CI=true npm test -- --watchAll=false
CI=true npm run build
```

The GitHub Pages workflow runs the production build before deployment.
