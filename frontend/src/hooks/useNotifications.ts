import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';

export interface Notification {
  id: number;
  message: string;
  type: string;
  is_read: boolean;
  created_at: string;
  related_entity_id?: number;
}

export const useNotifications = () => {
  return useQuery({
    queryKey: ['notifications'],
    queryFn: async () => {
      // Note: trailing slash is required to avoid 307 redirect from FastAPI
      const response = await api.get<Notification[]>('/notifications/');
      return response.data;
    },
    // Poll every 60 seconds — notifications are not real-time critical
    refetchInterval: 60000,
    // Don't refetch when window regains focus to avoid burst requests
    refetchOnWindowFocus: false,
  });
};

export const useMarkAsRead = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: number) => {
      const response = await api.put(`/notifications/${id}/read`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
};

export const useMarkAllAsRead = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async () => {
      const response = await api.put(`/notifications/read-all`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    },
  });
};
