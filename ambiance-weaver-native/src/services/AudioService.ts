import TrackPlayer, { Event, State } from 'react-native-track-player';

let isSetup = false;
let loopCount = 0;
let totalLoops = 3;
let onLoopComplete = null;

export const setupPlayer = async () => {
  if (isSetup) return;

  try {
    await TrackPlayer.setupPlayer();
    await TrackPlayer.updateOptions({
      capabilities: [
        TrackPlayer.CAPABILITY_PLAY,
        TrackPlayer.CAPABILITY_PAUSE,
        TrackPlayer.CAPABILITY_SKIP_TO_NEXT,
        TrackPlayer.CAPABILITY_SKIP_TO_PREVIOUS,
      ],
      compactCapabilities: [
        TrackPlayer.CAPABILITY_PLAY,
        TrackPlayer.CAPABILITY_PAUSE,
      ],
    });
    
    // 设置播放结束事件监听
    TrackPlayer.addEventListener(Event.PlaybackTrackChanged, async (event) => {
      if (event.nextTrack === null && loopCount < totalLoops - 1) {
        // 继续循环播放
        loopCount++;
        const currentTrack = await TrackPlayer.getCurrentTrack();
        if (currentTrack !== null) {
          await TrackPlayer.seekTo(0);
          await TrackPlayer.play();
        }
      } else if (event.nextTrack === null && loopCount >= totalLoops - 1) {
        // 播放完成
        loopCount = 0;
        if (onLoopComplete) {
          onLoopComplete();
        }
      }
    });
    
    isSetup = true;
  } catch (error) {
    console.error('Error setting up player:', error);
  }
};

export const setLoopSettings = (loops: number, onComplete?: () => void) => {
  totalLoops = loops;
  onLoopComplete = onComplete;
};

export const resetLoopCount = () => {
  loopCount = 0;
};

export const getLoopStatus = () => {
  return { loopCount, totalLoops };
};

export const addTrack = async (track) => {
  try {
    await TrackPlayer.reset();
    await TrackPlayer.add(track);
  } catch (error) {
    console.error('Error adding track:', error);
  }
};

export const togglePlayback = async () => {
  const state = await TrackPlayer.getState();
  if (state === State.Playing) {
    await TrackPlayer.pause();
  } else {
    await TrackPlayer.play();
  }
};

export const skipToNext = async () => {
  try {
    await TrackPlayer.skipToNext();
  } catch (error) {
    console.error('Error skipping to next:', error);
  }
};

export const skipToPrevious = async () => {
  try {
    await TrackPlayer.skipToPrevious();
  } catch (error) {
    console.error('Error skipping to previous:', error);
  }
};

export const getProgress = async () => {
  try {
    const position = await TrackPlayer.getPosition();
    const duration = await TrackPlayer.getDuration();
    return { position, duration };
  } catch (error) {
    console.error('Error getting progress:', error);
    return { position: 0, duration: 0 };
  }
};

export const seekTo = async (position) => {
  try {
    await TrackPlayer.seekTo(position);
  } catch (error) {
    console.error('Error seeking:', error);
  }
};

export const setVolume = async (volume) => {
  try {
    await TrackPlayer.setVolume(volume / 100);
  } catch (error) {
    console.error('Error setting volume:', error);
  }
}; 