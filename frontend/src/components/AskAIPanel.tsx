import React, { useState } from 'react';
import { X, Send, Bot, User, FileText, Globe } from 'lucide-react';
import { useAskAIContext } from '../contexts/AskAIContext';
import { useAskAI } from '../hooks/useAskAI';
import type { ChatMessage, AskSource } from '../types/ask';

export function AskAIPanel() {
  const { isOpen, setIsOpen, history, addMessage, clearHistory } = useAskAIContext();
  const [input, setInput] = useState('');
  const [selectedProvider, setSelectedProvider] = useState('gemini');
  const { mutate: askAI, isPending } = useAskAI();

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isPending) return;

    const userMsg: ChatMessage = { role: 'user', content: input };
    addMessage(userMsg);
    
    askAI(
      { question: input, model_provider: selectedProvider },
      {
        onSuccess: (data) => {
          addMessage({ role: 'assistant', content: data.answer, sources: data.sources });
        },
        onError: (err: any) => {
          const errMsg = err.response?.data?.detail || "Sorry, I encountered an error. Please try again.";
          addMessage({ role: 'assistant', content: errMsg });
        }
      }
    );
    
    setInput('');
  };

  return (
    <div className="fixed inset-y-0 right-0 z-50 w-full sm:w-96 bg-white dark:bg-zinc-900 shadow-2xl border-l border-gray-200 dark:border-zinc-800 flex flex-col transform transition-transform duration-300">
      <div className="p-4 border-b border-gray-200 dark:border-zinc-800 flex items-center justify-between bg-blue-50 dark:bg-zinc-950">
        <div className="flex items-center gap-2 text-blue-700 dark:text-blue-400 font-medium">
          <Bot size={20} />
          <span>Ask AI Atlas</span>
        </div>
        <div className="flex items-center gap-2">
          <select 
            value={selectedProvider} 
            onChange={(e) => setSelectedProvider(e.target.value)}
            className="text-xs bg-white dark:bg-zinc-800 border border-gray-300 dark:border-zinc-700 rounded px-2 py-1 outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="gemini">Gemini</option>
            <option value="groq">Groq</option>
            <option value="ollama">Ollama</option>
          </select>
          {history.length > 0 && (
            <button onClick={clearHistory} className="text-xs text-blue-600 dark:text-blue-400 hover:underline ml-2">
              Clear
            </button>
          )}
          <button onClick={() => setIsOpen(false)} className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 ml-2">
            <X size={20} />
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {history.length === 0 ? (
          <div className="text-center text-gray-500 dark:text-gray-400 mt-10 space-y-3">
            <Bot size={48} className="mx-auto opacity-20" />
            <p>I am your AI intelligence assistant.</p>
            <p className="text-sm">Ask me about companies, use cases, or recent F&B trends.</p>
          </div>
        ) : (
          history.map((msg, i) => (
            <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
                msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-zinc-800 text-blue-600 dark:text-blue-400'
              }`}>
                {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
              </div>
              <div className={`px-4 py-2 rounded-2xl max-w-[80%] ${
                msg.role === 'user' 
                  ? 'bg-blue-600 text-white rounded-tr-none' 
                  : 'bg-gray-100 dark:bg-zinc-800 text-gray-800 dark:text-gray-200 rounded-tl-none'
              }`}>
                <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                {msg.role === 'assistant' && msg.sources && msg.sources.length > 0 && (
                  <div className="mt-3 pt-3 border-t border-gray-200 dark:border-zinc-700 space-y-2">
                    <p className="text-xs font-semibold text-gray-500 dark:text-gray-400">Sources:</p>
                    {msg.sources.map((src: AskSource, idx: number) => {
                      let href = '#';
                      if (src.source_type === 'company' || src.source_type === 'problem') {
                        // In a real app we'd link to the exact company via slug. Here we fallback to directory if slug not available, or search by ID.
                        href = '/companies';
                      } else if (src.source_type === 'news') {
                        href = '/news';
                      }
                      
                      return (
                        <div key={idx} className="flex items-start gap-2 text-xs text-gray-600 dark:text-gray-400">
                          <a href={href} className="font-mono text-blue-500 hover:underline">[{src.marker}]</a>
                          <div className="flex flex-col">
                            <a href={href} className="font-medium capitalize hover:underline text-gray-700 dark:text-gray-300">
                              {src.source_type} (ID: {src.source_id})
                            </a>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        {isPending && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 bg-gray-200 dark:bg-zinc-800 text-blue-600 dark:text-blue-400">
              <Bot size={16} />
            </div>
            <div className="px-4 py-2 rounded-2xl bg-gray-100 dark:bg-zinc-800 rounded-tl-none">
              <div className="flex gap-1 items-center h-5">
                <div className="w-2 h-2 rounded-full bg-blue-400 animate-bounce" />
                <div className="w-2 h-2 rounded-full bg-blue-400 animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 rounded-full bg-blue-400 animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="p-4 border-t border-gray-200 dark:border-zinc-800 bg-white dark:bg-zinc-900">
        <form onSubmit={handleSubmit} className="relative">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about anything..."
            disabled={isPending}
            className="w-full pl-4 pr-12 py-3 bg-gray-100 dark:bg-zinc-800 border-transparent focus:bg-white dark:focus:bg-zinc-950 rounded-full text-sm outline-none focus:ring-2 focus:ring-blue-500 transition-all disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={!input.trim() || isPending}
            className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 flex items-center justify-center bg-blue-600 text-white rounded-full hover:bg-blue-700 disabled:opacity-50 disabled:hover:bg-blue-600 transition-colors"
          >
            <Send size={14} />
          </button>
        </form>
      </div>
    </div>
  );
}
