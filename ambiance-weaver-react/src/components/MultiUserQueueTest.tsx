import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Button,
  Paper,
  Container,
  Grid,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Alert,
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import QueueAudioGenerator from './QueueAudioGenerator';
import { uiSystem } from '../theme/uiSystem';

interface UserTask {
  userId: string;
  taskId: string;
  description: string;
  status: string;
  progress: number;
  queuePosition?: number;
}

const MultiUserQueueTest: React.FC = () => {
  const [users, setUsers] = useState<string[]>(['user1', 'user2', 'user3']);
  const [userTasks, setUserTasks] = useState<UserTask[]>([]);
  const [queueStats, setQueueStats] = useState<any>(null);
  const [newUserId, setNewUserId] = useState('');
  const navigate = useNavigate();

  // 获取队列统计
  const fetchQueueStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/queue/stats');
      if (response.ok) {
        const stats = await response.json();
        setQueueStats(stats);
      }
    } catch (error) {
      console.error('Failed to fetch queue stats:', error);
    }
  };

  // 获取用户任务
  const fetchUserTasks = async (userId: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/queue/user/${userId}/tasks`);
      if (response.ok) {
        const data = await response.json();
        return data.tasks || [];
      }
    } catch (error) {
      console.error(`Failed to fetch tasks for user ${userId}:`, error);
    }
    return [];
  };

  // 更新所有用户任务
  const updateAllUserTasks = async () => {
    const allTasks: UserTask[] = [];
    for (const userId of users) {
      const tasks = await fetchUserTasks(userId);
      tasks.forEach((task: any) => {
        allTasks.push({
          userId,
          taskId: task.task_id,
          description: task.result?.description || 'Unknown',
          status: task.status,
          progress: task.progress || 0,
          queuePosition: task.queue_position,
        });
      });
    }
    setUserTasks(allTasks);
  };

  // 添加新用户
  const addUser = () => {
    if (newUserId && !users.includes(newUserId)) {
      setUsers([...users, newUserId]);
      setNewUserId('');
    }
  };

  // 移除用户
  const removeUser = (userId: string) => {
    setUsers(users.filter(u => u !== userId));
    setUserTasks(userTasks.filter(t => t.userId !== userId));
  };

  // 定期更新数据
  useEffect(() => {
    const interval = setInterval(() => {
      fetchQueueStats();
      updateAllUserTasks();
    }, 2000);

    return () => clearInterval(interval);
  }, [users]);

  // 初始加载
  useEffect(() => {
    fetchQueueStats();
    updateAllUserTasks();
  }, []);

  const handleComplete = (audioUrl: string, taskResult: any) => {
    console.log('Task completed:', { audioUrl, taskResult });
    navigate('/player', { 
      state: { 
        audioUrl, 
        description: taskResult.description,
        taskResult 
      } 
    });
  };

  const handleError = (error: string) => {
    console.error('Queue error:', error);
  };

  const handleCancel = () => {
    console.log('Task cancelled');
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ textAlign: 'center', mb: 4 }}>
        <Typography variant="h4" sx={{ color: uiSystem.colors.white, mb: 2 }}>
          Multi-User Queue Test
        </Typography>
        <Typography variant="body1" sx={{ color: uiSystem.colors.white70 }}>
          Test the queue system with multiple concurrent users
        </Typography>
      </Box>

      {/* 队列统计 */}
      {queueStats && (
        <Paper sx={{ p: 3, mb: 3, bgcolor: 'rgba(255, 255, 255, 0.05)', border: `1px solid ${uiSystem.colors.white20}` }}>
          <Typography variant="h6" sx={{ color: uiSystem.colors.white, mb: 2 }}>
            Queue Statistics
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: uiSystem.colors.primary }}>
                  {queueStats.queue_size || 0}
                </Typography>
                <Typography variant="body2" sx={{ color: uiSystem.colors.white70 }}>
                  Queue Size
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: uiSystem.colors.primary }}>
                  {queueStats.running_count || 0}
                </Typography>
                <Typography variant="body2" sx={{ color: uiSystem.colors.white70 }}>
                  Running Tasks
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: uiSystem.colors.primary }}>
                  {queueStats.estimated_wait_time || 0}
                </Typography>
                <Typography variant="body2" sx={{ color: uiSystem.colors.white70 }}>
                  Est. Wait (min)
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={6} md={3}>
              <Box sx={{ textAlign: 'center' }}>
                <Typography variant="h4" sx={{ color: uiSystem.colors.primary }}>
                  {queueStats.max_concurrent_tasks || 3}
                </Typography>
                <Typography variant="body2" sx={{ color: uiSystem.colors.white70 }}>
                  Max Concurrent
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </Paper>
      )}

      {/* 用户管理 */}
      <Paper sx={{ p: 3, mb: 3, bgcolor: 'rgba(255, 255, 255, 0.05)', border: `1px solid ${uiSystem.colors.white20}` }}>
        <Typography variant="h6" sx={{ color: uiSystem.colors.white, mb: 2 }}>
          User Management
        </Typography>
        <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
          <TextField
            label="New User ID"
            value={newUserId}
            onChange={(e) => setNewUserId(e.target.value)}
            size="small"
            sx={{
              '& .MuiOutlinedInput-root': {
                color: uiSystem.colors.white,
                fieldset: { borderColor: uiSystem.colors.white20 },
              },
              '& .MuiInputLabel-root': {
                color: uiSystem.colors.white70,
              },
            }}
          />
          <Button
            variant="contained"
            onClick={addUser}
            disabled={!newUserId}
            sx={uiSystem.buttons.primary}
          >
            Add User
          </Button>
        </Box>
        <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          {users.map((userId) => (
            <Chip
              key={userId}
              label={userId}
              onDelete={() => removeUser(userId)}
              sx={{
                bgcolor: uiSystem.colors.white05,
                color: uiSystem.colors.primary,
                border: `1px solid ${uiSystem.colors.white20}`,
                '& .MuiChip-deleteIcon': {
                  color: uiSystem.colors.white70,
                },
              }}
            />
          ))}
        </Box>
      </Paper>

      {/* 用户任务 */}
      <Grid container spacing={3}>
        {users.map((userId) => (
          <Grid item xs={12} md={6} lg={4} key={userId}>
            <Paper
              sx={{
                p: 3,
                bgcolor: 'rgba(255, 255, 255, 0.05)',
                border: `1px solid ${uiSystem.colors.white20}`,
                borderRadius: 2,
              }}
            >
              <Typography variant="h6" sx={{ color: uiSystem.colors.white, mb: 2 }}>
                User: {userId}
              </Typography>
              
              <QueueAudioGenerator
                description={`${userId}'s audio request`}
                duration={20}
                mode="default"
                userId={userId}
                priority="normal"
                onComplete={handleComplete}
                onError={handleError}
                onCancel={handleCancel}
              />

              {/* 用户任务列表 */}
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" sx={{ color: uiSystem.colors.white70, mb: 1 }}>
                  Recent Tasks:
                </Typography>
                {userTasks
                  .filter(task => task.userId === userId)
                  .slice(0, 3)
                  .map((task) => (
                    <Box key={task.taskId} sx={{ mb: 1, p: 1, bgcolor: 'rgba(255, 255, 255, 0.03)', borderRadius: 1 }}>
                      <Typography variant="body2" sx={{ color: uiSystem.colors.white }}>
                        {task.description}
                      </Typography>
                      <Typography variant="caption" sx={{ color: uiSystem.colors.white70 }}>
                        {task.status} - {task.progress}%
                        {task.queuePosition && ` (Queue: ${task.queuePosition})`}
                      </Typography>
                    </Box>
                  ))}
              </Box>
            </Paper>
          </Grid>
        ))}
      </Grid>

      {/* 返回按钮 */}
      <Box sx={{ mt: 4, textAlign: 'center' }}>
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

export default MultiUserQueueTest; 