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
  ];

  return (
    <Box
      sx={{
        p: 4,
        maxWidth: '100vw', // Full width
        minHeight: '100vh', // Full height
        margin: '0 auto',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: `url(${process.env.PUBLIC_URL}/cover.png) no-repeat center center fixed`, // Set background image using PUBLIC_URL
        backgroundSize: 'cover',
        position: 'relative',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'linear-gradient(to bottom, rgba(12, 26, 26, 0.8), rgba(12, 26, 26, 0.5), rgba(12, 26, 26, 0.8))', // Greenish overlay
          zIndex: 1,
        },
      }}
    >
      <Box sx={{ position: 'relative', zIndex: 2, textAlign: 'center', mb: 4 }}>
        <img src={`${process.env.PUBLIC_URL}/logo.png`} alt="Nightingale Logo" style={{ width: '150px', height: 'auto', marginBottom: '20px' }} />
        <Typography variant="h3" sx={{ mb: 4, textAlign: 'center', color: 'white' }}>
          Nightingale - Screen Overview
        </Typography>
      </Box>

      <Box sx={{ position: 'relative', zIndex: 2, display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, gap: 3, maxWidth: 800 }}>
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