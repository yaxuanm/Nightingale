import React from 'react';
import { View, StyleSheet, Image } from 'react-native';
import { Text, Button } from 'react-native-paper';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';

const OnboardingScreen = () => {
  const navigation = useNavigation();

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.content}>
        <View style={styles.logoContainer}>
          <Image
            source={require('../../assets/logo.png')}
            style={styles.logo}
            resizeMode="contain"
          />
        </View>

        <Text variant="headlineMedium" style={styles.title}>
          Nightingale
        </Text>

        <Text variant="bodyLarge" style={styles.subtitle}>
          Transform your thoughts into personalized soundscapes for focus, relaxation, and inspiration
        </Text>

        <Button
          mode="contained"
          onPress={() => navigation.navigate('Main')}
          style={styles.button}
          labelStyle={styles.buttonLabel}
        >
          Get Started
        </Button>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a2332',
  },
  content: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  logoContainer: {
    width: 120,
    height: 120,
    borderRadius: 28,
    backgroundColor: 'rgba(45, 156, 147, 0.2)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 32,
  },
  logo: {
    width: 100,
    height: 100,
    borderRadius: 24,
  },
  title: {
    color: '#ffffff',
    marginBottom: 12,
    textAlign: 'center',
    fontWeight: '700',
  },
  subtitle: {
    color: '#a0a0a0',
    textAlign: 'center',
    marginBottom: 60,
    maxWidth: 300,
    lineHeight: 24,
  },
  button: {
    width: 200,
    height: 50,
    backgroundColor: '#2d9c93',
    borderRadius: 25,
    justifyContent: 'center',
  },
  buttonLabel: {
    fontSize: 16,
    fontWeight: '600',
  },
});

export default OnboardingScreen; 