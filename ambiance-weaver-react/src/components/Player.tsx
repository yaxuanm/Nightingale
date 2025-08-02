import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Slider,
  Button,
  styled,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  CircularProgress,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  ArrowBack as ArrowBackIcon,
  Share as ShareIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
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
  height: 40,
  background: 'rgba(255, 255, 255, 0.05)',
  border: '1px solid rgba(45, 156, 147, 0.2)',
  borderRadius: '20px',
  color: '#ffffff',
  fontSize: 18,
  fontWeight: 500,
  backdropFilter: 'blur(10px)',
  '&:hover': {
    background: 'rgba(255, 255, 255, 0.1)',
    transform: 'translateY(-1px)',
  },
}));

interface PlayerProps {
  audioUrl?: string;
  description?: string;
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
  const { 
    audioUrl: stateAudioUrl, 
    backgroundImageUrl: stateBackgroundImageUrl,
    description: stateDescription 
  } = location.state || {};
  
  const currentAudioUrl = audioUrl || stateAudioUrl;
  const currentBackgroundImageUrl = backgroundImageUrl || stateBackgroundImageUrl;
  const currentDescription = description || stateDescription;

  const [isPlaying, setIsPlaying] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [isMuted, setIsMuted] = useState(false);

  const audioRef = useRef<HTMLAudioElement>(null);
  const musicRef = useRef<HTMLAudioElement>(null);

  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string }>({ open: false, message: '' });
  const [shareDialogOpen, setShareDialogOpen] = useState(false);
  const [shareUrl, setShareUrl] = useState<string | null>(null);
  const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(false);

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

  // 文本截断函数
  const truncateDescription = (text: string, maxLength: number = 300) => {
    if (text.length <= maxLength) return { truncated: text, isLong: false };
    // 找到最后一个完整的句子或单词边界
    const truncated = text.substring(0, maxLength);
    const lastPeriod = truncated.lastIndexOf('.');
    const lastSpace = truncated.lastIndexOf(' ');
    const cutPoint = Math.max(lastPeriod, lastSpace);
    
    if (cutPoint > maxLength * 0.8) { // 如果截断点太靠前，就用空格
      return { 
        truncated: truncated.substring(0, lastSpace) + '...', 
        isLong: true,
        full: text 
      };
    } else {
      return { 
        truncated: truncated.substring(0, cutPoint) + '...', 
        isLong: true,
        full: text 
      };
    }
  };

  const handlePlayPause = () => {
    if (audioRef.current && currentAudioUrl) {
      if (isPlaying) {
        audioRef.current.pause();
      } else {
        audioRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const handleShare = async () => {
    if (!currentAudioUrl) {
      setSnackbar({ open: true, message: 'No audio available to share' });
      return;
    }
    
    setShareDialogOpen(true);
    
    try {
      // 调用后端API创建分享链接
      const response = await fetch('http://localhost:8000/api/create-share', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          audio_url: currentAudioUrl,
          background_url: currentBackgroundImageUrl,
          description: currentDescription,
          title: 'My Nightingale Soundscape'
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to create share');
      }
      
      const shareData = await response.json();
      const shareUrl = shareData.share_url;
      
      // 复制分享链接到剪贴板
      await navigator.clipboard.writeText(shareUrl);
      setSnackbar({ open: true, message: 'Share link copied to clipboard!' });
      
      // 更新对话框中的链接
      setShareUrl(shareUrl);
      
    } catch (error) {
      console.error('Share creation failed:', error);
      // 回退到原来的方式
      const fallbackUrl = window.location.href;
      await navigator.clipboard.writeText(fallbackUrl);
      setSnackbar({ open: true, message: 'Failed to create share link. Copied current page URL instead.' });
      setShareUrl(fallbackUrl);
    }
  };

  const handleDownload = async () => {
    if (!currentAudioUrl) {
      setSnackbar({ open: true, message: 'No audio available to download' });
      return;
    }
    
    setIsDownloading(true);
    
    try {
      // 下载音频文件
      if (currentAudioUrl) {
        const audioResponse = await fetch(currentAudioUrl);
        const audioBlob = await audioResponse.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audioLink = document.createElement('a');
        audioLink.href = audioUrl;
        audioLink.download = `nightingale_audio_${Date.now()}.wav`;
        document.body.appendChild(audioLink);
        audioLink.click();
        document.body.removeChild(audioLink);
        URL.revokeObjectURL(audioUrl);
      }

      // 下载背景图片
      if (currentBackgroundImageUrl) {
        const imageResponse = await fetch(currentBackgroundImageUrl);
        const imageBlob = await imageResponse.blob();
        const imageUrl = URL.createObjectURL(imageBlob);
        const imageLink = document.createElement('a');
        imageLink.href = imageUrl;
        imageLink.download = `nightingale_background_${Date.now()}.png`;
        document.body.appendChild(imageLink);
        imageLink.click();
        document.body.removeChild(imageLink);
        URL.revokeObjectURL(imageUrl);
      }
    } catch (error) {
      console.error('Download failed:', error);
      setSnackbar({ open: true, message: 'Download failed. Please try again.' });
    } finally {
      setIsDownloading(false);
    }
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
    if (audioRef.current && currentAudioUrl) {
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
          flexDirection: 'column',
          alignItems: 'center',
          gap: 3,
        }}
      >
        {/* Header with Logo and Prompt */}
        <Box sx={{
          display: 'flex',
          alignItems: 'flex-start',
          gap: 2,
          mb: 2,
          width: '100%',
        }}>
          {/* Logo */}
          <Box sx={{
            width: 48,
            height: 48,
            borderRadius: '12px',
            overflow: 'hidden',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'rgba(45,156,147,0.10)',
            flexShrink: 0,
          }}>
            <img
              src={`${process.env.PUBLIC_URL}/logo.png`}
              alt="Nightingale Logo"
              style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
            />
          </Box>
          
          {/* Prompt */}
          {currentDescription && (
            <Box sx={{ flexGrow: 1 }}>
              {(() => {
                const textInfo = truncateDescription(currentDescription);
                const displayText = isDescriptionExpanded ? textInfo.full : textInfo.truncated;
                
                return (
                  <Box sx={{ position: 'relative', mb: 1 }}>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: '#ffffff',
                        fontSize: '0.7rem',
                        lineHeight: 1.3,
                        maxHeight: isDescriptionExpanded ? 'none' : '75px',
                        overflow: 'hidden',
                        wordWrap: 'break-word',
                        whiteSpace: 'pre-wrap',
                        padding: '4px 0',
                        paddingRight: textInfo.isLong && !isDescriptionExpanded ? '24px' : '0',
                      }}
                    >
                      {displayText}
                    </Typography>
                    {textInfo.isLong && (
                      <Box
                        onClick={() => setIsDescriptionExpanded(!isDescriptionExpanded)}
                        sx={{
                          position: 'absolute',
                          right: 0,
                          top: '2px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          cursor: 'pointer',
                          width: '20px',
                          height: '20px',
                          color: 'rgba(255,255,255,0.6)',
                          fontSize: '14px',
                          '&:hover': {
                            color: 'rgba(255,255,255,0.8)',
                          },
                        }}
                      >
                        {isDescriptionExpanded ? '−' : '+'}
                      </Box>
                    )}
                  </Box>
                );
              })()}
            </Box>
          )}
        </Box>

        {/* Progress Bar */}
        <Box sx={{ width: '100%', display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
          <Typography sx={{ 
            color: '#ffffff', 
            fontSize: '8px !important',
            fontWeight: 400,
            lineHeight: 1,
            minWidth: '20px',
            textAlign: 'center',
          }}>
            {formatTime(currentTime)}
          </Typography>
          <Slider
            aria-label="time-slider"
            value={currentTime}
            min={0}
            max={duration}
            onChange={handleSeek}
            sx={{
              color: '#2d9c93',
              height: 3,
              '& .MuiSlider-thumb': {
                width: 10,
                height: 10,
                backgroundColor: '#ffffff',
                boxShadow: '0 0 0 2px rgba(45, 156, 147, 0.3)',
                '&:hover, &.Mui-focusVisible': {
                  boxShadow: '0 0 0 4px rgba(45, 156, 147, 0.4)',
                },
              },
              '& .MuiSlider-rail': {
                backgroundColor: 'rgba(255, 255, 255, 0.3)',
              },
            }}
          />
          <Typography sx={{ 
            color: '#ffffff', 
            fontSize: '8px !important',
            fontWeight: 400,
            lineHeight: 1,
            minWidth: '20px',
            textAlign: 'center',
          }}>
            {formatTime(duration)}
          </Typography>
        </Box>

        {/* Control Buttons */}
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          width: '100%',
        }}>
          <IconButton 
            onClick={handleDownload} 
            disabled={isDownloading}
            sx={{ 
              width: 36, 
              height: 36, 
              color: '#ffffff',
              fontSize: 20,
            }}
          >
            {isDownloading ? <CircularProgress size={16} /> : <DownloadIcon />}
          </IconButton>
          
          <IconButton 
            onClick={handlePlayPause}
            sx={{ 
              width: 40, 
              height: 40, 
              background: 'rgba(255, 255, 255, 0.05)',
              borderRadius: '50%',
              color: '#ffffff',
              fontSize: 20,
            }}
          >
            {isPlaying ? <PauseIcon /> : <PlayIcon />}
          </IconButton>
          
          <IconButton 
            onClick={handleShare}
            sx={{ 
              width: 36, 
              height: 36, 
              color: '#ffffff',
              fontSize: 20,
            }}
          >
            <ShareIcon />
          </IconButton>
        </Box>
      </Box>

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
        <DialogTitle sx={{ color: '#ffffff', borderBottom: '1px solid rgba(255,255,255,0.1)', pb: 1 }}>
          Share this soundscape
        </DialogTitle>
        <DialogContent sx={{ pt: 2 }}>
          <Typography sx={{ color: '#ffffff', mb: 2 }}>
            Share this link with your friends to let them experience your soundscape:
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <TextField
              value={shareUrl || window.location.href}
              fullWidth
              InputProps={{ readOnly: true, sx: { color: '#fff' } }}
              variant="outlined"
              size="small"
            />
            <Button onClick={async () => {
              try {
                await navigator.clipboard.writeText(shareUrl || window.location.href);
                setSnackbar({ open: true, message: 'Link copied to clipboard!' });
              } catch {
                setSnackbar({ open: true, message: 'Failed to copy link. Please copy manually.' });
              }
            }} sx={{ color: '#2d9c93', minWidth: 80 }}>
              Copy
            </Button>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShareDialogOpen(false)} sx={{ color: '#2d9c93' }}>
            Close
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );

  return usePageLayout ? (
    <PageLayout backgroundImageUrl={currentBackgroundImageUrl} maxWidth={420} minHeight="auto">
      {playerContent}
    </PageLayout>
  ) : (
    <>
      {playerContent}
    </>
  );
};

export default Player; 