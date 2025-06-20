import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import Onboarding from './Onboarding';
import MainScreen from './MainScreen';
import ChatScreen from './ChatScreen';
import Player from './Player';
import { styled } from '@mui/material/styles';

const SCALE = 0.6;
const DEMO_PAGE_WIDTH = 700; // 调整Demo页面宽度
const DEMO_PAGE_HEIGHT = 750;

// Custom wrapper for demo pages without scrollbars
const DemoPageWrapper = styled(Paper)(({ theme }) => ({
  position: 'relative',
  zIndex: 2,
  display: 'flex',
  flexDirection: 'column',
  background: 'rgba(255, 255, 255, 0.05)',
  backdropFilter: 'blur(10px)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '16px',
  width: '100%',
  maxWidth: 900,
  minWidth: 320,
  boxSizing: 'border-box',
  overflow: 'hidden',
  margin: theme.spacing(2),
  alignItems: 'center',
  justifyContent: 'flex-start',
  padding: theme.spacing(3),
}));

const ScaledContent = ({ children }: { children: React.ReactNode }) => (
  <div
    style={{
      transform: `scale(${SCALE})`,
      transformOrigin: 'top left',
      width: `${DEMO_PAGE_WIDTH}px`,
      height: `${DEMO_PAGE_HEIGHT}px`,
      pointerEvents: 'auto',
      display: 'inline-block',
    }}
  >
    {children}
  </div>
);

// Custom components for demo that bypass PageLayout
const DemoOnboarding = () => (
  <DemoPageWrapper>
    <Onboarding usePageLayout={false} />
  </DemoPageWrapper>
);

const DemoMainScreen = () => (
  <DemoPageWrapper>
    <MainScreen usePageLayout={false} />
  </DemoPageWrapper>
);

const DemoChatScreen = () => (
  <DemoPageWrapper>
    <ChatScreen usePageLayout={false} />
  </DemoPageWrapper>
);

const DemoPlayer = () => (
  <DemoPageWrapper>
    <Player audioUrl="" description="" usePageLayout={false} />
  </DemoPageWrapper>
);

export default function AllScreensShowcase() {
  return (
    <Box
      sx={{
        minHeight: '100vh',
        width: '100vw',
        background: `url(${process.env.PUBLIC_URL}/cover.png) no-repeat center center fixed`,
        backgroundSize: 'cover',
        position: 'relative',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '20px',
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
      {/* Title */}
      <Typography
        variant="h1"
        sx={{
          color: '#ffffff',
          textAlign: 'center',
          mb: 4,
          position: 'relative',
          zIndex: 2,
          fontSize: '3rem',
          fontWeight: 700,
        }}
      >
        Nightingale Demo
      </Typography>

      {/* Screens Grid */}
      <Box
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: '1fr 1fr' },
          gridTemplateRows: { xs: 'auto', sm: 'auto auto' },
          gap: 4,
          justifyContent: 'center',
          alignItems: 'start',
          width: 'fit-content',
          margin: '0 auto',
          position: 'relative',
          zIndex: 2,
        }}
      >
        {[
          {
            title: 'Onboarding',
            component: <DemoOnboarding />
          },
          {
            title: 'Main Screen',
            component: <DemoMainScreen />
          },
          {
            title: 'AI Chat',
            component: <DemoChatScreen />
          },
          {
            title: 'Player',
            component: <DemoPlayer />
          }
        ].map(({ title, component }, idx) => (
          <Box
            key={title}
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              mb: 2,
            }}
          >
            <Typography
              variant="h3"
              sx={{
                color: '#ffffff',
                textAlign: 'center',
                mb: 2,
                fontSize: '1.5rem',
                fontWeight: 600,
              }}
            >
              {title}
            </Typography>
            {component}
          </Box>
        ))}
      </Box>
    </Box>
  );
} 