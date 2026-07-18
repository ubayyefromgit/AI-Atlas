import { useMutation } from '@tanstack/react-query';
import api from '../services/api';
import type { AskAIRequest, AskAIResponse } from '../types/ask';

export const useAskAI = () => {
  return useMutation({
    mutationFn: async (data: AskAIRequest) => {
      const response = await api.post<AskAIResponse>('/ask', data);
      return response.data;
    },
  });
};
