import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Typography,
  Button,
  CircularProgress,
  LinearProgress,
  Alert,
  IconButton,
  Paper,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { uiSystem } from '../theme/uiSystem';

interface QueueTask {
  task_id: string;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  progress?: number;
  queue_position?: number;
  estimated_wait_time?: number;
  result?: {
    audio_url?: string;
    description?: string;
    duration?: number;
    mode?: string;
  };
  error?: string;
}

interface QueueAudioGeneratorProps {
  description: string;
  duration?: number;
  mode?: string;
  userId?: string;
  priority?: 'low' | 'normal' | 'high' | 'urgent';
  onComplete?: (audioUrl: string, taskResult: any) => void;
  onError?: (error: string) => void;
  onCancel?: () => void;
}

const QueueAudioGenerator: React.FC<QueueAudioGeneratorProps> = ({
  description,
  duration = 20,
  mode = 'default',
  userId = 'anonymous',
  priority = 'normal',
  onComplete,
  onError,
  onCancel,
}) => {
  const [task, setTask] = useState<QueueTask | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const pollIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // 创建队列任务
  const createTask = async () => {
    try {
      setIsLoading(true);
      setError(null);

      const response = await fetch('http://localhost:8000/api/queue/audio-generation', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          description,
          duration,
          mode,
          user_id: userId,
          priority,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create task');
      }

      const taskData = await response.json();
      setTask(taskData);
      setIsPolling(true);
      startPolling(taskData.task_id);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create task';
      setError(errorMessage);
      onError?.(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // 开始轮询任务状态
  const startPolling = (taskId: string) => {
    const pollTask = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/queue/status/${taskId}`);
        if (!response.ok) return;

        const statusData = await response.json();
        setTask(statusData);

        if (statusData.status === 'completed') {
          setIsPolling(false);
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
          if (statusData.result?.audio_url) {
            onComplete?.(statusData.result.audio_url, statusData.result);
          }
        } else if (statusData.status === 'failed' || statusData.status === 'cancelled') {
          setIsPolling(false);
          if (pollIntervalRef.current) {
            clearInterval(pollIntervalRef.current);
            pollIntervalRef.current = null;
          }
          const errorMsg = statusData.error || `Task ${statusData.status}`;
          setError(errorMsg);
          onError?.(errorMsg);
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    };

    // 立即执行一次
    pollTask();
    // 每2秒轮询一次
    pollIntervalRef.current = setInterval(pollTask, 2000);
  };

  // 取消任务
  const cancelTask = async () => {
    if (!task?.task_id) return;

    try {
      const response = await fetch(`http://localhost:8000/api/queue/cancel/${task.task_id}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setIsPolling(false);
        if (pollIntervalRef.current) {
          clearInterval(pollIntervalRef.current);
          pollIntervalRef.current = null;
        }
        onCancel?.();
      }
    } catch (err) {
      console.error('Cancel error:', err);
    }
  };

  // 清理轮询
  useEffect(() => {
    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, []);

  // 获取状态文本
  const getStatusText = () => {
    if (!task) return 'Preparing...';
    
    switch (task.status) {
      case 'pending':
        const queuePosition = task.queue_position || 0;
        return `Task queued... (Position: ${queuePosition})`;
      case 'running':
        return `Generating audio... ${task.progress || 0}%`;
      case 'completed':
        return 'Audio generated successfully!';
      case 'failed':
        return 'Generation failed';
      case 'cancelled':
        return 'Task cancelled';
      default:
        return 'Processing...';
    }
  };

  // 获取进度值
  const getProgressValue = () => {
    if (!task) return 0;
    if (task.status === 'completed') return 100;
    return task.progress || 0;
  };

  // 渲染状态指示器
  const renderStatusIndicator = () => {
    if (task?.status === 'completed') {
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring", stiffness: 500, damping: 30 }}
          >
            <Box
              sx={{
                width: 24,
                height: 24,
                borderRadius: '50%',
                bgcolor: 'success.main',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Typography variant="body2" sx={{ color: 'white', fontWeight: 'bold' }}>
                ✓
              </Typography>
            </Box>
          </motion.div>
          <Typography variant="body1" sx={{ color: uiSystem.colors.white }}>
            {getStatusText()}
          </Typography>
        </Box>
      );
    }

    if (task?.status === 'failed' || task?.status === 'cancelled') {
      return (
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box
            sx={{
              width: 24,
              height: 24,
              borderRadius: '50%',
              bgcolor: 'error.main',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <Typography variant="body2" sx={{ color: 'white', fontWeight: 'bold' }}>
              ✕
            </Typography>
          </Box>
          <Typography variant="body1" sx={{ color: uiSystem.colors.white }}>
            {getStatusText()}
          </Typography>
        </Box>
      );
    }

    return (
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <CircularProgress size={24} sx={{ color: uiSystem.colors.primary }} />
        <Typography variant="body1" sx={{ color: uiSystem.colors.white }}>
          {getStatusText()}
        </Typography>
      </Box>
    );
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <Paper
        sx={{
          p: 3,
          bgcolor: 'rgba(255, 255, 255, 0.05)',
          border: `1px solid ${uiSystem.colors.white20}`,
          borderRadius: 2,
        }}
      >
        <Box sx={{ mb: 2 }}>
          <Typography variant="h6" sx={{ color: uiSystem.colors.white, mb: 1 }}>
            Audio Generation Queue
          </Typography>
          <Typography variant="body2" sx={{ color: uiSystem.colors.white70 }}>
            {description}
          </Typography>
        </Box>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        {!task && !isLoading && (
          <Button
            variant="contained"
            fullWidth
            onClick={createTask}
            sx={uiSystem.buttons.primary}
          >
            Start Generation
          </Button>
        )}

        {isLoading && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CircularProgress size={20} />
            <Typography variant="body2" sx={{ color: uiSystem.colors.white70 }}>
              Creating task...
            </Typography>
          </Box>
        )}

        {task && (
          <Box>
            {renderStatusIndicator()}
            
            {task.status === 'running' && (
              <Box sx={{ mt: 2 }}>
                <LinearProgress
                  variant="determinate"
                  value={getProgressValue()}
                  sx={{
                    height: 8,
                    borderRadius: 4,
                    bgcolor: 'rgba(255, 255, 255, 0.1)',
                    '& .MuiLinearProgress-bar': {
                      bgcolor: uiSystem.colors.primary,
                    },
                  }}
                />
              </Box>
            )}

            {isPolling && task.status !== 'completed' && (
              <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                <Button
                  variant="outlined"
                  size="small"
                  onClick={cancelTask}
                  startIcon={<StopIcon />}
                  sx={{
                    color: uiSystem.colors.white,
                    borderColor: uiSystem.colors.white20,
                    '&:hover': {
                      borderColor: 'error.main',
                      color: 'error.main',
                    },
                  }}
                >
                  Cancel
                </Button>
              </Box>
            )}

            {task.status === 'completed' && task.result?.audio_url && (
              <Box sx={{ mt: 2 }}>
                <Button
                  variant="contained"
                  fullWidth
                  startIcon={<PlayIcon />}
                  onClick={() => onComplete?.(task.result!.audio_url!, task.result!)}
                  sx={uiSystem.buttons.primary}
                >
                  Play Audio
                </Button>
              </Box>
            )}
          </Box>
        )}
      </Paper>
    </motion.div>
  );
};

export default QueueAudioGenerator; 