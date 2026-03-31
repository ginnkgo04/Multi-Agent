import { notFound } from 'next/navigation';
import { Suspense } from 'react';
import Link from 'next/link';
import { ArrowLeft, MessageSquare, User, Calendar, ThumbsUp } from 'lucide-react';
import { getThread, getPosts, getCategory } from '@/lib/api';
import { getCurrentUser } from '@/lib/auth';
import PostEditor from '@/components/PostEditor';
import NotificationCenter from '@/components/NotificationCenter';

interface PageProps {
  params: Promise<{
    category: string;
    threadId: string;
  }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
}

export default async function ThreadPage({ params, searchParams }: PageProps) {
  const { category: categorySlug, threadId } = await params;
  const searchParamsObj = await searchParams;
  const page = searchParamsObj.page ? parseInt(searchParamsObj.page as string) : 1;
  const limit = 20;

  try {
    const [category, thread, postsData, user] = await Promise.all([
      getCategory(categorySlug),
      getThread(threadId),
      getPosts(threadId, page, limit),
      getCurrentUser(),
    ]);

    if (!category || !thread) {
      notFound();
    }

    const { posts, total } = postsData;

    const totalPages = Math.ceil(total / limit);

    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Breadcrumb */}
          <nav className="mb-6">
            <ol className="flex items-center space-x-2 text-sm text-gray-600">
              <li>
                <Link href="/" className="hover:text-blue-600 transition-colors">
                  Home
                </Link>
              </li>
              <li>/</li>
              <li>
                <Link href={`/forum/${category.slug}`} className="hover:text-blue-600 transition-colors">
                  {category.name}
                </Link>
              </li>
              <li>/</li>
              <li className="font-medium text-gray-900 truncate max-w-xs">{thread.title}</li>
            </ol>
          </nav>

          <div className="flex flex-col lg:flex-row gap-8">
            {/* Main Content */}
            <div className="lg:w-3/4">
              {/* Thread Header */}
              <div className="bg-white rounded-lg shadow-md p-6 mb-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h1 className="text-2xl font-bold text-gray-900 mb-2">{thread.title}</h1>
                    <div className="flex items-center space-x-4 text-sm text-gray-600">
                      <div className="flex items-center">
                        <User className="w-4 h-4 mr-1" />
                        <span className="font-medium">{thread.author?.username || 'Anonymous'}</span>
                      </div>
                      <div className="flex items-center">
                        <Calendar className="w-4 h-4 mr-1" />
                        <span>{new Date(thread.created_at).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center">
                        <MessageSquare className="w-4 h-4 mr-1" />
                        <span>{total} replies</span>
                      </div>
                      <div className="flex items-center">
                        <ThumbsUp className="w-4 h-4 mr-1" />
                        <span>{thread.vote_count || 0} votes</span>
                      </div>
                    </div>
                  </div>
                  <Link
                    href={`/forum/${category.slug}`}
                    className="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Back to Threads
                  </Link>
                </div>

                <div className="prose max-w-none">
                  <p className="text-gray-700 whitespace-pre-wrap">{thread.content}</p>
                </div>
              </div>

              {/* Posts List */}
              <div className="space-y-4 mb-8">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Replies ({total})</h2>
                {posts.length === 0 ? (
                  <div className="bg-white rounded-lg shadow-md p-8 text-center">
                    <MessageSquare className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                    <p className="text-gray-600">No replies yet. Be the first to respond!</p>
                  </div>
                ) : (
                  posts.map((post) => (
                    <div key={post.id} className="bg-white rounded-lg shadow-md p-6">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                            <User className="w-5 h-5 text-blue-600" />
                          </div>
                          <div>
                            <h3 className="font-medium text-gray-900">
                              {post.author?.username || 'Anonymous'}
                            </h3>
                            <p className="text-sm text-gray-500">
                              {new Date(post.created_at).toLocaleString()}
                            </p>
                          </div>
                        </div>
                        {post.is_edited && (
                          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
                            Edited
                          </span>
                        )}
                      </div>
                      <div className="prose max-w-none">
                        <p className="text-gray-700 whitespace-pre-wrap">{post.content}</p>
                      </div>
                      <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
                        <div className="flex items-center space-x-4">
                          <button className="flex items-center text-sm text-gray-600 hover:text-blue-600 transition-colors">
                            <ThumbsUp className="w-4 h-4 mr-1" />
                            <span>{post.vote_count || 0}</span>
                          </button>
                          <button className="text-sm text-gray-600 hover:text-blue-600 transition-colors">
                            Reply
                          </button>
                        </div>
                        {user?.id === post.author_id && (
                          <button className="text-sm text-blue-600 hover:text-blue-800 transition-colors">
                            Edit
                          </button>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Pagination */}
              {totalPages > 1 && (
                <div className="flex justify-center mb-8">
                  <nav className="flex items-center space-x-2">
                    {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNum) => (
                      <Link
                        key={pageNum}
                        href={`?page=${pageNum}`}
                        className={`px-3 py-2 rounded-md text-sm font-medium ${
                          page === pageNum
                            ? 'bg-blue-600 text-white'
                            : 'text-gray-700 hover:bg-gray-100'
                        }`}
                      >
                        {pageNum}
                      </Link>
                    ))}
                  </nav>
                </div>
              )}

              {/* Reply Editor */}
              <div className="bg-white rounded-lg shadow-md p-6">
                <h3 className="text-lg font-bold text-gray-900 mb-4">
                  {user ? 'Post a Reply' : 'Login to Reply'}
                </h3>
                {user ? (
                  <PostEditor
                    threadId={thread.id}
                    onSuccess={() => {
                      // This will be handled by the PostEditor component
                    }}
                  />
                ) : (
                  <div className="text-center py-8">
                    <p className="text-gray-600 mb-4">You need to be logged in to post a reply.</p>
                    <Link
                      href="/auth/login"
                      className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                    >
                      Login
                    </Link>
                  </div>
                )}
              </div>
            </div>

            {/* Sidebar */}
            <div className="lg:w-1/4">
              <div className="sticky top-8 space-y-6">
                {/* Category Info */}
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="font-bold text-gray-900 mb-4">Category Info</h3>
                  <div className="space-y-3">
                    <div>
                      <p className="text-sm text-gray-600">Category</p>
                      <p className="font-medium">{category.name}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Description</p>
                      <p className="text-gray-700">{category.description}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600">Threads</p>
                      <p className="font-medium">{category.thread_count || 0}</p>
                    </div>
                  </div>
                </div>

                {/* Thread Stats */}
                <div className="bg-white rounded-lg shadow-md p-6">
                  <h3 className="font-bold text-gray-900 mb-4">Thread Stats</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Replies</span>
                      <span className="font-medium">{total}</span