import { useEffect, useRef, useCallback } from 'react';
import { createWebSocket } from '@/lib/api';

interface WebSocketMessage {
  type: 'progress' | 'status' | 'error';
  data: unknown;
}

export const useWebSocket = (jobId: string, onMessage: (message: WebSocketMessage) => void) => {
  const ws = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) return;

    ws.current = createWebSocket(jobId);

    ws.current.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.current.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data) as WebSocketMessage;
        onMessage(message);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.current.onerror = (error: Event) => {
      console.error('WebSocket error:', error);
    };

    ws.current.onclose = () => {
      console.log('WebSocket disconnected');
      // Attempt to reconnect after 5 seconds
      setTimeout(connect, 5000);
    };
  }, [jobId, onMessage]);

  useEffect(() => {
    connect();

    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [connect]);

  const sendMessage = useCallback((message: WebSocketMessage) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify(message));
    }
  }, []);

  return { sendMessage };
}; 