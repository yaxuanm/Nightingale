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

It also provides lightweight fallback endpoints for prompt and option generation
so the public portfolio can run without a paid Gemini backend.
