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
  VolumeUp as VolumeUpIcon,
  VolumeOff as VolumeOffIcon,
  MusicNote as MusicNoteIcon,
  Image as ImageIcon,
  HelpOutline as HelpOutlineIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useAiName } from '../utils/AiNameContext';

interface PlayerScreenProps {
  backgroundImageUrl?: string;
}

const PlayerScreen = styled(Box)<PlayerScreenProps>(({ theme, backgroundImageUrl }) => ({
  height: '100vh',
  display: 'flex',
  flexDirection: 'column',
  position: 'relative',
  overflow: 'visible',
  fontFamily: '-apple-system, BlinkMacSystemFont, "SF Pro Display", sans-serif',
  background: `url(${backgroundImageUrl || `${process.env.PUBLIC_URL}/cover.png`}) no-repeat center center fixed`,
  backgroundSize: 'cover',
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
}));

const BackgroundOverlay = styled(Box)({
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  zIndex: 1,
});

const PlayerContent = styled(Box)(({ theme }) => ({
  position: 'relative',
  zIndex: 2,
  padding: theme.spacing(3),
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'space-between',
  background: 'rgba(255, 255, 255, 0.05)',
  backdropFilter: 'blur(10px)',
  borderRadius: '16px',
  border: '1px solid rgba(255, 255, 255, 0.1)',
  maxWidth: '90%',
  width: '100%',
  margin: '0 auto',
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

const EffectsPanel = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(3),
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

interface PlayerProps {
  audioUrl: string;
  description: string;
  onGenerateMusic?: () => void;
  onGenerateBackground?: () => void;
  backgroundImageUrl?: string;
  musicUrl?: string;
}

const Player: React.FC<PlayerProps> = ({
  audioUrl,
  description,
  onGenerateMusic,
  onGenerateBackground,
  backgroundImageUrl,
  musicUrl
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { audioUrl: stateAudioUrl, backgroundImageUrl: stateBackgroundImageUrl } = location.state || {};
  
  const currentAudioUrl = audioUrl || stateAudioUrl;
  const currentBackgroundImageUrl = backgroundImageUrl || stateBackgroundImageUrl;

  const { aiName } = useAiName();

  const [isPlaying, setIsPlaying] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);
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
  const [showHelp, setShowHelp] = useState(false);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [duration, setDuration] = useState(0);
  const [currentTime, setCurrentTime] = useState(0);
  const [isMusicPlaying, setIsMusicPlaying] = useState(false);
  
  const musicRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    if (!audioRef.current) {
      audioRef.current = new Audio();
      audioRef.current.onended = () => setIsPlaying(false);
    }
  }, []);

  useEffect(() => {
    if (audioRef.current && currentAudioUrl) {
      if (audioRef.current.src !== currentAudioUrl) {
        audioRef.current.src = currentAudioUrl;
        audioRef.current.load();
      }

      if (isPlaying) {
        audioRef.current.play();
      } else {
        audioRef.current.pause();
      }
    }
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
      }
    };
  }, [currentAudioUrl, isPlaying]);

  useEffect(() => {
    if (musicRef.current) {
      musicRef.current.src = musicUrl || '';
      if (isMusicPlaying) {
        musicRef.current.play();
      } else {
        musicRef.current.pause();
      }
    }
    return () => {
      if (musicRef.current) {
        musicRef.current.pause();
      }
    };
  }, [musicUrl, isMusicPlaying]);

  useEffect(() => {
    if (audioRef.current) {
      audioRef.current.volume = isMuted ? 0 : volume;
    }
    if (musicRef.current) {
      musicRef.current.volume = isMuted ? 0 : volume;
    }
  }, [volume, isMuted]);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleFavorite = () => {
    setIsFavorite(!isFavorite);
  };

  const handleSliderChange = (name: keyof SoundscapeState) => (event: Event, value: number | number[]) => {
    setSoundscape((prev) => ({ ...prev, [name]: value as number }));
  };

  const handleEffectToggle = (index: number) => {
    setEffects((prev) =>
      prev.map((effect, i) => (i === index ? { ...effect, enabled: !effect.enabled } : effect))
    );
  };

  const handleEffectParamChange = (effectIndex: number, paramName: string, value: number) => {
    setEffects((prev) =>
      prev.map((effect, i) =>
        i === effectIndex
          ? { ...effect, params: { ...effect.params, [paramName]: value } }
          : effect
      )
    );
  };

  const renderEffectControls = () => (
    <EffectsPanel>
      {effects.map((effect, index) => (
        <EffectControl key={effect.type}>
          <FormControlLabel
            control={
              <Switch
                checked={effect.enabled}
                onChange={() => handleEffectToggle(index)}
                sx={{
                  '& .MuiSwitch-switchBase.Mui-checked': {
                    color: '#2d9c93',
                    '&:hover': {
                      backgroundColor: 'rgba(45, 156, 147, 0.08)',
                    },
                  },
                  '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                    backgroundColor: '#2d9c93',
                  },
                }}
              />
            }
            label={<Typography sx={{ color: '#ffffff' }}>{effect.type}</Typography>}
          />
          <Collapse in={effect.enabled}>
            <Box sx={{ pl: 4, pt: 1 }}>
              {Object.entries(effect.params).map(([paramName, paramValue]) => (
                <EffectControl key={paramName}>
                  <Typography sx={{ color: '#ffffff', fontSize: 12 }}>{paramName}: {paramValue}</Typography>
                  <Slider
                    value={paramValue}
                    onChange={(e, v) => handleEffectParamChange(index, paramName, v as number)}
                    min={0}
                    max={1}
                    step={0.1}
                    sx={{
                      color: '#2d9c93',
                      '& .MuiSlider-thumb': {
                        width: 16,
                        height: 16,
                        backgroundColor: '#ffffff',
                        border: '2px solid currentColor',
                        '&:focus, &:hover, &.Mui-active': {
                          boxShadow: 'inherit',
                        },
                      },
                      '& .MuiSlider-rail': {
                        opacity: 0.5,
                        backgroundColor: '#bfbfbf',
                      },
                    }}
                  />
                </EffectControl>
              ))}
            </Box>
          </Collapse>
        </EffectControl>
      ))}
    </EffectsPanel>
  );

  const handleMusicPlayPause = () => {
    setIsMusicPlaying(!isMusicPlaying);
  };

  const handleVolumeChange = (event: Event, newValue: number | number[]) => {
    setVolume(newValue as number);
  };

  const handleMute = () => {
    setIsMuted(!isMuted);
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (audioRef.current) {
      setDuration(audioRef.current.duration);
    }
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;
  };

  const handleSeek = (event: Event, newValue: number | number[]) => {
    if (audioRef.current) {
      audioRef.current.currentTime = newValue as number;
      setCurrentTime(newValue as number);
    }
  };

  return (
    <PlayerScreen backgroundImageUrl={currentBackgroundImageUrl}>
      <BackgroundOverlay />
      <Box
        sx={{
          position: 'relative',
          zIndex: 2,
          flexGrow: 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: 3,
          width: '100%',
        }}
      >
        {/* Main Content Card */}
        <PlayerContent
          sx={{
            flexGrow: 1,
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'center',
            alignItems: 'center',
            maxWidth: 600,
            width: '100%',
            p: 4,
          }}
        >
          {/* Header - Moved inside PlayerContent */}
          <Box
            sx={{
              width: '100%',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
            }}
          >
            <IconButton onClick={() => navigate(-1)} sx={{ color: '#ffffff' }}>
              <ArrowBackIcon />
            </IconButton>
            <Typography variant="h6" sx={{ color: '#ffffff', fontWeight: 600 }}>
              Now Playing
            </Typography>
            <IconButton sx={{ color: '#ffffff' }}>
              <ShareIcon />
            </IconButton>
          </Box>

          {/* Middle Content Wrapper */}
          <Box sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            flexGrow: 1,
            justifyContent: 'center', // Vertically center content within this wrapper
          }}>
            <motion.img
              src={`${process.env.PUBLIC_URL}/logo.png`} // Changed to logo.png
              alt="Nightingale Logo" // Changed to Nightingale Logo
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.5 }}
              style={{ width: 150, height: 150, borderRadius: '50%', marginBottom: 20 }} // Made logo circular and larger
            />
            <Typography variant="h5" sx={{ color: '#ffffff', fontWeight: 700, mt: 2 }}>
              Your personalized soundscape
            </Typography>
            <Typography variant="body2" sx={{ color: '#c0c0c0', mb: 3 }}>
              Generated by {aiName}
            </Typography>

            {/* Playback Controls */}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 3 }}>
              <PlayPauseButton onClick={handlePlayPause}>
                {isPlaying ? <PauseIcon sx={{ fontSize: 40 }} /> : <PlayIcon sx={{ fontSize: 40 }} />}
              </PlayPauseButton>
            </Box>

            {/* Progress Bar and Time */}
            <Box sx={{ width: '100%', display: 'flex', alignItems: 'center', gap: 1, mb: 3 }}>
              <Typography sx={{ color: '#ffffff', fontSize: 12 }}>{formatTime(currentTime)}</Typography>
              <Slider
                aria-label="time-slider"
                value={currentTime}
                min={0}
                max={duration}
                onChange={handleSeek}
                sx={{
                  color: '#2d9c93',
                  height: 4,
                  '& .MuiSlider-thumb': {
                    width: 12,
                    height: 12,
                    backgroundColor: '#ffffff',
                    boxShadow: '0 0 0 4px rgba(45, 156, 147, 0.3)',
                    '&:hover, &.Mui-focusVisible': {
                      boxShadow: '0 0 0 6px rgba(45, 156, 147, 0.4)',
                    },
                  },
                  '& .MuiSlider-rail': {
                    backgroundColor: 'rgba(255, 255, 255, 0.3)',
                  },
                }}
              />
              <Typography sx={{ color: '#ffffff', fontSize: 12 }}>{formatTime(duration)}</Typography>
              <IconButton onClick={() => setShowHelp(true)} sx={{ color: '#ffffff', ml: 1, p: '4px' }}>
                <HelpOutlineIcon sx={{ fontSize: 18 }} />
              </IconButton>
            </Box>
          </Box>

          {/* Action Buttons (Favorite and Effects) - Moved inside PlayerContent */}
          <Box sx={{
            width: '100%',
            display: 'flex',
            gap: 2,
          }}>
            <ActionButton onClick={handleFavorite} startIcon={<FavoriteIcon />}>
              Favorite
            </ActionButton>
            <ActionButton onClick={() => setShowEffects(true)} startIcon={<TuneIcon />}>
              Effects
            </ActionButton>
          </Box>

        </PlayerContent>

        {/* Effects Dialog */}
        <Dialog open={showEffects} onClose={() => setShowEffects(false)} PaperProps={{
          sx: {
            background: 'rgba(12, 26, 26, 0.9)',
            backdropFilter: 'blur(15px)',
            borderRadius: '20px',
            border: '1px solid rgba(45, 156, 147, 0.3)',
            color: '#ffffff',
          }
        }}>
          <DialogTitle sx={{ color: '#ffffff', borderBottom: '1px solid rgba(255,255,255,0.1)', pb: 1 }}>Audio Effects</DialogTitle>
          <DialogContent sx={{ pt: 2 }}>
            {renderEffectControls()}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowEffects(false)} sx={{ color: '#2d9c93' }}>Close</Button>
          </DialogActions>
        </Dialog>

        {/* Help Dialog */}
        <Dialog open={showHelp} onClose={() => setShowHelp(false)} PaperProps={{
          sx: {
            background: 'rgba(12, 26, 26, 0.9)',
            backdropFilter: 'blur(15px)',
            borderRadius: '20px',
            border: '1px solid rgba(45, 156, 147, 0.3)',
            color: '#ffffff',
          }
        }}>
          <DialogTitle sx={{ color: '#ffffff', borderBottom: '1px solid rgba(255,255,255,0.1)', pb: 1 }}>Help</DialogTitle>
          <DialogContent sx={{ pt: 2 }}>
            <Typography sx={{ color: '#ffffff', mb: 2 }}>
              This is the Ambiance AI Player. You can play generated soundscapes, adjust effects, and manage your favorites.
            </Typography>
            <Typography sx={{ color: '#ffffff', mb: 2 }}>
              Use the playback controls to play, pause, and skip tracks.
            </Typography>
            <Typography sx={{ color: '#ffffff', mb: 2 }}>
              The "Effects" button allows you to apply various audio effects to your soundscape.
            </Typography>
            <Typography sx={{ color: '#ffffff', mb: 2 }}>
              Click "Favorite" to save your current soundscape for quick access later.
            </Typography>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setShowHelp(false)} sx={{ color: '#2d9c93' }}>Got It</Button>
          </DialogActions>
        </Dialog>

        <audio ref={audioRef} onTimeUpdate={handleTimeUpdate} onLoadedMetadata={handleLoadedMetadata} />
        <audio ref={musicRef} loop />
      </Box>
    </PlayerScreen>
  );
};

export default Player; 