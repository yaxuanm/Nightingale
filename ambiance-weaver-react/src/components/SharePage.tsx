import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  IconButton,
  Slider,
  Snackbar,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Share as ShareIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import PageLayout from './PageLayout';
import { API_CONFIG } from '../config/api';
import { copyTextWithMessage } from '../utils/clipboard';
import { parseShareData, isSharePage, cleanShareParams, generateShareTitle } from '../utils/shareUtils';



interface ShareData {
  id?: string;
  audio_url: string;
  background_url?: string;
  description?: string;
  title?: string;
  created_at?: string;
  views?: number;
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
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string }>({ open: false, message: '' });

  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    const loadShareData = async () => {
      // 首先尝试从 URL 参数加载数据（纯前端分享）
      const urlShareData = parseShareData();
      if (urlShareData) {
        setShareData(urlShareData);
        setLoading(false);
        return;
      }
      
      // 如果没有 URL 参数，尝试从后端 API 加载（传统方式）
      if (!shareId) {
        setError('No share data found');
        setLoading(false);
        return;
      }
      
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

    loadShareData();
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
    const copyResult = await copyTextWithMessage(window.location.href);
    setSnackbar({ open: true, message: copyResult.message });
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
      setSnackbar({ open: true, message: 'Download failed. Please try again.' });
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
          <Box sx={{ flexGrow: 1 }}>
            {/* Title */}
            {shareData.title && (
              <Typography 
                variant="h6" 
                sx={{ 
                  color: '#ffffff',
                  fontSize: '0.9rem',
                  fontWeight: 600,
                  mb: 1,
                  wordWrap: 'break-word',
                }}
              >
                {shareData.title}
              </Typography>
            )}
            
            {/* Description */}
            {shareData.description && (
              <Box sx={{ position: 'relative', mb: 1 }}>
                <Typography 
                  variant="body2" 
                  sx={{ 
                    color: '#ffffff',
                    fontSize: '0.7rem',
                    lineHeight: 1.3,
                    wordWrap: 'break-word',
                    whiteSpace: 'pre-wrap',
                    padding: '4px 0',
                  }}
                >
                  {shareData.description}
                </Typography>
              </Box>
            )}
          </Box>
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

        {/* Stats */}
        <Box sx={{ mt: 2, opacity: 0.7, textAlign: 'center' }}>
          <Typography variant="caption" sx={{ color: '#c0c0c0', fontSize: '10px' }}>
            {shareData.created_at ? (
              <>Views: {shareData.views || 0} • Created: {new Date(shareData.created_at).toLocaleDateString()}</>
            ) : (
              <>Shared via Nightingale</>
            )}
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

      <Snackbar
        open={snackbar.open}
        autoHideDuration={2500}
        onClose={() => setSnackbar({ open: false, message: '' })}
        message={snackbar.message}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
    </>
  );

  return (
    <PageLayout backgroundImageUrl={shareData.background_url} maxWidth={420} minHeight="auto">
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