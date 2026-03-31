import { Header } from '@/components/Header';
import ThreadList from '@/components/ThreadList';
import Link from 'next/link';
import { getCategories, getFeaturedThreads } from '@/lib/api';

export default async function Home() {
  // Fetch data on the server
  const categories = await getCategories();
  const featuredThreads = await getFeaturedThreads();

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-gray-100">
      <Header />
      
      <main className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Hero Section */}
        <section className="mb-12 text-center">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Welcome to the Community Forum
          </h1>
          <p className="text-lg md:text-xl text-gray-600 max-w-3xl mx-auto">
            Join discussions, share knowledge, and connect with like-minded people across various topics.
          </p>
          <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/auth/register"
              className="inline-flex items-center justify-center px-6 py-3 border border-transparent text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 transition-colors duration-200"
            >
              Get Started
            </Link>
            <Link
              href="/forum/general"
              className="inline-flex items-center justify-center px-6 py-3 border border-gray-300 text-base font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 transition-colors duration-200"
            >
              Browse Discussions
            </Link>
          </div>
        </section>

        {/* Categories Grid */}
        <section className="mb-12">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900">Forum Categories</h2>
            <Link
              href="/forum"
              className="text-indigo-600 hover:text-indigo-800 font-medium transition-colors duration-200"
            >
              View all categories →
            </Link>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {categories.map((category) => (
              <Link
                key={category.id}
                href={`/forum/${category.slug}`}
                className="block bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 p-6 border border-gray-200"
              >
                <div className="flex items-start space-x-4">
                  <div className={`p-3 rounded-lg ${category.color} bg-opacity-10`}>
                    <div className={`w-6 h-6 ${category.iconColor}`} />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">{category.name}</h3>
                    <p className="text-gray-600 text-sm mb-3">{category.description}</p>
                    <div className="flex items-center text-sm text-gray-500">
                      <span>{category.threadCount} threads</span>
                      <span className="mx-2">•</span>
                      <span>{category.postCount} posts</span>
                    </div>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </section>

        {/* Featured Threads */}
        <section className="mb-12">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-2xl md:text-3xl font-bold text-gray-900">Featured Discussions</h2>
            <Link
              href="/forum/general"
              className="text-indigo-600 hover:text-indigo-800 font-medium transition-colors duration-200"
            >
              View all threads →
            </Link>
          </div>
          
          <div className="bg-white rounded-lg shadow-md overflow-hidden">
            <ThreadList threads={featuredThreads} showCategory={true} />
          </div>
        </section>

        {/* Stats Section */}
        <section className="bg-white rounded-lg shadow-md p-6 mb-12">
          <h2 className="text-2xl md:text-3xl font-bold text-gray-900 mb-6 text-center">Community Stats</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-indigo-600 mb-2">1,234</div>
              <div className="text-gray-600">Active Members</div>
            </div>
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-indigo-600 mb-2">5,678</div>
              <div className="text-gray-600">Total Threads</div>
            </div>
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-indigo-600 mb-2">23,456</div>
              <div className="text-gray-600">Total Posts</div>
            </div>
            <div className="text-center">
              <div className="text-3xl md:text-4xl font-bold text-indigo-600 mb-2">89</div>
              <div className="text-gray-600">Online Now</div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl shadow-xl p-8 md:p-12 text-center">
          <h2 className="text-2xl md:text-3xl font-bold text-white mb-4">Ready to join the conversation?</h2>
          <p className="text-indigo-100 mb-8 max-w-2xl mx-auto">
            Create an account to start participating in discussions, ask questions, and share your knowledge with the community.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/auth/register"
              className="inline-flex items-center justify-center px-6 py-3 border-2 border-white text-base font-medium rounded-md text-indigo-600 bg-white hover:bg-gray-50 transition-colors duration-200"
            >
              Sign Up Free
            </Link>
            <Link
              href="/auth/login"
              className="inline-flex items-center justify-center px-6 py-3 border-2 border-white text-base font-medium rounded-md text-white hover:bg-white hover:text-indigo-600 transition-colors duration-200"
            >
              Log In
            </Link>
          </div>
        </section>
      </main>

      <footer className="bg-gray-900 text-white py-8 mt-12">
        <div className="container mx-auto px-4 max-w-7xl">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-6 md:mb-0">
              <h3 className="text-xl font-bold mb-2">Community Forum</h3>
              <p className="text-gray-400">Connecting people through meaningful discussions</p>
            </div>
            <div className="flex space-x-6">
              <Link href="/about" className="text-gray-400 hover:text-white transition-colors duration-200">
                About
              </Link>
              <Link href="/privacy" className="text-gray-400 hover:text-white transition-colors duration-200">
                Privacy
              </Link>
              <Link href="/terms" className="text-gray-400 hover:text-white transition-colors duration-200">
                Terms
              </Link>
              <Link href="/contact" className="text-gray-400 hover:text-white transition-colors duration-200">
                Contact
              </Link>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-gray-800 text-center text-gray-400 text-sm">
            <p>© {new Date().getFullYear()} Community Forum. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}