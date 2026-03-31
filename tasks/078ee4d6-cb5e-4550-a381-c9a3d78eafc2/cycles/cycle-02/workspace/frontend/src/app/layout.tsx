import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Header from '@/components/Header'
import NotificationCenter from '@/components/NotificationCenter'
import { AuthProvider } from '@/lib/auth'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Forum Platform',
  description: 'A modern forum platform with real-time notifications',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-50 text-gray-900`}>
        <AuthProvider>
          <div className="min-h-screen flex flex-col">
            <Header />
            <main className="flex-1 container mx-auto px-4 py-6 md:px-6 lg:px-8">
              {children}
            </main>
            <NotificationCenter />
            <footer className="bg-white border-t border-gray-200 py-6">
              <div className="container mx-auto px-4 text-center text-gray-500 text-sm">
                <p>© {new Date().getFullYear()} Forum Platform. All rights reserved.</p>
                <p className="mt-1">Built with Next.js, FastAPI, and WebSocket</p>
              </div>
            </footer>
          </div>
        </AuthProvider>
      </body>
    </html>
  )
}