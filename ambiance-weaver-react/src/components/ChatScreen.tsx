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
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Send as SendIcon,
  Close as CloseIcon,
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
  | 'complete'
  | 'story_script_edit';

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

  // 1. 在 useState 区域增加 isPromptGenerated 状态
  const [isPromptGenerated, setIsPromptGenerated] = useState(false);

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

  // 1. 新增：通用 prompt 编辑状态
  const [finalPrompt, setFinalPrompt] = useState<string>('');
  const [showPromptEdit, setShowPromptEdit] = useState(false);
  const [aiEditInput, setAiEditInput] = useState('');

  // 2. 修改 handleOptionSelect，移除 setShowPromptEdit、setFinalPrompt、setIsPromptGenerated
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
    if (type === 'audio_mood') {
      setAudioChoices((prev) => ({ ...prev, audio_mood: option }));
      setCurrentStage('audio_elements'); // 关键：推进到下一个阶段
      setMessages((prev) => [
        ...prev,
        { sender: 'user', text: option, isUser: true },
      ]);
      return;
    }
    if (type === 'audio_elements') {
      setAudioChoices((prev) => {
        const newChoices = { ...prev };
        if (newChoices.audio_elements.includes(option)) {
          newChoices.audio_elements = newChoices.audio_elements.filter((item) => item !== option);
        } else {
          if (newChoices.audio_elements.length < 3) {
            newChoices.audio_elements = [...newChoices.audio_elements, option];
          } else {
            // console.log('Cannot add more elements, max 3 reached'); // Removed console.log
          }
        }
        // story mode 下不再自动生成音频，去除自动 handleGenerate 逻辑
        return newChoices;
      });
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
      } else if (type === 'music_usage') {
        newChoices.usage = option;
      }
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

  // 1. handleTypeSelect 只设置 currentStage，不请求 narrative
  const handleTypeSelect = (type: 'audio' | 'music') => {
    setSelectedType(type);
    if (type === 'audio') {
      setCurrentStage('audio_mood');
    } else {
      setCurrentStage('music_genre');
    }
    setMessages((prev) => [
      ...prev,
      { sender: 'ai', text: type === 'audio'
          ? "Let's build your perfect soundscape! What kind of mood or feeling do you want to evoke?"
          : "Let's compose your music! First, what genre or style do you want?", isUser: false }
    ]);
  };

  // 2. audio_elements 阶段，story mode 下出现“生成故事脚本”按钮
  // 在 chatMainContent 渲染区：
  // {mode === 'story' && currentStage === 'audio_elements' && !showPromptEdit && !showPlaybackButtons && audioChoices.audio_elements.length > 0 && (
  //   <Box ...>
  //     <Button onClick={handleGenerateStoryScript}>生成故事脚本</Button>
  //   </Box>
  // )}

  // 3. 新增 handleGenerateStoryScript
  // handleGenerateStoryScript 只弹出编辑弹窗，不生成音频
  const handleGenerateStoryScript = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/generate-scene', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: initialInput,
          mode: 'story',
          mood: audioChoices.audio_mood,
          elements: audioChoices.audio_elements,
        }),
      });
      const data = await res.json();
      setFinalPrompt(data.narrative_script || '');
      setShowPromptEdit(true); // 只弹出编辑弹窗
    } finally {
      setIsLoading(false);
    }
  };

  // 非story模式下生成prompt的函数
  const handleGeneratePrompt = async () => {
    setIsLoading(true);
    try {
      // 添加调试信息
      console.log('Debug - selectedType:', selectedType);
      console.log('Debug - audioChoices:', audioChoices);
      
      // 使用简洁的buildAudioGenPrompt生成prompt
      const subjects = audioChoices.audio_elements;
      const actions = audioChoices.audio_mood ? [audioChoices.audio_mood] : [];
      const scenes = [
        ...(audioChoices.audio_atmosphere ? [audioChoices.audio_atmosphere] : []),
        ...(mode && mode !== 'default' ? [`for ${mode}`] : [])
      ];
      const extraInputs = audioChoices.extraInputs && audioChoices.extraInputs.length > 0 ? audioChoices.extraInputs : [];
      const allSubjects = [...subjects, ...extraInputs];
      
      // 确保selectedType正确
      const promptType = selectedType === 'music' ? 'music' : 'audio';
      console.log('Debug - promptType:', promptType);
      
      const structuredPrompt = buildAudioGenPrompt({
        subjects: allSubjects.length > 0 ? allSubjects : [initialInput],
        actions,
        scenes,
        type: promptType
      });
      
      console.log('Debug - structuredPrompt:', structuredPrompt);
      
      // 直接使用简洁的structuredPrompt，而不是调用后端API
      setFinalPrompt(structuredPrompt);
      setShowPromptEdit(true); // 显示编辑弹窗
    } catch (error) {
      console.error('Error generating prompt:', error);
      // 如果buildAudioGenPrompt失败，使用默认的prompt
      const subjects = audioChoices.audio_elements;
      const actions = audioChoices.audio_mood ? [audioChoices.audio_mood] : [];
      const scenes = [
        ...(audioChoices.audio_atmosphere ? [audioChoices.audio_atmosphere] : []),
        ...(mode && mode !== 'default' ? [`for ${mode}`] : [])
      ];
      const extraInputs = audioChoices.extraInputs && audioChoices.extraInputs.length > 0 ? audioChoices.extraInputs : [];
      const allSubjects = [...subjects, ...extraInputs];
      const structuredPrompt = buildAudioGenPrompt({
        subjects: allSubjects.length > 0 ? allSubjects : [initialInput],
        actions,
        scenes,
        type: selectedType === 'music' ? 'music' : 'audio'
      });
      setFinalPrompt(structuredPrompt);
      setShowPromptEdit(true);
    } finally {
      setIsLoading(false);
    }
  };

  // handleGenerate 只在 narrative 编辑弹窗点击后调用，生成音频，生成后只显示 Enter Player/Regenerate 按钮
  const handleGenerate = async () => {
    try {
      setIsLoading(true);
      setError(null);
      setShowPromptEdit(false); // 关闭编辑弹窗
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
      const structuredPrompt = buildAudioGenPrompt({
        subjects: allSubjects.length > 0 ? allSubjects : [initialInput],
        actions,
        scenes,
        type: selectedType === 'music' ? 'music' : 'audio'
      });
      const storyPrompt = [
        finalPrompt,
        initialInput,
        structuredPrompt
      ].filter(Boolean).join('\n\n');
      if (mode === 'story') {
        const storyResponse = await fetch('http://localhost:8000/api/create-story', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            prompt: storyPrompt,
            original_description: initialInput || ''
          }),
          signal: abortControllerRef.current.signal,
        });
        if (!storyResponse.ok) {
          const errorData = await storyResponse.json();
          throw new Error(errorData.detail || 'Failed to create story');
        }
        const storyData = await storyResponse.json();
        audioOrMusicUrl = storyData.audio_url;
        setCurrentAudioUrl(storyData.audio_url);
        setMessages((prevMessages) => [
          ...prevMessages,
          { sender: 'ai' as Message['sender'], text: 'Your personalized story with narration and soundscape is ready! What would you like to do?', isUser: false },
        ]);
      } else {
        const audioResponse = await fetch('http://localhost:8001/api/generate-audio', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            description: finalPrompt, // 使用用户编辑后的prompt
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
      }
      
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
      setShowPlaybackButtons(true); // 只显示 Enter Player/Regenerate 按钮
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

  // 恢复 AI 选项 fetch 逻辑，去掉 audio_atmosphere 阶段
  useEffect(() => {
    if (currentStage === 'audio_mood') {
      setIsLoading(true);
      fetch('http://localhost:8000/api/generate-options', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode,
          input: initialInput,
          stage: 'mood',
        }),
      })
        .then(res => res.json())
        .then(data => setMoodOptions(data.options || defaultOptions.audio_mood))
        .catch(() => setMoodOptions(defaultOptions.audio_mood))
        .finally(() => setIsLoading(false));
    }
    if (currentStage === 'audio_elements') {
      setIsLoading(true);
      fetch('http://localhost:8000/api/generate-options', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mode,
          input: initialInput,
          stage: 'elements',
        }),
      })
        .then(res => res.json())
        .then(data => setElementOptions(data.options || defaultOptions.audio_elements))
        .catch(() => setElementOptions(defaultOptions.audio_elements))
        .finally(() => setIsLoading(false));
    }
  }, [currentStage, mode, initialInput]);

  // 添加调试useEffect
  useEffect(() => {
    if (currentStage === 'audio_elements') {
      console.log('Debug - currentStage:', currentStage);
      console.log('Debug - elementOptions:', elementOptions);
      console.log('Debug - audioChoices.audio_elements:', audioChoices.audio_elements);
    }
  }, [currentStage, elementOptions, audioChoices.audio_elements]);

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

  const handleImprovePrompt = async () => {
    // TODO: 实现 AI 改写逻辑
  };

  // 1. 新增：通用 prompt 编辑状态
  // 2. 修改 handleOptionSelect，移除 setShowPromptEdit、setFinalPrompt、setIsPromptGenerated
  // 3. 新增 handleGeneratePrompt 函数
  // 4. 弹窗只在 showPromptEdit 时显示，内容为 finalPrompt，按钮为“Generate Soundscape”按钮和右上角关闭X
  // 5. 选完元素后不再自动 setShowPromptEdit(true)，移除相关逻辑
  // 在 ChatScreen 组件内添加如下 useEffect，确保初始消息和 stage：
  useEffect(() => {
    let introMessage = `Welcome to Nightingale!`;
    if (initialInput) {
      introMessage += ` And you've started with the idea: "${initialInput}".`;
    }
    introMessage += ` What do you want to generate?`;
    setMessages([
      ...(initialInput ? [{ sender: 'user' as const, text: initialInput, isUser: true }] : []),
      { sender: 'ai' as const, text: introMessage, isUser: false },
    ]);
    setCurrentStage('selectType');
    setInputText('');
  }, [initialInput, mode, aiName]);

  // 删除“Edit your soundscape description”相关 UI 和逻辑
  // 删除“Generate Prompt”按钮和 handleGeneratePrompt 相关逻辑
  // showPromptEdit 只在 story mode 下 narrative 编辑时用
  // 1. 删除 showPromptEdit 相关的 soundscape prompt 编辑弹窗
  // 2. 删除 Generate Prompt 按钮
  // 3. 删除 aiEditInput 相关的 AI 改写输入框
  // 4. 删除 handleGeneratePrompt 函数
  // 5. 只保留 story mode 下 narrative 编辑弹窗（mode === 'story' && showPromptEdit）和 story_script_edit 阶段的 narrative 编辑弹窗
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
          Chat with Nightingale
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
      {currentStage === 'selectType' && !showPlaybackButtons && (
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
      {/* story mode 下，audio_elements 阶段显示"Generate Story Script"按钮 */}
      {mode === 'story' && currentStage === 'audio_elements' && !showPromptEdit && !showPlaybackButtons && !isLoading && audioChoices.audio_elements.length > 0 && (
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center', gap: 2 }}>
          <Button
            variant="contained"
            color="primary"
            onClick={handleGenerateStoryScript}
            disabled={isLoading}
            sx={{ minWidth: 180, fontWeight: 700, fontSize: 18 }}
          >
            Generate Story Script
          </Button>
        </Box>
      )}
      {/* 非story模式下，audio_elements 阶段显示"Generate Prompt"按钮 */}
      {mode !== 'story' && currentStage === 'audio_elements' && !showPromptEdit && !showPlaybackButtons && !isLoading && audioChoices.audio_elements.length > 0 && (
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center', gap: 2 }}>
          <Button
            variant="contained"
            color="primary"
            onClick={handleGeneratePrompt}
            disabled={isLoading}
            sx={{ minWidth: 180, fontWeight: 700, fontSize: 18 }}
          >
            Generate Prompt
          </Button>
        </Box>
      )}
      {/* 1. 弹窗部分优化 */}
      {/* 已彻底删除860行左右的 {mode === 'story' && showPromptEdit && (...)} story script 编辑弹窗（含注释和 Box 内容），只保留底部的那一段。 */}
      {mode === 'story' && showPromptEdit && (
        <Box sx={{ mt: 4, p: 3, background: 'rgba(45,156,147,0.06)', borderRadius: 4, border: '1px solid rgba(255,255,255,0.10)' }}>
          <Typography variant="h6" sx={{ mb: 2, color: 'white' }}>Edit your story script</Typography>
          <TextField
            multiline
            minRows={5}
            fullWidth
            value={finalPrompt}
            onChange={e => setFinalPrompt(e.target.value)}
            variant="standard"
            sx={{
              mb: 2,
              background: 'rgba(255,255,255,0.03)',
              borderRadius: 2,
              color: 'white',
              '& .MuiInputBase-input': { color: 'white' },
            }}
            InputProps={{
              style: { color: 'white' },
              disableUnderline: true,
            }}
          />
          <Button
            variant="contained"
            onClick={handleGenerate}
            sx={{ mt: 2, color: 'white', fontWeight: 700, background: 'linear-gradient(90deg, #2d9c93 60%, #3be584 100%)', '&:hover': { background: 'linear-gradient(90deg, #2d9c93 80%, #3be584 100%)' } }}
            fullWidth
          >
            Generate Soundscape
          </Button>
        </Box>
      )}
      {/* 非story模式下，prompt编辑弹窗 */}
      {mode !== 'story' && showPromptEdit && (
        <Box sx={{ mt: 4, p: 3, background: 'rgba(45,156,147,0.06)', borderRadius: 4, border: '1px solid rgba(255,255,255,0.10)' }}>
          <Typography variant="h6" sx={{ mb: 2, color: 'white' }}>Edit your soundscape description</Typography>
          <TextField
            multiline
            minRows={5}
            fullWidth
            value={finalPrompt}
            onChange={e => setFinalPrompt(e.target.value)}
            variant="standard"
            sx={{
              mb: 2,
              background: 'rgba(255,255,255,0.03)',
              borderRadius: 2,
              color: 'white',
              '& .MuiInputBase-input': { color: 'white' },
            }}
            InputProps={{
              style: { color: 'white' },
              disableUnderline: true,
            }}
          />
          <Button
            variant="contained"
            onClick={handleGenerate}
            sx={{ mt: 2, color: 'white', fontWeight: 700, background: 'linear-gradient(90deg, #2d9c93 60%, #3be584 100%)', '&:hover': { background: 'linear-gradient(90deg, #2d9c93 80%, #3be584 100%)' } }}
            fullWidth
          >
            Generate Soundscape
          </Button>
        </Box>
      )}

      {/* 2. 主页面按钮区优化 */}
      {/* story mode 下，audio_elements 有内容时显示“Generate Soundscape”按钮 */}
      {mode === 'story' && currentStage === 'audio_elements' && !showPlaybackButtons && audioChoices.audio_elements.length > 0 && (
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center', gap: 2 }}>
          {/* 删除 Generate Prompt 按钮 */}
        </Box>
      )}
      {/* 只在 showPromptEdit=false 时渲染主按钮区 */}
      {!showPromptEdit && showPlaybackButtons && (
        <Box sx={{ mt: 2, display: 'flex', justifyContent: 'space-between', gap: 2 }}>
          <Button
            variant="outlined"
            color="primary"
            onClick={handleRegenerate}
            sx={{ minWidth: 140, fontWeight: 600 }}
          >
            Regenerate
          </Button>
          <Button
            variant="contained"
            color="primary"
            onClick={() => navigate('/player', {
              state: {
                audioUrl: currentMusicUrl || currentAudioUrl,
                backgroundImageUrl: currentBackgroundImageUrl,
                description: finalPrompt,
              },
            })}
            sx={{ minWidth: 180, fontWeight: 700, fontSize: 18 }}
          >
            Enter Player
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
      {/* story_script_edit 阶段渲染 */}
      {/* 删除 story_script_edit 阶段的编辑弹窗，只保留 showPromptEdit 的弹窗 */}
      {false && currentStage === 'story_script_edit' && (
        <Box sx={{ mt: 4, p: 3, background: 'rgba(45,156,147,0.06)', borderRadius: 4, border: '1px solid rgba(255,255,255,0.10)' }}>
          <Typography variant="h6" sx={{ mb: 2, color: 'white' }}>Edit your story script</Typography>
          <TextField
            multiline
            minRows={5}
            fullWidth
            value={finalPrompt}
            onChange={e => setFinalPrompt(e.target.value)}
            variant="standard"
            sx={{
              mb: 2,
              background: 'rgba(255,255,255,0.03)',
              borderRadius: 2,
              color: 'white',
              '& .MuiInputBase-input': { color: 'white' },
            }}
            InputProps={{
              style: { color: 'white' },
              disableUnderline: true,
            }}
          />
          <Button
            variant="contained"
            onClick={() => { setShowPromptEdit(false); setCurrentStage('confirm'); }}
            sx={{
              mt: 2,
              color: 'white',
              fontWeight: 700,
              background: 'linear-gradient(90deg, #2d9c93 60%, #3be584 100%)',
              '&:hover': { background: 'linear-gradient(90deg, #2d9c93 80%, #3be584 100%)' }
            }}
            fullWidth
          >
            Confirm and continue
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