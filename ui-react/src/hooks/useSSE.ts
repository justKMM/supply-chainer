import { useEffect, useState } from 'react';
import type { LiveMessage } from '../types';

export function useSSE(isRunning: boolean) {
  const [messages, setMessages] = useState<LiveMessage[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    if (!isRunning) return;

    const eventSource = new EventSource('/api/stream');

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
