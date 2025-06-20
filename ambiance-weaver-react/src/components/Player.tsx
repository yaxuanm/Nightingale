import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Slider,
  Button,
  FormControlLabel,
  Switch,
  styled,
  Collapse,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
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
import PageLayout from './PageLayout';
import Snackbar from '@mui/material/Snackbar';

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
  usePageLayout?: boolean;
}

const Player: React.FC<PlayerProps> = ({
  audioUrl,
  description,
  onGenerateMusic,
  onGenerateBackground,
  backgroundImageUrl,
  musicUrl,
  usePageLayout = true
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
  const [showHelp, setShowHelp] = useState(false);
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
        feedback: 0.3,
        mix: 0.5,
      },
    },
    {
      type: 'fade',
      enabled: false,
      params: {
        fadeIn: 2000,
        fadeOut: 3000,
      },
    },
    {
      type: 'volume',
      enabled: true,
      params: {
        level: 0.8,
      },
    },
  ]);

  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [isMuted, setIsMuted] = useState(false);

  const audioRef = useRef<HTMLAudioElement>(null);
  const musicRef = useRef<HTMLAudioElement>(null);

  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string }>({ open: false, message: '' });
  const [shareDialogOpen, setShareDialogOpen] = useState(false);

  useEffect(() => {
    if (currentAudioUrl && audioRef.current) {
      audioRef.current.src = currentAudioUrl;
    }
  }, [currentAudioUrl]);

  useEffect(() => {
    if (musicUrl && musicRef.current) {
      musicRef.current.src = musicUrl;
    }
  }, [musicUrl]);

  const handlePlayPause = () => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleShare = async () => {
    setShareDialogOpen(true);
    const shareUrl = window.location.href;
    try {
      await navigator.clipboard.writeText(shareUrl);
      setSnackbar({ open: true, message: 'Link copied to clipboard!' });
    } catch {
      setSnackbar({ open: true, message: 'Failed to copy link. Please copy manually.' });
    }
  };

  const handleFavorite = () => {
    setIsFavorite((prev) => {
      const newValue = !prev;
      setSnackbar({ open: true, message: newValue ? 'Added to favorites!' : 'Removed from favorites.' });
      return newValue;
    });
  };

  const handleSliderChange = (name: keyof SoundscapeState) => (event: Event, value: number | number[]) => {
    // Handle soundscape parameter changes - 保留用于未来功能扩展
  };

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
                  },
                  '& .MuiSwitch-switchBase.Mui-checked + .MuiSwitch-track': {
                    backgroundColor: '#2d9c93',
                  },
                }}
              />
            }
            label={
              <Typography sx={{ color: '#ffffff', textTransform: 'capitalize' }}>
                {effect.type}
              </Typography>
            }
          />
          {effect.enabled && (
            <Box sx={{ mt: 1, ml: 4 }}>
              {Object.entries(effect.params).map(([paramName, value]) => (
                <Box key={paramName} sx={{ mb: 1 }}>
                  <Typography sx={{ color: '#c0c0c0', fontSize: 14, mb: 0.5 }}>
                    {paramName}
                  </Typography>
                  <Slider
                    value={value}
                    min={0}
                    max={1}
                    step={0.01}
                    onChange={(_, newValue) => handleEffectParamChange(index, paramName, newValue as number)}
                    sx={{
                      color: '#2d9c93',
                      height: 4,
                      '& .MuiSlider-thumb': {
                        width: 12,
                        height: 12,
                        backgroundColor: '#ffffff',
                      },
                    }}
                  />
                </Box>
              ))}
            </Box>
          )}
        </EffectControl>
      ))}
    </EffectsPanel>
  );

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

  const playerContent = (
    <>
      <Box
        sx={{
          width: '100%',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          mb: 3,
        }}
      >
        <IconButton onClick={() => navigate(-1)} sx={{ color: '#ffffff' }}>
          <ArrowBackIcon />
        </IconButton>
        <Typography variant="h6" sx={{ color: '#ffffff', fontWeight: 600 }}>
          Now Playing
        </Typography>
        <IconButton sx={{ color: '#ffffff' }} onClick={handleShare}>
          <ShareIcon />
        </IconButton>
      </Box>
      <Box sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        flexGrow: 1,
        justifyContent: 'center',
      }}>
        <motion.img
          src={`${process.env.PUBLIC_URL}/logo.png`}
          alt="Nightingale Logo"
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
          style={{ width: 150, height: 150, borderRadius: '50%', marginBottom: 20 }}
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
          <Typography sx={{ color: '#ffffff', fontSize: 14 }}>{formatTime(currentTime)}</Typography>
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
          <Typography sx={{ color: '#ffffff', fontSize: 14 }}>{formatTime(duration)}</Typography>
          <IconButton onClick={() => setShowHelp(true)} sx={{ color: '#ffffff', ml: 1, p: '4px' }}>
            <HelpOutlineIcon sx={{ fontSize: 18 }} />
          </IconButton>
        </Box>
      </Box>

      {/* Action Buttons */}
      <Box sx={{
        width: '100%',
        display: 'flex',
        gap: 2,
      }}>
        <ActionButton onClick={handleFavorite} startIcon={<FavoriteIcon color={isFavorite ? 'error' : 'inherit'} />}>
          {isFavorite ? 'Favorited' : 'Favorite'}
        </ActionButton>
        <ActionButton onClick={() => setShowEffects(true)} startIcon={<TuneIcon />}>
          Effects
        </ActionButton>
      </Box>

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
          <Typography sx={{ color: '#ffffff', mb: 2 }}>
            Adjust the audio effects below to personalize your soundscape. Enable or disable effects and fine-tune their parameters.
          </Typography>
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
            Welcome to the Ambiance AI Player! Here you can:
          </Typography>
          <ul style={{ color: '#fff', marginLeft: 20, marginBottom: 16 }}>
            <li>Play, pause, and seek through your generated soundscape.</li>
            <li>Adjust audio effects for a personalized experience.</li>
            <li>Click "Favorite" to save your favorite soundscapes.</li>
            <li>Use the "Share" button to copy a link and share with friends.</li>
          </ul>
          <Typography sx={{ color: '#ffffff', mb: 2 }}>
            If you have any questions or feedback, feel free to contact us!
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowHelp(false)} sx={{ color: '#2d9c93' }}>Got It</Button>
        </DialogActions>
      </Dialog>

      <audio ref={audioRef} onTimeUpdate={handleTimeUpdate} onLoadedMetadata={handleLoadedMetadata} />
      <audio ref={musicRef} loop />

      <Snackbar
        open={snackbar.open}
        autoHideDuration={2500}
        onClose={() => setSnackbar({ open: false, message: '' })}
        message={snackbar.message}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />

      <Dialog open={shareDialogOpen} onClose={() => setShareDialogOpen(false)} PaperProps={{
        sx: {
          background: 'rgba(12, 26, 26, 0.95)',
          backdropFilter: 'blur(15px)',
          borderRadius: '20px',
          border: '1px solid rgba(45, 156, 147, 0.3)',
          color: '#ffffff',
        }
      }}>
        <DialogTitle sx={{ color: '#ffffff', borderBottom: '1px solid rgba(255,255,255,0.1)', pb: 1 }}>Share this soundscape</DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          <Typography sx={{ color: '#ffffff', mb: 2 }}>
            Share this link with your friends to let them experience your soundscape:
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <TextField
              value={window.location.href}
              fullWidth
              InputProps={{ readOnly: true, sx: { color: '#fff' } }}
              variant="outlined"
              size="small"
            />
            <Button onClick={async () => {
              try {
                await navigator.clipboard.writeText(window.location.href);
                setSnackbar({ open: true, message: 'Link copied to clipboard!' });
              } catch {
                setSnackbar({ open: true, message: 'Failed to copy link. Please copy manually.' });
              }
            }} sx={{ color: '#2d9c93', minWidth: 80 }}>Copy</Button>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShareDialogOpen(false)} sx={{ color: '#2d9c93' }}>Close</Button>
        </DialogActions>
      </Dialog>
    </>
  );

  if (usePageLayout) {
    return (
      <PageLayout backgroundImageUrl={currentBackgroundImageUrl} minHeight="700px">
        {playerContent}
        <Box sx={{ width: '100%', textAlign: 'center', mt: 4, mb: 2 }}>
          <Typography variant="subtitle2" sx={{ color: '#c0c0c0', fontStyle: 'italic', letterSpacing: 1 }}>
            Let Sound Touch the Soul.
          </Typography>
        </Box>
      </PageLayout>
    );
  }
  return (
    <>
      {playerContent}
      <Box sx={{ width: '100%', textAlign: 'center', mt: 4, mb: 2 }}>
        <Typography variant="subtitle2" sx={{ color: '#c0c0c0', fontStyle: 'italic', letterSpacing: 1 }}>
          Let Sound Touch the Soul.
        </Typography>
      </Box>
    </>
  );
};

export default Player; 