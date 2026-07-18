import React, { createContext, useContext, useState } from 'react';
import type { ChatMessage } from '../types/ask';

interface AskAIContextType {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
  toggle: () => void;
  history: ChatMessage[];
  addMessage: (msg: ChatMessage) => void;
  clearHistory: () => void;
}

const AskAIContext = createContext<AskAIContextType | undefined>(undefined);

export function AskAIProvider({ children }: { children: React.ReactNode }) {
  const [isOpen, setIsOpen] = useState(false);
  const [history, setHistory] = useState<ChatMessage[]>([]);

  const toggle = () => setIsOpen((prev) => !prev);
  const addMessage = (msg: ChatMessage) => setHistory((prev) => [...prev, msg]);
  const clearHistory = () => setHistory([]);

  return (
    <AskAIContext.Provider value={{ isOpen, setIsOpen, toggle, history, addMessage, clearHistory }}>
      {children}
    </AskAIContext.Provider>
  );
}

export const useAskAIContext = () => {
  const context = useContext(AskAIContext);
  if (context === undefined) {
    throw new Error('useAskAIContext must be used within an AskAIProvider');
  }
  return context;
};
