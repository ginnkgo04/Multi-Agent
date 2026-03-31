'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { Bell, Check, X, MessageSquare, ThumbsUp, UserPlus, AlertCircle } from 'lucide-react';
import { useAuth } from '@/lib/auth';
import { useWebSocket } from '@/lib/websocket';
import { markNotificationAsRead, markAllNotificationsAsRead, deleteNotification, fetchNotifications } from '@/lib/api';

export interface Notification {
  id: string;
  type: 'new_reply' | 'new_like' | 'new_follower' | 'thread_update' | 'system';
  title: string;
  message: string;
  threadId?: string;
  postId?: string;
  userId?: string;
  read: boolean;
  createdAt: string;
  metadata?: Record<string, any>;
}

interface NotificationCenterProps {
  maxNotifications?: number;
  autoCloseDelay?: number;
}

export default function NotificationCenter({ 
  maxNotifications = 20, 
  autoCloseDelay = 5000 
}: NotificationCenterProps) {
  const { user, isAuthenticated } = useAuth();
  const { notifications: wsNotifications, sendNotificationAck } = useWebSocket();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const notificationRef = useRef<HTMLDivElement>(null);
  const autoCloseTimerRef = useRef<NodeJS.Timeout | null>(null);

  const loadNotifications = useCallback(async () => {
    if (!isAuthenticated || !user) return;
    
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await fetchNotifications();
      setNotifications(data.slice(0, maxNotifications));
    } catch (err) {
      setError('Failed to load notifications');
      console.error('Error loading notifications:', err);
    } finally {
      setIsLoading(false);
    }
  }, [isAuthenticated, user, maxNotifications]);

  useEffect(() => {
    if (isAuthenticated) {
      loadNotifications();
    } else {
      setNotifications([]);
    }
  }, [isAuthenticated, loadNotifications]);

  useEffect(() => {
    if (wsNotifications.length > 0) {
      const newNotifications = wsNotifications.map(wsNotif => ({
        id: wsNotif.id || `ws-${Date.now()}-${Math.random()}`,
        type: wsNotif.type as Notification['type'],
        title: wsNotif.title,
        message: wsNotif.message,
        threadId: wsNotif.threadId,
        postId: wsNotif.postId,
        userId: wsNotif.userId,
        read: false,
        createdAt: new Date().toISOString(),
        metadata: wsNotif.metadata
      }));
      
      setNotifications(prev => [...newNotifications, ...prev].slice(0, maxNotifications));
      
      wsNotifications.forEach(notif => {
        if (notif.id) {
          sendNotificationAck(notif.id);
        }
      });
    }
  }, [wsNotifications, maxNotifications, sendNotificationAck]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    if (isOpen && autoCloseDelay > 0) {
      if (autoCloseTimerRef.current) {
        clearTimeout(autoCloseTimerRef.current);
      }
      
      autoCloseTimerRef.current = setTimeout(() => {
        setIsOpen(false);
      }, autoCloseDelay);
    }
    
    return () => {
      if (autoCloseTimerRef.current) {
        clearTimeout(autoCloseTimerRef.current);
      }
    };
  }, [isOpen, autoCloseDelay]);

  const handleMarkAsRead = async (notificationId: string) => {
    try {
      await markNotificationAsRead(notificationId);
      setNotifications(prev =>
        prev.map(notif =>
          notif.id === notificationId ? { ...notif, read: true } : notif
        )
      );
    } catch (err) {
      console.error('Error marking notification as read:', err);
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await markAllNotificationsAsRead();
      setNotifications(prev =>
        prev.map(notif => ({ ...notif, read: true }))
      );
    } catch (err) {
      console.error('Error marking all notifications as read:', err);
    }
  };

  const handleDeleteNotification = async (notificationId: string) => {
    try {
      await deleteNotification(notificationId);
      setNotifications(prev => prev.filter(notif => notif.id !== notificationId));
    } catch (err) {
      console.error('Error deleting notification:', err);
    }
  };

  const handleNotificationClick = (notification: Notification) => {
    if (!notification.read) {
      handleMarkAsRead(notification.id);
    }
    
    if (notification.threadId) {
      window.location.href = `/forum/${notification.metadata?.category || 'general'}/${notification.threadId}`;
    }
    
    setIsOpen(false);
  };

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'new_reply':
        return <MessageSquare className="w-5 h-5 text-blue-500" />;
      case 'new_like':
        return <ThumbsUp className="w-5 h-5 text-green-500" />;
      case 'new_follower':
        return <UserPlus className="w-5 h-5 text-purple-500" />;
      case 'thread_update':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'system':
        return <AlertCircle className="w-5 h-5 text-gray-500" />;
      default:
        return <Bell className="w-5 h-5 text-gray-500" />;
    }
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="relative" ref={notificationRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="relative p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
        aria-label="Notifications"
      >
        <Bell className="w-6 h-6 text-gray-700 dark:text-gray-300" />
        {unreadCount > 0 && (
          <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white dark:bg-gray-900 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 z-50 max-h-[80vh] overflow-hidden">
          <div className="p-4 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Notifications
                {unreadCount > 0 && (
                  <span className="ml-2 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs px-2 py-1 rounded-full">
                    {unreadCount} new
                  </span>
                )}
              </h3>
              <div className="flex items-center space-x-2">
                {unreadCount > 0 && (
                  <button
                    onClick={handleMarkAllAsRead}
                    className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                  >
                    Mark all read
                  </button>
                )}
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>

          <div className="overflow-y-auto max-h-[60vh]">
            {isLoading ? (
              <div className="p-8 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="mt-2 text-gray-600 dark:text-gray-400">Loading notifications...</p>
              </div>
            ) : error ? (
              <div className="p-4 text-center">
                <AlertCircle className="w-8 h-8 text-red-500 mx-auto mb-2" />
                <p className="text-red-600 dark:text-red-400">{error}</p>
                <button
                  onClick={loadNotifications}