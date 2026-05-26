import React from 'react';
import {
  Box,
  Button,
  Chip,
  Grid,
  Stack,
  Typography,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Download as DownloadIcon,
  GraphicEq as GraphicEqIcon,
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import PageLayout from './PageLayout';

const demoSamples = [
  {
    slug: 'warm-summer-evening',
    title: 'Warm Summer Evening',
    duration: 8,
    seed: 1742,
    prompt: 'Warm summer evening ambience with cicadas, distant birds, soft wind through trees, nostalgic and calm.',
    file: '/demo-audio/warm-summer-evening.wav',
  },
  {
    slug: 'rain-window-focus',
    title: 'Rain Window Focus',
    duration: 8,
    seed: 2518,
    prompt: 'Steady rain tapping on a window, soft room tone, muted city distance, focused and peaceful.',
    file: '/demo-audio/rain-window-focus.wav',
  },
  {
    slug: 'ocean-breath-meditation',
    title: 'Ocean Breath Meditation',
    duration: 8,
    seed: 3107,
    prompt: 'Slow ocean waves rolling onto sand, airy coastal wind, spacious and meditative atmosphere.',
    file: '/demo-audio/ocean-breath-meditation.wav',
  },
  {
    slug: 'midnight-library',
    title: 'Midnight Library',
    duration: 8,
    seed: 4309,
    prompt: 'Quiet midnight library ambience, soft page turns, faint wooden room tone, intimate and reflective.',
    file: '/demo-audio/midnight-library.wav',
  },
];

const modelName = 'stabilityai/stable-audio-3-small-sfx';

const DemoSamples: React.FC = () => {
  const navigate = useNavigate();

  return (
    <PageLayout showBackground={false}>
      <Box
        sx={{
          width: '100%',
          maxWidth: 1080,
          display: 'flex',
          flexDirection: 'column',
          gap: 3,
        }}
      >
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/demo')}
          sx={{ alignSelf: 'flex-start', color: 'rgba(255,255,255,0.78)' }}
        >
          Back to demo
        </Button>

        <Box>
          <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 1 }}>
            <GraphicEqIcon sx={{ color: '#64d6cb' }} />
            <Typography variant="h4" sx={{ color: '#fff', fontWeight: 700 }}>
              Stable Audio 3 Samples
            </Typography>
          </Stack>
          <Typography sx={{ color: 'rgba(255,255,255,0.72)', maxWidth: 760 }}>
            Pre-generated portfolio clips created with the official Stability AI Stable Audio 3
            Hugging Face Space. Each sample keeps its prompt, model, duration, and seed visible
            so the demo remains traceable.
          </Typography>
        </Box>

        <Grid container spacing={2.5}>
          {demoSamples.map((sample) => {
            const audioSrc = `${process.env.PUBLIC_URL}${sample.file}`;
            return (
              <Grid item xs={12} md={6} key={sample.slug}>
                <Box
                  sx={{
                    height: '100%',
                    p: 2.5,
                    borderRadius: 2,
                    border: '1px solid rgba(255,255,255,0.14)',
                    background: 'rgba(255,255,255,0.055)',
                    backdropFilter: 'blur(16px)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: 2,
                  }}
                >
                  <Box>
                    <Typography variant="h6" sx={{ color: '#fff', fontWeight: 700, mb: 0.75 }}>
                      {sample.title}
                    </Typography>
                    <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                      <Chip label={`${sample.duration}s`} size="small" />
                      <Chip label={`seed ${sample.seed}`} size="small" />
                      <Chip label="Stable Audio 3" size="small" />
                    </Stack>
                  </Box>

                  <Typography
                    sx={{
                      color: 'rgba(255,255,255,0.76)',
                      fontSize: '0.92rem',
                      lineHeight: 1.55,
                      minHeight: { md: 68 },
                    }}
                  >
                    {sample.prompt}
                  </Typography>

                  <Box
                    component="audio"
                    controls
                    preload="metadata"
                    src={audioSrc}
                    sx={{ width: '100%' }}
                  />

                  <Stack direction="row" justifyContent="space-between" alignItems="center" spacing={2}>
                    <Typography sx={{ color: 'rgba(255,255,255,0.54)', fontSize: '0.78rem' }}>
                      {modelName}
                    </Typography>
                    <Button
                      component="a"
                      href={audioSrc}
                      download={`${sample.slug}.wav`}
                      startIcon={<DownloadIcon />}
                      size="small"
                      sx={{ color: '#64d6cb', flexShrink: 0 }}
                    >
                      Download
                    </Button>
                  </Stack>
                </Box>
              </Grid>
            );
          })}
        </Grid>
      </Box>
    </PageLayout>
  );
};

export default DemoSamples;
