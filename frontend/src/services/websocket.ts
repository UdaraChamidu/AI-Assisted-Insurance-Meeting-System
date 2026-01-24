/**
 * WebSocket service for real-time communication
 */

import { config } from '../config';

export type WSEventType =
  | 'connection.established'
  | 'transcription.new'
  | 'ai.response'
  | 'ai.processing'
  | 'rag.context'
  | 'session.participant_joined'
  | 'session.participant_left';

export interface WSEvent {
  event_type: WSEventType;
  session_id: string;
  timestamp: string;
  data: any;
}

type EventHandler = (event: WSEvent) => void;

class WebSocketService {
  private ws: WebSocket | null = null;
  private handlers: Map<WSEventType, EventHandler[]> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 2000;

  connect(sessionId: string, role: string = 'staff') {
    const url = `${config.wsUrl}/ws/${sessionId}?role=${role}`;

    this.ws = new WebSocket(url);

    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
    };

    this.ws.onmessage = (event) => {
      try {
        const data: WSEvent = JSON.parse(event.data);
        this.handleEvent(data);
      } catch (error) {
        console.error('Failed to parse WebSocket message:', error);
      }
    };

    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.ws.onclose = () => {
      console.log('WebSocket disconnected');
      this.attemptReconnect(sessionId, role);
    };
  }

  private attemptReconnect(sessionId: string, role: string) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(
        `Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`
      );
      setTimeout(() => {
        this.connect(sessionId, role);
      }, this.reconnectDelay);
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  on(eventType: WSEventType, handler: EventHandler) {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, []);
    }
    this.handlers.get(eventType)!.push(handler);
  }

  off(eventType: WSEventType, handler: EventHandler) {
    const handlers = this.handlers.get(eventType);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  private handleEvent(event: WSEvent) {
    const handlers = this.handlers.get(event.event_type);
    if (handlers) {
      handlers.forEach((handler) => handler(event));
    }

    // Also trigger 'all' handlers
    const allHandlers = this.handlers.get('*' as WSEventType);
    if (allHandlers) {
      allHandlers.forEach((handler) => handler(event));
    }
  }

  send(eventType: string, data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(
        JSON.stringify({
          event_type: eventType,
          data,
          timestamp: new Date().toISOString(),
        })
      );
    }
  }

  sendAudio(audioData: Blob | ArrayBuffer) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(audioData);
    }
  }
}

export const wsService = new WebSocketService();
