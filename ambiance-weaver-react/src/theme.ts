import { createTheme } from '@mui/material/styles';

export const theme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#2d9c93',
      light: '#1a5f5a',
      dark: '#1a5f5a',
    },
    background: {
      default: '#0a0a0a',
      paper: '#121212',
    },
    text: {
      primary: '#ffffff',
      secondary: '#a0a0a0',
    },
  },
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif',
    h1: {
      fontSize: '2.8rem',
      fontWeight: 700,
      letterSpacing: '-0.02em',
    },
    h2: {
      fontSize: '24px',
      fontWeight: 700,
      letterSpacing: '-0.01em',
    },
    body1: {
      fontSize: '14px',
      color: '#a0a0a0',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '25px',
          textTransform: 'none',
          fontWeight: 600,
        },
        contained: {
          background: 'linear-gradient(135deg, #2d9c93 0%, #1a5f5a 100%)',
          boxShadow: '0 8px 24px rgba(45, 156, 147, 0.3)',
          '&:hover': {
            background: 'linear-gradient(135deg, #1a5f5a 0%, #2d9c93 100%)',
            boxShadow: '0 12px 32px rgba(45, 156, 147, 0.4)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: '16px',
            backgroundColor: 'rgba(255, 255, 255, 0.05)',
            '&:hover': {
              backgroundColor: 'rgba(255, 255, 255, 0.08)',
            },
          },
        },
      },
    },
  },
}); 