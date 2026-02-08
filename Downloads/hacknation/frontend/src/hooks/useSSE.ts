import { useEffect, useRef, useState, useCallback } from "react";
import { subscribeToStream } from "@/api/client";
import type { LiveMessage } from "@/data/types";

export function useSSE() {
  const [messages, setMessages] = useState<LiveMessage[]>([]);
  const [connected, setConnected] = useState(false);
  const esRef = useRef<EventSource | null>(null);

  const connect = useCallback(() => {
    if (esRef.current) {
      esRef.current.close();
    }
    const es = subscribeToStream(
      (msg) => {
        setMessages((prev) => [...prev, msg]);
        setConnected(true);
      },
      () => {
        setConnected(false);
      },
    );
    es.onopen = () => setConnected(true);
    esRef.current = es;
  }, []);

  const disconnect = useCallback(() => {
    esRef.current?.close();
    esRef.current = null;
    setConnected(false);
  }, []);

  const clear = useCallback(() => {
    setMessages([]);
  }, []);

  useEffect(() => {
    return () => {
      esRef.current?.close();
    };
  }, []);

  return { messages, connected, connect, disconnect, clear };
}
