import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, Grid, TextField } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  WorkOutline as WorkIcon,
  Spa as SpaIcon,
  AutoStories as StoryIcon,
  MusicNote as MusicIcon,
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
    icon: StoryIcon,
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
          mb: uiSystem.spacing.large,
        }}
      >
        <Box
          sx={{
            width: 120,
            height: 120,
            borderRadius: uiSystem.borderRadius.medium,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'linear-gradient(135deg, #2d9c93 0%, #1a5f5a 100%)',
            overflow: 'hidden',
          }}
        >
          <img src={`${process.env.PUBLIC_URL}/logo.png`} alt="App Logo" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
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
                p: uiSystem.spacing.large,
                cursor: 'pointer',
                height: '200px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                background: uiSystem.colors.white05,
                border: '1px solid',
                borderColor: uiSystem.colors.white20,
                borderRadius: uiSystem.borderRadius.medium,
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: uiSystem.shadows.medium,
                }
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: uiSystem.spacing.medium }}>
                <mode.icon sx={{ color: uiSystem.colors.white, fontSize: 32 }} />
                <Typography 
                  variant="h3" 
                  sx={{ 
                    color: uiSystem.colors.white,
                    ...uiSystem.typography.h3,
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