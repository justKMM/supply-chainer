import { useEffect, useState } from 'react';
import type { LiveMessage } from '../types';

const API_BASE_URL =
  (import.meta as { env?: { VITE_API_BASE_URL?: string } }).env?.VITE_API_BASE_URL ||
  'http://localhost:8000';

function apiUrl(path: string) {
  if (!path.startsWith('/')) return `${API_BASE_URL}/${path}`;
  return `${API_BASE_URL}${path}`;
}

export function useSSE(isRunning: boolean) {
  const [messages, setMessages] = useState<LiveMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!isRunning) return;

    const eventSource = new EventSource(apiUrl('/api/stream'));

    eventSource.onopen = () => setIsConnected(true);

    eventSource.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        if (msg.type === 'heartbeat') return;
        
        setMessages((prev) => [msg, ...prev].slice(0, 100)); // Keep last 100 messages
      } catch (e) {
        console.error('Failed to parse SSE message', e);
      }
    };

    eventSource.onerror = () => {
      setIsConnected(false);
      eventSource.close();
    };

    return () => {
      eventSource.close();
      setIsConnected(false);
    };
  }, [isRunning]);

  const clearMessages = () => setMessages([]);

  return { messages, isConnected, clearMessages };
}
