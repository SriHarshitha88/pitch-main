export interface Deck {
  id: string;
  startup_name: string;
  created_at: string;
  updated_at: string;
  file_path: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
}

export interface Analysis {
  id: string;
  deck_id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  progress: number;
  created_at: string;
  updated_at: string;
}

export interface AnalysisResult {
  id: string;
  deck_id: string;
  score: number;
  feedback: string;
  suggestions: string[];
  created_at: string;
}

export interface KnowledgeFile {
  id: string;
  name: string;
  type: string;
  size: number;
  created_at: string;
  updated_at: string;
  content?: string;
}

export interface ComparisonResult {
  deck1_id: string;
  deck2_id: string;
  similarity_score: number;
  differences: string[];
  created_at: string;
}

export interface User {
  id: string;
  email: string;
  is_active: boolean;
  created_at: string;
} 