import React, { useState } from 'react';
import { Box, Typography, Button, Paper, Grid } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  WorkOutline as WorkIcon,
  Spa as SpaIcon,
  AutoStories as StoryIcon,
  MusicNote as MusicIcon,
} from '@mui/icons-material';

const modes = [
  {
    id: 'focus',
    title: '专注模式',
    description: '为学习和工作创造专注的环境',
    icon: WorkIcon,
    color: '#2d9c93'
  },
  {
    id: 'relax',
    title: '放松模式',
    description: '帮助缓解压力和焦虑',
    icon: SpaIcon,
    color: '#9c2d8f'
  },
  {
    id: 'story',
    title: '故事模式',
    description: '将文字转化为沉浸式音景',
    icon: StoryIcon,
    color: '#2d8f9c'
  },
  {
    id: 'music',
    title: '音乐模式',
    description: '创作独特的背景音乐',
    icon: MusicIcon,
    color: '#8f9c2d'
  }
];

const Onboarding = () => {
  const navigate = useNavigate();
  const [selectedMode, setSelectedMode] = useState<string | null>(null);

  const handleModeSelect = (modeId: string) => {
    setSelectedMode(modeId);
  };

  const handleStart = () => {
    if (selectedMode) {
      navigate('/main', { state: { mode: selectedMode } });
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #1a2332 0%, #0f1419 100%)',
        p: 3
      }}
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <Paper
          elevation={3}
          sx={{
            p: 4,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: 3,
            maxWidth: 800,
            width: '100%',
            background: 'rgba(255, 255, 255, 0.05)',
            backdropFilter: 'blur(10px)',
            border: '1px solid rgba(255, 255, 255, 0.1)'
          }}
        >
          <Box
            sx={{
              width: 120,
              height: 120,
              borderRadius: 4,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: 'linear-gradient(135deg, #2d9c93 0%, #1a5f5a 100%)',
              mb: 2
            }}
          >
            <img src="/logo.svg" alt="App Logo" style={{ width: 100, height: 100, borderRadius: 28 }} />
          </Box>

          <Typography variant="h4" sx={{ color: 'white', fontWeight: 700, textAlign: 'center' }}>
            Ambiance Weaver
          </Typography>

          <Typography
            variant="body1"
            sx={{
              color: 'rgba(255, 255, 255, 0.7)',
              textAlign: 'center',
              mb: 4
            }}
          >
            选择一种模式，开始你的音景创作之旅
          </Typography>

          <Grid container spacing={3} sx={{ mb: 4 }}>
            {modes.map((mode) => (
              <Grid item xs={12} sm={6} key={mode.id}>
                <Paper
                  onClick={() => handleModeSelect(mode.id)}
                  sx={{
                    p: 3,
                    cursor: 'pointer',
                    background: selectedMode === mode.id 
                      ? `linear-gradient(135deg, ${mode.color} 0%, ${mode.color}80 100%)`
                      : 'rgba(255, 255, 255, 0.05)',
                    border: '1px solid',
                    borderColor: selectedMode === mode.id ? mode.color : 'rgba(255, 255, 255, 0.1)',
                    transition: 'all 0.3s ease',
                    '&:hover': {
                      transform: 'translateY(-4px)',
                      boxShadow: 3
                    }
                  }}
                >
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                    <mode.icon sx={{ color: mode.color, fontSize: 32 }} />
                    <Typography variant="h6" sx={{ color: 'white' }}>
                      {mode.title}
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                    {mode.description}
                  </Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>

          <Button
            variant="contained"
            size="large"
            onClick={handleStart}
            disabled={!selectedMode}
            sx={{
              width: '100%',
              height: 50,
              background: selectedMode 
                ? 'linear-gradient(135deg, #2d9c93 0%, #1a5f5a 100%)'
                : 'rgba(255, 255, 255, 0.1)',
              borderRadius: 25,
              color: 'white',
              fontSize: 16,
              fontWeight: 600,
              '&:hover': {
                background: selectedMode
                  ? 'linear-gradient(135deg, #1a5f5a 0%, #2d9c93 100%)'
                  : 'rgba(255, 255, 255, 0.1)'
              }
            }}
          >
            开始创作
          </Button>
        </Paper>
      </motion.div>
    </Box>
  );
};

export default Onboarding; 