import { useQuery } from '@tanstack/react-query';
import api from '../services/api';

export interface EvalResult {
  id: number;
  description: string;
  question: string;
  answer: string;
  passed: boolean;
  expected_keywords: string[];
  expect_refusal: boolean;
  error: string | null;
}

export interface EvalResponse {
  total_tests: number;
  passed_count: number;
  results: EvalResult[];
  score_percentage: number;
}

export const useEval = () => {
  return useQuery({
    queryKey: ['system-evaluation'],
    queryFn: async (): Promise<EvalResponse> => {
      const response = await api.get('/admin/eval');
      return response.data;
    },
    enabled: false, // Don't run automatically, wait for user action
    retry: false
  });
};
