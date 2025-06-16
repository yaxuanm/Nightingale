import React from 'react';
import { Box, Typography, Paper, Grid, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';

const Overview = () => {
  const navigate = useNavigate();

  const screens = [
    {
      title: 'Onboarding',
      description: 'Welcome screen with app introduction',
      path: '/onboarding'
    },
    {
      title: 'Main Screen',
      description: 'Main interaction screen with text input and tags',
      path: '/main'
    },
    {
      title: 'AI Chat',
      description: 'Interactive chat with AI assistant',
      path: '/chat'
    },
    {
      title: 'Player',
      description: 'Soundscape player with controls',
      path: '/player'
    },
    {
      title: 'Lock Screen',
      description: 'Lock screen music player',
      path: '/lockscreen'
    }
  ];

  return (
    <Box sx={{ p: 4, maxWidth: 1200, margin: '0 auto' }}>
      <Typography variant="h3" sx={{ mb: 4, textAlign: 'center' }}>
        Ambiance Weaver - Screen Overview
      </Typography>
      
      <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, gap: 3 }}>
        {screens.map((screen, index) => (
          <Paper
            key={index}
            sx={{
              p: 3,
              height: '100%',
              display: 'flex',
              flexDirection: 'column',
              gap: 2,
              transition: 'transform 0.2s',
              '&:hover': {
                transform: 'translateY(-4px)',
                boxShadow: 3
              }
            }}
          >
            <Typography variant="h5" color="primary">
              {screen.title}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {screen.description}
            </Typography>
            <Button
              variant="contained"
              onClick={() => navigate(screen.path)}
              sx={{ mt: 'auto' }}
            >
              View Screen
            </Button>
          </Paper>
        ))}
      </Box>
    </Box>
  );
};

export default Overview; 