import { useState, useEffect } from 'react';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';
import { Thread, Category } from '@/lib/api';
import { useAuth } from '@/lib/auth';

interface ThreadListProps {
  categoryId?: string;
  categoryName?: string;
  initialThreads?: Thread[];
  showCreateButton?: boolean;
  onThreadCreated?: () => void;
}

export default function ThreadList({
  categoryId,
  categoryName,
  initialThreads = [],
  showCreateButton = true,
  onThreadCreated
}: ThreadListProps) {
  const { user, isAuthenticated } = useAuth();
  const [threads, setThreads] = useState<Thread[]>(initialThreads);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [creatingThread, setCreatingThread] = useState(false);
  const [newThreadTitle, setNewThreadTitle] = useState('');
  const [newThreadContent, setNewThreadContent] = useState('');

  const fetchThreads = async (pageNum: number, append = false) => {
    if (!categoryId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(
        `http://localhost:8000/api/categories/${categoryId}/threads?page=${pageNum}&limit=20`
      );
      
      if (!response.ok) {
        throw new Error('Failed to fetch threads');
      }
      
      const data = await response.json();
      
      if (append) {
        setThreads(prev => [...prev, ...data.threads]);
      } else {
        setThreads(data.threads);
      }
      
      setHasMore(data.has_more);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load threads');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (categoryId) {
      fetchThreads(1, false);
    }
  }, [categoryId]);

  const handleCreateThread = async () => {
    if (!newThreadTitle.trim() || !newThreadContent.trim() || !categoryId) return;
    
    setCreatingThread(true);
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        throw new Error('Not authenticated');
      }
      
      const response = await fetch(`http://localhost:8000/api/categories/${categoryId}/threads`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          title: newThreadTitle,
          content: newThreadContent
        })
      });
      
      if (!response.ok) {
        throw new Error('Failed to create thread');
      }
      
      const newThread = await response.json();
      
      // Add new thread to the beginning of the list
      setThreads(prev => [newThread, ...prev]);
      
      // Reset form
      setNewThreadTitle('');
      setNewThreadContent('');
      
      // Notify parent
      if (onThreadCreated) {
        onThreadCreated();
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create thread');
    } finally {
      setCreatingThread(false);
    }
  };

  const loadMore = () => {
    if (hasMore && !loading) {
      const nextPage = page + 1;
      setPage(nextPage);
      fetchThreads(nextPage, true);
    }
  };

  const formatDate = (dateString: string) => {
    try {
      return formatDistanceToNow(new Date(dateString), { addSuffix: true });
    } catch {
      return dateString;
    }
  };

  if (error && !threads.length) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="text-center text-red-600">
          <p className="mb-2">Error loading threads</p>
          <p className="text-sm text-gray-500">{error}</p>
          <button
            onClick={() => fetchThreads(1, false)}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Create Thread Form */}
      {showCreateButton && isAuthenticated && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">Create New Thread</h3>
          <div className="space-y-4">
            <div>
              <label htmlFor="threadTitle" className="block text-sm font-medium text-gray-700 mb-1">
                Title
              </label>
              <input
                type="text"
                id="threadTitle"
                value={newThreadTitle}
                onChange={(e) => setNewThreadTitle(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Enter thread title"
                maxLength={200}
              />
            </div>
            <div>
              <label htmlFor="threadContent" className="block text-sm font-medium text-gray-700 mb-1">
                Content
              </label>
              <textarea
                id="threadContent"
                value={newThreadContent}
                onChange={(e) => setNewThreadContent(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 min-h-[100px]"
                placeholder="Enter your post content"
                maxLength={5000}
              />
            </div>
            <div className="flex justify-end">
              <button
                onClick={handleCreateThread}
                disabled={creatingThread || !newThreadTitle.trim() || !newThreadContent.trim()}
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {creatingThread ? 'Creating...' : 'Create Thread'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Threads List */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-xl font-semibold text-gray-800">
            {categoryName ? `Threads in ${categoryName}` : 'All Threads'}
          </h2>
          {threads.length > 0 && (
            <p className="text-sm text-gray-500 mt-1">
              {threads.length} thread{threads.length !== 1 ? 's' : ''}
            </p>
          )}
        </div>

        {threads.length === 0 && !loading ? (
          <div className="text-center py-12">
            <p className="text-gray-500">No threads yet. Be the first to start a discussion!</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {threads.map((thread) => (
              <div key={thread.id} className="px-6 py-4 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <Link
                      href={`/forum/${thread.category_id}/${thread.id}`}
                      className="block group"
                    >
                      <h3 className="text-lg font-medium text-gray-900 group-hover:text-blue-600 truncate">
                        {thread.title}
                      </h3>
                      <p className="mt-1 text-sm text-gray-600 line-clamp-2">
                        {thread.content}
                      </p>
                    </Link>
                    
                    <div className="mt-2 flex items-center text-sm text-gray-500">
                      <span className="flex items-center">
                        <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                        </svg>
                        {thread.author_username}
                      </span>
                      <span className="mx-2">•</span>
                      <span>{formatDate(thread.created_at)}</span>
                      {thread.updated_at !== thread.created_at && (
                        <>
                          <span className="mx-2">•</span>
                          <span className="text-xs bg-gray-100 px-2 py-1 rounded">
                            Edited
                          </span>
                        </>
                      )}
                    </div>
                  </div>
                  
                  <div className="ml-4 flex flex-col items-end">
                    <div className="flex items-center space-x-4">
                      <div className="text-center">
                        <div className="text-lg font-semibold text-gray-900">
                          {thread.post_count}
                        </div>
                        <div className="text-xs text-gray-500">Replies</div>
                      </div>
                      <div className="text-center">
                        <div className="text-lg font-semibold text-gray-900">
                          {thread.vote_count}
                        </div>
                        <div className="text-xs text-gray-500">Votes</div>
                      </div>
                    </div>
                    
                    {thread.last_post_at && (
                      <div className="mt-2 text-xs text-gray-500">
                        Last reply {formatDate(thread.last_post_at)}