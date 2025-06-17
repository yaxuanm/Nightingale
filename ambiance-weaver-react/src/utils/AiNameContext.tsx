import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';

interface AiNameContextType {
  aiName: string | null;
  setAiName: (name: string) => void;
}

const AiNameContext = createContext<AiNameContextType | undefined>(undefined);

export const AiNameProvider = ({ children }: { children: ReactNode }) => {
  const [aiName, setAiNameState] = useState<string | null>(null);

  // Load AI name from localStorage on initial render
  useEffect(() => {
    const storedAiName = localStorage.getItem('aiName');
    if (storedAiName) {
      setAiNameState(storedAiName);
    }
  }, []);

  // Save AI name to localStorage whenever it changes
  const setAiName = (name: string) => {
    setAiNameState(name);
    localStorage.setItem('aiName', name);
  };

  return (
    <AiNameContext.Provider value={{ aiName, setAiName }}>
      {children}
    </AiNameContext.Provider>
  );
};

export const useAiName = () => {
  const context = useContext(AiNameContext);
  if (context === undefined) {
    throw new Error('useAiName must be used within an AiNameProvider');
  }
  return context;
}; 