import React, { useState } from 'react';
import {
  Box,
  Typography,
  TextField,
  Button,
  IconButton,
  Paper,
  Tooltip,
  Popover,
  styled,
  Chip,
  Stack,
} from '@mui/material';
import {
  Mic as MicIcon,
  HelpOutline as HelpIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';

const MainScreen = () => {
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const [inputValue, setInputValue] = useState('');
  const navigate = useNavigate();
  const location = useLocation();
  const { mode } = (location.state as { mode: string } | null) || { mode: 'default' };

  const suggestedPrompts = [
    "A cozy cafe on a rainy afternoon",
    "Gentle forest sounds with a distant waterfall",
    "The calm before a thunderstorm",
    "A quiet library with turning pages",
    "Meditative ocean waves",
    "Lively city street during rush hour",
  ];

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
    navigate('/chat', { state: { initialInput: suggestion, mode: mode } });
  };

  return (
    <Box sx={{ p: 3, maxWidth: 600, mx: 'auto' }}>
      <Box sx={{ textAlign: 'center', mb: 5 }}>
        <Typography variant="h2" sx={{ mb: 1 }}>
          Welcome back, Alex
        </Typography>
        <Typography variant="body1">
          Describe your perfect atmosphere or paste a poem, quote, or movie line to inspire music
        </Typography>
      </Box>

      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1, mb: 1 }}>
          <Tooltip title="Voice input">
            <IconButton>
              <MicIcon />
            </IconButton>
          </Tooltip>
          <IconButton onClick={handleHelpClick}>
            <HelpIcon />
          </IconButton>
        </Box>

        <TextField
          multiline
          fullWidth
          minRows={5}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder={`Try: "A cozy cafe on a rainy afternoon"
Try: "Gentle forest sounds with a distant waterfall"
Try: "The calm before a thunderstorm"
Try: "A quiet library with turning pages"
Try: "To see a world in a grain of sand..."`}
          sx={{ mb: 3 }}
        />

        <Typography variant="subtitle1" sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
          Or try these inspirations:
        </Typography>
        <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap sx={{ mb: 3 }}>
          {suggestedPrompts.map((prompt) => (
            <Chip
              key={prompt}
              label={prompt}
              onClick={() => handleSuggestionClick(prompt)}
              sx={{
                bgcolor: 'rgba(45, 156, 147, 0.1)',
                color: '#2d9c93',
                border: '1px solid rgba(45, 156, 147, 0.2)',
                cursor: 'pointer',
                '&:hover': {
                  bgcolor: 'rgba(45, 156, 147, 0.2)',
                },
              }}
            />
          ))}
        </Stack>

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
          <Box sx={{ p: 2, maxWidth: 260 }}>
            <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
              What can I type?
            </Typography>
            <Box component="ul" sx={{ m: 0, pl: 2 }}>
              <li>Describe your ideal soundscape</li>
              <li>Paste a poem, quote, or movie line</li>
              <li>Try: "A cozy café on a rainy afternoon"</li>
              <li>Try: "Gentle forest sounds with a distant waterfall"</li>
              <li>Try: "The calm before a thunderstorm"</li>
              <li>Try: "A quiet library with turning pages"</li>
              <li>Try: "\"To see a world in a grain of sand...\""</li>
            </Box>
            <Typography variant="body2" sx={{ mt: 1, color: 'primary.light' }}>
              AI will generate a unique soundscape for you!
            </Typography>
          </Box>
        </Popover>
      </Box>

      <Button
        variant="contained"
        fullWidth
        size="large"
        disabled={!inputValue}
        onClick={handleChatWithAI}
        sx={{ opacity: 1 }}
      >
        Chat with Ambiance AI
      </Button>
    </Box>
  );
};

export default MainScreen; 