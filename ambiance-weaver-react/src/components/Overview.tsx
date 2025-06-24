import React, { useState } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Grid, 
  Button, 
  Dialog,
  DialogContent,
  DialogTitle,
  IconButton,
  Chip,
  Stack,
  Card,
  CardContent,
  CardMedia
} from '@mui/material';
import {
  Close as CloseIcon,
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
  VolumeUp as VolumeIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const Overview = () => {
  const navigate = useNavigate();
  const [selectedScreen, setSelectedScreen] = useState<any>(null);
  const [openDialog, setOpenDialog] = useState(false);

  const screens = [
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
      ],
      modes: [
        { name: 'Focus Mode', icon: WorkIcon, desc: 'Create focused environment for study and work' },
        { name: 'Relax Mode', icon: SpaIcon, desc: 'Help relieve stress and anxiety' },
        { name: 'Story Mode', icon: StoryIcon, desc: 'Transform text into immersive soundscapes' },
        { name: 'Music Mode', icon: MusicIcon, desc: 'Create unique background music' }
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
      ],
      suggestions: [
        "A cozy cafe on a rainy afternoon",
        "Gentle forest sounds with a distant waterfall",
        "The calm before a thunderstorm",
        "A quiet library with turning pages"
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
      ],
      chatFlow: [
        'Welcome and needs understanding',
        'Atmosphere and mood selection',
        'Sound effect element configuration',
        'AI generation processing',
        'Playback options provision'
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
      ],
      effects: [
        { name: 'Reverb', desc: 'Room size, damping, wet/dry ratio' },
        { name: 'Echo', desc: 'Delay, decay, repeat count' },
        { name: 'Fade', desc: 'Smooth volume transitions' },
        { name: 'Volume', desc: 'Precise volume control' }
      ]
    }
  ];

  const handleScreenClick = (screen: any) => {
    setSelectedScreen(screen);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedScreen(null);
  };

  return (
    <Box
      sx={{
        p: 4,
        maxWidth: '100vw',
        minHeight: '100vh',
        margin: '0 auto',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
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
      <Box sx={{ position: 'relative', zIndex: 2, textAlign: 'center', mb: 4 }}>
        <motion.img 
          src={`${process.env.PUBLIC_URL}/logo.png`} 
          alt="Nightingale Logo" 
          style={{ width: '150px', height: 'auto', marginBottom: '20px' }}
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
        />
        <Typography variant="h3" sx={{ mb: 2, textAlign: 'center', color: 'white', fontWeight: 700 }}>
          Nightingale
        </Typography>
        <Typography variant="h5" sx={{ mb: 4, textAlign: 'center', color: 'rgba(255, 255, 255, 0.8)' }}>
          Intelligent Soundscape Generation App - Screen Overview
        </Typography>
      </Box>

      <Box sx={{ position: 'relative', zIndex: 2, display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, gap: 3, maxWidth: 1200 }}>
        {screens.map((screen, index) => (
          <motion.div
            key={index}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: index * 0.1 }}
          >
            <Paper
              sx={{
                p: 3,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                gap: 2,
                transition: 'all 0.3s ease',
                cursor: 'pointer',
                background: 'rgba(255, 255, 255, 0.05)',
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                '&:hover': {
                  transform: 'translateY(-8px)',
                  boxShadow: '0 20px 40px rgba(0,0,0,0.3)',
                  border: `1px solid ${screen.color}`,
                }
              }}
              onClick={() => handleScreenClick(screen)}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
                <Box
                  sx={{
                    width: 50,
                    height: 50,
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: `linear-gradient(135deg, ${screen.color} 0%, ${screen.color}80 100%)`,
                  }}
                >
                  <screen.icon sx={{ color: 'white', fontSize: 24 }} />
                </Box>
                <Box>
                  <Typography variant="h5" sx={{ color: 'white', fontWeight: 600 }}>
                    {screen.title}
                  </Typography>
                  <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                    {screen.subtitle}
                  </Typography>
                </Box>
              </Box>
              
              <Typography variant="body1" sx={{ color: 'rgba(255, 255, 255, 0.8)', mb: 2 }}>
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
                      fontSize: '0.75rem',
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
                      fontSize: '0.75rem',
                    }}
                  />
                )}
              </Stack>

              <Box sx={{ display: 'flex', gap: 1, mt: 'auto' }}>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    navigate(screen.path);
                  }}
                  sx={{ 
                    borderColor: screen.color, 
                    color: screen.color,
                    '&:hover': { borderColor: screen.color, bgcolor: `${screen.color}10` }
                  }}
                >
                  View Screen
                </Button>
                <Button
                  variant="contained"
                  size="small"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleScreenClick(screen);
                  }}
                  sx={{ 
                    bgcolor: screen.color,
                    '&:hover': { bgcolor: `${screen.color}dd` }
                  }}
                >
                  Details
                </Button>
              </Box>
            </Paper>
          </motion.div>
        ))}
      </Box>

      {/* 详细信息对话框 */}
      <Dialog
        open={openDialog}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
        PaperProps={{
          sx: {
            background: 'rgba(20, 37, 37, 0.95)',
            backdropFilter: 'blur(20px)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            borderRadius: '16px',
          }
        }}
      >
        <DialogTitle sx={{ color: 'white', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            {selectedScreen && (
              <>
                <Box
                  sx={{
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    background: `linear-gradient(135deg, ${selectedScreen.color} 0%, ${selectedScreen.color}80 100%)`,
                  }}
                >
                  <selectedScreen.icon sx={{ color: 'white', fontSize: 20 }} />
                </Box>
                <Typography variant="h6">
                  {selectedScreen?.title} - {selectedScreen?.subtitle}
                </Typography>
              </>
            )}
          </Box>
          <IconButton onClick={handleCloseDialog} sx={{ color: 'white' }}>
            <CloseIcon />
          </IconButton>
        </DialogTitle>
        
        <DialogContent sx={{ color: 'white' }}>
          {selectedScreen && (
            <Box>
              <Typography variant="body1" sx={{ mb: 3, color: 'rgba(255, 255, 255, 0.8)' }}>
                {selectedScreen.description}
              </Typography>

              <Typography variant="h6" sx={{ mb: 2, color: 'white' }}>
                Main Features
              </Typography>
              <Grid container spacing={2} sx={{ mb: 3 }}>
                {selectedScreen.features.map((feature: string, idx: number) => (
                  <Grid item xs={12} sm={6} key={idx}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box
                        sx={{
                          width: 8,
                          height: 8,
                          borderRadius: '50%',
                          bgcolor: selectedScreen.color,
                        }}
                      />
                      <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                        {feature}
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>

              {/* 特殊内容展示 */}
              {selectedScreen.modes && (
                <>
                  <Typography variant="h6" sx={{ mb: 2, color: 'white' }}>
                    Usage Modes
                  </Typography>
                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    {selectedScreen.modes.map((mode: any, idx: number) => (
                      <Grid item xs={12} sm={6} key={idx}>
                        <Paper sx={{ p: 2, bgcolor: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <mode.icon sx={{ color: selectedScreen.color }} />
                            <Typography variant="subtitle2" sx={{ color: 'white' }}>
                              {mode.name}
                            </Typography>
                          </Box>
                          <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                            {mode.desc}
                          </Typography>
                        </Paper>
                      </Grid>
                    ))}
                  </Grid>
                </>
              )}

              {selectedScreen.suggestions && (
                <>
                  <Typography variant="h6" sx={{ mb: 2, color: 'white' }}>
                    Preset Suggestions
                  </Typography>
                  <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mb: 3 }}>
                    {selectedScreen.suggestions.map((suggestion: string, idx: number) => (
                      <Chip
                        key={idx}
                        label={suggestion}
                        size="small"
                        sx={{
                          bgcolor: 'rgba(45, 156, 147, 0.1)',
                          color: '#2d9c93',
                          border: '1px solid rgba(45, 156, 147, 0.2)',
                        }}
                      />
                    ))}
                  </Stack>
                </>
              )}

              {selectedScreen.chatFlow && (
                <>
                  <Typography variant="h6" sx={{ mb: 2, color: 'white' }}>
                    Chat Flow
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mb: 3 }}>
                    {selectedScreen.chatFlow.map((step: string, idx: number) => (
                      <Box key={idx} sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                        <Box
                          sx={{
                            width: 24,
                            height: 24,
                            borderRadius: '50%',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            bgcolor: selectedScreen.color,
                            fontSize: '0.9rem',
                            fontWeight: 'bold',
                          }}
                        >
                          {idx + 1}
                        </Box>
                        <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                          {step}
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                </>
              )}

              {selectedScreen.effects && (
                <>
                  <Typography variant="h6" sx={{ mb: 2, color: 'white' }}>
                    Audio Effects
                  </Typography>
                  <Grid container spacing={2} sx={{ mb: 3 }}>
                    {selectedScreen.effects.map((effect: any, idx: number) => (
                      <Grid item xs={12} sm={6} key={idx}>
                        <Paper sx={{ p: 2, bgcolor: 'rgba(255, 255, 255, 0.05)', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
                          <Typography variant="subtitle2" sx={{ color: 'white', mb: 1 }}>
                            {effect.name}
                          </Typography>
                          <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
                            {effect.desc}
                          </Typography>
                        </Paper>
                      </Grid>
                    ))}
                  </Grid>
                </>
              )}

              <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
                <Button
                  variant="contained"
                  onClick={() => {
                    handleCloseDialog();
                    navigate(selectedScreen.path);
                  }}
                  sx={{ 
                    bgcolor: selectedScreen.color,
                    '&:hover': { bgcolor: `${selectedScreen.color}dd` }
                  }}
                >
                  Experience Screen
                </Button>
                <Button
                  variant="outlined"
                  onClick={handleCloseDialog}
                  sx={{ 
                    borderColor: selectedScreen.color, 
                    color: selectedScreen.color,
                    '&:hover': { borderColor: selectedScreen.color, bgcolor: `${selectedScreen.color}10` }
                  }}
                >
                  Close
                </Button>
              </Box>
            </Box>
          )}
        </DialogContent>
      </Dialog>

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
          onClick={() => navigate('/showcase')}
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
          View Demo
        </Button>
        <Button
          variant="outlined"
          size="large"
          onClick={() => navigate('/video-intro')}
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
  );
};

export default Overview; 