import React from 'react';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { theme } from './theme';
import MainScreen from './components/MainScreen';
import Overview from './components/Overview';
import DemoOverview from './components/DemoOverview';
import Onboarding from './components/Onboarding';
import Player from './components/Player';
import Lockscreen from './components/Lockscreen';
import ChatScreen from './components/ChatScreen';
import AllScreensShowcase from './components/AllScreensShowcase';
import VideoIntro from './components/VideoIntro';
import SharePage from './components/SharePage';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<VideoIntro />} />
          <Route path="/overview" element={<Overview />} />
          <Route path="/demo" element={<DemoOverview />} />
          <Route path="/onboarding" element={<Onboarding />} />
          <Route path="/main" element={<MainScreen />} />
          <Route path="/chat" element={<ChatScreen />} />
          <Route path="/player" element={<Player audioUrl={''} description={''} />} />
          <Route path="/share/:shareId" element={<SharePage />} />
          <Route path="/video-intro" element={<VideoIntro />} />
          <Route path="/showcase" element={<AllScreensShowcase />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;
