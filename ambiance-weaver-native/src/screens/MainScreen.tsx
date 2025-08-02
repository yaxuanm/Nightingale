import React, { useState } from 'react';
import {
  View,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
} from 'react-native';
import { Text, Button, IconButton, Surface } from 'react-native-paper';
import { useNavigation } from '@react-navigation/native';
import { SafeAreaView } from 'react-native-safe-area-context';

const TagCard = ({ icon: Icon, title, onPress }) => (
  <TouchableOpacity onPress={onPress}>
    <Surface style={styles.tagCard}>
      <Icon size={24} color="#2d9c93" />
      <Text style={styles.tagTitle}>{title}</Text>
    </Surface>
  </TouchableOpacity>
);

const MainScreen = () => {
  const navigation = useNavigation();
  const [inputValue, setInputValue] = useState('');
  const [selectedTag, setSelectedTag] = useState(null);

  const handleTagPress = (tag) => {
    setSelectedTag(tag);
  };

  const handleSubmit = () => {
    navigation.navigate('Player');
  };

  return (
    <SafeAreaView style={styles.container}>
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.header}>
          <Text variant="headlineMedium" style={styles.title}>
            Welcome back, Alex
          </Text>
          <Text variant="bodyLarge" style={styles.subtitle}>
            Describe your perfect atmosphere or paste a poem, quote, or movie line to inspire music
          </Text>
        </View>

        <View style={styles.inputContainer}>
          <View style={styles.inputHeader}>
            <IconButton
              icon="microphone"
              size={24}
              onPress={() => {}}
            />
            <IconButton
              icon="help-circle-outline"
              size={24}
              onPress={() => {}}
            />
          </View>

          <TextInput
            multiline
            style={styles.input}
            value={inputValue}
            onChangeText={setInputValue}
            placeholder="Try: 'A cozy café on a rainy afternoon'"
            placeholderTextColor="#666"
          />
        </View>

        <View style={styles.tagsContainer}>
          <View style={styles.tagsGrid}>
            <TagCard
              icon="brain"
              title="Focus"
              onPress={() => handleTagPress('focus')}
            />
            <TagCard
              icon="bed"
              title="Relax"
              onPress={() => handleTagPress('relax')}
            />
            <TagCard
              icon="lightbulb"
              title="Inspire"
              onPress={() => handleTagPress('inspire')}
            />
            <TagCard
              icon="spa"
              title="Meditate"
              onPress={() => handleTagPress('meditate')}
            />
          </View>
        </View>

        <Button
          mode="contained"
          onPress={handleSubmit}
          disabled={!selectedTag && !inputValue}
          style={styles.button}
        >
          Chat with Nightingale
        </Button>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a2332',
  },
  scrollContent: {
    padding: 16,
  },
  header: {
    alignItems: 'center',
    marginBottom: 32,
  },
  title: {
    color: '#fff',
    marginBottom: 8,
    textAlign: 'center',
  },
  subtitle: {
    color: '#ccc',
    textAlign: 'center',
  },
  inputContainer: {
    marginBottom: 24,
  },
  inputHeader: {
    flexDirection: 'row',
    justifyContent: 'flex-end',
    marginBottom: 8,
  },
  input: {
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderWidth: 1.5,
    borderColor: 'rgba(255, 255, 255, 0.13)',
    borderRadius: 8,
    padding: 16,
    color: '#fff',
    minHeight: 120,
    textAlignVertical: 'top',
  },
  tagsContainer: {
    marginBottom: 24,
  },
  tagsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 16,
  },
  tagCard: {
    flex: 1,
    minWidth: '45%',
    padding: 16,
    alignItems: 'center',
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderWidth: 1.5,
    borderColor: 'rgba(255, 255, 255, 0.13)',
    borderRadius: 8,
  },
  tagTitle: {
    color: '#fff',
    marginTop: 8,
    fontWeight: '600',
  },
  button: {
    marginTop: 16,
  },
});

export default MainScreen; 