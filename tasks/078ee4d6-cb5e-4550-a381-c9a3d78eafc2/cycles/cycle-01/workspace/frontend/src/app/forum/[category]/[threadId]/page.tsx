'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Header from '@/components/Header';
import PostEditor from '@/components/PostEditor';
import { getThread, getPosts, createPost, type Thread, type Post } from '@/lib/api';
import { useAuth } from '@/lib/auth';
import { formatDistanceToNow } from 'date-fns';

export default function ThreadPage() {
  const params = useParams();
  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
  
  const category = params.category as string;
  const threadId = params.threadId as string;
  
  const [thread, setThread] = useState<Thread | null>(null);
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [replyingTo, setReplyingTo] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);

  useEffect(() => {
    loadThreadAndPosts();
  }, [category, threadId, page]);

  const loadThreadAndPosts = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const threadData = await getThread(threadId);
      setThread(threadData);
      
      const postsData = await getPosts(threadId, page);
      if (page === 1) {
        setPosts(postsData.items);
      } else {
        setPosts(prev => [...prev, ...postsData.items]);
      }
      setHasMore(postsData.hasMore);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load thread');
    } finally {
      setLoading(false);
    }
  };

  const handleReply = async (content: string) => {
    if (!isAuthenticated) {
      router.push('/auth/login');
      return;
    }

    try {
      const newPost = await createPost({
        threadId,
        content,
        replyToId: replyingTo || undefined,
      });
      
      setPosts(prev => [newPost, ...prev]);
      setReplyingTo(null);
      
      // Refresh thread to update post count
      const updatedThread = await getThread(threadId);
      setThread(updatedThread);
    } catch (err) {
      alert(err instanceof Error ? err.message : 'Failed to post reply');
    }
  };

  const handleVote = async (postId: string, voteType: 'up' | 'down') => {
    if (!isAuthenticated) {
      router.push('/auth/login');
      return;
    }

    // TODO: Implement vote API call
    console.log(`Voting ${voteType} on post ${postId}`);
  };

  const loadMorePosts = () => {
    if (hasMore && !loading) {
      setPage(prev => prev + 1);
    }
  };

  if (loading && page === 1) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/4 mb-8"></div>
            <div className="space-y-4">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-32 bg-gray-200 rounded"></div>
              ))}
            </div>
          </div>
        </main>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h2 className="text-red-800 font-semibold">Error</h2>
            <p className="text-red-600">{error}</p>
            <button
              onClick={() => router.push(`/forum/${category}`)}
              className="mt-2 text-blue-600 hover:text-blue-800"
            >
              ← Back to {category} category
            </button>
          </div>
        </main>
      </div>
    );
  }

  if (!thread) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-700 mb-2">Thread not found</h2>
            <button
              onClick={() => router.push(`/forum/${category}`)}
              className="text-blue-600 hover:text-blue-800"
            >
              ← Back to {category} category
            </button>
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <main className="container mx-auto px-4 py-8">
        {/* Breadcrumb */}
        <nav className="mb-6">
          <ol className="flex items-center space-x-2 text-sm text-gray-600">
            <li>
              <button
                onClick={() => router.push('/')}
                className="hover:text-blue-600"
              >
                Home
              </button>
            </li>
            <li>›</li>
            <li>
              <button
                onClick={() => router.push(`/forum/${category}`)}
                className="hover:text-blue-600"
              >
                {category}
              </button>
            </li>
            <li>›</li>
            <li className="font-medium text-gray-900 truncate max-w-xs">
              {thread.title}
            </li>
          </ol>
        </nav>

        {/* Thread Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{thread.title}</h1>
          <div className="flex items-center justify-between text-sm text-gray-600 mb-4">
            <div className="flex items-center space-x-4">
              <span className="font-medium">{thread.author.username}</span>
              <span>•</span>
              <span>{formatDistanceToNow(new Date(thread.createdAt), { addSuffix: true })}</span>
              <span>•</span>
              <span>{thread.viewCount} views</span>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setReplyingTo(null)}
                className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
              >
                Reply
              </button>
            </div>
          </div>
          
          <div className="prose max-w-none">
            <p className="text-gray-700 whitespace-pre-wrap">{thread.content}</p>
          </div>
          
          <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-200">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => handleVote(thread.id, 'up')}
                className="flex items-center space-x-1 text-gray-600 hover:text-green-600"
              >
                <span className="text-lg">↑</span>
                <span>{thread.upvotes}</span>
              </button>
              <button
                onClick={() => handleVote(thread.id, 'down')}
                className="flex items-center space-x-1 text-gray-600 hover:text-red-600"
              >
                <span className="text-lg">↓</span>
                <span>{thread.downvotes}</span>
              </button>
            </div>
            <div className="text-sm text-gray-600">
              {thread.postCount} {thread.postCount === 1 ? 'reply' : 'replies'}
            </div>
          </div>
        </div>

        {/* Reply Editor */}
        {replyingTo !== null && (
          <div className="mb-6">
            <PostEditor
              onSubmit={handleReply}
              onCancel={() => setReplyingTo(null)}
              placeholder={`Replying to ${replyingTo ? 'post' : 'thread'}...`}
              submitLabel="Post Reply"
            />
          </div>
        )}

        {/* Posts List */}
        <div className="space-y-4">
          {posts.map(post => (
            <div
              key={post.id}
              className="bg-white rounded-lg shadow-sm border border-gray-200 p-6"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="flex items-center space-x-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="font-semibold text-blue-600">
                      {post.author.username.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <div className="font-medium text-gray-900">
                      {post.author.username}
                    </div>
                    <div className="text-sm text-gray-600">
                      {formatDistanceToNow(new Date(post.createdAt), { addSuffix: true })}
                    </div>
                  </div>
                </div>
                
                {isAuthenticated && (
                  <button
                    onClick={() => setReplyingTo(post.id)}
                    className="px-3 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 transition-colors"
                  >
                    Reply
                  </button>
                )}
              </div>
              
              <div className="prose max-w-none mb-4">
                <p className="text-gray-700 whitespace-pre-wrap">{post