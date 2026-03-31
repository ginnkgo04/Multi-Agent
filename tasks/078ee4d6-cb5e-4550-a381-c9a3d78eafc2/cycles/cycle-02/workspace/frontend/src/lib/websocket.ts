import { getToken } from './auth';

export type NotificationType = 'new_post' | 'new_reply' | 'thread_update' | 'mention' | 'vote';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  threadId?: string;
  postId?: string;
  userId?: string;
  read: boolean;
  createdAt: string;
}

export interface WebSocketMessage {
  type: 'notification' | 'ping' | 'pong' | 'auth' | 'error';
  data?: any;
}

class WebSocketClient {
  private ws: WebSocket | null = null;
  private url: string;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private isConnecting = false;
  private messageHandlers: Map<string, ((data: any) => void)[]> = new Map();
  private notificationCallbacks: ((notification: Notification) => void)[] = [];

  constructor(url: string = 'ws://localhost:8000/ws') {
    this.url = url;
  }

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        resolve();
        return;
      }

      if (this.isConnecting) {
        reject(new Error('Already connecting'));
        return;
      }

      this.isConnecting = true;

      try {
        const token = getToken();
        const wsUrl = token ? `${this.url}?token=${token}` : this.url;
        
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          resolve();
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason);
          this.isConnecting = false;
          this.stopHeartbeat();
          this.handleReconnect();
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnecting = false;
          reject(error);
        };

        this.ws.onmessage = (event) => {
          this.handleMessage(event);
        };
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  disconnect(): void {
    this.stopHeartbeat();
    if (this.ws) {
      this.ws.close(1000, 'Client disconnected');
      this.ws = null;
    }
    this.messageHandlers.clear();
    this.notificationCallbacks = [];
  }

  private handleMessage(event: MessageEvent): void {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);
      
      switch (message.type) {
        case 'notification':
          if (message.data) {
            this.notificationCallbacks.forEach(callback => {
              callback(message.data);
            });
          }
          break;
        case 'pong':
          // Heartbeat response, do nothing
          break;
        case 'error':
          console.error('WebSocket server error:', message.data);
          break;
      }

      // Call registered handlers for this message type
      const handlers = this.messageHandlers.get(message.type);
      if (handlers) {
        handlers.forEach(handler => handler(message.data));
      }
    } catch (error) {
      console.error('Failed to parse WebSocket message:', error);
    }
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      if (this.ws?.readyState !== WebSocket.OPEN) {
        this.connect().catch(error => {
          console.error('Reconnection failed:', error);
        });
      }
    }, delay);
  }

  private heartbeatInterval: NodeJS.Timeout | null = null;

  private startHeartbeat(): void {
    this.stopHeartbeat();
    
    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' });
      }
    }, 30000); // Send ping every 30 seconds
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  send(message: WebSocketMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  onMessage(type: string, handler: (data: any) => void): void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, []);
    }
    this.messageHandlers.get(type)!.push(handler);
  }

  offMessage(type: string, handler: (data: any) => void): void {
    const handlers = this.messageHandlers.get(type);
    if (handlers) {
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    }
  }

  onNotification(callback: (notification: Notification) => void): void {
    this.notificationCallbacks.push(callback);
  }

  offNotification(callback: (notification: Notification) => void): void {
    const index = this.notificationCallbacks.indexOf(callback);
    if (index > -1) {
      this.notificationCallbacks.splice(index, 1);
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  getConnectionState(): string {
    if (!this.ws) return 'DISCONNECTED';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'CONNECTING';
      case WebSocket.OPEN:
        return 'CONNECTED';
      case WebSocket.CLOSING:
        return 'CLOSING';
      case WebSocket.CLOSED:
        return 'DISCONNECTED';
      default:
        return 'UNKNOWN';
    }
  }
}

// Create a singleton instance
export const websocket = new WebSocketClient();

// Helper function to subscribe to thread updates
export function subscribeToThread(threadId: string): void {
  if (websocket.isConnected()) {
    websocket.send({
      type: 'subscribe',
      data: { threadId }
    });
  }
}

// Helper function to unsubscribe from thread updates
export function unsubscribeFromThread(threadId: string): void {
  if (websocket.isConnected()) {
    websocket.send({
      type: 'unsubscribe',
      data: { threadId }
    });
  }
}

// Helper function to mark notification as read
export function markNotificationAsRead(notificationId: string): void {
  if (websocket.isConnected()) {
    websocket.send({
      type: 'mark_read',
      data: { notificationId }
    });
  }
}

export default websocket;