import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import Header from '@/components/Header'
import { AuthProvider } from '@/lib/auth'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'Forum Platform',
  description: 'A modern forum platform built with Next.js and FastAPI',
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
            <main className="flex-1 container mx-auto px-4 py-8">
              {children}
            </main>
            <footer className="bg-white border-t py-6">
              <div className="container mx-auto px-4 text-center text-gray-500 text-sm">
                <p>© {new Date().getFullYear()} Forum Platform. All rights reserved.</p>
                <p className="mt-2">Built with Next.js, FastAPI, and PostgreSQL</p>
              </div>
            </footer>
          </div>
        </AuthProvider>
      </body>
    </html>
  )
}