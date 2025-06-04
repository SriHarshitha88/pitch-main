export interface Deck {
  id: string;
  name: string;
  startupName: string;
  createdAt: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
}

export interface Analysis {
  id: string;
  deckId: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  createdAt: string;
  completedAt?: string;
}

export interface AnalysisResult {
  id: string;
  deckId: string;
  insights: string[];
  recommendations: string[];
  score: number;
  createdAt: string;
}

export interface KnowledgeFile {
  id: string;
  name: string;
  type: string;
  size: number;
  uploadedAt: string;
  content?: string;
} 