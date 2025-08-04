import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  Paper,
  IconButton,
  styled,
  Slider,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Share as ShareIcon,
  ArrowBack as ArrowBackIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import PageLayout from './PageLayout';
import { API_CONFIG } from '../config/api';

const PlayPauseButton = styled(IconButton)(({ theme }) => ({
  width: 80,
  height: 80,
  background: 'linear-gradient(135deg, #2d9c93 0%, #1a5f5a 100%)',
  border: 'none',
  boxShadow: '0 8px 24px rgba(45, 156, 147, 0.3)',
  color: '#ffffff',
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
  fontSize: 13,
  fontWeight: 500,
  backdropFilter: 'blur(10px)',
  '&:hover': {
    background: 'rgba(255, 255, 255, 0.1)',
    transform: 'translateY(-1px)',
  },
}));

interface ShareData {
  id: string;
  audio_url: string;
  background_url?: string;
  description: string;
  title: string;
  created_at: string;
  views: number;
}

const SharePage: React.FC = () => {
  const { shareId } = useParams<{ shareId: string }>();
  const navigate = useNavigate();
  const [shareData, setShareData] = useState<ShareData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    const fetchShareData = async () => {
      if (!shareId) return;
      
      try {
        const response = await fetch(`${API_CONFIG.GEMINI_API_BASE_URL}/api/share/${shareId}`);
        if (!response.ok) {
          throw new Error('Share not found');
        }
        
        const data = await response.json();
        setShareData(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load share');
      } finally {
        setLoading(false);
      }
    };

    fetchShareData();
  }, [shareId]);

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

  const handleShare = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      // 可以添加一个toast通知
    } catch {
      // 处理错误
    }
  };

  const handleDownload = async () => {
    if (!shareData) return;
    
    setIsDownloading(true);
    
    try {
      // 下载音频文件
      if (shareData.audio_url) {
        const audioResponse = await fetch(shareData.audio_url);
        const audioBlob = await audioResponse.blob();
        const audioUrl = URL.createObjectURL(audioBlob);
        const audioLink = document.createElement('a');
        audioLink.href = audioUrl;
        audioLink.download = `nightingale_audio_${shareData.id}.wav`;
        document.body.appendChild(audioLink);
        audioLink.click();
        document.body.removeChild(audioLink);
        URL.revokeObjectURL(audioUrl);
      }

      // 下载背景图片
      if (shareData.background_url) {
        const imageResponse = await fetch(shareData.background_url);
        const imageBlob = await imageResponse.blob();
        const imageUrl = URL.createObjectURL(imageBlob);
        const imageLink = document.createElement('a');
        imageLink.href = imageUrl;
        imageLink.download = `nightingale_background_${shareData.id}.png`;
        document.body.appendChild(imageLink);
        imageLink.click();
        document.body.removeChild(imageLink);
        URL.revokeObjectURL(imageUrl);
      }
    } catch (error) {
      console.error('Download failed:', error);
    } finally {
      setIsDownloading(false);
    }
  };

  if (loading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          background: 'linear-gradient(135deg, #0c1a1a 0%, #1a3a3a 100%)',
        }}
      >
        <CircularProgress sx={{ color: '#2d9c93' }} />
      </Box>
    );
  }

  if (error || !shareData) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '100vh',
          background: 'linear-gradient(135deg, #0c1a1a 0%, #1a3a3a 100%)',
          color: '#ffffff',
        }}
      >
        <Typography variant="h4" sx={{ mb: 2 }}>
          Share Not Found
        </Typography>
        <Typography variant="body1" sx={{ mb: 3, opacity: 0.8 }}>
          {error || 'This share link is invalid or has expired.'}
        </Typography>
        <Button
          variant="contained"
          onClick={() => navigate('/')}
          sx={{ background: '#2d9c93' }}
        >
          Go Home
        </Button>
      </Box>
    );
  }

  const shareContent = (
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
        {/* Header */}
        <Box sx={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          width: '100%',
          mb: 3,
        }}>
          <IconButton onClick={() => navigate('/')} sx={{ color: '#ffffff' }}>
            <ArrowBackIcon />
          </IconButton>
          <Typography variant="h6" sx={{ color: '#ffffff', fontWeight: 600 }}>
            Shared Soundscape
          </Typography>
          <IconButton sx={{ color: '#ffffff' }} onClick={handleShare}>
            <ShareIcon />
          </IconButton>
        </Box>

        {/* Content */}
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Box sx={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            textAlign: 'center',
          }}>
            <Box sx={{
              width: 120,
              height: 120,
              borderRadius: '50%',
              overflow: 'hidden',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: 'rgba(45,156,147,0.10)',
              mb: 2,
            }}>
              <img
                src={`${process.env.PUBLIC_URL}/logo.png`}
                alt="Nightingale Logo"
                style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
              />
            </Box>
            
            <Typography variant="h5" sx={{ color: '#ffffff', fontWeight: 700, mt: 2 }}>
              {shareData.title}
            </Typography>
            
            {shareData.description && (
              <Typography 
                variant="body2" 
                sx={{ 
                  color: '#2d9c93',
                  textAlign: 'center',
                  maxWidth: '80%',
                  mx: 'auto',
                  mt: 1,
                  mb: 2,
                  fontFamily: 'monospace',
                  fontSize: '0.9rem',
                  wordBreak: 'break-word',
                  bgcolor: 'rgba(45,156,147,0.08)',
                  px: 2,
                  py: 1,
                  borderRadius: 1,
                  border: '1px solid rgba(45,156,147,0.15)',
                }}
              >
                {shareData.description}
              </Typography>
            )}
            
            <Typography variant="body2" sx={{ color: '#c0c0c0', mb: 3 }}>
              Generated by Nightingale
            </Typography>
          </Box>
        </motion.div>

        {/* Player Controls */}
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
        </Box>

        {/* Action Buttons */}
        <Box sx={{
          width: '100%',
          display: 'flex',
          gap: 2,
        }}>
          <ActionButton 
            onClick={handleDownload} 
            startIcon={isDownloading ? <CircularProgress size={16} color="inherit" /> : <DownloadIcon />}
            disabled={isDownloading}
          >
            {isDownloading ? 'Downloading...' : 'Download'}
          </ActionButton>
          <ActionButton onClick={handleShare} startIcon={<ShareIcon />}>
            Share
          </ActionButton>
        </Box>

        {/* Stats */}
        <Box sx={{ mt: 4, opacity: 0.7 }}>
          <Typography variant="caption" sx={{ color: '#c0c0c0' }}>
            Views: {shareData.views} • Created: {new Date(shareData.created_at).toLocaleDateString()}
          </Typography>
        </Box>
      </Box>

      {/* Hidden audio element */}
      <audio 
        ref={audioRef} 
        src={shareData.audio_url}
        onTimeUpdate={handleTimeUpdate} 
        onLoadedMetadata={handleLoadedMetadata} 
      />
    </>
  );

  return (
    <PageLayout backgroundImageUrl={shareData.background_url} minHeight="700px">
      {shareContent}
      <Box sx={{ width: '100%', textAlign: 'center', mt: 4, mb: 2 }}>
        <Typography variant="subtitle2" sx={{ color: '#c0c0c0', fontStyle: 'italic', letterSpacing: 1 }}>
          Let Sound Touch the Soul.
        </Typography>
      </Box>
    </PageLayout>
  );
};

export default SharePage; 