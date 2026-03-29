import FeatureExperience from '@/components/FeatureExperience';
import { TreePine, Mountain, Leaf, ShieldAlert, Heart } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-amber-50 to-orange-50">
      {/* Hero Section */}
      <header className="relative overflow-hidden bg-gradient-to-r from-red-600 to-orange-500 text-white">
        <div className="container mx-auto px-4 py-16 md:py-24">
          <div className="max-w-3xl">
            <h1 className="text-4xl md:text-6xl font-bold mb-4">
              小熊猫
              <span className="block text-2xl md:text-3xl font-light mt-2">
                The Red Panda (Ailurus fulgens)
              </span>
            </h1>
            <p className="text-xl md:text-2xl mb-8 opacity-90">
              世界上最可爱的动物之一，生活在喜马拉雅山脉东部
            </p>
            <div className="flex flex-wrap gap-4">
              <span className="bg-white/20 px-4 py-2 rounded-full">濒危物种</span>
              <span className="bg-white/20 px-4 py-2 rounded-full">喜马拉雅山脉</span>
              <span className="bg-white/20 px-4 py-2 rounded-full">竹食动物</span>
            </div>
          </div>
        </div>
        <div className="absolute bottom-0 right-0 w-64 h-64 md:w-96 md:h-96 opacity-20">
          <div className="w-full h-full bg-[url('https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?auto=format&fit=crop&w=800')] bg-cover bg-center rounded-full"></div>
        </div>
      </header>

      <main className="container mx-auto px-4 py-12">
        {/* Introduction Section */}
        <section className="mb-16">
          <div className="grid md:grid-cols-2 gap-8 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-800 mb-6">认识小熊猫</h2>
              <p className="text-gray-600 mb-4 text-lg">
                小熊猫（学名：Ailurus fulgens），又称红熊猫，是一种小型哺乳动物，原产于喜马拉雅山脉东部和中国西南地区。
              </p>
              <p className="text-gray-600 mb-4">
                尽管名字中有"熊猫"，但它们与大熊猫的亲缘关系并不近。小熊猫属于小熊猫科，是唯一现存的物种。
              </p>
              <p className="text-gray-600">
                它们以其红褐色的皮毛、长而蓬松的尾巴和可爱的面部特征而闻名，常被称为"世界上最可爱的动物"之一。
              </p>
            </div>
            <div className="relative h-64 md:h-80 rounded-2xl overflow-hidden shadow-xl">
              <div className="absolute inset-0 bg-gradient-to-r from-red-500 to-orange-400 opacity-20"></div>
              <div className="absolute inset-0 bg-[url('https://images.unsplash.com/photo-1599236449652-f2a5d0a5c5c9?auto=format&fit=crop&w=800')] bg-cover bg-center"></div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-center text-gray-800 mb-12">主要特征</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
              <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mb-4">
                <TreePine className="w-6 h-6 text-red-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">栖息地</h3>
              <p className="text-gray-600">生活在海拔2000-4800米的温带森林中，喜欢竹林茂密的地区。</p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <Leaf className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">饮食习性</h3>
              <p className="text-gray-600">主要以竹子为食，也吃水果、橡子、根茎和小型动物。</p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Mountain className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">分布范围</h3>
              <p className="text-gray-600">分布于尼泊尔、印度、不丹、缅甸和中国西南部。</p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-lg hover:shadow-xl transition-shadow">
              <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center mb-4">
                <ShieldAlert className="w-6 h-6 text-yellow-600" />
              </div>
              <h3 className="text-xl font-semibold mb-2">保护状态</h3>
              <p className="text-gray-600">被世界自然保护联盟列为濒危物种，野外数量持续减少。</p>
            </div>
          </div>
        </section>

        {/* Interactive Experience */}
        <section className="mb-16">
          <FeatureExperience />
        </section>

        {/* Conservation Section */}
        <section className="bg-gradient-to-r from-red-50 to-orange-50 rounded-2xl p-8 mb-16">
          <div className="max-w-3xl mx-auto text-center">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <Heart className="w-8 h-8 text-red-600" />
            </div>
            <h2 className="text-3xl font-bold text-gray-800 mb-4">保护小熊猫</h2>
            <p className="text-gray-600 mb-6 text-lg">
              小熊猫面临栖息地丧失、非法捕猎和气候变化等多重威胁。全球野生小熊猫数量估计不足10,000只。
            </p>
            <div className="grid md:grid-cols-3 gap-6 mt-8">
              <div className="bg-white p-6 rounded-xl">
                <h4 className="font-semibold mb-2">栖息地保护</h4>
                <p className="text-sm text-gray-600">建立自然保护区，保护现有森林</p>
              </div>
              <div className="bg-white p-6 rounded-xl">
                <h4 className="font-semibold mb-2">反盗猎行动</h4>
                <p className="text-sm text-gray-600">加强执法，打击非法野生动物贸易</p>
              </div>
              <div className="bg-white p-6 rounded-xl">
                <h4 className="font-semibold mb-2">公众教育</h4>
                <p className="text-sm text-gray-600">提高公众保护意识，支持可持续旅游</p>
              </div>
            </div>
          </div>
        </section>

        {/* Fun Facts */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-center text-gray-800 mb-8">有趣的事实</h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-xl shadow-md">
              <h3 className="font-semibold mb-2">灵活的脚踝</h3>
              <p className="text-gray-600">小熊猫的脚踝可以旋转180度，帮助它们头朝下爬下树木。</p>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-md">
              <h3 className="font-semibold mb-2">伪拇指</h3>
              <p className="text-gray-600">像大熊猫一样，小熊猫也有一个"伪拇指"，帮助它们抓握竹子。</p>
            </div>
            <div className="bg-white p-6 rounded-xl shadow-md">
              <h3 className="font-semibold mb-2">温度调节</h3>
              <p className="text-gray-600">它们用毛茸茸的尾巴包裹身体来保暖，在寒冷天气中睡觉。</p>
            </div>
          </div>
        </section>
      </main>

      <footer className="bg-gray-800 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="mb-6 md:mb-0">
              <h3 className="text-2xl font-bold mb-2">小熊猫保护计划</h3>
              <p className="text-gray-300">致力于保护这种神奇的生物</p>
            </div>
            <div className="text-center md:text-right">
              <p className="text-gray-300 mb-2">© 2024 小熊猫保护组织</p>
              <p className="text-gray-400 text-sm">
                本网站旨在提高公众对小熊猫的认识和保护意识
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}