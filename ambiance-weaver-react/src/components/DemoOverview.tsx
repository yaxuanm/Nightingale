import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  Button, 
  IconButton,
  Chip,
  Stack,
  Card,
  CardContent,
  CardMedia
} from '@mui/material';
import {
  Chat as ChatIcon,
  MusicNote as MusicIcon,
  PlayArrow as PlayIcon,
  Settings as SettingsIcon,
  Favorite as FavoriteIcon,
  Mic as MicIcon,
  HelpOutline as HelpIcon,
  WorkOutline as WorkIcon,
  Spa as SpaIcon,
  AutoStories as StoryIcon,
  SkipNext as NextIcon,
  SkipPrevious as PreviousIcon,
  Tune as TuneIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const DemoOverview = () => {
  const navigate = useNavigate();

  const screenPreviews = [
    {
      title: 'Onboarding',
      subtitle: 'Welcome Screen',
      description: 'Welcome users and guide them to choose usage modes',
      path: '/onboarding',
      icon: SettingsIcon,
      color: '#2d9c93',
      features: [
        'App introduction and brand showcase',
        'Four usage mode selections',
        'AI assistant name customization',
        'Personalized settings guidance'
      ]
    },
    {
      title: 'Main Screen',
      subtitle: 'Main Interface',
      description: 'Core interaction interface, user input and AI chat entry',
      path: '/main',
      icon: ChatIcon,
      color: '#9c2d8f',
      features: [
        'Text input box (supports multi-line input)',
        'Voice input functionality',
        'Preset prompt suggestions',
        'Help prompt system',
        'AI chat entry'
      ]
    },
    {
      title: 'AI Chat',
      subtitle: 'AI Chat Interface',
      description: 'Intelligent dialogue system, guiding users to create personalized soundscapes',
      path: '/chat',
      icon: ChatIcon,
      color: '#2d8f9c',
      features: [
        'Intelligent dialogue interaction',
        'Atmosphere selection (cozy/spacious/lively/etc.)',
        'Mood selection (relaxed/focused/inspired/etc.)',
        'Sound effect element selection',
        'Real-time soundscape generation',
        'Background image generation'
      ]
    },
    {
      title: 'Player',
      subtitle: 'Soundscape Player',
      description: 'Complete soundscape playback and control interface',
      path: '/player',
      icon: PlayIcon,
      color: '#8f9c2d',
      features: [
        'Play/pause control',
        'Progress bar and time display',
        'Volume control and mute',
        'Audio effect adjustment',
        'Favorites functionality',
        'Background image display'
      ]
    }
  ];

  return (
    <Box
      sx={{
        p: 4,
        maxWidth: '100vw',
        minHeight: '100vh',
        background: `url(${process.env.PUBLIC_URL}/cover.png) no-repeat center center fixed`,
        backgroundSize: 'cover',
        position: 'relative',
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
      {/* 标题区域 */}
      <Box sx={{ position: 'relative', zIndex: 2, textAlign: 'center', mb: 4 }}>
        <motion.img 
          src={`${process.env.PUBLIC_URL}/logo.png`} 
          alt="Nightingale Logo" 
          style={{ width: '120px', height: 'auto', marginBottom: '20px' }}
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
        />
        <Typography variant="h3" sx={{ mb: 2, color: 'white', fontWeight: 700 }}>
          Nightingale Demo
        </Typography>
        <Typography variant="h6" sx={{ mb: 4, color: 'rgba(255, 255, 255, 0.8)' }}>
          Intelligent Soundscape Generation App - Complete Feature Demo
        </Typography>
      </Box>

      {/* 页面预览网格 */}
      <Box sx={{ position: 'relative', zIndex: 2, maxWidth: 1400, margin: '0 auto' }}>
        <Grid container spacing={3}>
          
          {screenPreviews.map((screen, index) => (
            <Grid item xs={12} md={6} lg={3} key={index}>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
              >
                <Card
                  sx={{
                    height: 500,
                    background: 'rgba(255, 255, 255, 0.05)',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '16px',
                    overflow: 'hidden',
                    transition: 'all 0.3s ease',
                    cursor: 'pointer',
                    '&:hover': {
                      transform: 'translateY(-8px)',
                      boxShadow: '0 20px 40px rgba(0,0,0,0.3)',
                      border: `1px solid ${screen.color}`,
                    }
                  }}
                  onClick={() => navigate(screen.path)}
                >
                  {/* 页面标题 */}
                  <CardContent sx={{ p: 3, pb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                      <Box
                        sx={{
                          width: 40,
                          height: 40,
                          borderRadius: '50%',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          background: `linear-gradient(135deg, ${screen.color} 0%, ${screen.color}80 100%)`,
                        }}
                      >
                        <screen.icon sx={{ color: 'white', fontSize: 20 }} />
                      </Box>
                      <Box>
                        <Typography variant="h6" sx={{ color: 'white', fontWeight: 600 }}>
                          {screen.title}
                        </Typography>
                        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                          {screen.subtitle}
                        </Typography>
                      </Box>
                    </Box>

                    <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)', mb: 2 }}>
                      {screen.description}
                    </Typography>

                    <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                      {screen.features.slice(0, 3).map((feature, idx) => (
                        <Chip
                          key={idx}
                          label={feature}
                          size="small"
                          sx={{
                            bgcolor: 'rgba(45, 156, 147, 0.1)',
                            color: '#2d9c93',
                            border: '1px solid rgba(45, 156, 147, 0.2)',
                            fontSize: '0.7rem',
                          }}
                        />
                      ))}
                      {screen.features.length > 3 && (
                        <Chip
                          label={`+${screen.features.length - 3} more`}
                          size="small"
                          sx={{
                            bgcolor: 'rgba(255, 255, 255, 0.1)',
                            color: 'rgba(255, 255, 255, 0.7)',
                            fontSize: '0.9rem',
                          }}
                        />
                      )}
                    </Stack>
                  </CardContent>

                  {/* 页面截图预览区域 */}
                  <Box sx={{ 
                    height: 300, 
                    background: 'rgba(0, 0, 0, 0.3)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    position: 'relative',
                    overflow: 'hidden'
                  }}>
                    {/* 这里可以放置实际的页面截图 */}
                    <Box sx={{
                      width: '90%',
                      height: '80%',
                      background: 'rgba(255, 255, 255, 0.1)',
                      borderRadius: '8px',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      position: 'relative'
                    }}>
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.6)', textAlign: 'center' }}>
                        {screen.title} Preview
                      </Typography>
                      <Box
                        sx={{
                          position: 'absolute',
                          top: '50%',
                          left: '50%',
                          transform: 'translate(-50%, -50%)',
                          width: 60,
                          height: 60,
                          borderRadius: '50%',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          background: `linear-gradient(135deg, ${screen.color} 0%, ${screen.color}80 100%)`,
                          opacity: 0.3,
                        }}
                      >
                        <screen.icon sx={{ color: 'white', fontSize: 24 }} />
                      </Box>
                    </Box>
                    
                    {/* 点击提示 */}
                    <Box
                      sx={{
                        position: 'absolute',
                        bottom: 10,
                        right: 10,
                        background: 'rgba(0, 0, 0, 0.7)',
                        color: 'white',
                        px: 2,
                        py: 1,
                        borderRadius: '20px',
                        fontSize: '0.9rem',
                        opacity: 0.8,
                      }}
                    >
                      Click to view
                    </Box>
                  </Box>
                </Card>
              </motion.div>
            </Grid>
          ))}
        </Grid>

        {/* 底部操作按钮 */}
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'center', 
          gap: 2, 
          mt: 4,
          position: 'relative',
          zIndex: 3
        }}>
          <Button
            variant="contained"
            size="large"
            onClick={() => navigate('/')}
            sx={{
              bgcolor: '#2d9c93 !important',
              px: 4,
              py: 1.5,
              '&:hover': { 
                bgcolor: '#1a5f5a !important',
                boxShadow: '0 15px 40px rgba(45, 156, 147, 0.5)'
              },
              cursor: 'pointer',
              position: 'relative',
              zIndex: 3,
              '&.MuiButton-contained': {
                background: 'linear-gradient(135deg, #2d9c93 0%, #1a5f5a 100%) !important',
                boxShadow: '0 10px 30px rgba(45, 156, 147, 0.4)',
              }
            }}
          >
            Back to Overview
          </Button>
          <Button
            variant="outlined"
            size="large"
            onClick={() => navigate('/onboarding')}
            sx={{
              borderColor: '#2d9c93 !important',
              color: '#2d9c93 !important',
              px: 4,
              py: 1.5,
              '&:hover': { 
                borderColor: '#2d9c93 !important', 
                bgcolor: 'rgba(45, 156, 147, 0.1) !important' 
              },
              cursor: 'pointer',
              position: 'relative',
              zIndex: 3,
              '&.MuiButton-outlined': {
                borderColor: '#2d9c93',
                color: '#2d9c93',
              }
            }}
          >
            Start Experience
          </Button>
        </Box>
      </Box>
    </Box>
  );
};

export default DemoOverview; 