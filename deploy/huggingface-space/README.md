---
title: Nightingale Stable Audio 3 Demo
emoji: 🎧
colorFrom: indigo
colorTo: green
sdk: gradio
sdk_version: 5.35.0
app_file: app.py
pinned: false
license: other
---

# Nightingale Stable Audio 3 Demo

This Space is a lightweight real-time audio generation demo for Nightingale, an
AI soundscape product that turns emotional prompts into personalized ambience.

The demo uses `stabilityai/stable-audio-3-small-sfx` through
`stable-audio-tools`. It is designed for short soundscape clips rather than long
music tracks, which fits the product's focus on focus, memory, sleep, and
immersive ambience.

## Runtime Notes

This Space expects `HF_TOKEN` to be configured as a Space secret. The token must
belong to a Hugging Face account that has accepted the gated Stable Audio 3 model
terms.

For real-time generation, GPU hardware is recommended. Hugging Face CPU Spaces
can build and display the app, but Stable Audio 3 generation will be too slow for
a polished public demo. For a zero-cost portfolio presentation, use the main
GitHub Pages app with pre-generated sample clips, or start a temporary local or
Colab GPU runtime during live demos.

Main portfolio app: https://yaxuanm.github.io/Nightingale/
