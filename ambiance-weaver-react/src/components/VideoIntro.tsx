import React, { useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Box, Button } from '@mui/material';

const VIDEO_URL = '/promo.mp4'; // 视频放在 public 目录下

const VideoIntro: React.FC = () => {
  const navigate = useNavigate();
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    const handleEnded = () => navigate('/onboarding');
    const video = videoRef.current;
    if (video) {
      video.addEventListener('ended', handleEnded);
      return () => video.removeEventListener('ended', handleEnded);
    }
  }, [navigate]);

  return (
    <Box
      sx={{
        width: '100vw',
        height: '100vh',
        bgcolor: 'black',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
      }}
    >
      <video
        ref={videoRef}
        src={VIDEO_URL}
        autoPlay
        controls={false}
        style={{ width: '100vw', height: '100vh', objectFit: 'cover' }}
      />
      <Button
        variant="contained"
        sx={{
          position: 'absolute',
          top: 32,
          right: 32,
          bgcolor: 'rgba(0,0,0,0.5)',
          color: 'white',
        }}
        onClick={() => navigate('/onboarding')}
      >
        Skip
      </Button>
    </Box>
  );
};

export default VideoIntro; 