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
import PageLayout from '../components/PageLayout';
import { uiSystem } from '../theme/uiSystem';
import { buildAudioGenPrompt } from '../utils/promptBuilder';

interface Message {
  sender: 'user' | 'ai';
  text: string;
  isUser: boolean;
  audioUrl?: string;
  backgroundImageUrl?: string;
  musicUrl?: string;
}

type ChatStage =
  | 'selectType'
  | 'audio_atmosphere'
  | 'audio_mood'
  | 'audio_elements'
  | 'music_genre'
  | 'music_instruments'
  | 'music_tempo'
  | 'music_usage'
  | 'confirm'
  | 'free_chat'
  | 'complete';

interface ChatScreenProps {
  usePageLayout?: boolean;
}

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

const ChatScreen: React.FC<ChatScreenProps> = ({ usePageLayout = true }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { mode, initialInput } = (location.state as { mode: string; initialInput: string } | null) || { mode: 'default', initialInput: '' };
  const { aiName } = useAiName();

  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentStage, setCurrentStage] = useState<ChatStage>('selectType');
  const [selectedType, setSelectedType] = useState<'audio' | 'music' | null>(null);
  const [audioChoices, setAudioChoices] = useState<{
    audio_atmosphere?: string;
    audio_mood?: string;
    audio_elements: string[];
    extraInputs: string[];
  }>({ audio_elements: [], extraInputs: [] });
  const [musicChoices, setMusicChoices] = useState<{
    genre?: string;
    instruments: string[];
    tempo?: string;
    usage?: string;
  }>({ instruments: [] });
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

  const [atmosphereOptions, setAtmosphereOptions] = useState<string[]>([]);
  const [moodOptions, setMoodOptions] = useState<string[]>([]);
  const [elementOptions, setElementOptions] = useState<string[]>([]);
  const defaultOptions = {
    audio_atmosphere: [
      "Cozy and intimate",
      "Spacious and airy",
      "Lively and energetic",
      "Calm and serene",
      "Mysterious and intriguing",
    ],
    audio_mood: [
      "Relaxed",
      "Focused",
      "Inspired",
      "Dreamy",
      "Uplifting",
      "Melancholic",
    ],
    audio_elements: [
      "Rain", "Wind", "Birds chirping", "Ocean waves", "Fire crackling",
      "Coffee machine sounds", "Distant chatter", "Footsteps", "Gentle music",
      "Thunderstorm", "Night crickets", "City hum", "Train passing",
    ],
  };

  const abortControllerRef = useRef<AbortController | null>(null);

  const [musicGenreOptions, setMusicGenreOptions] = useState<string[]>([]);
  const [musicInstrumentOptions, setMusicInstrumentOptions] = useState<string[]>([]);
  const [musicTempoOptions, setMusicTempoOptions] = useState<string[]>([]);
  const [musicUsageOptions, setMusicUsageOptions] = useState<string[]>([]);

  // Add a state to store the final prompt
  const [finalPrompt, setFinalPrompt] = useState<string>('');

  const fetchOptions = async (stage: 'audio_atmosphere' | 'audio_mood' | 'audio_elements') => {
    try {
      const res = await fetch('http://localhost:8000/api/generate-options', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ mode, input: initialInput, stage }),
      });
      if (res.ok) {
        const data = await res.json();
        return Array.isArray(data.options) ? data.options : [];
      }
    } catch (e) {}
    return [];
  };

  const fetchMusicGenOptions = async (stage: 'genre' | 'instruments' | 'tempo' | 'usage', userInput: string = '') => {
    try {
      const res = await fetch('http://localhost:8000/api/generate-musicgen-options', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stage, user_input: userInput }),
      });
      if (res.ok) {
        const data = await res.json();
        return Array.isArray(data.options) ? data.options : [];
      }
    } catch (e) {}
    return [];
  };

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
    if (currentStage === 'audio_elements') {
      setShowElementSelectionAndButton(true);
    } else {
      setShowElementSelectionAndButton(false);
    }
  }, [currentStage]);

  useEffect(() => {
    let introMessage = `Welcome to ${aiName || 'Nightingale'}!`;
    if (initialInput) {
      introMessage += ` And you've started with the idea: "${initialInput}".`;
    }
    introMessage += ` What do you want to generate?`;
    setMessages([
      ...(initialInput ? [{ sender: 'user' as Message['sender'], text: initialInput, isUser: true }] : []),
      { sender: 'ai' as Message['sender'], text: introMessage, isUser: false },
    ]);
    setCurrentStage('selectType');
    setInputText('');
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

  const handleOptionSelect = (
    option: string,
    type:
      | 'audio_atmosphere'
      | 'audio_mood'
      | 'audio_elements'
      | 'music_genre'
      | 'music_instruments'
      | 'music_tempo'
      | 'music_usage'
  ) => {
    if (type === 'audio_atmosphere' || type === 'audio_mood' || type === 'audio_elements') {
      setAudioChoices((prev) => {
        const newChoices = { ...prev };
        if (type === 'audio_elements') {
          if (newChoices.audio_elements.includes(option)) {
            newChoices.audio_elements = newChoices.audio_elements.filter((item) => item !== option);
          } else {
            if (newChoices.audio_elements.length < 3) {
              newChoices.audio_elements = [...newChoices.audio_elements, option];
            }
          }
        } else if (type === 'audio_atmosphere' || type === 'audio_mood') {
          newChoices[type] = option;
        }
        return newChoices;
      });
      if (type === 'audio_atmosphere') setCurrentStage('audio_mood');
      else if (type === 'audio_mood') setCurrentStage('audio_elements');
      setMessages((prev) => [
        ...prev,
        { sender: 'user', text: option, isUser: true },
      ]);
      return;
    }
    // MusicGen 分支
    setMusicChoices((prev) => {
      const newChoices = { ...prev };
      if (type === 'music_instruments') {
        newChoices.instruments = [option];
      } else if (type === 'music_genre') {
        newChoices.genre = option;
      } else if (type === 'music_tempo') {
        newChoices.tempo = option;
        console.log('musicChoices.tempo set:', option);
      } else if (type === 'music_usage') {
        newChoices.usage = option;
        console.log('musicChoices.usage set:', option);
      }
      console.log('musicChoices', newChoices);
      return newChoices;
    });
    if (type === 'music_genre') setCurrentStage('music_instruments');
    else if (type === 'music_instruments') setCurrentStage('music_tempo');
    else if (type === 'music_tempo') setCurrentStage('music_usage');
    setMessages((prev) => [
      ...prev,
      { sender: 'user', text: option, isUser: true },
    ]);
  };

  const handleTypeSelect = (type: 'audio' | 'music') => {
    setSelectedType(type);
    if (type === 'audio') {
      setCurrentStage('audio_atmosphere');
    } else {
      setCurrentStage('music_genre');
    }
    setMessages((prev) => [
      ...prev,
      { sender: 'ai', text: type === 'audio'
          ? "Let's build your perfect soundscape! First, what kind of atmosphere are you looking for?"
          : "Let's compose your music! First, what genre or style do you want?", isUser: false }
    ]);
  };

  const handleGenerate = async () => {
    try {
      setIsLoading(true);
      setError(null);
      abortControllerRef.current = new AbortController();
      let audioOrMusicUrl = null;
      let prompt = '';
      const subjects = audioChoices.audio_elements;
      const actions = audioChoices.audio_mood ? [audioChoices.audio_mood] : [];
      const scenes = [
        ...(audioChoices.audio_atmosphere ? [audioChoices.audio_atmosphere] : []),
        ...(mode && mode !== 'default' ? [`for ${mode}`] : [])
      ];
      const extraInputs = audioChoices.extraInputs && audioChoices.extraInputs.length > 0 ? audioChoices.extraInputs : [];
      const allSubjects = [...subjects, ...extraInputs];
      prompt = buildAudioGenPrompt({ subjects: allSubjects, actions, scenes });
      setFinalPrompt(prompt);
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'ai', text: 'Generating your soundscape...', isUser: false },
        { sender: 'ai', text: `Prompt: ${prompt}`, isUser: false },
      ]);
      const audioResponse = await fetch('http://localhost:8000/api/generate-audio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description: prompt,
          duration: 10,
          is_poem: false,
          mode: mode,
          effects_config: null,
        }),
        signal: abortControllerRef.current.signal,
      });
      if (!audioResponse.ok) {
        const errorData = await audioResponse.json();
        throw new Error(errorData.detail || 'Failed to generate audio');
      }
      const audioData = await audioResponse.json();
      audioOrMusicUrl = audioData.audio_url;
      setCurrentAudioUrl(audioData.audio_url);
      // 1.2 自动生成背景图片
      const backgroundDescription = initialInput || 'a beautiful soundscape background';
      const bgResponse = await fetch('http://localhost:8000/api/generate-background', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description: backgroundDescription }),
        signal: abortControllerRef.current.signal,
      });
      if (bgResponse.ok) {
        const bgData = await bgResponse.json();
        setCurrentBackgroundImageUrl(bgData.image_url);
      }
      // 1.3 完成后显示播放/再生成按钮
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'ai' as Message['sender'], text: 'Your personalized soundscape is ready! What would you like to do?', isUser: false },
      ]);
      setShowPlaybackButtons(true);
      setCurrentStage('complete');
    } catch (err) {
      if (err && typeof err === 'object' && 'name' in err && (err as any).name === 'AbortError') {
        setMessages((prev) => [...prev, { sender: 'ai', text: 'Generation cancelled.', isUser: false }]);
      } else {
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
        setMessages((prevMessages) => [
          ...prevMessages,
          { sender: 'ai' as Message['sender'], text: `Error generating content: ${err instanceof Error ? err.message : 'An unknown error occurred'}.`, isUser: false },
        ]);
        console.error("Error generating content:", err);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handlePlayback = () => {
    const isMusic = selectedType === 'music';
    navigate('/player', {
      state: {
        audioUrl: isMusic ? currentMusicUrl : currentAudioUrl,
        backgroundImageUrl: currentBackgroundImageUrl,
        selectedChoices: selectedType === 'music' ? musicChoices : audioChoices,
        description: finalPrompt
      }
    });
  };

  const handleRegenerate = () => {
    setShowPlaybackButtons(false);
    setCurrentStage('selectType');
    setMessages([]);
    setAudioChoices({ audio_elements: [], extraInputs: [] });
    setMusicChoices({ instruments: [] });
    setCurrentAudioUrl(null);
    setCurrentBackgroundImageUrl(null);
    setCurrentMusicUrl(null);
    setError(null);
  };

  const handleSendMessage = async () => {
    if (selectedType === 'music') {
      if (inputText.trim() !== '') {
        setMessages((prevMessages) => [...prevMessages, { sender: 'user', text: inputText, isUser: true }]);
        setInputText('');
      }
      return;
    }
    if ((currentStage as string) === 'audio_elements') {
      if (inputText.trim() !== '') {
        setAudioChoices((prev) => ({
          ...prev,
          audio_elements: [...prev.audio_elements, inputText.trim()],
        }));
        setMessages((prevMessages) => [...prevMessages, { sender: 'ai', text: `Added "${inputText.trim()}" to your elements. Click Generate Soundscape when ready!`, isUser: false }]);
        setInputText('');
      }
      return;
    }
    if (inputText.trim() !== '') {
      setMessages((prevMessages) => [...prevMessages, { sender: 'user', text: inputText, isUser: true }]);
      setInputText('');
    }

    // If in elements stage and user types, assume they are adding custom elements or confirming
    if ((currentStage as string) === 'audio_elements') {
      if (inputText.trim() !== '') {
        setAudioChoices((prev) => ({
          ...prev,
          audio_elements: [...prev.audio_elements, inputText.trim()],
        }));
        setMessages((prevMessages) => [...prevMessages, { sender: 'ai', text: `Added "${inputText.trim()}" to your elements. Click Generate Soundscape when ready!`, isUser: false }]);
      }
      // Do not transition stage automatically here, wait for generate button click
      return;
    }

    if (currentStage === 'selectType') {
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
      handleOptionSelect(inputText, currentStage as 'audio_atmosphere' | 'audio_mood');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleReturnToGuidedMode = () => {
    setCurrentStage('audio_atmosphere');
    setMessages((prevMessages) => [
      ...prevMessages,
      { sender: 'user' as Message['sender'], text: 'Return to guided mode', isUser: true },
      { sender: 'ai' as Message['sender'], text: "Okay, let's start over. What kind of atmosphere are you looking for?", isUser: false }
    ]);
    // Reset choices and URLs if returning to beginning of guided mode
    setAudioChoices({ audio_elements: [], extraInputs: [] });
    setMusicChoices({ instruments: [] });
    setCurrentAudioUrl(null);
    setCurrentBackgroundImageUrl(null);
    setCurrentMusicUrl(null);
    setError(null);
    // showElementSelectionAndButton will be handled by useEffect based on currentStage
  };

  const handleCancelGenerate = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    setIsLoading(false);
    setShowPlaybackButtons(false);
    setCurrentStage('selectType');
    setMessages([
      { sender: 'ai', text: 'Generation cancelled. What do you want to generate?', isUser: false },
    ]);
    setAudioChoices({ audio_elements: [], extraInputs: [] });
    setMusicChoices({ instruments: [] });
    setCurrentAudioUrl(null);
    setCurrentBackgroundImageUrl(null);
    setCurrentMusicUrl(null);
    setError(null);
  };

  useEffect(() => {
    if (currentStage === 'audio_atmosphere') {
      fetchOptions('audio_atmosphere').then((options) => {
        setAtmosphereOptions(options.length > 0 ? options : defaultOptions.audio_atmosphere);
      });
    }
    if (currentStage === 'audio_mood') {
      fetchOptions('audio_mood').then((options) => {
        setMoodOptions(options.length > 0 ? options : defaultOptions.audio_mood);
      });
    }
    if (currentStage === 'audio_elements') {
      fetchOptions('audio_elements').then((options) => {
        // 去重逻辑：过滤掉与 atmosphere（audio_atmosphere）、灵感种子（initialInput）重复的元素
        let keywords: string[] = [];
        if (audioChoices.audio_atmosphere) {
          keywords = keywords.concat(audioChoices.audio_atmosphere.split(/,|，|\s+| and |、|。|\.|\n/).map(s => s.trim()).filter(Boolean));
        }
        if (initialInput) {
          keywords = keywords.concat(initialInput.split(/,|，|\s+| and |、|。|\.|\n/).map(s => s.trim()).filter(Boolean));
        }
        // 只保留未在 keywords 中出现的元素
        const filtered = options.filter((opt: string) => !keywords.some(kw => kw && opt.toLowerCase().includes(kw.toLowerCase())));
        setElementOptions(filtered.length > 0 ? filtered : options);
      });
    }
  }, [currentStage, mode, initialInput, audioChoices.audio_atmosphere]);

  useEffect(() => {
    if (currentStage === 'music_genre') {
      fetchMusicGenOptions('genre', initialInput).then((options) => {
        setMusicGenreOptions(options);
      });
    }
    if (currentStage === 'music_instruments') {
      fetchMusicGenOptions('instruments', musicChoices.genre || '').then((options) => {
        setMusicInstrumentOptions(options);
      });
    }
    if (currentStage === 'music_tempo') {
      fetchMusicGenOptions('tempo', musicChoices.instruments.join(', ')).then((options) => {
        setMusicTempoOptions(options);
      });
    }
    if (currentStage === 'music_usage') {
      fetchMusicGenOptions('usage', musicChoices.tempo || '').then((options) => {
        setMusicUsageOptions(options);
      });
    }
  }, [currentStage, initialInput, musicChoices]);

  useEffect(() => {
    if (currentStage === 'music_usage') {
      setMusicChoices((prev) => ({ ...prev, usage: undefined }));
    }
  }, [currentStage]);

  const handleGenerateMusic = async () => {
    try {
      setIsLoading(true);
      setError(null);
      abortControllerRef.current = new AbortController();
      // Compose a music prompt string for display
      const musicPrompt = `Genre: ${musicChoices.genre || ''}, Instruments: ${musicChoices.instruments.join(', ')}, Tempo: ${musicChoices.tempo || ''}, Usage: ${musicChoices.usage || ''}, Input: ${initialInput || ''}`;
      setFinalPrompt(musicPrompt);
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'ai', text: 'Generating your music...', isUser: false },
        { sender: 'ai', text: musicPrompt, isUser: false },
      ]);
      const res = await fetch('http://localhost:8000/api/generate-music', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          genre: musicChoices.genre,
          instruments: musicChoices.instruments,
          tempo: musicChoices.tempo,
          usage: musicChoices.usage,
          userInput: initialInput,
          duration: 30,
        }),
        signal: abortControllerRef.current.signal,
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to generate music');
      }
      const data = await res.json();
      setCurrentMusicUrl(data.music_url);
      // Use the prompt from backend response
      const finalMusicPrompt = data.prompt || musicPrompt;
      setFinalPrompt(finalMusicPrompt);
      // Set background image if available
      if (data.background_url) {
        setCurrentBackgroundImageUrl(data.background_url);
      }
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'ai', text: 'Your personalized music is ready! What would you like to do?', isUser: false },
      ]);
      setShowPlaybackButtons(true);
      setCurrentStage('complete');
    } catch (err) {
      if (err && typeof err === 'object' && 'name' in err && (err as any).name === 'AbortError') {
        setMessages((prev) => [...prev, { sender: 'ai', text: 'Generation cancelled.', isUser: false }]);
      } else {
        setError(err instanceof Error ? err.message : 'An unknown error occurred');
        setMessages((prevMessages) => [
          ...prevMessages,
          { sender: 'ai' as Message['sender'], text: `Error generating music: ${err instanceof Error ? err.message : 'An unknown error occurred'}.`, isUser: false },
        ]);
        console.error('Error generating music:', err);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const chatMainContent = (
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
          Chat with {aiName && aiName.trim() ? aiName : 'Nightingale'}
        </Typography>
      </Box>
      <Stack spacing={2} sx={{ flex: 1, width: '100%', overflow: 'auto', p: uiSystem.spacing.large }} ref={chatContainerRef}>
        {messages.map((msg, index) => (
          <Box
            key={index}
            sx={{
              alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
              display: 'flex',
              alignItems: 'flex-start',
              gap: 1.5,
              flexDirection: msg.sender === 'user' ? 'row-reverse' : 'row',
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
        <div ref={messagesEndRef} />
      </Stack>
      {currentStage === 'selectType' && (
        <Box sx={{ mt: 4, textAlign: 'center' }}>
          <Typography variant="h6" sx={{ mb: 2 }}>What do you want to generate?</Typography>
          <Button
            variant="outlined"
            sx={{
              mr: 2,
              minWidth: 160,
              borderRadius: 999,
              fontWeight: 600,
              background: selectedType === 'audio' ? 'linear-gradient(90deg, #2d9c93 60%, #3be584 100%)' : 'none',
              color: selectedType === 'audio' ? 'white' : '#2d9c93',
              borderColor: '#2d9c93',
              '&:hover': {
                background: 'linear-gradient(90deg, #2d9c93 60%, #3be584 100%)',
                color: 'white',
              },
              ...(selectedType === 'audio' && {
                boxShadow: '0 2px 8px rgba(45,156,147,0.15)',
              }),
            }}
            onClick={() => handleTypeSelect('audio')}
          >
            Background Sound
          </Button>
          <Button
            variant="outlined"
            sx={{
              minWidth: 160,
              borderRadius: 999,
              fontWeight: 600,
              background: selectedType === 'music' ? 'linear-gradient(90deg, #2d9c93 60%, #3be584 100%)' : 'none',
              color: selectedType === 'music' ? 'white' : '#2d9c93',
              borderColor: '#2d9c93',
              '&:hover': {
                background: 'linear-gradient(90deg, #2d9c93 60%, #3be584 100%)',
                color: 'white',
              },
              ...(selectedType === 'music' && {
                boxShadow: '0 2px 8px rgba(45,156,147,0.15)',
              }),
            }}
            onClick={() => handleTypeSelect('music')}
          >
            Music
          </Button>
        </Box>
      )}
      {currentStage === 'audio_atmosphere' && !isLoading && !showPlaybackButtons && (
        <OptionMessageBubbleContent sx={{ mt: 2 }}>
          <Typography variant="body1" sx={{ mb: 1 }}>What kind of atmosphere are you looking for?</Typography>
          <Stack direction="row" flexWrap="wrap" spacing={1}>
            {atmosphereOptions.map((option) => (
              <OptionChip
                key={option}
                label={option}
                onClick={() => handleOptionSelect(option, 'audio_atmosphere')}
                variant={audioChoices.audio_atmosphere === option ? 'filled' : 'outlined'}
                color={audioChoices.audio_atmosphere === option ? 'primary' : 'default'}
                sx={{
                  cursor: audioChoices.audio_atmosphere === option ? 'pointer' : 'pointer',
                  transition: 'all 0.2s',
                  fontWeight: audioChoices.audio_atmosphere === option ? 700 : 400,
                  boxShadow: audioChoices.audio_atmosphere === option ? '0 2px 8px rgba(45,156,147,0.15)' : 'none',
                }}
              />
            ))}
          </Stack>
        </OptionMessageBubbleContent>
      )}
      {currentStage === 'audio_mood' && !isLoading && !showPlaybackButtons && (
        <OptionMessageBubbleContent sx={{ mt: 2 }}>
          <Typography variant="body1" sx={{ mb: 1 }}>What kind of mood or feeling do you want to evoke?</Typography>
          <Stack direction="row" flexWrap="wrap" spacing={1}>
            {moodOptions.map((option) => (
              <OptionChip
                key={option}
                label={option}
                onClick={() => handleOptionSelect(option, 'audio_mood')}
                variant={audioChoices.audio_mood === option ? 'filled' : 'outlined'}
                color={audioChoices.audio_mood === option ? 'primary' : 'default'}
                sx={{
                  cursor: audioChoices.audio_mood === option ? 'pointer' : 'pointer',
                  transition: 'all 0.2s',
                  fontWeight: audioChoices.audio_mood === option ? 700 : 400,
                  boxShadow: audioChoices.audio_mood === option ? '0 2px 8px rgba(45,156,147,0.15)' : 'none',
                }}
              />
            ))}
          </Stack>
        </OptionMessageBubbleContent>
      )}
      {currentStage === 'audio_elements' && !isLoading && !showPlaybackButtons && (
        <OptionMessageBubbleContent sx={{ mt: 2 }}>
          <Typography variant="body1" sx={{ mb: 1 }}>Select sound elements (max 3):</Typography>
          <Stack direction="row" flexWrap="wrap" spacing={1}>
            {elementOptions.map((option) => {
              const isSelected = audioChoices.audio_elements.includes(option);
              const isDisabled = !isSelected && audioChoices.audio_elements.length >= 3;
              return (
                <OptionChip
                  key={option}
                  label={option}
                  onClick={() => handleOptionSelect(option, 'audio_elements')}
                  variant={isSelected ? 'filled' : 'outlined'}
                  color={isSelected ? 'primary' : 'default'}
                  disabled={isDisabled}
                  sx={{
                    cursor: isDisabled ? 'not-allowed' : 'pointer',
                    opacity: isDisabled ? 0.5 : 1,
                    transition: 'all 0.2s',
                    fontWeight: isSelected ? 700 : 400,
                    boxShadow: isSelected ? '0 2px 8px rgba(45,156,147,0.15)' : 'none',
                  }}
                />
              );
            })}
          </Stack>
        </OptionMessageBubbleContent>
      )}
      {currentStage === 'audio_elements' && !showPlaybackButtons && (
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center', gap: 2 }}>
          <Button
            variant="contained"
            onClick={handleGenerate}
            disabled={isLoading || audioChoices.audio_elements.length === 0}
            sx={{ minWidth: 140 }}
          >
            Generate Soundscape
          </Button>
          <Button
            variant="outlined"
            color="success"
            onClick={handleCancelGenerate}
            sx={{ minWidth: 100 }}
          >
            Cancel
          </Button>
        </Box>
      )}
      {showPlaybackButtons && (
        <Box sx={{ mt: 2, display: 'flex', gap: 2, justifyContent: 'center' }}>
          <Button
            variant="contained"
            onClick={() => navigate('/player', {
              state: {
                audioUrl: currentMusicUrl || currentAudioUrl,
                backgroundImageUrl: currentBackgroundImageUrl,
                description: finalPrompt,
              },
            })}
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
      {currentStage === 'music_genre' && !isLoading && !showPlaybackButtons && (
        <OptionMessageBubbleContent sx={{ mt: 2 }}>
          <Typography variant="body1" sx={{ mb: 1 }}>What genre or style do you want?</Typography>
          <Stack direction="row" flexWrap="wrap" spacing={1}>
            {musicGenreOptions.map((option) => (
              <OptionChip
                key={option}
                label={option}
                onClick={() => handleOptionSelect(option, 'music_genre')}
                variant={musicChoices.genre === option ? 'filled' : 'outlined'}
                color={musicChoices.genre === option ? 'primary' : 'default'}
              />
            ))}
          </Stack>
        </OptionMessageBubbleContent>
      )}
      {currentStage === 'music_instruments' && !isLoading && !showPlaybackButtons && (
        <OptionMessageBubbleContent sx={{ mt: 2 }}>
          <Typography variant="body1" sx={{ mb: 1 }}>Pick up to 3 instruments:</Typography>
          <Stack direction="row" flexWrap="wrap" spacing={1}>
            {musicInstrumentOptions.map((option) => (
              <OptionChip
                key={option}
                label={option}
                onClick={() => handleOptionSelect(option, 'music_instruments')}
                variant={musicChoices.instruments.includes(option) ? 'filled' : 'outlined'}
                color={musicChoices.instruments.includes(option) ? 'primary' : 'default'}
              />
            ))}
          </Stack>
        </OptionMessageBubbleContent>
      )}
      {currentStage === 'music_tempo' && !isLoading && !showPlaybackButtons && (
        <OptionMessageBubbleContent sx={{ mt: 2 }}>
          <Typography variant="body1" sx={{ mb: 1 }}>What tempo do you prefer?</Typography>
          <Stack direction="row" flexWrap="wrap" spacing={1}>
            {musicTempoOptions.map((option) => (
              <OptionChip
                key={option}
                label={option}
                onClick={() => handleOptionSelect(option, 'music_tempo')}
                variant={musicChoices.tempo === option ? 'filled' : 'outlined'}
                color={musicChoices.tempo === option ? 'primary' : 'default'}
              />
            ))}
          </Stack>
        </OptionMessageBubbleContent>
      )}
      {currentStage === 'music_usage' && !isLoading && !showPlaybackButtons && (
        <OptionMessageBubbleContent sx={{ mt: 2 }}>
          <Typography variant="body1" sx={{ mb: 1 }}>Where will you use this music?</Typography>
          <Stack direction="row" flexWrap="wrap" spacing={1}>
            {musicUsageOptions.map((option) => (
              <OptionChip
                key={option}
                label={option}
                onClick={() => handleOptionSelect(option, 'music_usage')}
                variant={musicChoices.usage === option ? 'filled' : 'outlined'}
                color={musicChoices.usage === option ? 'primary' : 'default'}
              />
            ))}
          </Stack>
        </OptionMessageBubbleContent>
      )}
      {currentStage === 'music_usage' && !showPlaybackButtons && musicChoices.usage && (
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center', gap: 2 }}>
          <Button
            variant="contained"
            onClick={handleGenerateMusic}
            disabled={
              isLoading ||
              !musicChoices.genre ||
              !musicChoices.tempo ||
              !musicChoices.usage ||
              !musicChoices.instruments ||
              musicChoices.instruments.length === 0
            }
            sx={{ minWidth: 140 }}
          >
            Generate Music
          </Button>
          <Button
            variant="outlined"
            color="success"
            onClick={handleCancelGenerate}
            sx={{ minWidth: 100 }}
          >
            Cancel
          </Button>
        </Box>
      )}
      <Box
        sx={{
          p: 0,
          borderTop: '1px solid rgba(255, 255, 255, 0.1)',
          position: 'relative',
          zIndex: 2,
          width: '100%',
          mt: 3,
        }}
      >
        <Box sx={{ display: 'flex', gap: 1, my: 1.5 }}>
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
    </>
  );

  if (usePageLayout) {
    return (
      <PageLayout>
        {chatMainContent}
      </PageLayout>
    );
  }
  return chatMainContent;
};

export default ChatScreen; 