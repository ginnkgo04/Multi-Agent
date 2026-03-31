import { Suspense } from 'react';
import Link from 'next/link';
import { getCategories } from '@/lib/api';
import { getCurrentUser } from '@/lib/auth';
import Header from '@/components/Header';
import NotificationCenter from '@/components/NotificationCenter';

interface Category {
  id: string;
  name: string;
  description: string;
  threadCount: number;
  postCount: number;
  lastActivity?: string;
}

export default async function HomePage() {
  const user = await getCurrentUser();
  const categories: Category[] = await getCategories();

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <Header user={user} />
      
      <main className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Main content */}
          <div className="lg:w-3/4">
            <div className="bg-white rounded-2xl shadow-lg p-6 mb-8">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h1 className="text-3xl font-bold text-gray-900">Forum Categories</h1>
                  <p className="text-gray-600 mt-2">
                    Browse discussions by category. Join the conversation!
                  </p>
                </div>
                {user && (
                  <Link
                    href="/forum/general"
                    className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200"
                  >
                    Start New Thread
                  </Link>
                )}
              </div>

              {/* Categories Grid */}
              <div className="space-y-4">
                {categories.map((category) => (
                  <div
                    key={category.id}
                    className="border border-gray-200 rounded-xl p-5 hover:border-blue-300 hover:shadow-md transition duration-200"
                  >
                    <div className="flex flex-col md:flex-row md:items-center justify-between">
                      <div className="mb-4 md:mb-0 md:w-2/3">
                        <div className="flex items-center gap-3 mb-2">
                          <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                          <Link
                            href={`/forum/${category.id}`}
                            className="text-xl font-bold text-gray-900 hover:text-blue-600 transition"
                          >
                            {category.name}
                          </Link>
                        </div>
                        <p className="text-gray-600">{category.description}</p>
                      </div>
                      
                      <div className="flex items-center gap-6 text-sm text-gray-500">
                        <div className="text-center">
                          <div className="font-bold text-gray-900">{category.threadCount}</div>
                          <div>Threads</div>
                        </div>
                        <div className="text-center">
                          <div className="font-bold text-gray-900">{category.postCount}</div>
                          <div>Posts</div>
                        </div>
                        <div className="text-center">
                          <div className="font-semibold text-gray-900">
                            {category.lastActivity ? 'Recent' : 'No activity'}
                          </div>
                          <div>Activity</div>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Stats Section */}
              <div className="mt-10 pt-8 border-t border-gray-200">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Forum Statistics</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-blue-50 rounded-xl p-5">
                    <div className="text-3xl font-bold text-blue-700">
                      {categories.reduce((sum, cat) => sum + cat.threadCount, 0)}
                    </div>
                    <div className="text-gray-700 font-medium">Total Threads</div>
                  </div>
                  <div className="bg-green-50 rounded-xl p-5">
                    <div className="text-3xl font-bold text-green-700">
                      {categories.reduce((sum, cat) => sum + cat.postCount, 0)}
                    </div>
                    <div className="text-gray-700 font-medium">Total Posts</div>
                  </div>
                  <div className="bg-purple-50 rounded-xl p-5">
                    <div className="text-3xl font-bold text-purple-700">
                      {categories.length}
                    </div>
                    <div className="text-gray-700 font-medium">Active Categories</div>
                  </div>
                </div>
              </div>
            </div>

            {/* Welcome Section for Guests */}
            {!user && (
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl shadow-lg p-8">
                <div className="flex flex-col md:flex-row items-center justify-between">
                  <div className="mb-6 md:mb-0 md:w-2/3">
                    <h2 className="text-2xl font-bold text-gray-900 mb-3">
                      Join Our Community
                    </h2>
                    <p className="text-gray-700 mb-4">
                      Create an account to participate in discussions, post threads, 
                      reply to others, and receive real-time notifications.
                    </p>
                    <div className="flex flex-wrap gap-4">
                      <Link
                        href="/auth/register"
                        className="bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200"
                      >
                        Sign Up Free
                      </Link>
                      <Link
                        href="/auth/login"
                        className="bg-white hover:bg-gray-50 text-blue-600 font-semibold py-3 px-6 rounded-lg border border-blue-300 transition duration-200"
                      >
                        Log In
                      </Link>
                    </div>
                  </div>
                  <div className="text-6xl">💬</div>
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="lg:w-1/4">
            {/* User Info Card */}
            {user ? (
              <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
                <div className="flex items-center gap-4 mb-4">
                  <div className="w-12 h-12 rounded-full bg-blue-100 flex items-center justify-center">
                    <span className="text-xl font-bold text-blue-600">
                      {user.username.charAt(0).toUpperCase()}
                    </span>
                  </div>
                  <div>
                    <div className="font-bold text-gray-900">{user.username}</div>
                    <div className="text-sm text-gray-500">Member</div>
                  </div>
                </div>
                <div className="space-y-3">
                  <Link
                    href="/forum/general"
                    className="block w-full text-center bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium py-2 rounded-lg transition"
                  >
                    My Threads
                  </Link>
                  <Link
                    href="/forum/general"
                    className="block w-full text-center bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium py-2 rounded-lg transition"
                  >
                    My Replies
                  </Link>
                </div>
              </div>
            ) : null}

            {/* Recent Activity */}
            <div className="bg-white rounded-2xl shadow-lg p-6 mb-6">
              <h3 className="font-bold text-gray-900 mb-4">Recent Activity</h3>
              <div className="space-y-4">
                {categories.slice(0, 3).map((category) => (
                  <div key={category.id} className="flex items-center gap-3">
                    <div className="w-2 h-2 rounded-full bg-green-500"></div>
                    <div className="text-sm">
                      <div className="font-medium text-gray-900">{category.name}</div>
                      <div className="text-gray-500">
                        {category.threadCount} active threads
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Links */}
            <div className="bg-white rounded-2xl shadow-lg p-6">
              <h3 className="font-bold text-gray-900 mb-4">Quick Links</h3>
              <div className="space-y-3">
                <Link
                  href="/forum/general"
                  className="block text-blue-600 hover:text-blue-800 font-medium"
                >
                  General Discussion
                </Link>
                <Link
                  href="/forum/help"
                  className="block text-blue-600 hover:text-blue-800 font-medium"
                >
                  Help & Support
                </Link>
                <Link
                  href="/forum/announcements"
                  className="block text-blue-600 hover:text-blue-800 font-medium"
                >
                  Announcements
                </Link>
                <Link
                  href="/forum/feedback"
                  className="block text-blue-600 hover:text-blue-800 font-medium"
                >
                  Feedback & Suggestions
                </Link>
              </div>
            </div>
          </div>
        </div>
      </main>

      {/* Notification Center */}
      <Suspense fallback={null}>
        {user && <NotificationCenter userId={user.id} />}
      </Suspense>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-8 mt-12">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-6 md:mb-0">
              <div className="text-2xl font-bold mb-2">Forum Platform</div>
              <div className="text-gray-400">Connect, discuss, and share knowledge</div>
            </div>
            <div className="flex gap-6">
              <