import type { Metadata } from 'next';
import { Inter } from 'next/font/google';
import './globals.css';
import { Home, Utensils, MapPin, Phone } from 'lucide-react';

const inter = Inter({ subsets: ['latin'] });

export const metadata: Metadata = {
  title: '沙县小吃 - 传统中国街头美食',
  description: '源自福建沙县的经典美食，传承百年制作工艺，为您带来地道的中国街头小吃体验',
  keywords: '沙县小吃, 中国美食, 街头小吃, 扁肉, 拌面, 蒸饺, 传统美食',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body className={inter.className}>
        {/* Navigation */}
        <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur-sm border-b border-gray-200">
          <div className="max-w-6xl mx-auto px-4">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center">
                <div className="flex items-center space-x-2">
                  <div className="w-8 h-8 bg-amber-600 rounded-full flex items-center justify-center">
                    <Utensils className="w-5 h-5 text-white" />
                  </div>
                  <span className="text-xl font-bold text-gray-900">沙县小吃</span>
                </div>
              </div>
              
              <div className="hidden md:flex items-center space-x-8">
                <a href="#home" className="text-gray-700 hover:text-amber-600 transition-colors flex items-center">
                  <Home className="w-4 h-4 mr-2" />
                  首页
                </a>
                <a href="#menu" className="text-gray-700 hover:text-amber-600 transition-colors flex items-center">
                  <Utensils className="w-4 h-4 mr-2" />
                  菜单
                </a>
                <a href="#locations" className="text-gray-700 hover:text-amber-600 transition-colors flex items-center">
                  <MapPin className="w-4 h-4 mr-2" />
                  门店
                </a>
                <a href="#contact" className="text-gray-700 hover:text-amber-600 transition-colors flex items-center">
                  <Phone className="w-4 h-4 mr-2" />
                  联系
                </a>
              </div>
              
              <button className="md:hidden">
                <svg className="w-6 h-6 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
            </div>
          </div>
        </nav>

        {/* Main Content */}
        <main>{children}</main>

        {/* Footer */}
        <footer className="bg-gray-900 text-white py-12 px-4">
          <div className="max-w-6xl mx-auto">
            <div className="grid md:grid-cols-4 gap-8">
              <div>
                <div className="flex items-center space-x-2 mb-4">
                  <div className="w-8 h-8 bg-amber-600 rounded-full flex items-center justify-center">
                    <Utensils className="w-5 h-5 text-white" />
                  </div>
                  <span className="text-xl font-bold">沙县小吃</span>
                </div>
                <p className="text-gray-400 text-sm">
                  传承百年工艺，品味地道美食
                </p>
              </div>
              
              <div>
                <h3 className="font-semibold text-lg mb-4">快速链接</h3>
                <ul className="space-y-2">
                  <li><a href="#menu" className="text-gray-400 hover:text-white transition-colors">菜单</a></li>
                  <li><a href="#about" className="text-gray-400 hover:text-white transition-colors">关于我们</a></li>
                  <li><a href="#locations" className="text-gray-400 hover:text-white transition-colors">门店查询</a></li>
                  <li><a href="#contact" className="text-gray-400 hover:text-white transition-colors">联系我们</a></li>
                </ul>
              </div>
              
              <div>
                <h3 className="font-semibold text-lg mb-4">联系我们</h3>
                <ul className="space-y-2 text-gray-400">
                  <li>客服热线: 400-123-4567</li>
                  <li>邮箱: contact@shaxian.com</li>
                  <li>营业时间: 6:30 - 22:00</li>
                </ul>
              </div>
              
              <div>
                <h3 className="font-semibold text-lg mb-4">关注我们</h3>
                <div className="flex space-x-4">
                  <a href="#" className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-gray-700 transition-colors">
                    <span className="text-sm">微</span>
                  </a>
                  <a href="#" className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-gray-700 transition-colors">
                    <span className="text-sm">抖</span>
                  </a>
                  <a href="#" className="w-10 h-10 bg-gray-800 rounded-full flex items-center justify-center hover:bg-gray-700 transition-colors">
                    <span className="text-sm">快</span>
                  </a>
                </div>
              </div>
            </div>
            
            <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-500 text-sm">
              <p>© 2024 沙县小吃. 保留所有权利.</p>
              <p className="mt-2">传承中华美食文化，服务全球顾客</p>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}