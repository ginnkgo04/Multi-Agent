import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: '粉色小猪 - 世界上最可爱的小猪',
  description: '欢迎来到粉色小猪的梦幻世界！认识这只可爱、粉嫩、充满活力的小猪，发现它的独特魅力和趣味小知识。',
  keywords: ['粉色小猪', '可爱动物', '宠物', '小猪', '粉色', '可爱'],
  authors: [{ name: '粉色小猪乐园' }],
  creator: '粉色小猪设计团队',
  publisher: '粉色小猪有限公司',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },
  openGraph: {
    type: 'website',
    locale: 'zh_CN',
    url: 'https://pink-pig.vercel.app',
    title: '粉色小猪 - 世界上最可爱的小猪',
    description: '欢迎来到粉色小猪的梦幻世界！',
    siteName: '粉色小猪乐园',
    images: [
      {
        url: '/og-image.png',
        width: 1200,
        height: 630,
        alt: '粉色小猪',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: '粉色小猪 - 世界上最可爱的小猪',
    description: '欢迎来到粉色小猪的梦幻世界！',
    images: ['/twitter-image.png'],
    creator: '@pinkpigworld',
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
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <head>
        <link rel="icon" href="/favicon.ico" sizes="any" />
        <link
          rel="icon"
          href="/icon?<generated>"
          type="image/<generated>"
          sizes="<generated>"
        />
        <link
          rel="apple-touch-icon"
          href="/apple-icon?<generated>"
          type="image/<generated>"
          sizes="<generated>"
        />
        <meta name="theme-color" content="#f472b6" />
        <script
          dangerouslySetInnerHTML={{
            __html: `
              // Simple theme detection
              (function() {
                try {
                  const theme = localStorage.getItem('pink-pig-theme') || 'pink';
                  document.documentElement.setAttribute('data-theme', theme);
                } catch (e) {}
              })();
            `,
          }}
        />
      </head>
      <body className={`${inter.className} antialiased`}>
        {children}
        
        {/* Simple analytics script */}
        <script
          dangerouslySetInnerHTML={{
            __html: `
              // Basic page view tracking
              (function() {
                if (typeof window !== 'undefined') {
                  console.log('粉色小猪页面加载完成！🐷');
                  
                  // Track page view
                  try {
                    localStorage.setItem('lastVisit', new Date().toISOString());
                  } catch (e) {}
                  
                  // Add to history
                  window.addEventListener('load', function() {
                    setTimeout(function() {
                      console.log('页面完全加载，准备展示可爱的小猪！');
                    }, 100);
                  });
                }
              })();
            `,
          }}
        />
      </body>
    </html>
  );
}