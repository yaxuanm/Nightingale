import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, Paper, Grid, TextField } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  WorkOutline as WorkIcon,
  Spa as SpaIcon,
  AutoStories as StoryIcon,
  MusicNote as MusicIcon,
} from '@mui/icons-material';
import { useAiName } from '../utils/AiNameContext';

const modes = [
  {
    id: 'focus',
    title: 'Focus Mode',
    description: 'Create a focused environment for study and work',
    icon: WorkIcon,
    color: '#2d9c93'
  },
  {
    id: 'relax',
    title: 'Relax Mode',
    description: 'Help relieve stress and anxiety',
    icon: SpaIcon,
    color: '#9c2d8f'
  },
  {
    id: 'story',
    title: 'Story Mode',
    description: 'Transform text into immersive soundscapes',
    icon: StoryIcon,
    color: '#2d8f9c'
  },
  {
    id: 'music',
    title: 'Music Mode',
    description: 'Create unique background music',
    icon: MusicIcon,
    color: '#8f9c2d'
  }
];

const Onboarding = () => {
  const navigate = useNavigate();
  const [selectedMode, setSelectedMode] = useState<string | null>(null);
  const { aiName, setAiName } = useAiName();

  // New: Local state for the input field, which will be cleared on mount
  const [localAiNameInput, setLocalAiNameInput] = useState('');

  // New: Clear local input on component mount
  useEffect(() => {
    setLocalAiNameInput('');
  }, []); // Run once on mount

  const handleModeSelect = (modeId: string) => {
    setSelectedMode(modeId);
  };

  const handleStart = () => {
    if (selectedMode) {
      // Update aiName in context (and localStorage) with the local input field's value
      setAiName(localAiNameInput);
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
        background: `url(${process.env.PUBLIC_URL}/cover.png) no-repeat center center fixed`,
        backgroundSize: 'cover',
        position: 'relative',
        p: 3,
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'linear-gradient(to bottom, rgba(12, 26, 26, 0.8), rgba(12, 26, 26, 0.5), rgba(12, 26, 26, 0.8))',
          zIndex: 1,
        },
      }}
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        style={{ position: 'relative', zIndex: 2, width: '100%', display: 'flex', justifyContent: 'center' }}
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
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '16px',
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
              mb: 2,
              overflow: 'hidden',
            }}
          >
            <img src={`${process.env.PUBLIC_URL}/logo.png`} alt="App Logo" style={{ width: '100%', height: '100%', objectFit: 'contain' }} />
          </Box>

          <Typography variant="h4" sx={{ color: 'white', fontWeight: 700, textAlign: 'center' }}>
            Nightingale
          </Typography>

          <TextField
            fullWidth
            variant="outlined"
            placeholder="Give your Nightingale a name"
            value={localAiNameInput} // Bind to local state
            onChange={(e) => setLocalAiNameInput(e.target.value)} // Update local state
            autoComplete="off"
            sx={{
              mb: 2,
              '& .MuiOutlinedInput-root': {
                color: 'white',
                fieldset: { borderColor: 'rgba(255, 255, 255, 0.2)' },
                '&:hover fieldset': { borderColor: '#2d9c93' },
                '&.Mui-focused fieldset': { borderColor: '#2d9c93' },
              },
              '& .MuiInputBase-input::placeholder': {
                color: 'rgba(255, 255, 255, 0.7)',
                opacity: 1,
              },
            }}
          />

          <Typography
            variant="body1"
            sx={{
              color: 'rgba(255, 255, 255, 0.7)',
              textAlign: 'center',
              mb: 4
            }}
          >
            Select a mode to begin your soundscape creation journey
          </Typography>

          <Grid container spacing={3} sx={{ mb: 4 }}>
            {modes.map((mode) => (
              <Grid item xs={12} sm={6} key={mode.id}>
                <Paper
                  onClick={() => handleModeSelect(mode.id)}
                  sx={{
                    p: 3,
                    cursor: 'pointer',
                    height: '180px',
                    display: 'flex',
                    flexDirection: 'column',
                    justifyContent: 'space-between',
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
                    <mode.icon sx={{ color: 'white', fontSize: 32 }} />
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
            fullWidth
            size="large"
            onClick={handleStart}
            disabled={!selectedMode} // Disable until a mode is selected
            sx={{
              mt: 2,
              height: 50,
              background: 'linear-gradient(135deg, #2d9c93 0%, #1a5f5a 100%)',
              borderRadius: 25,
              color: 'white',
              fontSize: 16,
              fontWeight: 600,
              '&:hover': {
                background: 'linear-gradient(135deg, #1a5f5a 0%, #2d9c93 100%)',
              },
            }}
          >
            Start Your Journey
          </Button>
        </Paper>
      </motion.div>
    </Box>
  );
};

export default Onboarding; 