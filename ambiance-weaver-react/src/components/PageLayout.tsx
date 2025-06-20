import React from 'react';
import { Box, Paper } from '@mui/material';
import { styled } from '@mui/material/styles';

interface PageLayoutProps {
  children: React.ReactNode;
  backgroundImageUrl?: string;
  maxWidth?: number | string;
  minHeight?: string;
  showBackground?: boolean;
}

const PageContainer = styled(Box)<{ backgroundImageUrl?: string; showBackground?: boolean }>(({ theme, backgroundImageUrl, showBackground }) => ({
  minHeight: '100vh',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  background: showBackground !== false ? `url(${backgroundImageUrl || `${process.env.PUBLIC_URL}/cover.png`}) no-repeat center center fixed` : 'transparent',
  backgroundSize: 'cover',
  position: 'relative',
  padding: theme.spacing(2),
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: showBackground !== false ? 'linear-gradient(to bottom, rgba(12, 26, 26, 0.8), rgba(12, 26, 26, 0.5), rgba(12, 26, 26, 0.8))' : 'transparent',
    zIndex: 1,
  },
  [theme.breakpoints.down('sm')]: {
    padding: theme.spacing(1),
  },
  [theme.breakpoints.up('lg')]: {
    padding: theme.spacing(3),
  },
}));

const ContentWrapper = styled(Paper)(({ theme }) => ({
  position: 'relative',
  zIndex: 2,
  padding: theme.spacing(4),
  display: 'flex',
  flexDirection: 'column',
  background: 'rgba(255, 255, 255, 0.05)',
  backdropFilter: 'blur(10px)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '16px',
  width: '100%',
  maxWidth: 800,
  minHeight: 600,
  maxHeight: '90vh',
  overflow: 'auto',
  
  [theme.breakpoints.down('sm')]: {
    padding: theme.spacing(3),
    minHeight: 500,
    maxHeight: '95vh',
  },
  [theme.breakpoints.up('md')]: {
    padding: theme.spacing(5),
    minHeight: 650,
  },
  [theme.breakpoints.up('lg')]: {
    padding: theme.spacing(6),
    minHeight: 700,
    maxWidth: 900,
  },
  [theme.breakpoints.up('xl')]: {
    padding: theme.spacing(7),
    minHeight: 750,
    maxWidth: 1000,
  },
}));

const PageLayout: React.FC<PageLayoutProps> = ({
  children,
  backgroundImageUrl,
  maxWidth = 800,
  minHeight = '600px',
  showBackground = true,
}) => {
  return (
    <PageContainer backgroundImageUrl={backgroundImageUrl} showBackground={showBackground}>
      <ContentWrapper
        sx={{
          maxWidth,
          minHeight,
        }}
      >
        {children}
      </ContentWrapper>
    </PageContainer>
  );
};

export default PageLayout; 