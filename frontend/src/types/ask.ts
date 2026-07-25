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

export interface AgentAskRequest {
  question: string;
  conversation_id?: string;
  model_provider?: string;
}

export interface AgentAskResponse {
  answer: string;
  sources: AskSource[];
  conversation_id: string;
  used_tools: string[];
  is_general_knowledge: boolean;
}
