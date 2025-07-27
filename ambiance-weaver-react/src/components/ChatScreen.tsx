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

// 多mode定制文案
const moodQuestions: Record<string, string> = {
  focus: 'What kind of focus do you want? (e.g. deep, alert, calm)',
  creative: 'What creative mood do you want to inspire? (e.g. playful, energetic, dreamy)',
  mindful: 'What kind of calm or peace do you seek? (e.g. serene, meditative, gentle)',
  sleep: 'What kind of sleep environment do you prefer? (e.g. quiet, cozy, gentle)',
  asmr: 'What kind of ASMR feeling do you want to evoke? (e.g. tingling, relaxing, satisfying)',
  story: 'What kind of mood or feeling do you want to evoke?',
  default: 'What kind of mood or feeling do you want to evoke?'
};
const elementQuestions: Record<string, string> = {
  focus: 'Select sounds that help you concentrate (max 3):',
  creative: 'Select elements that spark creativity (max 3):',
  mindful: 'Select soothing elements (max 3):',
  sleep: 'Select sounds that help you sleep (max 3):',
  asmr: 'Select ASMR triggers (max 3):',
  story: 'Select sound elements (max 3):',
  default: 'Select sound elements (max 3):'
};

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
  width: 64,
  height: 64,
  borderRadius: '50%',
  overflow: 'hidden',
  flexShrink: 0,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  marginRight: theme.spacing(2),
  backgroundColor: 'rgba(45, 156, 147, 0.2)',
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
  fontSize: '1.1rem',
  fontWeight: 500,
  letterSpacing: 0.1,
  lineHeight: 1.5,
  fontFamily: 'inherit',
  padding: 0,
  minHeight: 0,
  minWidth: '96px',
  borderRadius: '22px',
  height: '44px',
  paddingLeft: '24px',
  paddingRight: '24px',
  [theme.breakpoints.up('md')]: {
    fontSize: '1.3rem',
    borderRadius: '28px',
    height: '56px',
    minWidth: '120px',
    paddingLeft: '32px',
    paddingRight: '32px',
  },
  [theme.breakpoints.up('lg')]: {
    fontSize: '1.5rem',
    borderRadius: '32px',
    height: '64px',
    minWidth: '150px',
    paddingLeft: '40px',
    paddingRight: '40px',
  },
  '& .MuiChip-label': {
    fontSize: '1.1rem !important',
    fontWeight: 500,
    letterSpacing: 0.1,
    lineHeight: 1.5,
    fontFamily: 'inherit',
    padding: 0,
    minHeight: 0,
    minWidth: 0,
    [theme.breakpoints.up('md')]: {
      fontSize: '1.3rem !important',
    },
    [theme.breakpoints.up('lg')]: {
      fontSize: '1.5rem !important',
    },
  },
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

  // 静态音乐选项
  useEffect(() => {
    setMusicGenreOptions(['Ambient', 'Classical', 'Jazz', 'Electronic', 'Pop', 'Rock', 'Cinematic', 'Folk', 'Lo-fi', 'World']);
    setMusicInstrumentOptions(['Piano', 'Guitar', 'Synth', 'Drums', 'Violin', 'Flute', 'Bass', 'Strings', 'Brass', 'Percussion']);
    setMusicTempoOptions(['Slow', 'Medium', 'Fast', 'Variable']);
    setMusicUsageOptions(['Background', 'Focus', 'Relaxation', 'Party', 'Workout', 'Meditation', 'Study', 'Sleep']);
  }, []);

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
      if (type === 'music_genre') {
        newChoices.genre = option;
        setCurrentStage('music_tempo');
      } else if (type === 'music_tempo') {
        newChoices.tempo = option;
        setCurrentStage('music_instruments');
      } else if (type === 'music_instruments') {
        if (newChoices.instruments.includes(option)) {
          newChoices.instruments = newChoices.instruments.filter((item) => item !== option);
        } else {
          if (newChoices.instruments.length < 3) {
            newChoices.instruments = [...newChoices.instruments, option];
          }
        }
        // 不自动进入下一阶段
      }
      return newChoices;
    });
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

  // AI聊天编辑prompt的函数
  const handleAiEdit = async () => {
    if (!aiEditInput.trim() || isLoading) return;
    
    setIsLoading(true);
    try {
      // 区分story模式和非story模式
      const isStory = mode === 'story';
      const contentType = isStory ? 'narrative' : 'prompt';
      
      const response = await fetch('http://localhost:8000/api/edit-prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          current_prompt: finalPrompt,
          edit_instruction: aiEditInput,
          mode: mode,
          is_story: isStory,
          content_type: contentType
        }),
      });
      
      if (!response.ok) {
        throw new Error('Failed to edit prompt');
      }
      
      const data = await response.json();
      setFinalPrompt(data.edited_prompt);
      setAiEditInput(''); // 清空输入框
      
      // 添加用户消息到聊天记录
      setMessages((prev) => [
        ...prev,
        { sender: 'user', text: aiEditInput, isUser: true },
        { sender: 'ai', text: `I've updated your ${contentType}: "${data.edited_prompt}"`, isUser: false }
      ]);
      
    } catch (error) {
      console.error('Error editing prompt:', error);
      // 如果API调用失败，使用简单的文本替换作为fallback
      const lowerInstruction = aiEditInput.toLowerCase();
      let editedPrompt = finalPrompt;
      
      if (lowerInstruction.includes('shorter') || lowerInstruction.includes('shorten')) {
        editedPrompt = finalPrompt.split('.').slice(0, 2).join('.') + '.';
      } else if (lowerInstruction.includes('longer') || lowerInstruction.includes('expand')) {
        editedPrompt = finalPrompt + ' with more detailed atmospheric elements.';
      } else if (lowerInstruction.includes('poetic') || lowerInstruction.includes('poetry')) {
        editedPrompt = finalPrompt.replace(/\./g, ', like poetry in motion.');
      } else if (lowerInstruction.includes('dramatic') || lowerInstruction.includes('intense')) {
        editedPrompt = finalPrompt + ' with heightened dramatic tension.';
      }
      
      setFinalPrompt(editedPrompt);
      setAiEditInput('');
      
      const contentType = mode === 'story' ? 'narrative' : 'description';
      setMessages((prev) => [
        ...prev,
        { sender: 'user', text: aiEditInput, isUser: true },
        { sender: 'ai', text: `I've updated your ${contentType}: "${editedPrompt}"`, isUser: false }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  // 非story模式下生成prompt的函数
  const handleGeneratePrompt = async () => {
    setIsLoading(true);
    try {
      // 收集参数
      const userInput = initialInput;
      const mood = audioChoices.audio_mood || '';
      const elements = audioChoices.audio_elements;
      // 调用后端LLM生成自然语言prompt
      const res = await fetch('http://localhost:8000/api/generate-prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_input: userInput,
          mood: mood,
          elements: elements,
          mode: mode
        })
      });
      if (!res.ok) {
        throw new Error('Failed to generate prompt');
      }
      const data = await res.json();
      setFinalPrompt(data.prompt || '');
      setShowPromptEdit(true); // 显示编辑弹窗
    } catch (error) {
      console.error('Error generating prompt:', error);
      setFinalPrompt('');
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
        type: selectedType === 'music' ? 'music' : 'audio',
        mode: mode
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
        // 结合用户编辑的prompt和结构化prompt
        const combinedPrompt = finalPrompt ? `${finalPrompt}, ${structuredPrompt}` : structuredPrompt;
        
        const audioResponse = await fetch('http://localhost:8001/api/generate-audio', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            description: combinedPrompt, // 使用结合后的prompt
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

  const handleGenerateStoryMusic = async () => {
    try {
      setIsLoading(true);
      setError(null);
      setShowPromptEdit(false);
      abortControllerRef.current = new AbortController();

      // 旁白内容：用户在AI编辑弹窗中编辑的内容
      const narrative = finalPrompt;

      // 1. 先用musicChoices和initialInput生成music prompt（调用后端）
      let musicPrompt = '';
      try {
        const res = await fetch('http://localhost:8000/api/music-prompt', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            genre: musicChoices.genre,
            tempo: musicChoices.tempo,
            instruments: musicChoices.instruments,
            usage: mode,
            input: initialInput,
          }),
        });
        const data = await res.json();
        musicPrompt = data.prompt || '';
      } catch (e) {
        musicPrompt = '';
      }

      // 2. 生成story+music
      const res = await fetch('http://localhost:8000/api/create-story-music', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          narrative,
          music_prompt: musicPrompt,
          duration: 30,
        }),
        signal: abortControllerRef.current.signal,
      });
      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.detail || 'Failed to generate story music');
      }
      const data = await res.json();
      setCurrentMusicUrl(data.audio_url);
      setFinalPrompt(data.narrative_script || narrative);
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: 'ai', text: 'Your personalized story with music is ready! What would you like to do?', isUser: false },
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
          { sender: 'ai' as Message['sender'], text: `Error generating story music: ${err instanceof Error ? err.message : 'An unknown error occurred'}.`, isUser: false },
        ]);
        console.error('Error generating story music:', err);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateMusicPrompt = async () => {
    setIsLoading(true);
    try {
      // 生成音乐描述prompt，usage直接用mode
      const res = await fetch('http://localhost:8000/api/music-prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          genre: musicChoices.genre,
          tempo: musicChoices.tempo,
          instruments: musicChoices.instruments,
          usage: mode, // 直接用mode
          input: initialInput,
        }),
      });
      const data = await res.json();
      setFinalPrompt(data.prompt || '');
      setShowPromptEdit(true); // 显示编辑弹窗
    } catch (error) {
      console.error('Error generating music prompt:', error);
      setFinalPrompt('');
      setShowPromptEdit(true);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerateMusic = async () => {
    setShowPromptEdit(false); // 立即关闭编辑弹窗，与audio mode一致
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
    // asmr模式直接跳到audio_elements阶段
    if (mode === 'asmr') {
      setCurrentStage('audio_elements');
      setSelectedType('audio');
    } else {
      setCurrentStage('selectType');
    }
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
        <IconButton onClick={() => {
          if (isLoading && abortControllerRef.current) {
            abortControllerRef.current.abort();
          }
          navigate(-1);
        }} sx={{ color: uiSystem.colors.white, p: 0, mr: 2 }}>
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
                <img src={`${process.env.PUBLIC_URL}/ai_logo.png`} alt="AI Logo" style={{ width: 56, height: 56, objectFit: 'contain' }} />
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
              <img src={`${process.env.PUBLIC_URL}/ai_logo.png`} alt="AI Logo" style={{ width: 56, height: 56, objectFit: 'contain' }} />
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
      {currentStage === 'selectType' && !showPlaybackButtons && !showPromptEdit && mode !== 'asmr' && (
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
      {currentStage === 'audio_mood' && !isLoading && !showPlaybackButtons && !showPromptEdit && (
        <OptionMessageBubbleContent sx={{ mt: 2 }}>
          <Typography variant="body1" sx={{ mb: 1 }}>
            {moodQuestions[mode] || moodQuestions.default}
          </Typography>
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
      {currentStage === 'audio_elements' && !isLoading && !showPlaybackButtons && !showPromptEdit && (
        <OptionMessageBubbleContent sx={{ mt: 2 }}>
          <Typography variant="body1" sx={{ mb: 1 }}>
            {elementQuestions[mode] || elementQuestions.default}
          </Typography>
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
      {/* Story模式下的AI编辑弹窗 */}
      {mode === 'story' && showPromptEdit && (
        <Box sx={{ mt: 4, p: 3, background: 'rgba(45,156,147,0.06)', borderRadius: 4, border: '1px solid rgba(255,255,255,0.10)' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ color: 'white' }}>Edit your story narrative</Typography>
            <IconButton
              onClick={() => {
                setShowPromptEdit(false);
                // 完全重置，回到选择Background Sound/Music阶段
                setCurrentStage('selectType');
                setSelectedType(null);
                setAudioChoices({ audio_elements: [], extraInputs: [] });
                setMusicChoices({ instruments: [] });
                setFinalPrompt('');
                setAiEditInput('');
                setMessages([]);
              }}
              sx={{ color: 'white', '&:hover': { color: '#2d9c93' } }}
            >
              <CloseIcon />
            </IconButton>
          </Box>
          
          {/* 聊天编辑区域 */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" sx={{ mb: 1, color: 'white', opacity: 0.8 }}>
              Chat with AI to edit your story, or edit directly below:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <TextField
                size="small"
                placeholder="Try: 'make it shorter', 'add more emotion', 'make it more dramatic'..."
                value={aiEditInput}
                onChange={(e) => setAiEditInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAiEdit()}
                variant="outlined"
                sx={{
                  flex: 1,
                  '& .MuiOutlinedInput-root': {
                    color: 'white',
                    '& fieldset': {
                      borderColor: 'rgba(255,255,255,0.3)',
                    },
                    '&:hover fieldset': {
                      borderColor: 'rgba(255,255,255,0.5)',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#2d9c93',
                    },
                  },
                  '& .MuiInputBase-input': { 
                    color: 'white',
                    '&::placeholder': { 
                      color: 'rgba(255,255,255,0.5)',
                      opacity: 1,
                    },
                  },
                }}
              />
              <Button
                variant="contained"
                onClick={handleAiEdit}
                disabled={!aiEditInput.trim() || isLoading}
                sx={{ 
                  minWidth: 80, 
                  background: 'linear-gradient(135deg, #2d9c93 0%, #1a5f5a 100%)',
                  '&:hover': { background: 'linear-gradient(135deg, #1a5f5a 0%, #2d9c93 100%)' }
                }}
              >
                {isLoading ? 'Editing...' : 'Edit'}
              </Button>
            </Box>
          </Box>
          
          {/* 直接编辑区域 */}
          <Typography variant="body2" sx={{ mb: 1, color: 'white', opacity: 0.8 }}>
            Or edit your story directly:
          </Typography>
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
      {/* 非story模式下的AI编辑弹窗 */}
      {mode !== 'story' && showPromptEdit && (
        <Box sx={{ mt: 4, p: 3, background: 'rgba(45,156,147,0.06)', borderRadius: 4, border: '1px solid rgba(255,255,255,0.10)' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ color: 'white' }}>
              {selectedType === 'music' ? 'Edit your music description' : 'Edit your soundscape description'}
            </Typography>
            <IconButton
              onClick={() => {
                setShowPromptEdit(false);
                // 完全重置，回到选择Background Sound/Music阶段
                setCurrentStage('selectType');
                setSelectedType(null);
                setAudioChoices({ audio_elements: [], extraInputs: [] });
                setMusicChoices({ instruments: [] });
                setFinalPrompt('');
                setAiEditInput('');
                setMessages([]);
              }}
              sx={{ color: 'white', '&:hover': { color: '#2d9c93' } }}
            >
              <CloseIcon />
            </IconButton>
          </Box>
          
          {/* 聊天编辑区域 */}
          <Box sx={{ mb: 3 }}>
            <Typography variant="body2" sx={{ mb: 1, color: 'white', opacity: 0.8 }}>
              Chat with AI to edit your description, or edit directly below:
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <TextField
                size="small"
                placeholder="Try: 'make it shorter', 'add more details', 'make it more poetic'..."
                value={aiEditInput}
                onChange={(e) => setAiEditInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleAiEdit()}
                variant="outlined"
                sx={{
                  flex: 1,
                  '& .MuiOutlinedInput-root': {
                    color: 'white',
                    '& fieldset': {
                      borderColor: 'rgba(255,255,255,0.3)',
                    },
                    '&:hover fieldset': {
                      borderColor: 'rgba(255,255,255,0.5)',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#2d9c93',
                    },
                  },
                  '& .MuiInputBase-input': { 
                    color: 'white',
                    '&::placeholder': { 
                      color: 'rgba(255,255,255,0.5)',
                      opacity: 1,
                    },
                  },
                }}
              />
              <Button
                variant="contained"
                onClick={handleAiEdit}
                disabled={!aiEditInput.trim() || isLoading}
                sx={{ 
                  minWidth: 80, 
                  background: 'linear-gradient(135deg, #2d9c93 0%, #1a5f5a 100%)',
                  '&:hover': { background: 'linear-gradient(135deg, #1a5f5a 0%, #2d9c93 100%)' }
                }}
              >
                {isLoading ? 'Editing...' : 'Edit'}
              </Button>
            </Box>
          </Box>
          
          {/* 直接编辑区域 */}
          <Typography variant="body2" sx={{ mb: 1, color: 'white', opacity: 0.8 }}>
            Or edit directly:
          </Typography>
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
            onClick={
              mode === 'story' && selectedType === 'music'
                ? handleGenerateStoryMusic
                : selectedType === 'music'
                  ? handleGenerateMusic
                  : handleGenerate
            }
            sx={{ mt: 2, color: 'white', fontWeight: 700, background: 'linear-gradient(90deg, #2d9c93 60%, #3be584 100%)', '&:hover': { background: 'linear-gradient(90deg, #2d9c93 80%, #3be584 100%)' } }}
            fullWidth
          >
            {mode === 'story' && selectedType === 'music'
              ? 'Generate Story + Music'
              : selectedType === 'music'
                ? 'Generate Music'
                : 'Generate Soundscape'}
          </Button>
        </Box>
      )}

      {/* 2. 主页面按钮区优化 */}
      {/* story mode 下，audio_elements 有内容时显示“Generate Soundscape”按钮 */}
      {mode === 'story' && currentStage === 'audio_elements' && !showPlaybackButtons && !showPromptEdit && audioChoices.audio_elements.length > 0 && (
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
      {currentStage === 'music_genre' && !isLoading && !showPlaybackButtons && !showPromptEdit && (
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
      {currentStage === 'music_instruments' && !isLoading && !showPlaybackButtons && !showPromptEdit && (
        <>
          <OptionMessageBubbleContent sx={{ mt: 2 }}>
            <Typography variant="body1" sx={{ mb: 1 }}>Pick up to 3 instruments:</Typography>
            <Stack direction="row" flexWrap="wrap" spacing={1}>
              {musicInstrumentOptions.map((option) => {
                const selected = musicChoices.instruments.includes(option);
                const disabled = !selected && musicChoices.instruments.length >= 3;
                return (
                  <OptionChip
                    key={option}
                    label={option}
                    onClick={() => !disabled && handleOptionSelect(option, 'music_instruments')}
                    variant={selected ? 'filled' : 'outlined'}
                    color={selected ? 'primary' : 'default'}
                    disabled={disabled}
                    sx={disabled ? { opacity: 0.5, pointerEvents: 'none' } : {}}
                  />
                );
              })}
            </Stack>
          </OptionMessageBubbleContent>
          {musicChoices.instruments.length > 0 && (
            <Box sx={{ mt: 2, display: 'flex', justifyContent: 'center', gap: 2 }}>
              <Button
                variant="contained"
                onClick={async () => {
                  if (mode === 'story') {
                    setIsLoading(true);
                    try {
                      const res = await fetch('http://localhost:8000/api/generate-scene', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                          prompt: initialInput,
                          mode: 'story',
                          // 这里可以根据需要传musicChoices参数
                          genre: musicChoices.genre,
                          tempo: musicChoices.tempo,
                          instruments: musicChoices.instruments,
                        }),
                      });
                      const data = await res.json();
                      setFinalPrompt(data.narrative_script || '');
                      setShowPromptEdit(true);
                    } catch (e) {
                      setFinalPrompt('');
                      setShowPromptEdit(true);
                    } finally {
                      setIsLoading(false);
                    }
                  } else {
                    handleGenerateMusicPrompt(); // 非story模式走原逻辑
                  }
                }}
                disabled={isLoading || musicChoices.instruments.length === 0}
                sx={{ minWidth: 180, fontWeight: 700, fontSize: 18 }}
              >
                Generate
              </Button>
            </Box>
          )}
        </>
      )}
      {currentStage === 'music_tempo' && !isLoading && !showPlaybackButtons && !showPromptEdit && (
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
      {/* 移除music_usage相关UI和逻辑 */}
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
   
      {/* 删除底部聊天框 - 不再需要 */}
      {/* 原来的聊天框代码已删除，因为现在使用引导式流程和AI编辑弹窗 */}
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