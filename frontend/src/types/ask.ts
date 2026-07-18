export interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  sources?: AskSource[];
}

export interface AskAIRequest {
  question: string;
}

export interface AskSource {
  marker: string;
  source_type: string;
  source_id: number;
  chunk_key: string;
  score: number;
}

export interface AskAIResponse {
  answer: string;
  sources: AskSource[];
}
