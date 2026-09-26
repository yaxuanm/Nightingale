---
title: Nightingale Backend
emoji: 🎧
colorFrom: indigo
colorTo: green
sdk: docker
pinned: false
license: mit
---

# Nightingale Backend

Portfolio backend for Nightingale.

This Space exposes a small FastAPI service for the public GitHub Pages demo. It
proxies Stable Audio 3 generation through the official Stability AI Hugging Face
Space and returns generated WAV URLs to the frontend.

## Owner-managed Stability Audio

Visitors never provide an API key. Configure `STABILITY_API_KEY` as a Hugging
Face Space **Secret** so this backend can call Stable Audio 2.5 directly. The
key is never returned to the browser or written to logs. If the secret is
absent, the existing Hugging Face Space proxy remains the fallback.

Stable Audio 2.5 supports up to 3 minutes per request; the public UI offers
10 seconds, 30 seconds, 1 minute, 2 minutes, and 3 minutes.

Server configuration:

```env
STABILITY_AUDIO_API_URL=https://api.stability.ai/v2beta/audio/stable-audio-2/text-to-audio
STABILITY_AUDIO_MODEL=stable-audio-2.5
STABILITY_AUDIO_MAX_DURATION=180
STABILITY_AUDIO_STEPS=8
STABILITY_AUDIO_CFG_SCALE=1.0
```

It also provides lightweight fallback endpoints for prompt and option generation
so the public portfolio can run without a paid Gemini backend.

## OpenAI scene backgrounds

For generated player backgrounds, set `OPENAI_API_KEY` as a Hugging Face Space
**Secret**. The backend uses `gpt-image-2.5-flare` at low quality and a 16:9
landscape size to keep generation latency and cost low. This key never reaches
the browser, source repository, or logs. If the provider is unavailable, the
frontend keeps using its curated local background instead.

```env
OPENAI_API_KEY=your_owner_managed_openai_key
OPENAI_IMAGE_MODEL=gpt-image-2.5-flare
OPENAI_IMAGE_SIZE=1536x864
OPENAI_IMAGE_QUALITY=low
```

## Gemini-guided demo

To make the sample-audio experience more interactive, set `GOOGLE_API_KEY` as a
Hugging Face Space **Secret**, never a frontend environment variable. With this
secret configured, the demo uses Gemini for inspirations, choices, prompt edits,
and story copy. OpenAI backgrounds take priority whenever `OPENAI_API_KEY` is
configured. If either provider is unavailable, these endpoints return local
fallbacks. Provider secrets are never exposed to visitors.

```env
GOOGLE_API_KEY=your_owner_managed_gemini_key
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_IMAGE_MODEL=gemini-3.1-flash-image
```
