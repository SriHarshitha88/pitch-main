import { Deck, Analysis, AnalysisResult, KnowledgeFile } from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
const WS_BASE_URL = 'ws://localhost:8000';

class ApiService {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.statusText}`);
    }

    return response.json();
  }

  async analyzeDeck(file: File, startupName: string): Promise<Analysis> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('startupName', startupName);

    const response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Failed to analyze deck: ${response.statusText}`);
    }

    return response.json();
  }

  async getDecks(): Promise<Deck[]> {
    return this.request<Deck[]>('/api/decks');
  }

  async getDeck(id: string): Promise<Deck> {
    return this.request<Deck>(`/api/decks/${id}`);
  }

  async getAnalysisStatus(jobId: string): Promise<Analysis> {
    return this.request<Analysis>(`/api/analysis/${jobId}/status`);
  }

  async getAnalysisResult(jobId: string): Promise<AnalysisResult> {
    return this.request<AnalysisResult>(`/api/analysis/${jobId}/result`);
  }

  async uploadKnowledgeFile(file: File): Promise<KnowledgeFile> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/knowledge`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`Failed to upload knowledge file: ${response.statusText}`);
    }

    return response.json();
  }

  async getKnowledgeFiles(): Promise<KnowledgeFile[]> {
    return this.request<KnowledgeFile[]>('/api/knowledge');
  }

  async searchKnowledge(query: string): Promise<KnowledgeFile[]> {
    return this.request<KnowledgeFile[]>(`/api/knowledge/search?q=${encodeURIComponent(query)}`);
  }
}

export const apiService = new ApiService();

// WebSocket helper
export const createWebSocket = (jobId: string) => {
  return new WebSocket(`${WS_BASE_URL}/ws/${jobId}`);
}; 