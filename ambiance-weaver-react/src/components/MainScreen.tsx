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

  
  // 新增状态用于动态inspiration chips
  // inspiration chips 状态，初始为默认prompts
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

  // Story Mode: custom prompt and UI
  const isStoryMode = mode === 'story';

  // 在story模式下重置inspiration chips状态
  useEffect(() => {
    if (isStoryMode) {
      setInspirationChips([]);
      setIsLoadingChips(false);
      fetchedRef.current = false;
    }
  }, [isStoryMode]);

  // 获取随机的inspiration chips，支持是否显示loading
  const fetchInspirationChips = async (showLoading = false) => {
    if (showLoading) setIsLoadingChips(true);
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
        }
      }
    } catch (error) {
      console.error('Failed to fetch inspiration chips:', error);
    } finally {
      if (showLoading) setIsLoadingChips(false);
    }
  };

  // 防止 inspirations 自动刷新两次
  // 用 useRef 保证 fetchInspirationChips 只在首次加载时调用
  const fetchedRef = useRef(false);
  useEffect(() => {
    // 只在非story模式下才获取inspiration chips
    if (fetchedRef.current || isStoryMode) return;
    fetchedRef.current = true;
    fetchInspirationChips(false);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isStoryMode]);

  // 刷新inspiration chips（手动刷新时才显示loading）
  const handleRefreshChips = () => {
    // 只在非story模式下才允许刷新
    if (!isStoryMode) {
      fetchInspirationChips(true);
    }
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

  const modePrompts: Record<string, string> = {
    focus: 'Describe a soundscape that helps you focus.',
    creative: 'Describe a scene or idea to spark your creativity.',
    mindful: 'Describe a calming or peaceful soundscape.',
    sleep: 'Describe a soothing soundscape to help you sleep.',
    story: 'Describe a memory, story, or scene you want to relive.',
    asmr: 'Describe an ASMR sound or trigger (e.g. tapping, brushing, etc.).',
    default: 'Describe your perfect atmosphere or paste a poem, quote, or movie line.'
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
          {isStoryMode ? 'Story Mode' : 'Welcome back, Scarlett'}
        </Typography>
        <Typography 
          variant="body1" 
          sx={{ 
            color: uiSystem.colors.white70,
            ...uiSystem.typography.body1,
          }}
        >
          {modePrompts[mode] || modePrompts.default}
        </Typography>
      </Box>

      {/* Main Content Section */}
      <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        {/* Input Section */}
        <Box sx={{ mb: uiSystem.spacing.large }}>
          {/* Toolbar */}
          <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1, mb: uiSystem.spacing.small }}>
            <IconButton onClick={handleHelpClick} sx={uiSystem.buttons.icon}>
              <HelpIcon />
            </IconButton>
          </Box>
          {/* Text Input */}
          <TextField
            multiline
            fullWidth
            minRows={isStoryMode ? 7 : 5}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={modePrompts[mode] || modePrompts.default}
            InputProps={isStoryMode ? {
              sx: {
                fontSize: 20,
                '&::placeholder': {
                  fontSize: 18,
                  fontStyle: 'italic',
                  color: uiSystem.colors.white70,
                  opacity: 1,
                },
              },
            } : {}}
            sx={{ 
              mb: uiSystem.spacing.large,
              '& .MuiOutlinedInput-root': {
                color: uiSystem.colors.white,
                fieldset: { borderColor: uiSystem.colors.white20 },
                '&:hover fieldset': { borderColor: uiSystem.colors.primary },
                '&.Mui-focused fieldset': { borderColor: uiSystem.colors.primary },
                fontSize: isStoryMode ? 20 : undefined,
              },
              '& .MuiInputBase-input::placeholder': {
                fontSize: isStoryMode ? 18 : undefined,
                fontStyle: isStoryMode ? 'italic' : undefined,
                color: uiSystem.colors.white70,
                opacity: 1,
              },
            }}
          />
          {/* Suggestions Section */}
          {!isStoryMode && (
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
          )}
          {!isStoryMode && (
          <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mb: uiSystem.spacing.large }}>
            {isLoadingChips ? (
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, width: '100%' }}>
                <CircularProgress size={20} color="primary" />
                <Typography variant="body2" sx={{ color: uiSystem.colors.white70 }}>
                  Generating new inspirations...
                </Typography>
              </Box>
            ) : (
              inspirationChips.map((prompt) => {
                // 去掉末尾括号和模式标签
                const cleanPrompt = prompt.replace(/\s*\([^)]*\)\s*$/, '');
                return (
                  <Chip
                    key={prompt}
                    label={cleanPrompt}
                    onClick={() => setInputValue(cleanPrompt)}
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
                );
              })
            )}
          </Stack>
          )}
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
          <Box sx={{ p: uiSystem.spacing.medium, maxWidth: 320, bgcolor: uiSystem.colors.background }}>
            <Typography 
              variant="subtitle1" 
              sx={{ 
                mb: uiSystem.spacing.small, 
                color: uiSystem.colors.white,
                ...uiSystem.typography.h4,
              }}
            >
              {isStoryMode ? 'How to use Story Mode?' : 'What can I type?'}
            </Typography>
            <Box component="ul" sx={{ m: 0, pl: 2, color: uiSystem.colors.white70 }}>
              {isStoryMode ? (
                <>
                  <li>Describe a memory, story, or scene you want to relive.</li>
                  <li>Be as vivid or as simple as you like—details help bring your story to life!</li>
                  <li>Example: "A summer afternoon at grandma’s house, cicadas singing, watermelon in hand."</li>
                  <li>Example: "The first snowfall you remember, quiet streets, warm lights in windows."</li>
                  <li>The AI will narrate your story and create a matching soundscape.</li>
                </>
              ) : (
                <>
              <li>Describe your ideal soundscape</li>
              <li>Paste a poem, quote, or movie line</li>
              <li>Try: "The rain falls like silver threads on cobblestone streets"</li>
              <li>Try: "Grandma's kitchen on Sunday morning, cinnamon in the air"</li>
              <li>Try: "A library where time stands still, dust motes dance in sunbeams"</li>
              <li>Try: "The quiet before dawn, when the world holds its breath"</li>
              <li>Try: "To see a world in a grain of sand..."</li>
                </>
              )}
            </Box>
            <Typography 
              variant="body2" 
              sx={{ 
                mt: uiSystem.spacing.small, 
                color: uiSystem.colors.primary,
                ...uiSystem.typography.body3,
              }}
            >
              {isStoryMode ? 'Let your story come alive with sound.' : 'AI will generate a unique soundscape for you!'}
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