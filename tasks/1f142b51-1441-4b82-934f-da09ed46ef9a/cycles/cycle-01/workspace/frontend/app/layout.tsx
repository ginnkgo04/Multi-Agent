import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: '小熊猫介绍 - 世界上最可爱的动物',
  description: '探索小熊猫的奇妙世界：了解这种濒危物种的习性、栖息地、饮食和保护现状。',
  keywords: ['小熊猫', '红熊猫', '濒危动物', '野生动物保护', '喜马拉雅山脉'],
  authors: [{ name: '小熊猫保护组织' }],
  creator: '小熊猫保护组织',
  publisher: '小熊猫保护组织',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  metadataBase: new URL('https://red-panda-website.vercel.app'),
  alternates: {
    canonical: '/',
  },
  openGraph: {
    title: '小熊猫介绍 - 世界上最可爱的动物',
    description: '探索小熊猫的奇妙世界：了解这种濒危物种的习性、栖息地、饮食和保护现状。',
    url: 'https://red-panda-website.vercel.app',
    siteName: '小熊猫介绍网站',
    images: [
      {
        url: 'https://images.unsplash.com/photo-1599236449652-f2a5d0a5c5c9?auto=format&fit=crop&w=1200',
        width: 1200,
        height: 630,
        alt: '小熊猫在树枝上休息',
      },
    ],
    locale: 'zh_CN',
    type: 'website',
  },
  twitter: {
    card: 'summary_large_image',
    title: '小熊猫介绍 - 世界上最可爱的动物',
    description: '探索小熊猫的奇妙世界：了解这种濒危物种的习性、栖息地、饮食和保护现状。',
    images: ['https://images.unsplash.com/photo-1599236449652-f2a5d0a5c5c9?auto=format&fit=crop&w=1200'],
    creator: '@redpandacare',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
  verification: {
    google: 'google-site-verification-code',
    yandex: 'yandex-verification-code',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link
          rel="apple-touch-icon"
          href="/apple-touch-icon.png"
          type="image/png"
          sizes="180x180"
        />
        <link
          rel="icon"
          href="/favicon-32x32.png"
          type="image/png"
          sizes="32x32"
        />
        <link
          rel="icon"
          href="/favicon-16x16.png"
          type="image/png"
          sizes="16x16"
        />
        <link rel="manifest" href="/site.webmanifest" />
        <meta name="theme-color" content="#f97316" />
        <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5" />
        
        {/* Structured Data for SEO */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "WebSite",
              "name": "小熊猫介绍网站",
              "url": "https://red-panda-website.vercel.app",
              "description": "探索小熊猫的奇妙世界：了解这种濒危物种的习性、栖息地、饮食和保护现状。",
              "publisher": {
                "@type": "Organization",
                "name": "小熊猫保护组织",
                "logo": {
                  "@type": "ImageObject",
                  "url": "https://red-panda-website.vercel.app/logo.png"
                }
              }
            })
          }}
        />
      </head>
      <body className={`${inter.className} antialiased`}>
        {/* Skip to main content link for accessibility */}
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-red-500 text-white px-4 py-2 rounded-lg z-50"
        >
          跳转到主要内容
        </a>
        
        <div id="main-content">
          {children}
        </div>
        
        {/* Accessibility widget */}
        <div className="fixed bottom-4 right-4 z-40">
          <button
            aria-label="调整字体大小"
            className="bg-red-500 text-white p-3 rounded-full shadow-lg hover:bg-red-600 transition-colors"
            onClick={() => {
              document.documentElement.style.fontSize = '110%'
            }}
          >
            A+
          </button>
        </div>
      </body>
    </html>
  )
}