/**
 * 纯前端分享工具函数
 * 通过 URL 参数传递数据，无需后端支持
 */

export interface ShareData {
  audio_url: string;
  background_url?: string;
  description?: string;
  title?: string;
}

/**
 * 生成分享 URL
 */
export const generateShareUrl = (data: ShareData): string => {
  const baseUrl = window.location.origin + window.location.pathname;
  const params = new URLSearchParams();
  
  // 添加数据到 URL 参数
  if (data.audio_url) {
    params.append('audio', encodeURIComponent(data.audio_url));
  }
  if (data.background_url) {
    params.append('bg', encodeURIComponent(data.background_url));
  }
  if (data.description) {
    params.append('desc', encodeURIComponent(data.description));
  }
  if (data.title) {
    params.append('title', encodeURIComponent(data.title));
  }
  
  // 添加时间戳确保唯一性
  params.append('t', Date.now().toString());
  
  return `${baseUrl}?${params.toString()}`;
};

/**
 * 从 URL 参数解析分享数据
 */
export const parseShareData = (): ShareData | null => {
  const params = new URLSearchParams(window.location.search);
  
  const audio_url = params.get('audio');
  if (!audio_url) {
    return null; // 没有音频 URL，不是分享链接
  }
  
  try {
    return {
      audio_url: decodeURIComponent(audio_url),
      background_url: params.get('bg') ? decodeURIComponent(params.get('bg')!) : undefined,
      description: params.get('desc') ? decodeURIComponent(params.get('desc')!) : undefined,
      title: params.get('title') ? decodeURIComponent(params.get('title')!) : undefined,
    };
  } catch (error) {
    console.error('Error parsing share data:', error);
    return null;
  }
};

/**
 * 检查当前页面是否是分享页面
 */
export const isSharePage = (): boolean => {
  return parseShareData() !== null;
};

/**
 * 清理 URL 参数（移除分享参数）
 */
export const cleanShareParams = (): void => {
  const url = new URL(window.location.href);
  const params = url.searchParams;
  
  // 移除分享相关的参数
  params.delete('audio');
  params.delete('bg');
  params.delete('desc');
  params.delete('title');
  params.delete('t');
  
  // 更新 URL（不刷新页面）
  window.history.replaceState({}, '', url.toString());
};

/**
 * 生成分享页面的标题
 */
export const generateShareTitle = (data: ShareData): string => {
  if (data.title) {
    return data.title;
  }
  if (data.description) {
    return data.description.length > 50 
      ? data.description.substring(0, 50) + '...'
      : data.description;
  }
  return 'Nightingale Soundscape';
}; 