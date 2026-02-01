/**
 * AI API Client
 * Handles AI guide chat and interactions
 */

import { apiClient } from './client';

export interface AIChatRequest {
  node_id: string;
  message: string;
  context?: {
    node_title?: string;
    node_type?: string;
    conversation_history?: Array<{
      role: 'user' | 'assistant';
      content: string;
    }>;
    [key: string]: any;
  };
}

export interface AIChatResponse {
  response: string;
  context_used?: any;
}

export interface ChatHistory {
  id: number;
  user_id: number;
  node_id: string;
  message: string;
  response: string;
  context: any;
  created_at: string;
}

export const aiAPI = {
  /**
   * Send a message to AI guide
   */
  async sendMessage(request: AIChatRequest): Promise<AIChatResponse> {
    return apiClient.post<AIChatResponse>('/v1/ai/guide-chat', request);
  },

  /**
   * Get chat history for a node
   */
  async getChatHistory(nodeId: string): Promise<ChatHistory[]> {
    const response = await apiClient.get<{ history: ChatHistory[] }>(`/v1/ai/chat-history/${nodeId}`);
    return response.history || [];
  },

  /**
   * Clear chat history for a node
   */
  async clearChatHistory(nodeId: string): Promise<{ message: string }> {
    return apiClient.delete(`/v1/ai/chat-history/${nodeId}`);
  },

  /**
   * Get AI suggestions based on current context
   */
  async getSuggestions(nodeId: string, context?: any): Promise<{ suggestions: string[] }> {
    return apiClient.post('/v1/ai/suggestions', { node_id: nodeId, context });
  },
};
