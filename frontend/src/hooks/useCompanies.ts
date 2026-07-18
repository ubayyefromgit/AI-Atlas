import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';
import type { Company, CompanyListResponse, CompanyStatistics, Problem } from '../types/company';

export const useCompanies = (params: { page?: number; size?: number; search?: string; country?: string; category?: string; segment?: string; company_type?: string; maturity?: number; status?: string }) => {
  return useQuery({
    queryKey: ['companies', params],
    queryFn: async () => {
      const { page = 1, size = 12, ...rest } = params;
      const skip = (page - 1) * size;
      const response = await api.get<CompanyListResponse>('/companies', {
        params: { 
          skip, 
          limit: size, 
          search: rest.search, 
          country: rest.country, 
          ai_category: rest.category, 
          segment: rest.segment,
          company_type: rest.company_type,
          maturity: rest.maturity,
          status: rest.status
        },
      });
      return response.data;
    },
  });
};

export const useCompany = (slug: string | undefined) => {
  return useQuery({
    queryKey: ['company', slug],
    queryFn: async () => {
      if (!slug) throw new Error('Slug is required');
      const response = await api.get<Company>(`/companies/${slug}`);
      return response.data;
    },
    enabled: !!slug,
  });
};

export const useCompanyProblems = (slug: string | undefined) => {
  return useQuery({
    queryKey: ['company-problems', slug],
    queryFn: async () => {
      if (!slug) throw new Error('Slug is required');
      const response = await api.get<Problem[]>(`/companies/${slug}/problems`);
      return response.data;
    },
    enabled: !!slug,
  });
};

export const useCompanyStatistics = () => {
  return useQuery({
    queryKey: ['companies-statistics'],
    queryFn: async () => {
      const response = await api.get<CompanyStatistics>('/companies/statistics');
      return response.data;
    },
  });
};

export const useCompanyFilters = () => {
  return useQuery({
    queryKey: ['companies-filters'],
    queryFn: async () => {
      const response = await api.get('/companies/filters');
      return response.data as {
        segments: { value: string; count: number }[];
        ai_categories: { value: string; count: number }[];
        company_types: { value: string; count: number }[];
        countries: { value: string; count: number }[];
      };
    },
  });
};

export const useCreateCompany = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (data: any) => {
      const response = await api.post('/companies/', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['companies'] });
      queryClient.invalidateQueries({ queryKey: ['companies-statistics'] });
    },
  });
};

export const useFollowCompany = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (slug: string) => {
      const response = await api.post(`/companies/${slug}/follow`);
      return response.data;
    },
    onSuccess: (data, slug) => {
      queryClient.invalidateQueries({ queryKey: ['company', slug] });
      queryClient.invalidateQueries({ queryKey: ['companies'] });
    },
  });
};

export const useUnfollowCompany = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async (slug: string) => {
      const response = await api.post(`/companies/${slug}/unfollow`);
      return response.data;
    },
    onSuccess: (data, slug) => {
      queryClient.invalidateQueries({ queryKey: ['company', slug] });
      queryClient.invalidateQueries({ queryKey: ['companies'] });
    },
  });
};

export const useUpdateCompany = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: async ({ slug, data }: { slug: string; data: any }) => {
      const response = await api.put(`/companies/${slug}`, data);
      return response.data;
    },
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: ['company', variables.slug] });
      queryClient.invalidateQueries({ queryKey: ['companies'] });
      queryClient.invalidateQueries({ queryKey: ['companies-statistics'] });
    },
  });
};

export const useQuickDiscover = () => {
  return useMutation({
    mutationFn: async (name: string) => {
      const response = await api.get<any>(`/companies/discover/quick`, {
        params: { name }
      });
      return response.data;
    }
  });
};
