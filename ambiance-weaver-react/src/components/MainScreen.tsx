import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  IconButton,
  Tooltip,
  Popover,
  Chip,
  Stack,
  Paper,
  CircularProgress,
} from '@mui/material';
import {
  Mic as MicIcon,
  ArrowBack as ArrowBackIcon,
  HelpOutline as HelpIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import PageLayout from './PageLayout';
import { uiSystem } from '../theme/uiSystem';

interface MainScreenProps {
  usePageLayout?: boolean;
}

const MainScreen: React.FC<MainScreenProps> = ({ usePageLayout = true }) => {
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const [inputValue, setInputValue] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const { mode } = (location.state as { mode: string } | null) || { mode: 'default' };
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef<any>(null);
  
  // 新增状态用于动态inspiration chips
  const [inspirationChips, setInspirationChips] = useState<string[]>([]);
  const [isLoadingChips, setIsLoadingChips] = useState(false);

  // 默认的fallback选项
  const defaultSuggestedPrompts = [
    "The rain falls like silver threads on cobblestone streets",
    "Grandma's kitchen on Sunday morning, cinnamon in the air",
    "A library where time stands still, dust motes dance in sunbeams",
    "The quiet before dawn, when the world holds its breath",
    "A steampunk workshop where brass gears whisper secrets",
    "Fresh snow crunching underfoot, breath visible in cold air",
  ];

  // 获取随机的inspiration chips
  const fetchInspirationChips = async () => {
    setIsLoadingChips(true);
    try {
      const response = await fetch('http://localhost:8000/api/generate-inspiration-chips', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          mode: mode,
          user_input: inputValue,
        }),
      });
      
      if (response.ok) {
        const data = await response.json();
        if (data.chips && Array.isArray(data.chips)) {
          setInspirationChips(data.chips);
        } else {
          setInspirationChips(defaultSuggestedPrompts);
        }
      } else {
        setInspirationChips(defaultSuggestedPrompts);
      }
    } catch (error) {
      console.error('Failed to fetch inspiration chips:', error);
      setInspirationChips(defaultSuggestedPrompts);
    } finally {
      setIsLoadingChips(false);
    }
  };

  // 组件加载时获取inspiration chips
  useEffect(() => {
    fetchInspirationChips();
  }, []);

  // 刷新inspiration chips
  const handleRefreshChips = () => {
    fetchInspirationChips();
  };

  const handleHelpClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleHelpClose = () => {
    setAnchorEl(null);
  };

  const open = Boolean(anchorEl);

  const handleChatWithAI = () => {
    navigate('/chat', { state: { initialInput: inputValue, mode: mode } });
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputValue(suggestion);
  };

  const handleVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
      return;
    }
    if (!recognitionRef.current) {
      const SpeechRecognition = (window as any).webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US'; // English recognition
      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setInputValue((prev) => prev ? prev + ' ' + transcript : transcript);
      };
      recognitionRef.current.onend = () => setIsListening(false);
      recognitionRef.current.onerror = () => setIsListening(false);
    }
    if (!isListening) {
      recognitionRef.current.start();
      setIsListening(true);
    } else {
      recognitionRef.current.stop();
      setIsListening(false);
    }
  };

  const content = (
    <>
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          borderBottom: `1px solid ${uiSystem.colors.white20}`,
          px: 0,
          mx: 0,
          py: 1.5,
          minHeight: 56,
          background: 'transparent',
          width: '100%',
        }}
      >
        <IconButton onClick={() => navigate(-1)} sx={{ color: uiSystem.colors.white, p: 0, mr: 2 }}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h6" sx={{ color: uiSystem.colors.white, ...uiSystem.typography.h3 }}>
          Main Screen
        </Typography>
      </Box>
      {/* Header Section */}
      <Box sx={{ textAlign: 'center', mb: uiSystem.spacing.section, p: uiSystem.spacing.large }}>
        <Typography 
          variant="h2" 
          sx={{ 
            mb: uiSystem.spacing.medium, 
            color: uiSystem.colors.white,
            ...uiSystem.typography.h2,
          }}
        >
          Welcome back, Scarlett
        </Typography>
        <Typography 
          variant="body1" 
          sx={{ 
            color: uiSystem.colors.white70,
            ...uiSystem.typography.body1,
          }}
        >
          Describe your perfect atmosphere or paste a poem, quote, or movie line to inspire music
        </Typography>
      </Box>

      {/* Main Content Section */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        {/* Input Section */}
        <Box sx={{ mb: uiSystem.spacing.large }}>
          {/* Toolbar */}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1, mb: uiSystem.spacing.small }}>
            <Tooltip title="Voice input">
              <IconButton sx={uiSystem.buttons.icon} onClick={handleVoiceInput} color={isListening ? "primary" : "default"}>
                <MicIcon />
              </IconButton>
            </Tooltip>
            <IconButton onClick={handleHelpClick} sx={uiSystem.buttons.icon}>
              <HelpIcon />
            </IconButton>
          </Box>
          {/* Text Input */}
          <TextField
            multiline
            fullWidth
            minRows={5}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={`Try: "The rain falls like silver threads on cobblestone streets"\nTry: "Grandma's kitchen on Sunday morning, cinnamon in the air"\nTry: "A library where time stands still, dust motes dance in sunbeams"\nTry: "The quiet before dawn, when the world holds its breath"\nTry: "To see a world in a grain of sand..."`}
            sx={{ 
              mb: uiSystem.spacing.large,
              '& .MuiOutlinedInput-root': {
                color: uiSystem.colors.white,
                fieldset: { borderColor: uiSystem.colors.white20 },
                '&:hover fieldset': { borderColor: uiSystem.colors.primary },
                '&.Mui-focused fieldset': { borderColor: uiSystem.colors.primary },
              },
              '& .MuiInputBase-input::placeholder': {
                color: uiSystem.colors.white70,
                opacity: 1,
              },
            }}
          />
          {/* Suggestions Section */}
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: uiSystem.spacing.small }}>
            <Typography
              variant="subtitle1" 
              sx={{ 
                color: uiSystem.colors.white70,
                ...uiSystem.typography.body2,
              }}
            >
              Or try these inspirations:
            </Typography>
            <Tooltip title="Refresh inspiration chips">
              <IconButton 
                onClick={handleRefreshChips} 
                sx={uiSystem.buttons.icon} 
                disabled={isLoadingChips}
                size="small"
              >
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Box>
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mb: uiSystem.spacing.large }}>
            {isLoadingChips ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                <CircularProgress size={20} color="primary" />
                <Typography variant="body2" sx={{ color: uiSystem.colors.white70 }}>
                  Generating new inspirations...
                </Typography>
              </Box>
            ) : (
              inspirationChips.map((prompt) => (
                <Chip
                  key={prompt}
                  label={prompt}
                  onClick={() => setInputValue(prompt)}
                  sx={{
                    bgcolor: uiSystem.colors.white05,
                    color: uiSystem.colors.primary,
                    border: `1px solid ${uiSystem.colors.white20}`,
                    cursor: 'pointer',
                    fontSize: uiSystem.typography.label.fontSize,
                    fontWeight: uiSystem.typography.label.fontWeight,
                    '&:hover': {
                      bgcolor: uiSystem.colors.white10,
                      borderColor: uiSystem.colors.primary,
                    },
                  }}
                />
              ))
            )}
          </Stack>
        </Box>
        {/* Help Popover */}
        <Popover
          open={open}
          anchorEl={anchorEl}
          onClose={handleHelpClose}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
        >
          <Box sx={{ p: uiSystem.spacing.medium, maxWidth: 260, bgcolor: uiSystem.colors.background }}>
            <Typography 
              variant="subtitle1" 
              sx={{ 
                mb: uiSystem.spacing.small, 
                color: uiSystem.colors.white,
                ...uiSystem.typography.h4,
              }}
            >
              What can I type?
            </Typography>
            <Box component="ul" sx={{ m: 0, pl: 2, color: uiSystem.colors.white70 }}>
              <li>Describe your ideal soundscape</li>
              <li>Paste a poem, quote, or movie line</li>
              <li>Try: "The rain falls like silver threads on cobblestone streets"</li>
              <li>Try: "Grandma's kitchen on Sunday morning, cinnamon in the air"</li>
              <li>Try: "A library where time stands still, dust motes dance in sunbeams"</li>
              <li>Try: "The quiet before dawn, when the world holds its breath"</li>
              <li>Try: "To see a world in a grain of sand..."</li>
            </Box>
            <Typography 
              variant="body2" 
              sx={{ 
                mt: uiSystem.spacing.small, 
                color: uiSystem.colors.primary,
                ...uiSystem.typography.body3,
              }}
            >
              AI will generate a unique soundscape for you!
            </Typography>
          </Box>
        </Popover>
      </Box>
      {/* Action Button */}
      <Box sx={{ width: '100%', mt: 2 }}>
        <Button
          variant="contained"
          fullWidth
          size="large"
          disabled={!inputValue}
          onClick={handleChatWithAI}
          sx={uiSystem.buttons.primary}
        >
          Start with {mode.charAt(0).toUpperCase() + mode.slice(1)}
        </Button>
      </Box>
    </>
  );

  if (usePageLayout) {
    return <PageLayout>{content}</PageLayout>;
  }
  return content;
};

export default MainScreen; 