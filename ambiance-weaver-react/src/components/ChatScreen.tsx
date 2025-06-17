import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  IconButton,
  TextField,
  styled,
  CircularProgress,
  Stack,
  Chip,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Send as SendIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAiName } from '../utils/AiNameContext';
import Player from './Player';

interface Message {
  sender: 'user' | 'ai';
  text: string;
  isUser: boolean;
  audioUrl?: string;
  backgroundImageUrl?: string;
  musicUrl?: string;
}

type ChatStage = 'intro' | 'atmosphere' | 'mood' | 'elements' | 'confirm' | 'free_chat' | 'complete';

const ChatContainer = styled(Box)(({ theme }) => ({
  width: '100%',
  maxWidth: 800,
  height: 'auto',
  maxHeight: 'calc(100vh - 250px - 100px)', // Adjusted maxHeight to account for header and input
  overflowY: 'auto',
  padding: theme.spacing(2),
  margin: '0 auto',
}));

const AiAvatar = styled(Box)(({ theme }) => ({
  width: 40, // Increased size
  height: 40,
  borderRadius: '50%',
  overflow: 'hidden',
  flexShrink: 0, // Prevent shrinking
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  marginRight: theme.spacing(1.5), // Space between avatar and bubble
  backgroundColor: 'rgba(45, 156, 147, 0.2)', // Background for the avatar if needed
}));

const MessageBubbleContent = styled(Box)(({ theme, sender }: { theme?: any, sender: 'user' | 'ai' }) => ({
  background: sender === 'ai' ? 'rgba(45, 156, 147, 0.1)' : 'rgba(255, 255, 255, 0.1)',
  padding: theme.spacing(2),
  borderRadius: sender === 'ai' ? '0 12px 12px 12px' : '12px 0 12px 12px', // Bubble shape with tail
  maxWidth: '90%',
  // alignSelf: sender === 'user' ? 'flex-end' : 'flex-start', // Managed by parent Box now
  display: 'inline-flex', // Use inline-flex for content inside bubble
  alignItems: 'center',
  position: 'relative', // For tail positioning
  // No direct gap here, as avatar is outside
}));

const OptionMessageBubbleContent = styled(Box)(({ theme }) => ({
  background: 'rgba(45, 156, 147, 0.1)', // AI bubble background
  padding: theme.spacing(2),
  borderRadius: '12px', // Standard square corners for options
  maxWidth: '100%', // Ensure it takes full width for options
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'flex-start',
}));

const OptionChip = styled(Chip)(({ theme }) => ({
  background: 'rgba(255, 255, 255, 0.1)',
  color: '#ffffff',
  border: '1px solid rgba(45, 156, 147, 0.2)',
  cursor: 'pointer',
  '&:hover': {
    background: 'rgba(45, 156, 147, 0.2)',
  },
}));

const ChatScreen = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { mode, initialInput } = (location.state as { mode: string; initialInput: string } | null) || { mode: 'default', initialInput: '' };
  const { aiName } = useAiName();

  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentStage, setCurrentStage] = useState<ChatStage>('intro');
  const [selectedChoices, setSelectedChoices] = useState<{
    atmosphere?: string;
    mood?: string;
    elements: string[];
  }>({ elements: [] });
  const [currentAudioUrl, setCurrentAudioUrl] = useState<string | null>(null);
  const [currentBackgroundImageUrl, setCurrentBackgroundImageUrl] = useState<string | null>(null);
  const [currentMusicUrl, setCurrentMusicUrl] = useState<string | null>(null);

  // NEW STATE for controlling visibility of elements selection and button
  const [showElementSelectionAndButton, setShowElementSelectionAndButton] = useState(false);

  // Add state for showing playback buttons
  const [showPlaybackButtons, setShowPlaybackButtons] = useState(false);

  const chatContainerRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const loadingMessages = [
    "Composing unique sound elements...",
    "Enhancing your soundscape with AI...",
    "Fine-tuning audio effects...",
    "Almost ready to play!",
    "Did you know ambient sounds can improve focus?",
    "Preparing your personalized soundscape...",
    "Did you know certain frequencies can calm your mind?",
    "Our AI learns and adapts to your unique preferences.",
    "Exploring a world of sound just for you...",
    "Relax, your personalized soundscape is nearly complete.",
    "Discovering the perfect blend of elements.",
  ];

  const [currentLoadingMessageIndex, setCurrentLoadingMessageIndex] = useState(0);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (isLoading) {
      interval = setInterval(() => {
        setCurrentLoadingMessageIndex((prevIndex) =>
          (prevIndex + 1) % loadingMessages.length
        );
      }, 3000); // Change message every 3 seconds
    }
    return () => {
      clearInterval(interval);
    };
  }, [isLoading, loadingMessages.length]);

  // NEW useEffect to manage showElementSelectionAndButton based on currentStage
  useEffect(() => {
    if (currentStage === 'elements') {
      setShowElementSelectionAndButton(true);
    } else {
      setShowElementSelectionAndButton(false);
    }
  }, [currentStage]);

  const atmosphereOptions = [
    "Cozy and intimate",
    "Spacious and airy",
    "Lively and energetic",
    "Calm and serene",
    "Mysterious and intriguing",
  ];

  const moodOptions = [
    "Relaxed",
    "Focused",
    "Inspired",
    "Dreamy",
    "Uplifting",
    "Melancholic",
  ];

  const elementOptions = [
    "Rain", "Wind", "Birds chirping", "Ocean waves", "Fire crackling",
    "Coffee machine sounds", "Distant chatter", "Footsteps", "Gentle music",
    "Thunderstorm", "Night crickets", "City hum", "Train passing",
  ];

  useEffect(() => {
    let introMessage = `Welcome to ${aiName || 'Ambiance AI'}! You've chosen the ${mode} mode.`;
    if (initialInput) {
      introMessage += ` And you've started with the idea: "${initialInput}".`;
    }
    introMessage += ` Let's build your perfect soundscape step by step. First, what kind of atmosphere are you looking for? You can also type your thoughts below.`;

    setMessages([
      ...(initialInput ? [{ sender: 'user' as Message['sender'], text: initialInput, isUser: true }] : []),
      { sender: 'ai' as Message['sender'], text: introMessage, isUser: false },
    ]);
    setCurrentStage('atmosphere');
    setInputText(''); // Clear input text on initial load of ChatScreen
  }, [initialInput, mode, aiName]);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleOptionSelect = (option: string, type: 'atmosphere' | 'mood' | 'elements') => {
    setMessages((prevMessages) => [...prevMessages, { sender: 'user' as Message['sender'], text: option, isUser: true }]);

    let nextStageMessage = '';
    let nextStage: ChatStage = currentStage;

    setSelectedChoices((prev) => {
      const newChoices = { ...prev };
      if (type === 'elements') {
        if (newChoices.elements.includes(option)) {
          newChoices.elements = newChoices.elements.filter(item => item !== option);
        } else {
          // Only allow adding if less than 3 elements are already selected
          if (newChoices.elements.length < 3) {
            newChoices.elements = [...newChoices.elements, option];
          }
        }
      } else {
        (newChoices as any)[type] = option; // Update atmosphere or mood
      }
      return newChoices;
    });

    // Logic to move to the next stage or confirm
    if (currentStage === 'atmosphere') {
      nextStage = 'mood';
      nextStageMessage = `Great! You chose: ${option}. Now, what kind of mood or feeling do you want to evoke?`;
    } else if (currentStage === 'mood') {
      nextStage = 'elements';
      nextStageMessage = `Perfect! You chose: ${option}. Finally, let's add some specific sound elements. You can select multiple, or type any others you have in mind.`;
    } else if (currentStage === 'elements') {
      // Stay in elements stage, but prompt for more or confirm
      nextStage = 'elements'; // Stay in elements stage for multiple selections
      // No new AI message here, as user is selecting multiple elements.
    }

    // Only add AI message if it's a stage transition or new prompt within a stage
    if (nextStageMessage) {
      setMessages((prevMessages) => [...prevMessages, { sender: 'ai' as Message['sender'], text: nextStageMessage, isUser: false }]);
    }
    setCurrentStage(nextStage);
  };

  const handleGenerateContent = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Generate both audio and background image
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'ai' as Message['sender'], text: 'Generating your personalized soundscape and background...', isUser: false },
      ]);

      // Generate background image
      const backgroundResponse = await fetch('http://localhost:8000/api/generate-background', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description: "a serene forest scene" }), // This can be dynamic based on user's choices
      });

      if (!backgroundResponse.ok) {
        throw new Error('Failed to generate background image');
      }

      const backgroundData = await backgroundResponse.json();
      setCurrentBackgroundImageUrl(backgroundData.image_url);

      // Generate audio
      const audioResponse = await fetch('http://localhost:8000/api/generate-audio', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          description: "ambient sounds", // This can be dynamic based on user's choices
          elements: selectedChoices.elements 
        }),
      });

      if (!audioResponse.ok) {
        throw new Error('Failed to generate audio');
      }

      const audioData = await audioResponse.json();
      setCurrentAudioUrl(audioData.audio_url);

      // Show completion message with buttons
      setMessages((prevMessages) => [
        ...prevMessages,
        { 
          sender: 'ai' as Message['sender'], 
          text: 'Your personalized soundscape is ready! What would you like to do?', 
          isUser: false 
        },
      ]);

      // Add buttons for playback and regeneration
      setShowPlaybackButtons(true);
      setCurrentStage('complete');

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      setMessages((prevMessages) => [
        ...prevMessages,
        { 
          sender: 'ai' as Message['sender'], 
          text: `Error generating content: ${err instanceof Error ? err.message : 'An unknown error occurred'}.`, 
          isUser: false 
        },
      ]);
      console.error("Error generating content:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePlayback = () => {
    navigate('/player', { 
      state: { 
        audioUrl: currentAudioUrl,
        backgroundImageUrl: currentBackgroundImageUrl,
        selectedChoices
      }
    });
  };

  const handleRegenerate = () => {
    setShowPlaybackButtons(false);
    setCurrentStage('intro');
    setMessages([]);
    setSelectedChoices({ elements: [] });
    setCurrentAudioUrl(null);
    setCurrentBackgroundImageUrl(null);
    setCurrentMusicUrl(null);
    setError(null);
  };

  const handleSendMessage = async () => {
    if (inputText.trim() === '' && !selectedChoices.elements.length) return; // Only send if there's text or selected elements

    const userMessage: Message = { sender: 'user', text: inputText, isUser: true };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInputText('');
    setError(null); // Clear any previous error on new message

    // If in elements stage and user types, assume they are adding custom elements or confirming
    if (currentStage === 'elements') {
      if (inputText.trim() !== '') {
        setSelectedChoices((prev) => ({
          ...prev,
          elements: [...prev.elements, inputText.trim()],
        }));
        setMessages((prevMessages) => [...prevMessages, { sender: 'ai', text: `Added "${inputText.trim()}" to your elements. Click Generate Soundscape when ready!`, isUser: false }]);
      }
      // Do not transition stage automatically here, wait for generate button click
      return;
    }

    if (currentStage === 'intro') {
      // Should not happen as stage is set to atmosphere in useEffect
      return;
    }

    // For other stages (atmosphere, mood, confirm) treat as direct answer
    // For free_chat, send to AI service
    if (currentStage === 'free_chat') {
      try {
        setIsLoading(true);
        const aiResponse = await fetch('http://localhost:8000/api/chat', { // Replace with your actual chat API endpoint
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message: inputText }),
        });
        if (!aiResponse.ok) {
          throw new Error('Failed to get AI response');
        }
        const data = await aiResponse.json();
        setMessages((prevMessages) => [...prevMessages, { sender: 'ai', text: data.response, isUser: false }]);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
        setMessages((prevMessages) => [
          ...prevMessages,
          { sender: 'ai' as Message['sender'], text: `Error: ${err instanceof Error ? err.message : 'An unknown error occurred'}. Please try again.`, isUser: false },
        ]);
        console.error("Error sending message:", err);
      } finally {
        setIsLoading(false);
      }
    } else {
      // This is for atmosphere, mood stages if user types instead of selecting chip
      handleOptionSelect(inputText, currentStage as 'atmosphere' | 'mood');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleReturnToGuidedMode = () => {
    setCurrentStage('atmosphere');
    setMessages((prevMessages) => [
      ...prevMessages,
      { sender: 'user' as Message['sender'], text: 'Return to guided mode', isUser: true },
      { sender: 'ai' as Message['sender'], text: "Okay, let's start over. What kind of atmosphere are you looking for?", isUser: false }
    ]);
    // Reset choices and URLs if returning to beginning of guided mode
    setSelectedChoices({ elements: [] });
    setCurrentAudioUrl(null);
    setCurrentBackgroundImageUrl(null);
    setCurrentMusicUrl(null);
    setError(null);
    // showElementSelectionAndButton will be handled by useEffect based on currentStage
  };

  const handleGenerateMusic = async () => {
    try {
      setIsLoading(true);
      setError(null);
      // For music generation, we might use a predefined prompt or based on some context
      const musicDescription = "gentle, relaxing music"; // This can be dynamic
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'ai' as Message['sender'], text: 'Generating gentle music...', isUser: false },
      ]);

      const response = await fetch('http://localhost:8000/api/generate-music', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description: musicDescription }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate music');
      }

      const data = await response.json();
      console.log("Music generated:", data);
      setCurrentMusicUrl(data.music_url); // Assuming the response has music_url

      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'ai' as Message['sender'], text: 'Gentle music ready!', isUser: false },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'ai' as Message['sender'], text: `Error generating music: ${err instanceof Error ? err.message : 'An unknown error occurred'}.`, isUser: false },
      ]);
      console.error("Error generating music:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateBackground = async () => {
    try {
      setIsLoading(true);
      setError(null);
      // For background generation, we might use a predefined prompt or based on some context
      const backgroundDescription = "a serene forest scene"; // This can be dynamic
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'ai' as Message['sender'], text: 'Generating background image...', isUser: false },
      ]);

      const response = await fetch('http://localhost:8000/api/generate-background', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description: backgroundDescription }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to generate background image');
      }

      const data = await response.json();
      console.log("Background image generated:", data);
      setCurrentBackgroundImageUrl(data.image_url); // Assuming the response has image_url

      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'ai' as Message['sender'], text: 'Background image ready!', isUser: false },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred');
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'ai' as Message['sender'], text: `Error generating background: ${err instanceof Error ? err.message : 'An unknown error occurred'}.`, isUser: false },
      ]);
      console.error("Error generating background:", err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        background: `url(${process.env.PUBLIC_URL}/cover.png) no-repeat center center fixed`,
        backgroundSize: 'cover',
        position: 'relative',
        p: 3,
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
      <Paper
        elevation={3}
        sx={{
          p: 0, // Remove padding from Paper, its children will handle padding
          display: 'flex',
          flexDirection: 'column',
          maxWidth: 800,
          width: '100%',
          background: 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(45, 156, 147, 0.2)',
          borderRadius: '16px',
          position: 'relative',
          zIndex: 2,
          overflow: 'hidden', // Ensure internal elements don't break rounded corners
        }}
      >
        {/* Header */}
        <Box
          sx={{
            p: 2,
            display: 'flex',
            alignItems: 'center',
            borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          }}
        >
          <IconButton onClick={() => navigate(-1)} sx={{ color: 'white' }}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h6" sx={{ ml: 2, color: 'white' }}>
            Chat with {aiName || 'Ambiance AI'}
          </Typography>
        </Box>

        {/* Chat Content */}
        <ChatContainer ref={chatContainerRef} sx={{ position: 'relative', zIndex: 2, flexGrow: 1, maxHeight: 'calc(100vh - 250px - 100px)' }}>
          <Stack spacing={2}>
            {messages.map((msg, index) => (
              <Box
                key={index}
                sx={{
                  alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                  display: 'flex',
                  alignItems: 'flex-start', // Align avatar and bubble at the top
                  gap: 1.5, // Space between avatar and bubble
                  flexDirection: msg.sender === 'user' ? 'row-reverse' : 'row', // Reverse order for user messages
                }}
              >
                {msg.sender === 'ai' && (
                  <AiAvatar>
                    <img src={`${process.env.PUBLIC_URL}/ai_logo.png`} alt="AI Logo" style={{ width: 40, height: 40, objectFit: 'contain' }} />
                  </AiAvatar>
                )}
                <MessageBubbleContent sender={msg.sender}>
                  <Typography sx={{ color: 'white' }}>{msg.text}</Typography>
                </MessageBubbleContent>
              </Box>
            ))}
            {isLoading && (
              <Box
                sx={{
                  alignSelf: 'flex-start',
                  display: 'flex',
                  alignItems: 'flex-start',
                  gap: 1.5,
                }}
              >
                <AiAvatar>
                  <img src={`${process.env.PUBLIC_URL}/ai_logo.png`} alt="AI Logo" style={{ width: 40, height: 40, objectFit: 'contain' }} />
                </AiAvatar>
                <MessageBubbleContent sender="ai">
                  <motion.div
                    initial={{ scale: 0.8, opacity: 0.5 }}
                    animate={{ scale: [0.8, 1.2, 0.8], opacity: [0.5, 1, 0.5] }}
                    transition={{
                      duration: 1.5,
                      repeat: Infinity,
                      ease: "easeInOut",
                    }}
                    style={{
                      width: 20,
                      height: 20,
                      borderRadius: '50%',
                      backgroundColor: '#2d9c93',
                      marginRight: '8px', // Adjust spacing
                    }}
                  />
                  <Typography sx={{ color: 'white', ml: 1 }}>{loadingMessages[currentLoadingMessageIndex]}</Typography>
                </MessageBubbleContent>
              </Box>
            )}

            {/* Atmosphere selection chips */}
            {currentStage === 'atmosphere' && !isLoading && !showPlaybackButtons && (
              <OptionMessageBubbleContent sx={{ mt: 2 }}>
                <Typography variant="body1" sx={{ mb: 1 }}>What kind of atmosphere are you looking for?</Typography>
                <Stack direction="row" flexWrap="wrap" spacing={1}>
                  {atmosphereOptions.map((option) => (
                    <OptionChip
                      key={option}
                      label={option}
                      onClick={() => handleOptionSelect(option, 'atmosphere')}
                      variant={selectedChoices.atmosphere === option ? 'filled' : 'outlined'}
                      color={selectedChoices.atmosphere === option ? 'primary' : 'default'}
                    />
                  ))}
                </Stack>
              </OptionMessageBubbleContent>
            )}

            {/* Mood selection chips */}
            {currentStage === 'mood' && !isLoading && !showPlaybackButtons && (
              <OptionMessageBubbleContent sx={{ mt: 2 }}>
                <Typography variant="body1" sx={{ mb: 1 }}>What kind of mood or feeling do you want to evoke?</Typography>
                <Stack direction="row" flexWrap="wrap" spacing={1}>
                  {moodOptions.map((option) => (
                    <OptionChip
                      key={option}
                      label={option}
                      onClick={() => handleOptionSelect(option, 'mood')}
                      variant={selectedChoices.mood === option ? 'filled' : 'outlined'}
                      color={selectedChoices.mood === option ? 'primary' : 'default'}
                    />
                  ))}
                </Stack>
              </OptionMessageBubbleContent>
            )}

            {/* Sound element selection chips */}
            {currentStage === 'elements' && !isLoading && !showPlaybackButtons && (
              <OptionMessageBubbleContent sx={{ mt: 2 }}>
                <Typography variant="body1" sx={{ mb: 1 }}>Select sound elements (max 3):</Typography>
                <Stack direction="row" flexWrap="wrap" spacing={1}>
                  {elementOptions.map((option) => (
                    <OptionChip
                      key={option}
                      label={option}
                      onClick={() => handleOptionSelect(option, 'elements')}
                      variant={selectedChoices.elements.includes(option) ? 'filled' : 'outlined'}
                      color={selectedChoices.elements.includes(option) ? 'primary' : 'default'}
                      disabled={selectedChoices.elements.length >= 3 && !selectedChoices.elements.includes(option)}
                    />
                  ))}
                </Stack>
              </OptionMessageBubbleContent>
            )}

            {/* Generate Soundscape button */}
            {currentStage === 'elements' && !isLoading && !showPlaybackButtons && (
              <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center' }}>
                <Button
                  variant="contained"
                  sx={{
                    bgcolor: '#2D9C93',
                    '&:hover': {
                      bgcolor: '#258079',
                    },
                    padding: '12px 24px',
                    fontSize: '1rem',
                    borderRadius: '12px',
                  }}
                  onClick={handleGenerateContent}
                  disabled={isLoading || selectedChoices.elements.length === 0}
                >
                  {isLoading ? loadingMessages[currentLoadingMessageIndex] : 'Generate Soundscape'}
                </Button>
              </Box>
            )}
          </Stack>
        </ChatContainer>

        {/* Add playback buttons when content is generated - Moved inside Paper */}
        {showPlaybackButtons && (
          <Box sx={{ display: 'flex', gap: 2, mt: 2, justifyContent: 'center' }}>
            <Button
              variant="contained"
              onClick={handlePlayback}
              sx={{
                backgroundColor: 'rgba(45, 156, 147, 0.8)',
                '&:hover': {
                  backgroundColor: 'rgba(45, 156, 147, 1)',
                },
              }}
            >
              Enter Player
            </Button>
            <Button
              variant="outlined"
              onClick={handleRegenerate}
              sx={{
                borderColor: 'rgba(45, 156, 147, 0.8)',
                color: 'white',
                '&:hover': {
                  borderColor: 'rgba(45, 156, 147, 1)',
                  backgroundColor: 'rgba(45, 156, 147, 0.1)',
                },
              }}
            >
              Regenerate
            </Button>
          </Box>
        )}

        {/* Input and Generate Button */}
        <Box
          sx={{
            p: 2,
            borderTop: '1px solid rgba(255, 255, 255, 0.1)', // Only top border to separate from chat content
            position: 'relative', // Keep zIndex for content within Paper
            zIndex: 2, // Keep zIndex for content within Paper
          }}
        >
          <Box sx={{ display: 'flex', gap: 1 }}>
            {currentStage === 'free_chat' && (
              <Button
                variant="outlined"
                fullWidth
                onClick={handleReturnToGuidedMode}
                sx={{
                  color: 'white',
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                  height: 50,
                  '&:hover': {
                    borderColor: '#2d9c93',
                  },
                }}
              >
                Return to Guided Mode
              </Button>
            )}
            <TextField
              fullWidth
              variant="outlined"
              placeholder="Type your message..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              sx={{
                '& .MuiOutlinedInput-root': {
                },
                '& .MuiInputBase-input::placeholder': {
                  color: 'rgba(255, 255, 255, 0.7)',
                  opacity: 1,
                },
              }}
              disabled={isLoading || showPlaybackButtons || currentStage === 'complete'}
              autoComplete="off"
            />
            <IconButton
              sx={{
                bgcolor: '#2d9c93',
                color: 'white',
                '&:hover': {
                  bgcolor: '#1a5f5a',
                },
                width: 50,
                height: 50,
              }}
              onClick={handleSendMessage}
              disabled={isLoading || inputText.trim() === '' || showPlaybackButtons || currentStage === 'complete'}
            >
              {isLoading ? <CircularProgress size={24} color="inherit" /> : <SendIcon />}
            </IconButton>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default ChatScreen; 