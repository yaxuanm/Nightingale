import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, Grid, TextField } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  WorkOutline as WorkIcon,
  Spa as SpaIcon,
  AutoStories as StoryIcon,
  MusicNote as MusicIcon,
  Hearing as HearingIcon,
  MenuBook as BookIcon,
  Lightbulb as LightbulbIcon,
} from '@mui/icons-material';
import PageLayout from './PageLayout';
import { uiSystem } from '../theme/uiSystem';

const modes = [
  {
    id: 'focus',
    title: 'Deep Focus',
    description: 'Helps you concentrate for deep work.',
    icon: WorkIcon,
    color: '#2d9c93'
  },
  {
    id: 'creative',
    title: 'Creative Flow',
    description: 'Ignites creativity and inspiration.',
    icon: LightbulbIcon,
    color: '#2d8f9c'
  },
  {
    id: 'mindful',
    title: 'Mindful Escape',
    description: 'Brings calm and inner peace.',
    icon: SpaIcon,
    color: '#9c2d8f'
  },
  {
    id: 'sleep',
    title: 'Sleep',
    description: 'Helps you fall asleep and stay asleep.',
    icon: MusicIcon,
    color: '#8f9c2d'
  },
  {
    id: 'story',
    title: 'Story',
    description: 'Bring your story to life with narration and sound.',
    icon: BookIcon,
    color: '#e6b800'
  },
  {
    id: 'asmr',
    title: 'ASMR',
    description: 'Immersive, soothing sounds for relaxation and tingles.',
    icon: HearingIcon,
    color: '#b39ddb'
  }
];

interface OnboardingProps {
  usePageLayout?: boolean;
}

const Onboarding: React.FC<OnboardingProps> = ({ usePageLayout = true }) => {
  const navigate = useNavigate();

  const handleModeSelect = (modeId: string) => {
    navigate('/main', { state: { mode: modeId } });
  };

  const content = (
    <>
      {/* Logo Section */}
      <Box
        sx={{
          width: '100%',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          mb: { xs: uiSystem.spacing.large, md: uiSystem.spacing.section },
        }}
      >
        <Box
          sx={{
            width: { xs: 120, md: 150, lg: 180, xl: 200 },
            height: { xs: 120, md: 150, lg: 180, xl: 200 },
            borderRadius: '50%',
            overflow: 'hidden',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'rgba(45,156,147,0.10)',
          }}
        >
          <img src={`${process.env.PUBLIC_URL}/logo.png`} alt="App Logo" style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }} />
        </Box>
      </Box>

      <Typography
        variant="subtitle1"
        sx={{
          color: uiSystem.colors.white70,
          textAlign: 'center',
          mb: uiSystem.spacing.medium,
          fontStyle: 'italic',
          fontWeight: 400,
          letterSpacing: 1,
        }}
      >
        Let Sound Touch the Soul.
      </Typography>

      {/* Title */}
      <Typography 
        variant="h1" 
        sx={{ 
          color: uiSystem.colors.white, 
          textAlign: 'center',
          mb: uiSystem.spacing.large,
          ...uiSystem.typography.h1,
        }}
      >
        Nightingale
      </Typography>

      {/* Description */}
      <Typography
        variant="body1"
        sx={{
          color: uiSystem.colors.white70,
          textAlign: 'center',
          mb: uiSystem.spacing.section,
          ...uiSystem.typography.body1,
        }}
      >
        Select a mode to begin your soundscape creation journey
      </Typography>

      {/* Mode Selection Grid */}
      <Grid container spacing={3} sx={{ mb: uiSystem.spacing.section }}>
        {modes.map((mode) => (
          <Grid item xs={12} sm={6} key={mode.id}>
            <Box
              onClick={() => handleModeSelect(mode.id)}
              sx={{
                p: { xs: 3, md: 4, lg: 5 },
                cursor: 'pointer',
                height: { xs: 200, md: 220, lg: 260 },
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                background: uiSystem.colors.white05,
                border: '1px solid',
                borderColor: uiSystem.colors.white20,
                borderRadius: uiSystem.borderRadius.large,
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-8px)',
                  boxShadow: uiSystem.shadows.medium,
                }
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: { xs: 2, md: 3 }, mb: { xs: 2, md: 3 } }}>
                <mode.icon sx={{ color: uiSystem.colors.white, fontSize: { xs: 32, md: 40, lg: 48 } }} />
                <Typography 
                  variant="h3" 
                  sx={{ 
                    color: uiSystem.colors.white,
                    ...uiSystem.typography.h3,
                    fontSize: { xs: '1.3rem', md: '1.5rem', lg: '1.8rem' },
                  }}
                >
                  {mode.title}
                </Typography>
              </Box>
              <Typography 
                variant="body2" 
                sx={{ 
                  color: uiSystem.colors.white70,
                  ...uiSystem.typography.body2,
                  fontSize: { xs: '1.1rem', md: '1.15rem', lg: '1.2rem' },
                }}
              >
                {mode.description}
              </Typography>
            </Box>
          </Grid>
        ))}
      </Grid>
    </>
  );

  if (usePageLayout) {
    return (
      <PageLayout maxWidth={1000} minHeight="700px">
        {content}
      </PageLayout>
    );
  }

  return content;
};

export default Onboarding; 