// UI Design System - 统一的设计标准
export const uiSystem = {
  // 字号系统
  typography: {
    // 主标题 - 用于页面主要标题
    h1: {
      fontSize: '2rem',
      fontWeight: 700,
      lineHeight: 1.2,
      '@media (min-width:900px)': { fontSize: '2.5rem' },
      '@media (min-width:1280px)': { fontSize: '3rem' },
      '@media (min-width:1920px)': { fontSize: '3.5rem' },
    },
    // 副标题 - 用于页面次要标题
    h2: {
      fontSize: '1.3rem',
      fontWeight: 600,
      lineHeight: 1.3,
      '@media (min-width:900px)': { fontSize: '2rem' },
      '@media (min-width:1280px)': { fontSize: '2.4rem' },
      '@media (min-width:1920px)': { fontSize: '2.8rem' },
    },
    // 卡片标题 - 用于卡片和模块标题
    h3: {
      fontSize: '1.1rem',
      fontWeight: 600,
      lineHeight: 1.4,
      '@media (min-width:900px)': { fontSize: '1.5rem' },
      '@media (min-width:1280px)': { fontSize: '1.8rem' },
      '@media (min-width:1920px)': { fontSize: '2.2rem' },
    },
    // 小标题 - 用于分组标题
    h4: {
      fontSize: '1rem',
      fontWeight: 600,
      lineHeight: 1.4,
      '@media (min-width:900px)': { fontSize: '1.25rem' },
      '@media (min-width:1280px)': { fontSize: '1.5rem' },
      '@media (min-width:1920px)': { fontSize: '1.7rem' },
    },
    // 正文大 - 用于重要文本
    body1: {
      fontSize: '1rem',
      fontWeight: 400,
      lineHeight: 1.6,
      '@media (min-width:900px)': { fontSize: '1.2rem' },
      '@media (min-width:1280px)': { fontSize: '1.3rem' },
      '@media (min-width:1920px)': { fontSize: '1.5rem' },
    },
    // 正文 - 用于普通文本
    body2: {
      fontSize: '0.95rem',
      fontWeight: 400,
      lineHeight: 1.6,
      '@media (min-width:900px)': { fontSize: '1.1rem' },
      '@media (min-width:1280px)': { fontSize: '1.2rem' },
      '@media (min-width:1920px)': { fontSize: '1.3rem' },
    },
    // 正文小 - 用于辅助文本
    body3: {
      fontSize: '1rem',
      fontWeight: 400,
      lineHeight: 1.5,
      '@media (min-width:900px)': { fontSize: '1.1rem' },
      '@media (min-width:1280px)': { fontSize: '1.2rem' },
      '@media (min-width:1920px)': { fontSize: '1.3rem' },
    },
    // 标签 - 用于按钮、标签等
    label: {
      fontSize: '1rem',
      fontWeight: 500,
      lineHeight: 1.4,
      '@media (min-width:900px)': { fontSize: '1.1rem' },
      '@media (min-width:1280px)': { fontSize: '1.2rem' },
      '@media (min-width:1920px)': { fontSize: '1.3rem' },
    },
  },

  // 间距系统
  spacing: {
    // 页面级间距
    pagePadding: {
      xs: '16px',
      sm: '24px',
      md: '32px',
      lg: '48px',
      xl: '64px',
    },
    // 组件间距
    section: '32px', // 主要区块间距
    large: '24px',   // 大间距
    medium: '16px',  // 中等间距
    small: '12px',   // 小间距
    tiny: '8px',     // 微小间距
    '@media (min-width:1280px)': {
      section: '48px',
      large: '32px',
      medium: '24px',
      small: '16px',
      tiny: '12px',
    },
    '@media (min-width:1920px)': {
      section: '64px',
      large: '40px',
      medium: '32px',
      small: '20px',
      tiny: '16px',
    },
  },

  // 按钮系统
  buttons: {
    // 主要按钮 - 用于主要操作
    primary: {
      background: 'linear-gradient(135deg, #2d9c93 0%, #1a5f5a 100%)',
      color: '#ffffff',
      padding: '12px 32px',
      borderRadius: '25px',
      fontSize: '1.15rem',
      fontWeight: 600,
      border: 'none',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      '@media (min-width:900px)': { fontSize: '1.22rem' },
      '@media (min-width:1280px)': { fontSize: '1.28rem' },
      '@media (min-width:1920px)': { fontSize: '1.35rem' },
      '&:hover': {
        background: 'linear-gradient(135deg, #1a5f5a 0%, #2d9c93 100%)',
        transform: 'translateY(-2px)',
        boxShadow: '0 8px 24px rgba(45, 156, 147, 0.3)',
      },
      '&:disabled': {
        background: 'rgba(255, 255, 255, 0.1)',
        color: 'rgba(255, 255, 255, 0.5)',
        cursor: 'not-allowed',
        transform: 'none',
        boxShadow: 'none',
      },
    },
    // 次要按钮 - 用于次要操作
    secondary: {
      background: 'rgba(255, 255, 255, 0.05)',
      color: '#ffffff',
      padding: '10px 24px',
      borderRadius: '20px',
      fontSize: '1.08rem',
      fontWeight: 500,
      border: '1px solid rgba(255, 255, 255, 0.2)',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      '@media (min-width:900px)': { fontSize: '1.15rem' },
      '@media (min-width:1280px)': { fontSize: '1.22rem' },
      '@media (min-width:1920px)': { fontSize: '1.28rem' },
      '&:hover': {
        background: 'rgba(255, 255, 255, 0.1)',
        borderColor: '#2d9c93',
        transform: 'translateY(-1px)',
      },
    },
    // 图标按钮 - 用于工具按钮
    icon: {
      background: 'rgba(255, 255, 255, 0.05)',
      color: '#2d9c93',
      padding: '8px',
      borderRadius: '50%',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      cursor: 'pointer',
      transition: 'all 0.3s ease',
      '&:hover': {
        background: 'rgba(45, 156, 147, 0.1)',
        transform: 'scale(1.05)',
      },
    },
  },

  // 颜色系统
  colors: {
    primary: '#2d9c93',
    primaryDark: '#1a5f5a',
    primaryLight: '#4db3a9',
    white: '#ffffff',
    white70: 'rgba(255, 255, 255, 0.7)',
    white50: 'rgba(255, 255, 255, 0.5)',
    white20: 'rgba(255, 255, 255, 0.2)',
    white10: 'rgba(255, 255, 255, 0.1)',
    white05: 'rgba(255, 255, 255, 0.05)',
    background: 'rgba(12, 26, 26, 0.8)',
    surface: 'rgba(255, 255, 255, 0.05)',
  },

  // 圆角系统
  borderRadius: {
    small: '8px',
    medium: '12px',
    large: '16px',
    xlarge: '20px',
    round: '25px',
    circle: '50%',
  },

  // 阴影系统
  shadows: {
    small: '0 2px 8px rgba(0, 0, 0, 0.1)',
    medium: '0 4px 16px rgba(0, 0, 0, 0.15)',
    large: '0 8px 24px rgba(0, 0, 0, 0.2)',
    primary: '0 8px 24px rgba(45, 156, 147, 0.3)',
  },
};

// 响应式断点
export const breakpoints = {
  xs: 0,
  sm: 600,
  md: 960,
  lg: 1280,
  xl: 1920,
};

// 工具函数
export const getResponsiveValue = (values: { [key: string]: any }) => {
  return (theme: any) => {
    const breakpoint = theme.breakpoints.down('sm') ? 'xs' : 
                      theme.breakpoints.down('md') ? 'sm' :
                      theme.breakpoints.down('lg') ? 'md' :
                      theme.breakpoints.down('xl') ? 'lg' : 'xl';
    return values[breakpoint] || values.md || values.sm || values.xs;
  };
}; 