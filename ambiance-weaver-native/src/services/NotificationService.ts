import TrackPlayer, { Event } from 'react-native-track-player';
import { Platform } from 'react-native';

export const setupNotifications = async () => {
  if (Platform.OS === 'android') {
    await TrackPlayer.updateOptions({
      android: {
        appKilledPlaybackBehavior: 'StopPlaybackAndRemoveNotification',
      },
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
      notificationCapabilities: [
        TrackPlayer.CAPABILITY_PLAY,
        TrackPlayer.CAPABILITY_PAUSE,
        TrackPlayer.CAPABILITY_SKIP_TO_NEXT,
        TrackPlayer.CAPABILITY_SKIP_TO_PREVIOUS,
      ],
    });
  }
};

export const updateNotification = async (track) => {
  await TrackPlayer.updateNowPlayingMetadata({
    title: track.title,
    artist: 'Ambiance AI',
    artwork: track.artwork,
  });
};

export const setupPlayerEvents = () => {
  TrackPlayer.addEventListener(Event.RemotePlay, () => TrackPlayer.play());
  TrackPlayer.addEventListener(Event.RemotePause, () => TrackPlayer.pause());
  TrackPlayer.addEventListener(Event.RemoteNext, () => TrackPlayer.skipToNext());
  TrackPlayer.addEventListener(Event.RemotePrevious, () => TrackPlayer.skipToPrevious());
}; 