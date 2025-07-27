// API 配置
export const API_CONFIG = {
  // Gemini API 服务 (端口 8000)
  GEMINI_API_BASE_URL: process.env.REACT_APP_GEMINI_API_URL || 'http://localhost:8000',
  
  // Stable Audio 服务 (端口 8001)
  STABLE_AUDIO_API_BASE_URL: process.env.REACT_APP_STABLE_AUDIO_API_URL || 'http://localhost:8001',
  
  // 前端服务 (端口 3000)
  FRONTEND_BASE_URL: process.env.REACT_APP_FRONTEND_URL || 'http://localhost:3000',
};

// API 端点
export const API_ENDPOINTS = {
  // Gemini API 端点
  GENERATE_INSPIRATION_CHIPS: `${API_CONFIG.GEMINI_API_BASE_URL}/api/generate-inspiration-chips`,
  GENERATE_SCENE: `${API_CONFIG.GEMINI_API_BASE_URL}/api/generate-scene`,
  EDIT_PROMPT: `${API_CONFIG.GEMINI_API_BASE_URL}/api/edit-prompt`,
  GENERATE_PROMPT: `${API_CONFIG.GEMINI_API_BASE_URL}/api/generate-prompt`,
  CREATE_STORY: `${API_CONFIG.GEMINI_API_BASE_URL}/api/create-story`,
  GENERATE_BACKGROUND: `${API_CONFIG.GEMINI_API_BASE_URL}/api/generate-background`,
  CHAT: `${API_CONFIG.GEMINI_API_BASE_URL}/api/chat`,
  GENERATE_OPTIONS: `${API_CONFIG.GEMINI_API_BASE_URL}/api/generate-options`,
  MUSIC_PROMPT: `${API_CONFIG.GEMINI_API_BASE_URL}/api/music-prompt`,
  CREATE_STORY_MUSIC: `${API_CONFIG.GEMINI_API_BASE_URL}/api/create-story-music`,
  GENERATE_MUSIC: `${API_CONFIG.GEMINI_API_BASE_URL}/api/generate-music`,
  CREATE_SHARE: `${API_CONFIG.GEMINI_API_BASE_URL}/api/create-share`,
  SHARE: `${API_CONFIG.GEMINI_API_BASE_URL}/api/share`,
  
  // Stable Audio API 端点
  GENERATE_AUDIO: `${API_CONFIG.STABLE_AUDIO_API_BASE_URL}/api/generate-audio`,
};

// 获取完整的分享URL
export const getShareUrl = (shareId: string) => {
  return `${API_CONFIG.GEMINI_API_BASE_URL}/api/share/${shareId}`;
};

// 获取完整的API URL
export const getApiUrl = (endpoint: string) => {
  return `${API_CONFIG.GEMINI_API_BASE_URL}${endpoint}`;
}; 