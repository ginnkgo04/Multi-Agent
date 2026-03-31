import { Suspense } from 'react';
import Link from 'next/link';
import { notFound } from 'next/navigation';
import { Metadata } from 'next';
import { getCategoryThreads, getCategoryInfo } from '@/lib/api';
import ThreadList from '@/components/ThreadList';
import PostEditor from '@/components/PostEditor';
import { getCurrentUser } from '@/lib/auth';
import { Thread } from '@/lib/api';

type PageProps = {
  params: Promise<{ category: string }>;
  searchParams: Promise<{ page?: string }>;
};

export async function generateMetadata({ params }: PageProps): Promise<Metadata> {
  const { category } = await params;
  const categoryInfo = await getCategoryInfo(category);
  
  return {
    title: categoryInfo?.name || 'Category',
    description: categoryInfo?.description || 'Forum category page',
  };
}

export default async function CategoryPage({ params, searchParams }: PageProps) {
  const { category } = await params;
  const searchParamsObj = await searchParams;
  const page = parseInt(searchParamsObj.page || '1');
  
  const [categoryInfo, threads, user] = await Promise.all([
    getCategoryInfo(category),
    getCategoryThreads(category, page),
    getCurrentUser(),
  ]);
  
  if (!categoryInfo) {
    notFound();
  }
  
  const canCreateThread = !!user;
  
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Category Header */}
        <div className="mb-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{categoryInfo.name}</h1>
              <p className="mt-2 text-gray-600">{categoryInfo.description}</p>
              <div className="mt-2 flex items-center gap-4 text-sm text-gray-500">
                <span>{categoryInfo.threadCount} threads</span>
                <span>{categoryInfo.postCount} posts</span>
              </div>
            </div>
            {canCreateThread && (
              <Link
                href={`/forum/${category}/new`}
                className="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                New Thread
              </Link>
            )}
          </div>
        </div>

        {/* Thread Creation Form (for new threads) */}
        {canCreateThread && (
          <div className="mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Create New Thread</h2>
              <PostEditor
                category={category}
                onSuccess={(thread) => {
                  // In a real implementation, this would trigger a redirect or refresh
                  window.location.href = `/forum/${category}/${thread.id}`;
                }}
                onCancel={() => {
                  // Handle cancel
                }}
              />
            </div>
          </div>
        )}

        {/* Threads List */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-medium text-gray-900">Threads</h2>
              <div className="text-sm text-gray-500">
                Page {page} of {Math.ceil(categoryInfo.threadCount / 20)}
              </div>
            </div>
          </div>
          
          <Suspense fallback={
            <div className="px-6 py-8">
              <div className="animate-pulse space-y-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-20 bg-gray-200 rounded"></div>
                ))}
              </div>
            </div>
          }>
            <ThreadList 
              threads={threads} 
              category={category}
              currentPage={page}
              totalPages={Math.ceil(categoryInfo.threadCount / 20)}
            />
          </Suspense>
        </div>

        {/* Pagination */}
        {categoryInfo.threadCount > 20 && (
          <div className="mt-6 flex justify-center">
            <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
              {page > 1 && (
                <Link
                  href={`/forum/${category}?page=${page - 1}`}
                  className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                >
                  <span className="sr-only">Previous</span>
                  &larr; Previous
                </Link>
              )}
              
              {Array.from({ length: Math.min(5, Math.ceil(categoryInfo.threadCount / 20)) }, (_, i) => {
                const pageNum = i + 1;
                if (Math.ceil(categoryInfo.threadCount / 20) > 5) {
                  // Show limited pagination for many pages
                  if (page <= 3) {
                    if (pageNum <= 4) {
                      return (
                        <Link
                          key={pageNum}
                          href={`/forum/${category}?page=${pageNum}`}
                          className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                            page === pageNum
                              ? 'z-10 bg-indigo-50 border-indigo-500 text-indigo-600'
                              : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                          }`}
                        >
                          {pageNum}
                        </Link>
                      );
                    }
                    if (pageNum === 5) {
                      return (
                        <span key="ellipsis" className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                          ...
                        </span>
                      );
                    }
                  } else if (page >= Math.ceil(categoryInfo.threadCount / 20) - 2) {
                    // Handle last pages
                    if (pageNum >= Math.ceil(categoryInfo.threadCount / 20) - 3) {
                      return (
                        <Link
                          key={pageNum}
                          href={`/forum/${category}?page=${pageNum}`}
                          className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                            page === pageNum
                              ? 'z-10 bg-indigo-50 border-indigo-500 text-indigo-600'
                              : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                          }`}
                        >
                          {pageNum}
                        </Link>
                      );
                    }
                  } else {
                    // Handle middle pages
                    if (pageNum >= page - 1 && pageNum <= page + 1) {
                      return (
                        <Link
                          key={pageNum}
                          href={`/forum/${category}?page=${pageNum}`}
                          className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                            page === pageNum
                              ? 'z-10 bg-indigo-50 border-indigo-500 text-indigo-600'
                              : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                          }`}
                        >
                          {pageNum}
                        </Link>
                      );
                    }
                    if (pageNum === 1 || pageNum === Math.ceil(categoryInfo.threadCount / 20)) {
                      return (
                        <Link
                          key={pageNum}
                          href={`/forum/${category}?page=${pageNum}`}
                          className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                        >
                          {pageNum}
                        </Link>
                      );
                    }
                  }
                } else {
                  // Show all pages for few pages
                  return (
                    <Link
                      key={pageNum}
                      href={`/forum/${category}?page=${pageNum}`}
                      className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                        page === pageNum
                          ? 'z-10 bg-indigo-50 border-indigo-500 text-indigo-600'
                          : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                      }`}
                    >
                      {pageNum}
                    </Link>
                  );
                }
                return null;
              })}
              
              {page < Math.ceil(categoryInfo.threadCount / 20) && (
                <Link
                  href={`/forum/${category}?page=${page + 1}`}
                  className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50"
                >
                  <span className="sr-only">Next</span>
                  Next &rarr;
                </Link>
              )}
            </nav>
          </div>
        )}

        {/* Info for non-authenticated users */}
        {!user && (
          <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg className="h-5 w-5 text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-