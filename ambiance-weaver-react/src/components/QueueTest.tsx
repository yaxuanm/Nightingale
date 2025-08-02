import React, { useState } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Container,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import QueueAudioGenerator from './QueueAudioGenerator';
import { uiSystem } from '../theme/uiSystem';

const QueueTest: React.FC = () => {
  const [testDescription, setTestDescription] = useState('森林中的鸟叫声和雨声');
  const navigate = useNavigate();

  const handleComplete = (audioUrl: string, taskResult: any) => {
    console.log('Queue test completed:', { audioUrl, taskResult });
    navigate('/player', { 
      state: { 
        audioUrl, 
        description: testDescription,
        taskResult 
      } 
    });
  };

  const handleError = (error: string) => {
    console.error('Queue test error:', error);
  };

  const handleCancel = () => {
    console.log('Queue test cancelled');
  };

  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h4" sx={{ color: uiSystem.colors.white, mb: 2 }}>
          Queue System Test
        </Typography>
        <Typography variant="body1" sx={{ color: uiSystem.colors.white70 }}>
          Test the queue-based audio generation system
        </Typography>
      </Box>

      <Paper
        sx={{
          p: 3,
          bgcolor: 'rgba(255, 255, 255, 0.05)',
          border: `1px solid ${uiSystem.colors.white20}`,
          borderRadius: 2,
        }}
      >
        <Typography variant="h6" sx={{ color: uiSystem.colors.white, mb: 2 }}>
          Test Description
        </Typography>
        <Typography variant="body2" sx={{ color: uiSystem.colors.white70, mb: 3 }}>
          {testDescription}
        </Typography>

        <QueueAudioGenerator
          description={testDescription}
          duration={20}
          mode="default"
          onComplete={handleComplete}
          onError={handleError}
          onCancel={handleCancel}
        />
      </Paper>

      <Box sx={{ mt: 3, textAlign: 'center' }}>
        <Button
          variant="outlined"
          onClick={() => navigate('/')}
          sx={{
            color: uiSystem.colors.white,
            borderColor: uiSystem.colors.white20,
            '&:hover': {
              borderColor: uiSystem.colors.primary,
            },
          }}
        >
          Back to Main
        </Button>
      </Box>
    </Container>
  );
};

export default QueueTest; 