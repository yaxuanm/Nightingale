# Nightingale Deployment Guide

This document describes the current deployment approach for Nightingale as a
portfolio project and the upgrade path for live audio generation.

## Current Public URLs

- Portfolio frontend: https://yaxuanm.github.io/Nightingale/
- Stable Audio 3 demo Space: https://huggingface.co/spaces/yaxuanmmmmm/nightingale-stable-audio-3-demo
- GitHub repository: https://github.com/yaxuanm/Nightingale

## Deployment Strategy

Nightingale is split into independent deployable parts:

```text
React frontend          -> GitHub Pages
Main FastAPI service    -> CPU web service when needed
Stable Audio 3 service  -> GPU runtime when real-time generation is needed
Generated media         -> Supabase Storage
```

This keeps the portfolio version inexpensive while leaving a clean path to a
fully live demo.

## Option 1: Zero-Cost Portfolio Build

Use this for a stable public portfolio link.

- Host the React app on GitHub Pages.
- Show the product flow, generated scenes, and sample audio.
- Keep real-time Stable Audio generation disabled or available only as an
  experimental link.
- Run live generation locally or from a temporary notebook when presenting.

Benefits:

- No ongoing cost.
- Stable URL for resumes and portfolio pages.
- No risk of surprise GPU billing.

Limitations:

- Public visitors may not get real-time audio generation unless a GPU runtime is
  active.

## Option 2: Hugging Face Space Demo

The repo includes a Gradio Space package in:

```text
deploy/huggingface-space/
```

The package uses:

```env
STABLE_AUDIO_MODEL=stabilityai/stable-audio-3-small-sfx
STABLE_AUDIO_MAX_DURATION=11.0
```

Required Space secret:

```env
HF_TOKEN=hf_your_token_here
```

The token must belong to a Hugging Face account that has accepted the Stable
Audio 3 model terms.

Hardware note:

- CPU can build the Space but is not suitable for a polished real-time Stable
  Audio 3 demo.
- Personal Hugging Face accounts need PRO to host ZeroGPU Spaces.
- Paid GPU hardware can be enabled temporarily for presentations, but should not
  be turned on without a deliberate cost decision.

## Option 3: Production-Style Live Generation

Use this when the project needs reliable real-time generation.

Recommended architecture:

- Frontend: GitHub Pages, Vercel, or Netlify.
- Main API: Render, Fly.io, Railway, or another CPU FastAPI host.
- Audio generation: Modal or another serverless GPU provider with scale-to-zero.
- Storage: Supabase bucket for generated audio and images.
- Cache: hash prompt and generation settings to avoid paying for duplicate
  generations.

This is the best balance for a real product because the GPU is only active while
audio is being generated.

## GitHub Pages Frontend

The frontend is configured for the `/Nightingale/` base path. The workflow in
`.github/workflows/deploy-pages.yml` builds the React app and publishes it to
GitHub Pages.

Local verification:

```bash
cd ambiance-weaver-react
CI=true npm test -- --watchAll=false
CI=true npm run build
```

## Local Development

### Frontend

```bash
cd ambiance-weaver-react
npm install
npm start
```

### Main API

```bash
cd backend
python -m venv venv_gemini
source venv_gemini/bin/activate
pip install -r requirements-gemini-working.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Stable Audio 3 Service

```bash
cd backend
python -m venv venv_stableaudio
source venv_stableaudio/bin/activate
pip install -r requirements-stable-audio.txt
python -m uvicorn app.main_stable_audio:app --host 0.0.0.0 --port 8001
```

On Windows, activate virtual environments with:

```powershell
.\venv_gemini\Scripts\activate
.\venv_stableaudio\Scripts\activate
```

## Required Environment Variables

Backend:

```env
GOOGLE_API_KEY=your-google-api-key
STABILITY_API_KEY=your-stability-api-key
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key
HF_TOKEN=your-hugging-face-token
STABLE_AUDIO_MODEL=stabilityai/stable-audio-3-small-sfx
STABLE_AUDIO_DISPLAY_NAME=Stable Audio 3 Small SFX
STABLE_AUDIO_MAX_DURATION=11.0
CORS_ORIGINS=http://localhost:3000,https://yaxuanm.github.io
```

Frontend:

```env
REACT_APP_GEMINI_API_URL=http://localhost:8000
REACT_APP_STABLE_AUDIO_API_URL=http://localhost:8001
REACT_APP_FRONTEND_URL=http://localhost:3000
```

Never commit real `.env` files or API tokens.

## Health Checks

```bash
curl http://localhost:8000/health
curl http://localhost:8001/health
```

Python syntax check:

```bash
cd backend
python -m py_compile app/main.py app/main_stable_audio.py app/services/stable_audio_service.py
```

## Deployment Checklist

- [ ] Frontend production build succeeds.
- [ ] GitHub Pages workflow is green.
- [ ] Hugging Face token is stored only as a secret.
- [ ] Stable Audio 3 terms have been accepted by the token owner.
- [ ] GPU hardware choice is intentional and documented.
- [ ] Supabase keys are configured in the backend host.
- [ ] CORS origins match the deployed frontend URL.
- [ ] Sample audio or a live GPU runtime is available for portfolio review.
