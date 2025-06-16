import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Slider,
  Paper,
  Button,
  FormControlLabel,
  Switch,
  styled,
  Collapse,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  SkipNext as NextIcon,
  SkipPrevious as PreviousIcon,
  Favorite as FavoriteIcon,
  ArrowBack as ArrowBackIcon,
  Share as ShareIcon,
  Tune as TuneIcon,
  Help as HelpIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const PlayerScreen = styled(Box)(({ theme }) => ({
  height: '100vh',
  display: 'flex',
  flexDirection: 'column',
  background: 'linear-gradient(135deg, #1a2332 0%, #0f1419 100%)',
  position: 'relative',
  overflow: 'visible',
  fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif',
}));

const BackgroundOverlay = styled(Box)({
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  background: 'linear-gradient(180deg, rgba(18, 18, 18, 0.3) 0%, rgba(18, 18, 18, 0.8) 100%)',
  zIndex: 1,
});

const PlayerContent = styled(Box)(({ theme }) => ({
  position: 'relative',
  zIndex: 2,
  padding: theme.spacing(3),
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
}));

const ControlButton = styled(IconButton)(({ theme }) => ({
  width: 48,
  height: 48,
  background: 'rgba(255, 255, 255, 0.05)',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  borderRadius: '50%',
  color: '#ffffff',
  backdropFilter: 'blur(10px)',
  '&:hover': {
    background: 'rgba(255, 255, 255, 0.1)',
  },
}));

const PlayPauseButton = styled(ControlButton)(({ theme }) => ({
  width: 64,
  height: 64,
  background: 'linear-gradient(135deg, #2d9c93 0%, #1a5f5a 100%)',
  border: 'none',
  boxShadow: '0 8px 24px rgba(45, 156, 147, 0.3)',
  '&:hover': {
    background: 'linear-gradient(135deg, #1a5f5a 0%, #2d9c93 100%)',
  },
}));

const ActionButton = styled(Button)(({ theme }) => ({
  flex: 1,
  height: 44,
  background: 'rgba(255, 255, 255, 0.05)',
  border: '1px solid rgba(45, 156, 147, 0.2)',
  borderRadius: '22px',
  color: '#ffffff',
  fontSize: 14,
  fontWeight: 500,
  backdropFilter: 'blur(10px)',
  '&:hover': {
    background: 'rgba(255, 255, 255, 0.1)',
    transform: 'translateY(-1px)',
  },
}));

const VisualizerCanvas = styled('canvas')({
  width: '100%',
  height: '100px',
  background: 'rgba(255, 255, 255, 0.05)',
  borderRadius: '16px',
  marginBottom: '20px',
  border: '1px solid rgba(45, 156, 147, 0.2)',
  backdropFilter: 'blur(10px)',
});

const EffectsPanel = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  background: 'rgba(255, 255, 255, 0.05)',
  backdropFilter: 'blur(10px)',
  borderRadius: '16px',
  marginBottom: theme.spacing(3),
  border: '1px solid rgba(45, 156, 147, 0.2)',
}));

const EffectControl = styled(Box)(({ theme }) => ({
  marginBottom: theme.spacing(2),
  '&:last-child': {
    marginBottom: 0,
  },
}));

interface SoundscapeState {
  rainIntensity: number;
  cafeChatter: number;
  coffeeMachine: number;
  footsteps: number;
}

interface AudioEffect {
  type: 'reverb' | 'echo' | 'fade' | 'volume';
  enabled: boolean;
  params: {
    [key: string]: number;
  };
}

const Player = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { audioUrl: initialAudioUrl } = (location.state as { audioUrl: string | null } | null) || { audioUrl: null };

  const [isPlaying, setIsPlaying] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(initialAudioUrl);
  const [showEffects, setShowEffects] = useState(false);
  const [effects, setEffects] = useState<AudioEffect[]>([
    {
      type: 'reverb',
      enabled: false,
      params: {
        roomSize: 0.5,
        damping: 0.5,
        wetLevel: 0.3,
        dryLevel: 0.7,
      },
    },
    {
      type: 'echo',
      enabled: false,
      params: {
        delay: 300,
        decay: 0.5,
        repeats: 3,
      },
    },
    {
      type: 'fade',
      enabled: false,
      params: {
        fadeIn: 1000,
        fadeOut: 1000,
      },
    },
    {
      type: 'volume',
      enabled: false,
      params: {
        volumeDb: 0,
      },
    },
  ]);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [soundscape, setSoundscape] = useState<SoundscapeState>({
    rainIntensity: 50,
    cafeChatter: 50,
    coffeeMachine: 50,
    footsteps: 50,
  });
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animationFrameRef = useRef<number | undefined>(undefined);
  const [showHelp, setShowHelp] = useState(false);

  useEffect(() => {
    if (!audioRef.current) {
      audioRef.current = new Audio();
      audioRef.current.onended = () => setIsPlaying(false);
    }
    // Ensure audioUrl is set if provided from location.state
    if (initialAudioUrl && audioUrl !== initialAudioUrl) {
      setAudioUrl(initialAudioUrl);
    }
  }, [initialAudioUrl, audioUrl]);

  useEffect(() => {
    let audioContext: AudioContext | null = null;
    let analyser: AnalyserNode | null = null;
    let source: MediaElementAudioSourceNode | null = null;

    if (audioRef.current) {
      try {
        audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        
        source = audioContext.createMediaElementSource(audioRef.current);
        source.connect(analyser);
        analyser.connect(audioContext.destination);

        audioContextRef.current = audioContext;
        analyserRef.current = analyser;
      } catch (error) {
        console.error('Error setting up audio context:', error);
      }
    }

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      
      try {
        if (source) {
          source.disconnect();
        }
        if (analyser) {
          analyser.disconnect();
        }
        if (audioContext && audioContext.state !== 'closed') {
          audioContext.close();
        }
      } catch (error) {
        console.error('Error cleaning up audio resources:', error);
      }
    };
  }, []);

  useEffect(() => {
    if (audioUrl && audioRef.current) {
      audioRef.current.src = audioUrl;
      if (isPlaying) {
        audioRef.current.play().catch(e => console.error("Error playing audio:", e));
      }
    }
  }, [audioUrl, isPlaying]);

  const handlePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play().catch(e => console.error("Error playing audio:", e));
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleFavorite = () => {
    setIsFavorite(!isFavorite);
  };

  const handleSliderChange = (name: keyof SoundscapeState) => (event: Event, value: number | number[]) => {
    setSoundscape({ ...soundscape, [name]: value as number });
  };

  const drawVisualizer = () => {
    if (!canvasRef.current || !analyserRef.current) return;

    const canvas = canvasRef.current;
    const canvasCtx = canvas.getContext('2d');
    if (!canvasCtx) return;

    const WIDTH = canvas.width;
    const HEIGHT = canvas.height;

    const draw = () => {
      animationFrameRef.current = requestAnimationFrame(draw);

      const bufferLength = analyserRef.current!.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);
      analyserRef.current!.getByteFrequencyData(dataArray);

      canvasCtx.fillStyle = 'rgba(0, 0, 0, 0.2)';
      canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);

      const barWidth = (WIDTH / bufferLength) * 2.5;
      let barHeight;
      let x = 0;

      for (let i = 0; i < bufferLength; i++) {
        barHeight = dataArray[i] / 2;

        const gradient = canvasCtx.createLinearGradient(0, HEIGHT, 0, 0);
        gradient.addColorStop(0, '#2d9c93');
        gradient.addColorStop(1, '#1a5f5a');
        
        canvasCtx.fillStyle = gradient;
        canvasCtx.fillRect(x, HEIGHT - barHeight, barWidth, barHeight);

        x += barWidth + 1;
      }
    };

    draw();
  };

  useEffect(() => {
    if (isPlaying) {
      drawVisualizer();
    } else if (animationFrameRef.current) {
      cancelAnimationFrame(animationFrameRef.current);
    }
  }, [isPlaying]);

  const handleEffectToggle = (index: number) => {
    const newEffects = [...effects];
    newEffects[index].enabled = !newEffects[index].enabled;
    setEffects(newEffects);
  };

  const handleEffectParamChange = (effectIndex: number, paramName: string, value: number) => {
    const newEffects = [...effects];
    newEffects[effectIndex].params[paramName] = value;
    setEffects(newEffects);
  };

  const renderEffectControls = () => (
    <EffectsPanel>
      <Typography variant="h6" sx={{ color: 'white', mb: 2 }}>
        音频效果
      </Typography>
      {effects.map((effect, index) => (
        <EffectControl key={effect.type}>
          <FormControlLabel
            control={
              <Switch
                checked={effect.enabled}
                onChange={() => handleEffectToggle(index)}
                color="primary"
              />
            }
            label={
              <Typography sx={{ color: 'white' }}>
                {effect.type === 'reverb' && '混响'}
                {effect.type === 'echo' && '回声'}
                {effect.type === 'fade' && '淡入淡出'}
                {effect.type === 'volume' && '音量'}
              </Typography>
            }
          />
          {effect.enabled && (
            <Box sx={{ pl: 4 }}>
              {Object.entries(effect.params).map(([param, value]) => (
                <Box key={param} sx={{ mb: 1 }}>
                  <Typography variant="body2" sx={{ color: 'white' }}>
                    {param === 'roomSize' && '房间大小'}
                    {param === 'damping' && '阻尼'}
                    {param === 'wetLevel' && '湿信号'}
                    {param === 'dryLevel' && '干信号'}
                    {param === 'delay' && '延迟'}
                    {param === 'decay' && '衰减'}
                    {param === 'repeats' && '重复次数'}
                    {param === 'fadeIn' && '淡入时间'}
                    {param === 'fadeOut' && '淡出时间'}
                    {param === 'volumeDb' && '音量'}
                  </Typography>
                  <Slider
                    value={value}
                    onChange={(_, newValue) => handleEffectParamChange(index, param, newValue as number)}
                    min={0}
                    max={1}
                    step={0.01}
                    sx={{ color: 'gold' }}
                  />
                </Box>
              ))}
            </Box>
          )}
        </EffectControl>
      ))}
    </EffectsPanel>
  );

  return (
    <PlayerScreen>
      <BackgroundOverlay />
      <PlayerContent>
        <Box sx={{ 
          position: 'absolute', 
          top: 20, 
          left: 20, 
          display: 'flex', 
          gap: 2 
        }}>
          <IconButton
            onClick={() => navigate(-1)}
            sx={{ 
              color: 'white',
              background: 'rgba(255, 255, 255, 0.05)',
              backdropFilter: 'blur(10px)',
              '&:hover': {
                background: 'rgba(255, 255, 255, 0.1)',
              },
            }}
          >
            <ArrowBackIcon />
          </IconButton>
          <IconButton
            onClick={() => setShowHelp(true)}
            sx={{ 
              color: 'white',
              background: 'rgba(255, 255, 255, 0.05)',
              backdropFilter: 'blur(10px)',
              '&:hover': {
                background: 'rgba(255, 255, 255, 0.1)',
              },
            }}
          >
            <HelpIcon />
          </IconButton>
        </Box>

        <Box sx={{ textAlign: 'center', mb: 5 }}>
          <Typography 
            variant="h4" 
            sx={{ 
              color: 'white', 
              fontWeight: 700, 
              mb: 1,
              letterSpacing: '-0.02em',
            }}
          >
            场景氛围师
          </Typography>
          <Typography 
            variant="body1" 
            sx={{ 
              color: 'rgba(255, 255, 255, 0.7)',
              fontSize: '14px',
              lineHeight: 1.4,
            }}
          >
            将你的意境转化为沉浸式音景
          </Typography>
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 3, mb: 5 }}>
          <ControlButton>
            <PreviousIcon />
          </ControlButton>
          <PlayPauseButton onClick={handlePlayPause}>
            {isPlaying ? <PauseIcon /> : <PlayIcon />}
          </PlayPauseButton>
          <ControlButton>
            <NextIcon />
          </ControlButton>
        </Box>

        <Box sx={{ width: '100%', mb: 4 }}>
          <VisualizerCanvas ref={canvasRef} width={800} height={100} />
          
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
            <Button
              startIcon={<TuneIcon />}
              onClick={() => setShowEffects(!showEffects)}
              sx={{
                color: 'white',
                borderColor: 'rgba(45, 156, 147, 0.2)',
                background: 'rgba(255, 255, 255, 0.05)',
                backdropFilter: 'blur(10px)',
                borderRadius: '22px',
                '&:hover': {
                  background: 'rgba(255, 255, 255, 0.1)',
                  borderColor: 'rgba(45, 156, 147, 0.3)',
                },
              }}
              variant="outlined"
            >
              {showEffects ? '隐藏效果' : '显示效果'}
            </Button>
          </Box>
          
          <Collapse in={showEffects}>
            {renderEffectControls()}
          </Collapse>
          
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" sx={{ color: 'white' }}>Rain Intensity</Typography>
              <Typography variant="body2" sx={{ color: 'gold' }}>{soundscape.rainIntensity}%</Typography>
            </Box>
            <Slider
              value={soundscape.rainIntensity}
              onChange={handleSliderChange('rainIntensity')}
              sx={{ color: 'gold' }}
            />
          </Box>
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" sx={{ color: 'white' }}>Café Chatter</Typography>
              <Typography variant="body2" sx={{ color: 'gold' }}>{soundscape.cafeChatter}%</Typography>
            </Box>
            <Slider
              value={soundscape.cafeChatter}
              onChange={handleSliderChange('cafeChatter')}
              sx={{ color: 'gold' }}
            />
          </Box>
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" sx={{ color: 'white' }}>Coffee Machine</Typography>
              <Typography variant="body2" sx={{ color: 'gold' }}>{soundscape.coffeeMachine}%</Typography>
            </Box>
            <Slider
              value={soundscape.coffeeMachine}
              onChange={handleSliderChange('coffeeMachine')}
              sx={{ color: 'gold' }}
            />
          </Box>
          <Box sx={{ mb: 2 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
              <Typography variant="body2" sx={{ color: 'white' }}>Footsteps</Typography>
              <Typography variant="body2" sx={{ color: 'gold' }}>{soundscape.footsteps}%</Typography>
            </Box>
            <Slider
              value={soundscape.footsteps}
              onChange={handleSliderChange('footsteps')}
              sx={{ color: 'gold' }}
            />
          </Box>
        </Box>

        <Box sx={{ display: 'flex', gap: 2, width: '100%' }}>
          <ActionButton startIcon={<FavoriteIcon />}>
            Save to Favorites
          </ActionButton>
          <ActionButton startIcon={<ShareIcon />}>
            Share
          </ActionButton>
        </Box>

        <Dialog
          open={showHelp}
          onClose={() => setShowHelp(false)}
          PaperProps={{
            sx: {
              background: 'rgba(18, 18, 18, 0.95)',
              backdropFilter: 'blur(10px)',
              borderRadius: '16px',
              border: '1px solid rgba(45, 156, 147, 0.2)',
            },
          }}
        >
          <DialogTitle sx={{ color: 'white' }}>使用帮助</DialogTitle>
          <DialogContent>
            <Typography sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 2 }}>
              在这里你可以：
            </Typography>
            <Typography sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
              1. 播放/暂停音景
            </Typography>
            <Typography sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
              2. 调整各个音效的音量
            </Typography>
            <Typography sx={{ color: 'rgba(255, 255, 255, 0.7)', mb: 1 }}>
              3. 添加音频效果（混响、回声等）
            </Typography>
            <Typography sx={{ color: 'rgba(255, 255, 255, 0.7)' }}>
              4. 保存或分享你的音景
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button
              onClick={() => setShowHelp(false)}
              sx={{ color: '#2d9c93' }}
            >
              知道了
            </Button>
          </DialogActions>
        </Dialog>
      </PlayerContent>
    </PlayerScreen>
  );
};

export default Player; 