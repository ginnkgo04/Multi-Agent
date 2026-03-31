import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Thread } from '@/lib/api';
import { formatDistanceToNow } from 'date-fns';

interface ThreadListProps {
  category?: string;
  initialThreads?: Thread[];
  showCategory?: boolean;
  onThreadClick?: (threadId: string) => void;
}

export default function ThreadList({ 
  category, 
  initialThreads = [], 
  showCategory = true,
  onThreadClick 
}: ThreadListProps) {
  const [threads, setThreads] = useState<Thread[]>(initialThreads);
  const [loading, setLoading] = useState(!initialThreads.length);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchThreads = async (pageNum: number, append = false) => {
    try {
      setLoading(true);
      setError(null);
      
      // In a real implementation, this would call the API
      // const response = await api.getThreads({ category, page: pageNum });
      // const newThreads = response.threads;
      
      // Mock data for demonstration
      const mockThreads: Thread[] = Array.from({ length: 10 }, (_, i) => ({
        id: `thread-${pageNum}-${i}`,
        title: `Thread ${(pageNum - 1) * 10 + i + 1}${category ? ` in ${category}` : ''}`,
        content: `This is the content of thread ${(pageNum - 1) * 10 + i + 1}.`,
        author: {
          id: `user-${i % 5}`,
          username: `user${i % 5}`,
          email: `user${i % 5}@example.com`,
          createdAt: new Date(Date.now() - 86400000 * (i % 30)).toISOString(),
        },
        category: category || 'general',
        viewCount: Math.floor(Math.random() * 1000),
        postCount: Math.floor(Math.random() * 100),
        isLocked: i % 10 === 0,
        isPinned: i % 20 === 0,
        createdAt: new Date(Date.now() - 86400000 * i).toISOString(),
        updatedAt: new Date(Date.now() - 43200000 * i).toISOString(),
        lastPost: {
          id: `post-${i}`,
          author: {
            id: `user-${(i + 1) % 5}`,
            username: `user${(i + 1) % 5}`,
            email: `user${(i + 1) % 5}@example.com`,
            createdAt: new Date(Date.now() - 86400000 * ((i + 1) % 30)).toISOString(),
          },
          createdAt: new Date(Date.now() - 3600000 * i).toISOString(),
        },
      }));

      if (append) {
        setThreads(prev => [...prev, ...mockThreads]);
      } else {
        setThreads(mockThreads);
      }
      
      setHasMore(pageNum < 3); // Mock: only 3 pages of data
    } catch (err) {
      setError('Failed to load threads. Please try again.');
      console.error('Error fetching threads:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!initialThreads.length) {
      fetchThreads(1);
    }
  }, [category, initialThreads.length]);

  const handleLoadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchThreads(nextPage, true);
  };

  const handleThreadClick = (threadId: string) => {
    if (onThreadClick) {
      onThreadClick(threadId);
    }
  };

  if (loading && threads.length === 0) {
    return (
      <div className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <div key={i} className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 animate-pulse">
            <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
            <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-4"></div>
            <div className="flex justify-between">
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/4"></div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (error && threads.length === 0) {
    return (
      <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
        <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
        <button
          onClick={() => fetchThreads(1)}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  if (threads.length === 0) {
    return (
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-8 text-center">
        <div className="text-gray-400 dark:text-gray-500 mb-4">
          <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">No threads found</h3>
        <p className="text-gray-500 dark:text-gray-400">
          {category ? `No threads in ${category} yet.` : 'No threads available.'}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="bg-gray-50 dark:bg-gray-800 rounded-lg p-4 hidden md:grid grid-cols-12 gap-4 text-sm font-medium text-gray-600 dark:text-gray-400">
        <div className="col-span-6">Thread</div>
        <div className="col-span-2 text-center">Replies</div>
        <div className="col-span-2 text-center">Views</div>
        <div className="col-span-2">Last Post</div>
      </div>

      {threads.map((thread) => (
        <div
          key={thread.id}
          className={`bg-white dark:bg-gray-800 rounded-lg shadow hover:shadow-md transition-shadow ${
            thread.isPinned ? 'border-l-4 border-blue-500' : ''
          }`}
        >
          <div className="p-4 md:p-6">
            <div className="flex flex-col md:grid md:grid-cols-12 md:gap-4">
              {/* Thread info */}
              <div className="col-span-6 mb-4 md:mb-0">
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 rounded-full bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                      <span className="text-blue-600 dark:text-blue-300 font-semibold">
                        {thread.author.username.charAt(0).toUpperCase()}
                      </span>
                    </div>
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-1">
                      {thread.isPinned && (
                        <span className="px-2 py-1 text-xs font-medium bg-blue-100 dark:bg-blue-900 text-blue-600 dark:text-blue-300 rounded">
                          Pinned
                        </span>
                      )}
                      {thread.isLocked && (
                        <span className="px-2 py-1 text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 rounded">
                          Locked
                        </span>
                      )}
                    </div>
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                      <Link
                        href={`/forum/${thread.category}/${thread.id}`}
                        onClick={(e) => {
                          if (onThreadClick) {
                            e.preventDefault();
                            handleThreadClick(thread.id);
                          }
                        }}
                        className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                      >
                        {thread.title}
                      </Link>
                    </h3>
                    <div className="flex flex-wrap items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                      <span>by {thread.author.username}</span>
                      <span>•</span>
                      <span>{formatDistanceToNow(new Date(thread.createdAt), { addSuffix: true })}</span>
                      {showCategory && thread.category && (
                        <>
                          <span>•</