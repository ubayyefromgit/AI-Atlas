import { useMutation } from '@tanstack/react-query';
import api from '../services/api';
import type { AgentAskRequest, AgentAskResponse } from '../types/ask';

export const useAgentChat = () => {
  return useMutation({
    mutationFn: async (data: AgentAskRequest) => {
      const response = await api.post<AgentAskResponse>('/agent/chat', data);
      return response.data;
    },
  });
};
