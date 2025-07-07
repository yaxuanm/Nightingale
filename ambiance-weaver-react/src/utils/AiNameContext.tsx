import React, { createContext, useState, useContext, useEffect, ReactNode } from 'react';

interface AiNameContextType {
  aiName: string;
  setAiName: (name: string) => void;
}

const AiNameContext = createContext<AiNameContextType | undefined>(undefined);

export const AiNameProvider = ({ children }: { children: ReactNode }) => {
  // Always use 'Nightingale' as the AI name
  const aiName = 'Nightingale';
  const setAiName = () => {};
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