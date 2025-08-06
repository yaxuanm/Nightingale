/**
 * 安全的剪贴板操作工具函数
 * 支持现代浏览器的 Clipboard API 和回退到传统方法
 */

export const safeCopyToClipboard = async (text: string): Promise<boolean> => {
  try {
    // 检查 navigator.clipboard 是否存在且可用
    if (typeof navigator !== 'undefined' && 
        navigator.clipboard && 
        typeof navigator.clipboard.writeText === 'function') {
      await navigator.clipboard.writeText(text);
      return true;
    } else {
      // 回退到传统方法
      const tempInput = document.createElement('input');
      tempInput.value = text;
      tempInput.style.position = 'absolute';
      tempInput.style.left = '-9999px';
      tempInput.style.opacity = '0';
      document.body.appendChild(tempInput);
      tempInput.select();
      tempInput.setSelectionRange(0, 99999); // 兼容移动端
      const success = document.execCommand('copy');
      document.body.removeChild(tempInput);
      return success;
    }
  } catch (error) {
    console.error('Clipboard operation failed:', error);
    // 如果所有方法都失败，尝试显示文本让用户手动复制
    try {
      alert(`Please copy this link manually:\n\n${text}`);
      return false;
    } catch (alertError) {
      console.error('Alert also failed:', alertError);
      return false;
    }
  }
};

/**
 * 检查剪贴板是否可用
 */
export const isClipboardAvailable = (): boolean => {
  return !!(typeof navigator !== 'undefined' && 
            navigator.clipboard && 
            typeof navigator.clipboard.writeText === 'function');
};

/**
 * 复制文本到剪贴板并返回结果消息
 */
export const copyTextWithMessage = async (text: string): Promise<{ success: boolean; message: string }> => {
  const success = await safeCopyToClipboard(text);
  
  if (success) {
    return {
      success: true,
      message: 'Copied to clipboard!'
    };
  } else {
    return {
      success: false,
      message: 'Failed to copy. Please copy manually.'
    };
  }
}; 