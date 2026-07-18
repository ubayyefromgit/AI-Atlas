import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';
import type { DiscoveryCandidate, DiscoveryRequest, DiscoveryStatistics } from '../types/discovery';

export const useDiscoveryCandidates = () => {
  return useQuery({
    queryKey: ['discovery-candidates'],
    queryFn: async () => {
      const response = await api.get<DiscoveryCandidate[]>('/admin/discovery');
      return response.data;
    },
    refetchInterval: 30000, // Poll every 30 seconds for new pipeline candidates
    refetchOnWindowFocus: false,
    enabled: !!localStorage.getItem('adminToken'),
  });
};

export const useDiscoveryStatistics = () => {
  return useQuery({
    queryKey: ['discovery-statistics'],
    queryFn: async () => {
      const response = await api.get<DiscoveryStatistics>('/admin/statistics');
      return response.data;
    },
    enabled: !!localStorage.getItem('adminToken'),
  });
};

export const useRunDiscovery = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: DiscoveryRequest) => {
      const response = await api.post('/admin/discover', data);
      return response.data;
    },
    onSuccess: () => {
      // Typically discovery takes time, so we might want to poll or just refetch candidates later.
      queryClient.invalidateQueries({ queryKey: ['discovery-candidates'] });
    },
  });
};

export const useApproveCandidate = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: number) => {
      const response = await api.post(`/admin/discovery/${id}/approve`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['discovery-candidates'] });
      queryClient.invalidateQueries({ queryKey: ['discovery-statistics'] }); // Refresh stats
      queryClient.invalidateQueries({ queryKey: ['companies'] }); // Refresh directory
    },
  });
};

export const useRejectCandidate = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (id: number) => {
      const response = await api.post(`/admin/discovery/${id}/reject`);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['discovery-candidates'] });
      queryClient.invalidateQueries({ queryKey: ['discovery-statistics'] }); // Refresh stats
    },
  });
};

export const useUpdateCandidate = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ id, data }: { id: number, data: any }) => {
      const response = await api.put(`/admin/discovery/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['discovery-candidates'] });
    },
  });
};

export const useBulkApproveCandidates = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (ids: number[]) => {
      for (const id of ids) {
        await api.post(`/admin/discovery/${id}/approve`);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['discovery-candidates'] });
      queryClient.invalidateQueries({ queryKey: ['discovery-statistics'] });
      queryClient.invalidateQueries({ queryKey: ['companies'] });
    },
  });
};

export const useBulkRejectCandidates = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (ids: number[]) => {
      for (const id of ids) {
        await api.post(`/admin/discovery/${id}/reject`);
      }
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['discovery-candidates'] });
      queryClient.invalidateQueries({ queryKey: ['discovery-statistics'] });
    },
  });
};
