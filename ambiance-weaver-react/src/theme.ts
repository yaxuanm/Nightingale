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
      default: '#0c1a1a',
      paper: '#142525',
    },
    text: {
      primary: '#ffffff',
      secondary: '#a0a0a0',
    },
  },
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif',
    h1: {
      fontSize: '2.2rem',
      fontWeight: 700,
      letterSpacing: '-0.02em',
      '@media (min-width:900px)': {
        fontSize: '2.8rem',
      },
      '@media (min-width:1280px)': {
        fontSize: '3.2rem',
      },
      '@media (min-width:1920px)': {
        fontSize: '3.6rem',
      },
    },
    h2: {
      fontSize: '1.5rem',
      fontWeight: 700,
      letterSpacing: '-0.01em',
      '@media (min-width:900px)': {
        fontSize: '2rem',
      },
      '@media (min-width:1280px)': {
        fontSize: '2.4rem',
      },
      '@media (min-width:1920px)': {
        fontSize: '2.8rem',
      },
    },
    body1: {
      fontSize: '1rem',
      color: '#a0a0a0',
      '@media (min-width:900px)': {
        fontSize: '1.2rem',
      },
      '@media (min-width:1280px)': {
        fontSize: '1.3rem',
      },
      '@media (min-width:1920px)': {
        fontSize: '1.5rem',
      },
    },
    body2: {
      fontSize: '1rem',
      color: '#a0a0a0',
      '@media (min-width:900px)': {
        fontSize: '1.12rem',
      },
      '@media (min-width:1280px)': {
        fontSize: '1.18rem',
      },
      '@media (min-width:1920px)': {
        fontSize: '1.22rem',
      },
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: '30px',
          textTransform: 'none',
          fontWeight: 600,
          padding: '12px 24px',
          fontSize: '1.15rem',
          '@media (min-width:900px)': { fontSize: '1.22rem' },
          '@media (min-width:1280px)': { fontSize: '1.28rem' },
          '@media (min-width:1920px)': { fontSize: '1.35rem' },
        },
        contained: {
          background: 'linear-gradient(135deg, #388e3c 0%, #1a5f5a 100%)',
          boxShadow: '0 10px 30px rgba(56, 142, 60, 0.4)',
          '&:hover': {
            background: 'linear-gradient(135deg, #1a5f5a 0%, #388e3c 100%)',
            boxShadow: '0 15px 40px rgba(56, 142, 60, 0.5)',
          },
        },
        outlined: {
          borderRadius: '30px',
          borderColor: 'rgba(56, 142, 60, 0.5)',
          color: '#ffffff',
          '&:hover': {
            borderColor: '#388e3c',
            backgroundColor: 'rgba(56, 142, 60, 0.1)',
          },
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: '30px',
            backgroundColor: 'rgba(255, 255, 255, 0.08)',
            '&:hover fieldset': {
              borderColor: '#388e3c',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#388e3c',
            },
          },
          '& .MuiInputBase-input::placeholder': {
            color: 'rgba(255, 255, 255, 0.6)',
            opacity: 1,
          },
        },
      },
    },
  },
}); 