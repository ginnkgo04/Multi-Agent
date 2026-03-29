'use client';

import { useState } from 'react';
import { ChevronLeft, ChevronRight, Info, X } from 'lucide-react';

const galleryImages = [
  {
    id: 1,
    url: 'https://images.unsplash.com/photo-1599236449652-f2a5d0a5c5c9?auto=format&fit=crop&w=800',
    alt: 'Red panda sitting on a tree branch',
    title: '树上的小熊猫',
    description: '小熊猫在树枝上休息，展示其标志性的红褐色皮毛和长尾巴'
  },
  {
    id: 2,
    url: 'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7?auto=format&fit=crop&w-800',
    alt: 'Red panda looking at camera',
    title: '好奇的小熊猫',
    description: '小熊猫好奇地看着镜头，展示其可爱的面部特征'
  },
  {
    id: 3,
    url: 'https://images.unsplash.com/photo-1548681525-41a8e2c5f2f5?auto=format&fit=crop&w=800',
    alt: 'Red panda eating bamboo',
    title: '进食的小熊猫',
    description: '小熊猫正在吃竹子，展示其独特的进食方式'
  },
  {
    id: 4,
    url: 'https://images.unsplash.com/photo-1574870111867-089858b7ce9d?auto=format&fit=crop&w=800',
    alt: 'Red panda sleeping',
    title: '睡觉的小熊猫',
    description: '小熊猫蜷缩着睡觉，用尾巴包裹身体保暖'
  }
];

const funFacts = [
  {
    id: 1,
    fact: '小熊猫的学名"Ailurus fulgens"在拉丁语中意为"闪亮的猫"',
    detail: '这个名称来源于它们闪亮的红褐色皮毛'
  },
  {
    id: 2,
    fact: '小熊猫每天需要花费13小时进食',
    detail: '因为竹子营养含量低，它们需要大量进食来获取足够能量'
  },
  {
    id: 3,
    fact: '它们用尾巴来保持平衡和在树上导航',
    detail: '尾巴几乎和身体一样长，帮助它们在树上保持稳定'
  },
  {
    id: 4,
    fact: '小熊猫是独居动物',
    detail: '除了交配季节和母熊猫照顾幼崽时，它们通常独自生活'
  },
  {
    id: 5,
    fact: '它们通过气味标记领地',
    detail: '使用肛门腺分泌物和尿液标记树木和岩石'
  }
];

export default function FeatureExperience() {
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [showFactModal, setShowFactModal] = useState(false);
  const [selectedFact, setSelectedFact] = useState(funFacts[0]);

  const nextImage = () => {
    setCurrentImageIndex((prev) => (prev + 1) % galleryImages.length);
  };

  const prevImage = () => {
    setCurrentImageIndex((prev) => (prev - 1 + galleryImages.length) % galleryImages.length);
  };

  const selectFact = (fact: typeof funFacts[0]) => {
    setSelectedFact(fact);
    setShowFactModal(true);
  };

  return (
    <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
      <div className="p-8">
        <h2 className="text-3xl font-bold text-gray-800 mb-8 text-center">
          探索小熊猫的世界
        </h2>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Image Gallery */}
          <div className="space-y-6">
            <h3 className="text-2xl font-semibold text-gray-700 mb-4">图片画廊</h3>
            <div className="relative">
              <div className="relative h-64 md:h-80 rounded-xl overflow-hidden">
                <img
                  src={galleryImages[currentImageIndex].url}
                  alt={galleryImages[currentImageIndex].alt}
                  className="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
                />
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-4">
                  <h4 className="text-white font-semibold text-lg">
                    {galleryImages[currentImageIndex].title}
                  </h4>
                  <p className="text-white/80 text-sm">
                    {galleryImages[currentImageIndex].description}
                  </p>
                </div>
              </div>
              
              <div className="flex justify-between items-center mt-4">
                <button
                  onClick={prevImage}
                  className="p-2 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
                  aria-label="Previous image"
                >
                  <ChevronLeft className="w-5 h-5" />
                </button>
                
                <div className="flex space-x-2">
                  {galleryImages.map((_, index) => (
                    <button
                      key={index}
                      onClick={() => setCurrentImageIndex(index)}
                      className={`w-3 h-3 rounded-full transition-colors ${
                        index === currentImageIndex ? 'bg-red-500' : 'bg-gray-300'
                      }`}
                      aria-label={`Go to image ${index + 1}`}
                    />
                  ))}
                </div>
                
                <button
                  onClick={nextImage}
                  className="p-2 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors"
                  aria-label="Next image"
                >
                  <ChevronRight className="w-5 h-5" />
                </button>
              </div>
            </div>
          </div>

          {/* Fun Facts */}
          <div className="space-y-6">
            <h3 className="text-2xl font-semibold text-gray-700 mb-4">趣味知识</h3>
            <div className="space-y-4">
              {funFacts.map((fact) => (
                <div
                  key={fact.id}
                  className="p-4 bg-gradient-to-r from-red-50 to-orange-50 rounded-lg hover:from-red-100 hover:to-orange-100 transition-all cursor-pointer hover-card"
                  onClick={() => selectFact(fact)}
                >
                  <div className="flex items-start">
                    <div className="w-8 h-8 bg-red-100 rounded-full flex items-center justify-center mr-3 flex-shrink-0">
                      <Info className="w-4 h-4 text-red-600" />
                    </div>
                    <div>
                      <h4 className="font-semibold text-gray-800 mb-1">{fact.fact}</h4>
                      <p className="text-sm text-gray-600 line-clamp-2">{fact.detail}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-100">
              <p className="text-sm text-blue-700">
                <span className="font-semibold">提示：</span>
                点击任意趣味知识卡片查看详细信息
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Fact Modal */}
      {showFactModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-md w-full p-6 animate-fadeIn">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-2xl font-bold text-gray-800">趣味知识</h3>
              <button
                onClick={() => setShowFactModal(false)}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
                aria-label="Close modal"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="space-y-4">
              <div className="p-4 bg-gradient-to-r from-red-50 to-orange-50 rounded-lg">
                <h4 className="text-lg font-semibold text-gray-800 mb-2">
                  {selectedFact.fact}
                </h4>
                <p className="text-gray-600">{selectedFact.detail}</p>
              </div>
              
              <div className="flex items-center text-sm text-gray-500">
                <Info className="w-4 h-4 mr-2" />
                小熊猫是自然界中独特而迷人的生物
              </div>
            </div>
            
            <div className="mt-6 flex justify-end">
              <button
                onClick={() => setShowFactModal(false)}
                className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
              >
                关闭
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}