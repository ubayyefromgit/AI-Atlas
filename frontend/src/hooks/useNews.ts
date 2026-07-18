import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';
import type { NewsItem } from '../types/news';

export const useCompanyNews = (slug: string | undefined) => {
  return useQuery({
    queryKey: ['company-news', slug],
    queryFn: async () => {
      if (!slug) throw new Error('Slug is required');
      const response = await api.get<NewsItem[]>(`/news/companies/${slug}/news`);
      return response.data;
    },
    enabled: !!slug,
  });
};

export const useRefreshNews = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (slug: string) => {
      const response = await api.post(`/news/companies/${slug}/news/refresh`);
      return response.data;
    },
    onSuccess: (_, slug) => {
      queryClient.invalidateQueries({ queryKey: ['company-news', slug] });
    },
  });
};

export const useRecentNews = (limit = 20) => {
  return useQuery({
    queryKey: ['recent-news', limit],
    queryFn: async () => {
      const response = await api.get<NewsItem[]>('/news/recent', { params: { limit } });
      return response.data;
    },
  });
};

export const useNewsStatistics = () => {
  return useQuery({
    queryKey: ['news-statistics'],
    queryFn: async () => {
      const response = await api.get<import('../types/news').NewsStatisticsResponse>('/news/statistics');
      return response.data;
    },
  });
};

export const useNewsHealth = () => {
  return useQuery({
    queryKey: ['news-health'],
    queryFn: async () => {
      const response = await api.get<import('../types/news').NewsHealthResponse>('/news/health');
      return response.data;
    },
    refetchInterval: 60000,
    refetchOnWindowFocus: false,
  });
};
