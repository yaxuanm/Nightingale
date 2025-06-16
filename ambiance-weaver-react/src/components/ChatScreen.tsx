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
  SmartToy as AIIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { useNavigate, useLocation } from 'react-router-dom';

interface Message {
  sender: 'user' | 'ai';
  text: string;
}

type ChatStage = 'intro' | 'atmosphere' | 'mood' | 'elements' | 'confirm' | 'free_chat';

const ChatContainer = styled(Box)(({ theme }) => ({
  width: '100%',
  maxWidth: '90%',
  height: 'auto',
  maxHeight: 'calc(100vh - 250px)',
  overflowY: 'auto',
  padding: theme.spacing(2),
  background: 'rgba(255, 255, 255, 0.05)',
  backdropFilter: 'blur(10px)',
  borderRadius: '16px',
  border: '1px solid rgba(45, 156, 147, 0.2)',
  marginBottom: theme.spacing(2),
  margin: '0 auto',
}));

const MessageBubbleContent = styled(Box)(({ theme, sender }: { theme?: any, sender: 'user' | 'ai' }) => ({
  background: sender === 'ai' ? 'rgba(45, 156, 147, 0.1)' : 'rgba(255, 255, 255, 0.1)',
  padding: theme.spacing(2),
  borderRadius: '12px',
  maxWidth: '90%',
  alignSelf: sender === 'user' ? 'flex-end' : 'flex-start',
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1.5),
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

  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [currentStage, setCurrentStage] = useState<ChatStage>('intro');
  const [selectedChoices, setSelectedChoices] = useState<{
    atmosphere?: string;
    mood?: string;
    elements: string[];
  }>({ elements: [] });

  const chatContainerRef = useRef<HTMLDivElement>(null);

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
    let introMessage = `Welcome to Ambiance AI! You've chosen the ${mode} mode.`;
    if (initialInput) {
      introMessage += ` And you've started with the idea: "${initialInput}".`;
    }
    introMessage += ` Let's build your perfect soundscape step by step. First, what kind of atmosphere are you looking for? You can also type your thoughts below.`;

    setMessages([
      ...(initialInput ? [{ sender: 'user' as Message['sender'], text: initialInput }] : []),
      { sender: 'ai' as Message['sender'], text: introMessage },
    ]);
    setCurrentStage('atmosphere');
  }, [initialInput, mode]);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const handleOptionSelect = (option: string, type: 'atmosphere' | 'mood' | 'elements') => {
    setMessages((prevMessages) => [...prevMessages, { sender: 'user' as Message['sender'], text: option }]);

    let nextStageMessage = '';
    let nextStage: ChatStage = currentStage;

    setSelectedChoices((prev) => {
      const newChoices = { ...prev };
      if (type === 'elements') {
        if (newChoices.elements.includes(option)) {
          newChoices.elements = newChoices.elements.filter(item => item !== option);
        } else {
          newChoices.elements = [...newChoices.elements, option];
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
      setMessages((prevMessages) => [...prevMessages, { sender: 'ai' as Message['sender'], text: nextStageMessage }]);
    }
    setCurrentStage(nextStage);
  };

  const handleGenerateAudio = async () => {
    setIsLoading(true);
    const finalDescription = `Atmosphere: ${selectedChoices.atmosphere || 'N/A'}, Mood: ${selectedChoices.mood || 'N/A'}, Elements: ${selectedChoices.elements.join(', ')}.`;
    
    // Append any current input text if available, then clear it.
    let fullDescription = finalDescription;
    if (inputText.trim() !== '') {
      fullDescription += ` Additional input: ${inputText.trim()}.`;
      setInputText(''); // Clear input after appending
    }

    try {
      setMessages((prevMessages) => [...prevMessages, { sender: 'ai' as Message['sender'], text: 'Generating your soundscape...' }]);
      const audioGenerationResponse = await fetch('http://localhost:8000/api/generate-audio', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ description: fullDescription, effects_config: {} }),
      });

      if (!audioGenerationResponse.ok) {
        throw new Error(`Error from audio generation API: ${audioGenerationResponse.statusText}`);
      }

      const audioData = await audioGenerationResponse.json();
      if (audioData.audio_url) {
        navigate('/player', { state: { audioUrl: audioData.audio_url } });
      } else {
        setMessages((prevMessages) => [...prevMessages, { sender: 'ai' as Message['sender'], text: 'Sorry, could not generate audio. Please try again or provide more details.' }]);
      }
    } catch (error) {
      console.error('Error during audio generation API call:', error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'ai' as Message['sender'], text: `Sorry, I encountered an issue generating audio: ${error instanceof Error ? error.message : String(error)}. Please try again.` },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async () => {
    if (inputText.trim() === '') return;

    const newUserMessage: Message = { sender: 'user' as Message['sender'], text: inputText.trim() };
    setMessages((prevMessages) => [...prevMessages, newUserMessage]);
    setInputText('');
    setIsLoading(true);

    // If the user is in a guided stage, transition to free chat after sending their input
    if (currentStage !== 'free_chat') {
      setCurrentStage('free_chat');
      setMessages((prevMessages) => [...prevMessages, { sender: 'ai' as Message['sender'], text: '好的，现在进入自由对话模式。您可以在这里进一步描述您的音景，或者告诉我何时生成。' }]);
    }

    try {
      // Step 1: Call /api/generate-scene to get AI's conversational response or scene description
      const sceneResponse = await fetch('http://localhost:8000/api/generate-scene', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt: newUserMessage.text, mode: mode, chat_history: messages.filter(m => m.sender === 'user').map(m => m.text) }),
      });

      if (!sceneResponse.ok) {
        throw new Error(`Error from scene generation API: ${sceneResponse.statusText}`);
      }

      const sceneData = await sceneResponse.json();
      const aiTextResponse = sceneData.response; // Assuming the API returns a 'response' field

      setMessages((prevMessages) => [...prevMessages, { sender: 'ai' as Message['sender'], text: aiTextResponse }]);

      // Removed: Automatic audio generation based on keywords in handleSendMessage
      // This will now be handled by the dedicated handleGenerateAudio function triggered by the button.

    } catch (error) {
      console.error('Error during API call:', error);
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'ai' as Message['sender'], text: `Sorry, I encountered an issue processing your request: ${error instanceof Error ? error.message : String(error)}. Please try again.` },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column', background: 'linear-gradient(135deg, #1a2332 0%, #0f1419 100%)', }}>
      <Box
        sx={{
          p: 2,
          display: 'flex',
          alignItems: 'center',
          background: 'rgba(255, 255, 255, 0.05)',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
          backdropFilter: 'blur(20px)',
          position: 'sticky',
          top: 0,
          zIndex: 10,
        }}
      >
        <IconButton onClick={() => navigate(-1)} sx={{ color: 'white' }}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h6" sx={{ ml: 2, color: 'white' }}>
          Ambiance AI
        </Typography>
      </Box>

      <ChatContainer ref={chatContainerRef}>
        <Stack spacing={2}>
          {messages.map((msg, index) => (
            <Box key={index} sx={{ alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start' }}>
              <MessageBubbleContent sender={msg.sender}>
                {msg.sender === 'ai' && <AIIcon sx={{ color: '#2d9c93', fontSize: 20 }} />}
                <Typography sx={{ color: 'white' }}>{msg.text}</Typography>
              </MessageBubbleContent>
            </Box>
          ))}
          {isLoading && (
            <Box sx={{ alignSelf: 'flex-start' }}>
              <MessageBubbleContent sender="ai">
                <AIIcon sx={{ color: '#2d9c93', fontSize: 20 }} />
                <CircularProgress size={20} sx={{ color: '#2d9c93' }} />
                <Typography sx={{ color: 'white', ml: 1 }}>AI is thinking...</Typography>
              </MessageBubbleContent>
            </Box>
          )}

          {/* Conditional Options Rendering */}
          {(currentStage === 'atmosphere' || currentStage === 'mood' || currentStage === 'elements') && !isLoading && (
            <Box sx={{ alignSelf: 'flex-start', mt: 2, width: '100%' }}>
              <MessageBubbleContent sender="ai" sx={{ width: '100%' }}>
                <Typography sx={{ color: 'white', mb: 1 }}>
                  {currentStage === 'atmosphere' && 'Choose an atmosphere:'}
                  {currentStage === 'mood' && 'Choose a mood:'}
                  {currentStage === 'elements' && 'Select sound elements (or type others):'}
                </Typography>
                <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                  {(currentStage === 'atmosphere' ? atmosphereOptions :
                    currentStage === 'mood' ? moodOptions :
                    elementOptions).map((option) => (
                    <OptionChip
                      key={option}
                      label={option}
                      onClick={() => handleOptionSelect(option, currentStage)}
                      variant={selectedChoices.elements.includes(option) && currentStage === 'elements' ? 'filled' : 'outlined'}
                      sx={{
                        bgcolor: (selectedChoices.elements.includes(option) && currentStage === 'elements') ? 'rgba(45, 156, 147, 0.4)' : 'rgba(255, 255, 255, 0.1)',
                        borderColor: (selectedChoices.elements.includes(option) && currentStage === 'elements') ? '#2d9c93' : 'rgba(45, 156, 147, 0.2)',
                        color: 'white',
                        '&:hover': {
                          bgcolor: (selectedChoices.elements.includes(option) && currentStage === 'elements') ? 'rgba(45, 156, 147, 0.5)' : 'rgba(255, 255, 255, 0.2)',
                        },
                      }}
                    />
                  ))}
                </Stack>
              </MessageBubbleContent>
            </Box>
          )}
        </Stack>
      </ChatContainer>

      <Box
        sx={{
          p: 2,
          background: 'rgba(18, 18, 18, 0.8)',
          backdropFilter: 'blur(10px)',
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
          mt: 'auto', // Pushes input to the bottom
          maxWidth: '90%', // Also widen the input area
          margin: '0 auto', // Center the input area
        }}
      >
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Type your message..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyPress={handleKeyPress}
            sx={{
              '& .MuiOutlinedInput-root': {
                color: 'white',
                '& fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.2)',
                },
                '&:hover fieldset': {
                  borderColor: 'rgba(255, 255, 255, 0.3)',
                },
                '&.Mui-focused fieldset': {
                  borderColor: '#2d9c93',
                },
              },
              '& .MuiInputBase-input::placeholder': {
                color: 'rgba(255, 255, 255, 0.7)',
                opacity: 1,
              },
            }}
            disabled={isLoading}
          />
          <IconButton
            sx={{
              bgcolor: '#2d9c93', // Primary color
              color: 'white',
              '&:hover': {
                bgcolor: '#1a5f5a', // Darker primary on hover
              },
              width: 50, // Fixed width for icon button
              height: 50, // Fixed height for icon button
            }}
            onClick={handleSendMessage}
            disabled={isLoading || inputText.trim() === ''}
          >
            {isLoading ? <CircularProgress size={24} color="inherit" /> : <SendIcon />}
          </IconButton>
        </Box>
        {(currentStage === 'elements' || currentStage === 'confirm') && selectedChoices.elements.length > 0 && !isLoading && (
          <Button
            variant="contained"
            fullWidth
            size="large"
            onClick={handleGenerateAudio} // New function to trigger audio generation
            sx={{
              mt: 2,
              height: 50,
              background: 'linear-gradient(135deg, #2d9c93 0%, #1a5f5a 100%)',
              borderRadius: 25,
              color: 'white',
              fontSize: 16,
              fontWeight: 600,
              '&:hover': {
                background: 'linear-gradient(135deg, #1a5f5a 0%, #2d9c93 100%)',
              },
            }}
          >
            Generate Soundscape
          </Button>
        )}
      </Box>
    </Box>
  );
};

export default ChatScreen; 