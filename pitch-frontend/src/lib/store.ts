import { create } from 'zustand';
import type { StateCreator } from 'zustand';
import { Deck, Analysis, AnalysisResult, KnowledgeFile } from '@/types';
import { apiService } from './api';

interface AppState {
  // State
  decks: Deck[];
  currentDeck: Deck | null;
  analysis: Analysis | null;
  analysisResult: AnalysisResult | null;
  knowledgeFiles: KnowledgeFile[];
  loading: boolean;
  error: string | null;

  // Actions
  uploadDeck: (file: File, startupName: string) => Promise<void>;
  fetchDecks: () => Promise<void>;
  fetchDeck: (id: string) => Promise<void>;
  fetchAnalysisStatus: (jobId: string) => Promise<void>;
  fetchAnalysisResult: (jobId: string) => Promise<void>;
  uploadKnowledgeFile: (file: File) => Promise<void>;
  fetchKnowledgeFiles: () => Promise<void>;
  searchKnowledge: (query: string) => Promise<void>;
  setError: (error: string | null) => void;
  clearError: () => void;
}

const createAppStore: StateCreator<AppState> = (set, get) => ({
  // Initial state
  decks: [],
  currentDeck: null,
  analysis: null,
  analysisResult: null,
  knowledgeFiles: [],
  loading: false,
  error: null,

  // Actions
  uploadDeck: async (file: File, startupName: string) => {
    try {
      set({ loading: true, error: null });
      const result = await apiService.analyzeDeck(file, startupName);
      await get().fetchDecks();
      set({ loading: false });
    } catch (error) {
      set({ loading: false, error: (error as Error).message });
    }
  },

  fetchDecks: async () => {
    try {
      set({ loading: true, error: null });
      const decks = await apiService.getDecks();
      set({ decks, loading: false });
    } catch (error) {
      set({ loading: false, error: (error as Error).message });
    }
  },

  fetchDeck: async (id: string) => {
    try {
      set({ loading: true, error: null });
      const deck = await apiService.getDeck(id);
      set({ currentDeck: deck, loading: false });
    } catch (error) {
      set({ loading: false, error: (error as Error).message });
    }
  },

  fetchAnalysisStatus: async (jobId: string) => {
    try {
      set({ loading: true, error: null });
      const analysis = await apiService.getAnalysisStatus(jobId);
      set({ analysis, loading: false });
    } catch (error) {
      set({ loading: false, error: (error as Error).message });
    }
  },

  fetchAnalysisResult: async (jobId: string) => {
    try {
      set({ loading: true, error: null });
      const result = await apiService.getAnalysisResult(jobId);
      set({ analysisResult: result, loading: false });
    } catch (error) {
      set({ loading: false, error: (error as Error).message });
    }
  },

  uploadKnowledgeFile: async (file: File) => {
    try {
      set({ loading: true, error: null });
      await apiService.uploadKnowledgeFile(file);
      await get().fetchKnowledgeFiles();
      set({ loading: false });
    } catch (error) {
      set({ loading: false, error: (error as Error).message });
    }
  },

  fetchKnowledgeFiles: async () => {
    try {
      set({ loading: true, error: null });
      const files = await apiService.getKnowledgeFiles();
      set({ knowledgeFiles: files, loading: false });
    } catch (error) {
      set({ loading: false, error: (error as Error).message });
    }
  },

  searchKnowledge: async (query: string) => {
    try {
      set({ loading: true, error: null });
      const files = await apiService.searchKnowledge(query);
      set({ knowledgeFiles: files, loading: false });
    } catch (error) {
      set({ loading: false, error: (error as Error).message });
    }
  },

  setError: (error: string | null) => set({ error }),
  clearError: () => set({ error: null }),
});

export const useStore = create<AppState>(createAppStore); 