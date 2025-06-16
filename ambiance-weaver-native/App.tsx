import React, { useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { Provider as PaperProvider } from 'react-native-paper';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { setupPlayer } from './src/services/AudioService';
import { setupNotifications, setupPlayerEvents } from './src/services/NotificationService';

// Screens
import MainScreen from './src/screens/MainScreen';
import PlayerScreen from './src/screens/PlayerScreen';
import LockscreenScreen from './src/screens/LockscreenScreen';
import OnboardingScreen from './src/screens/OnboardingScreen';

const Stack = createNativeStackNavigator();

export default function App() {
  useEffect(() => {
    const setup = async () => {
      await setupPlayer();
      await setupNotifications();
      setupPlayerEvents();
    };
    setup();
  }, []);

  return (
    <SafeAreaProvider>
      <PaperProvider>
        <NavigationContainer>
          <Stack.Navigator
            initialRouteName="Onboarding"
            screenOptions={{
              headerShown: false,
              animation: 'fade',
            }}
          >
            <Stack.Screen name="Onboarding" component={OnboardingScreen} />
            <Stack.Screen name="Main" component={MainScreen} />
            <Stack.Screen name="Player" component={PlayerScreen} />
            <Stack.Screen name="Lockscreen" component={LockscreenScreen} />
          </Stack.Navigator>
        </NavigationContainer>
      </PaperProvider>
    </SafeAreaProvider>
  );
} 