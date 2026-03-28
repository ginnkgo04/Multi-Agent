import FeatureExperience from '@/components/FeatureExperience';
import { Heart, Star, Smile, Coffee, Cake, Music, Share2, Download } from 'lucide-react';
import Image from 'next/image';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-pink-50 to-rose-50">
      {/* Header/Navigation */}
      <header className="sticky top-0 z-50 bg-white/80 backdrop-blur-sm border-b border-pink-200">
        <div className="container mx-auto px-4 py-4">
          <nav className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-br from-pink-400 to-rose-400 rounded-full flex items-center justify-center">
                <span className="text-white text-2xl">🐷</span>
              </div>
              <h1 className="text-2xl font-bold text-pink-600">Pink Piggy</h1>
            </div>
            <div className="flex items-center space-x-6">
              <a href="#intro" className="text-pink-600 hover:text-pink-800 font-medium transition-colors">介绍</a>
              <a href="#characteristics" className="text-pink-600 hover:text-pink-800 font-medium transition-colors">特点</a>
              <a href="#facts" className="text-pink-600 hover:text-pink-800 font-medium transition-colors">趣事</a>
              <a href="#gallery" className="text-pink-600 hover:text-pink-800 font-medium transition-colors">相册</a>
              <button className="bg-gradient-to-r from-pink-500 to-rose-500 text-white px-6 py-2 rounded-full font-medium hover:shadow-lg hover:scale-105 transition-all duration-300">
                认识我
              </button>
            </div>
          </nav>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        {/* Hero Section */}
        <section className="text-center mb-20">
          <div className="relative inline-block mb-8">
            <div className="absolute -inset-4 bg-gradient-to-r from-pink-300 to-rose-300 rounded-full blur-xl opacity-30"></div>
            <div className="relative w-48 h-48 bg-gradient-to-br from-pink-400 to-rose-400 rounded-full flex items-center justify-center mx-auto">
              <span className="text-8xl">🐷</span>
            </div>
          </div>
          <h1 className="text-5xl md:text-6xl font-bold text-pink-700 mb-6">
            欢迎来到<span className="text-rose-500">粉色小猪</span>的世界！
          </h1>
          <p className="text-xl text-pink-600 max-w-3xl mx-auto mb-10">
            我是世界上最可爱的小猪，喜欢在泥巴里打滚，也喜欢在阳光下睡觉。让我带你走进我的粉色梦幻世界！
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <button className="bg-gradient-to-r from-pink-500 to-rose-500 text-white px-8 py-3 rounded-full font-medium text-lg hover:shadow-xl hover:scale-105 transition-all duration-300 flex items-center gap-2">
              <Heart className="w-5 h-5" />
              喜欢我
            </button>
            <button className="bg-white text-pink-600 border-2 border-pink-300 px-8 py-3 rounded-full font-medium text-lg hover:bg-pink-50 hover:border-pink-400 transition-all duration-300 flex items-center gap-2">
              <Share2 className="w-5 h-5" />
              分享给朋友
            </button>
          </div>
        </section>

        {/* Introduction Section */}
        <section id="intro" className="mb-20">
          <div className="bg-white rounded-3xl p-8 md:p-12 shadow-xl border border-pink-100">
            <div className="flex items-center gap-3 mb-8">
              <div className="w-12 h-12 bg-pink-100 rounded-full flex items-center justify-center">
                <Smile className="w-6 h-6 text-pink-600" />
              </div>
              <h2 className="text-3xl font-bold text-pink-700">关于我</h2>
            </div>
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <div>
                <p className="text-lg text-gray-700 mb-6">
                  我是一只特别的小猪，有着粉粉嫩嫩的皮肤和圆圆的大眼睛。我出生在一个美丽的农场，那里有绿油油的草地和清澈的小溪。
                </p>
                <p className="text-lg text-gray-700 mb-6">
                  我最喜欢的事情就是在温暖的阳光下打盹，在泥巴里快乐地打滚，还有和农场里的小伙伴们一起玩耍。虽然我看起来有点懒洋洋的，但其实我非常聪明可爱！
                </p>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <Star className="w-5 h-5 text-yellow-500 fill-yellow-500" />
                    <span className="text-pink-600 font-medium">超级可爱</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Coffee className="w-5 h-5 text-amber-600" />
                    <span className="text-pink-600 font-medium">喜欢美食</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Music className="w-5 h-5 text-purple-500" />
                    <span className="text-pink-600 font-medium">热爱音乐</span>
                  </div>
                </div>
              </div>
              <div className="relative">
                <div className="absolute -inset-4 bg-gradient-to-r from-pink-200 to-rose-200 rounded-3xl blur-xl opacity-50"></div>
                <div className="relative bg-gradient-to-br from-pink-100 to-rose-100 rounded-2xl p-8">
                  <div className="aspect-square bg-gradient-to-br from-pink-300 to-rose-300 rounded-2xl flex items-center justify-center">
                    <span className="text-9xl">🐽</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Characteristics Section */}
        <section id="characteristics" className="mb-20">
          <h2 className="text-3xl font-bold text-pink-700 text-center mb-12">我的特点</h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: "粉嫩皮肤",
                description: "我的皮肤是天然的粉红色，柔软光滑，像棉花糖一样可爱",
                icon: "🌸",
                color: "from-pink-400 to-rose-400"
              },
              {
                title: "圆圆体型",
                description: "圆滚滚的身体让我看起来更加可爱，也让我能储存更多能量",
                icon: "⚪",
                color: "from-purple-400 to-pink-400"
              },
              {
                title: "卷卷尾巴",
                description: "我的尾巴总是卷成一个小圈圈，这是我独特的标志",
                icon: "🌀",
                color: "from-rose-400 to-orange-400"
              },
              {
                title: "大耳朵",
                description: "大大的耳朵让我能听到很远的声音，也能帮我散热",
                icon: "👂",
                color: "from-blue-400 to-cyan-400"
              },
              {
                title: "湿湿鼻子",
                description: "湿润的鼻子让我有超强的嗅觉，能找到最好吃的食物",
                icon: "👃",
                color: "from-green-400 to-emerald-400"
              },
              {
                title: "快乐性格",
                description: "我天生乐观开朗，总是用微笑面对每一天",
                icon: "😊",
                color: "from-yellow-400 to-amber-400"
              }
            ].map((feature, index) => (
              <div key={index} className="group">
                <div className="bg-white rounded-2xl p-6 shadow-lg border border-pink-100 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 h-full">
                  <div className={`w-16 h-16 bg-gradient-to-br ${feature.color} rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300`}>
                    <span className="text-3xl">{feature.icon}</span>
                  </div>
                  <h3 className="text-xl font-bold text-pink-700 mb-3">{feature.title}</h3>
                  <p className="text-gray-600">{feature.description}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Fun Facts Section */}
        <FeatureExperience />

        {/* Gallery Section */}
        <section id="gallery" className="mb-20">
          <h2 className="text-3xl font-bold text-pink-700 text-center mb-12">我的相册</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {[
              { emoji: "🐷", title: "早晨散步", desc: "在草地上享受阳光" },
              { emoji: "🛁", title: "洗澡时间", desc: "保持干净很重要" },
              { emoji: "🍎", title: "美食时间", desc: "新鲜的苹果最好吃" },
              { emoji: "💤", title: "午睡时光", desc: "美美地睡个午觉" },
              { emoji: "🎵", title: "音乐时间", desc: "跟着节奏摇摆" },
              { emoji: "🎨", title: "艺术创作", desc: "用泥巴画画" },
              { emoji: "🏆", title: "获奖时刻", desc: "最可爱小猪奖" },
              { emoji: "❤️", title: "爱心满满", desc: "给朋友们送爱心" }
            ].map((item, index) => (
              <div key={index} className="group cursor-pointer">
                <div className="bg-white rounded-2xl p-6 shadow-lg border border-pink-100 hover:shadow-xl hover:bg-pink-50 transition-all duration-300 h-full">
                  <div className="aspect-square bg-gradient-to-br from-pink-100 to-rose-100 rounded-xl flex items-center justify-center mb-4 group-hover:scale-105 transition-transform duration-300">
                    <span className="text-5xl">{item.emoji}</span>
                  </div>
                  <h4 className="font-bold text-pink-700 mb-1">{item.title}</h4>
                  <p className="text-sm text-gray-600">{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Download Section */}
        <section className="bg-gradient-to-r from-pink-500 to-rose-500 rounded-3xl p-8 md:p-12 text-white mb-20">
          <div className="max-w-3xl mx-auto text-center">
            <Cake className="w-16 h-16 mx-auto mb-6" />
            <h2 className="text-3xl font-bold mb-6">想要更多粉色小猪的快乐吗？</h2>
            <p className="text-xl mb-8 opacity-90">
              下载我的专属壁纸、表情包和彩色涂鸦，让粉色小猪的可爱充满你的生活！
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <button className="bg-white text-pink-600 px-8 py-3 rounded-full font-medium text-lg hover:bg-pink-50 hover:scale-105 transition-all duration-300 flex items-center gap-2">
                <Download className="w-5 h-5" />
                下载壁纸
              </button>
              <button className="bg-pink-600/20 border-2 border-white/30 text-white px-8 py-3 rounded-full font-medium text-lg hover:bg-pink-600/30 hover:scale-105 transition-all duration-300 flex items-center gap-2">
                <span className="text-xl">🎨</span>
                涂鸦模板
              </button>
              <button className="bg-pink-600/20 border-2 border-white/30 text-white px-8 py-3 rounded-full font-medium text-lg hover:bg-pink-600/30 hover:scale-105 transition-all duration-300 flex items-center gap-2">
                <span className="text-xl">😊</span>
                表情包
              </button>
            </div>
          </div>
        </section>
      </main>

      <footer className="bg-pink-800 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-6 md:mb-0">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-12 h-12 bg-pink-600 rounded-full flex items-center justify-center">
                  <span className="text-2xl">🐷</span>
                </div>
                <h3 className="text-2xl font-bold">粉色小猪</h3>
              </div>
              <p className="text-pink-200">传播快乐，分享可爱</p>
            </div>
            <div className="flex gap-6">
              <a href="#" className="text-pink-200 hover:text-white transition-colors">关于我们</a>
              <a href="#" className="text-pink-200 hover:text-white transition-colors">联系我们</a>
              <a href="#" className="text-pink-200 hover:text-white transition-colors">隐私政策</a>
              <a href="#" className="text-pink-200 hover:text-white transition-colors">使用条款</a>
            </div>
          </div>
          <div className="border-t border-pink-700 mt-8 pt-8 text-center text-pink-300">
            <p>© 2024 粉色小猪乐园. 保留所有权利. 设计充满爱心 💖</p>
          </div>
        </div>
      </footer>
    </div>
  );
}