import { Suspense } from 'react';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';

import Header from '@/components/Header';
import ThreadList from '@/components/ThreadList';
import PostEditor from '@/components/PostEditor';
import { getCategoryThreads, getCategoryInfo } from '@/lib/api';
import { getCurrentUser } from '@/lib/auth';

type PageProps = {
  params: Promise<{ category: string }>;
  searchParams: Promise<{ [key: string]: string | string[] | undefined }>;
};

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { category } = await params;
  const categoryInfo = await getCategoryInfo(category);
  
  if (!categoryInfo) {
    return {
      title: 'Category Not Found',
    };
  }
  
  return {
    title: `${categoryInfo.name} - Forum`,
    description: categoryInfo.description,
  };
}

export default async function CategoryPage({ params, searchParams }: PageProps) {
  const { category } = await params;
  const searchParamsObj = await searchParams;
  const page = searchParamsObj.page ? parseInt(searchParamsObj.page as string) : 1;
  
  const [categoryInfo, threads, user] = await Promise.all([
    getCategoryInfo(category),
    getCategoryThreads(category, page),
    getCurrentUser(),
  ]);
  
  if (!categoryInfo) {
    notFound();
  }
  
  const isAuthenticated = !!user;
  
  return (
    <div className="min-h-screen bg-gray-50">
      <Header user={user} />
      
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        {/* Category Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{categoryInfo.name}</h1>
              <p className="text-gray-600 mt-2">{categoryInfo.description}</p>
            </div>
            <div className="text-sm text-gray-500">
              <span className="font-medium">{categoryInfo.threadCount}</span> threads •{' '}
              <span className="font-medium">{categoryInfo.postCount}</span> posts
            </div>
          </div>
          
          <div className="flex items-center space-x-4 text-sm">
            <Link 
              href="/" 
              className="text-blue-600 hover:text-blue-800 hover:underline"
            >
              ← Back to Categories
            </Link>
            <span className="text-gray-400">•</span>
            <span className="text-gray-600">
              Category: <span className="font-medium">{categoryInfo.name}</span>
            </span>
          </div>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Main Content - Threads List */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
              {/* Threads Header */}
              <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                <h2 className="text-xl font-semibold text-gray-800">Threads</h2>
                <div className="flex items-center space-x-2">
                  <span className="text-sm text-gray-500">Sort by:</span>
                  <select className="text-sm border border-gray-300 rounded px-3 py-1 bg-white">
                    <option>Latest</option>
                    <option>Most Popular</option>
                    <option>Most Replies</option>
                  </select>
                </div>
              </div>
              
              {/* Threads List */}
              <Suspense fallback={
                <div className="px-6 py-8">
                  <div className="animate-pulse space-y-4">
                    {[1, 2, 3].map((i) => (
                      <div key={i} className="h-24 bg-gray-200 rounded"></div>
                    ))}
                  </div>
                </div>
              }>
                <ThreadList 
                  threads={threads.threads} 
                  category={category}
                />
              </Suspense>
              
              {/* Pagination */}
              {threads.totalPages > 1 && (
                <div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
                  <div className="text-sm text-gray-500">
                    Showing page {page} of {threads.totalPages}
                  </div>
                  <div className="flex space-x-2">
                    {page > 1 && (
                      <Link
                        href={`/forum/${category}?page=${page - 1}`}
                        className="px-4 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50"
                      >
                        Previous
                      </Link>
                    )}
                    {page < threads.totalPages && (
                      <Link
                        href={`/forum/${category}?page=${page + 1}`}
                        className="px-4 py-2 text-sm border border-gray-300 rounded hover:bg-gray-50"
                      >
                        Next
                      </Link>
                    )}
                  </div>
                </div>
              )}
            </div>
            
            {/* Create New Thread */}
            <div className="mt-8">
              <h3 className="text-lg font-semibold text-gray-800 mb-4">Start a New Thread</h3>
              {isAuthenticated ? (
                <PostEditor 
                  category={category}
                  mode="thread"
                  onSuccess={() => window.location.reload()}
                />
              ) : (
                <div className="bg-white rounded-lg border border-gray-200 p-6 text-center">
                  <p className="text-gray-600 mb-4">
                    You need to be logged in to create a new thread.
                  </p>
                  <div className="flex justify-center space-x-4">
                    <Link
                      href="/auth/login"
                      className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                    >
                      Log In
                    </Link>
                    <Link
                      href="/auth/register"
                      className="px-4 py-2 border border-gray-300 text-gray-700 rounded hover:bg-gray-50"
                    >
                      Register
                    </Link>
                  </div>
                </div>
              )}
            </div>
          </div>
          
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="space-y-6">
              {/* Category Info */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="font-semibold text-gray-800 mb-4">Category Info</h3>
                <div className="space-y-3">
                  <div>
                    <div className="text-sm text-gray-500">Created</div>
                    <div className="font-medium">
                      {new Date(categoryInfo.createdAt).toLocaleDateString()}
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Moderators</div>
                    <div className="font-medium">
                      {categoryInfo.moderatorCount} moderators
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-gray-500">Rules</div>
                    <ul className="mt-1 text-sm text-gray-600 space-y-1">
                      <li>• Be respectful to others</li>
                      <li>• Stay on topic</li>
                      <li>• No spam or self-promotion</li>
                    </ul>
                  </div>
                </div>
              </div>
              
              {/* Quick Stats */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="font-semibold text-gray-800 mb-4">Quick Stats</h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Active Threads</span>
                    <span className="font-semibold">{categoryInfo.activeThreadCount}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Today's Posts</span>
                    <span className="font-semibold">{categoryInfo.todaysPostCount}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Total Members</span>
                    <span className="font-semibold">{categoryInfo.memberCount}</span>
                  </div>
                </div>
              </div>
              
              {/* Helpful Links */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="font-semibold text-gray-800 mb-4">Helpful Links</h3>
                <ul className="space-y-2">
                  <li>
                    <Link 
                      href="/forum/announcements" 
                      className="text-blue-600 hover:text-blue-800 hover:underline text-sm"
                    >
                      Forum Announcements
                    </Link>
                  </li>
                  <li>
                    <Link 
                      href="/forum/support" 
                      className="text-blue-600 hover:text-blue-800 hover:underline text-sm"
                    >
                      Technical Support
                    </Link>
                  </li>
                  <li>
                    <Link 
                      href="/forum/feedback" 
                      className="text-blue-600 hover:text-blue-800 hover:underline text-sm"
                    >
                      Give Feedback
                    </Link>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </main>
      
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="container mx-auto px-4 py-6 max-w-6xl">
          <div className="text-center text-gray-