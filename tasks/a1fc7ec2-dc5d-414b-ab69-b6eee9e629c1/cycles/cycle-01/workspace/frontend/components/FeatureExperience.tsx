'use client';

import { useState, useEffect } from 'react';
import { CheckCircle, Leaf, Shield, Truck } from 'lucide-react';

const features = [
  {
    id: 1,
    icon: Leaf,
    title: '新鲜食材',
    description: '每日采购新鲜食材，确保菜品品质',
    color: 'text-green-600',
    bgColor: 'bg-green-50'
  },
  {
    id: 2,
    icon: Shield,
    title: '安全卫生',
    description: '严格遵循食品安全标准，让您吃得放心',
    color: 'text-blue-600',
    bgColor: 'bg-blue-50'
  },
  {
    id: 3,
    icon: CheckCircle,
    title: '传统工艺',
    description: '传承百年制作工艺，保留地道风味',
    color: 'text-amber-600',
    bgColor: 'bg-amber-50'
  },
  {
    id: 4,
    icon: Truck,
    title: '快速服务',
    description: '高效出餐，满足快节奏生活需求',
    color: 'text-purple-600',
    bgColor: 'bg-purple-50'
  }
];

export default function FeatureExperience() {
  const [activeFeature, setActiveFeature] = useState(1);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
    
    // Auto rotate features
    const interval = setInterval(() => {
      setActiveFeature(prev => (prev % features.length) + 1);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const activeFeatureData = features.find(f => f.id === activeFeature);

  return (
    <div className="fade-in">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-4">我们的特色</h2>
        <p className="text-gray-600 max-w-2xl mx-auto">
          沙县小吃不仅是一种美食，更是一种文化体验
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-12 items-center">
        <div>
          <div className="grid grid-cols-2 gap-6">
            {features.map((feature) => {
              const Icon = feature.icon;
              const isActive = feature.id === activeFeature;
              
              return (
                <button
                  key={feature.id}
                  onClick={() => setActiveFeature(feature.id)}
                  className={`p-6 rounded-xl transition-all duration-300 ${
                    isActive 
                      ? `${feature.bgColor} border-2 border-gray-200 shadow-md` 
                      : 'bg-white border border-gray-200 hover:shadow-sm'
                  }`}
                >
                  <div className="flex flex-col items-center text-center">
                    <div className={`p-3 rounded-full ${feature.bgColor} mb-4`}>
                      <Icon className={`w-8 h-8 ${feature.color}`} />
                    </div>
                    <h3 className={`font-semibold text-lg mb-2 ${isActive ? 'text-gray-900' : 'text-gray-700'}`}>
                      {feature.title}
                    </h3>
                    <p className="text-sm text-gray-600">{feature.description}</p>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        <div className={`transition-all duration-500 ${isVisible ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
          {activeFeatureData && (
            <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-2xl p-8 h-full">
              <div className="flex items-center mb-6">
                <div className={`p-3 rounded-full ${activeFeatureData.bgColor} mr-4`}>
                  <activeFeatureData.icon className={`w-8 h-8 ${activeFeatureData.color}`} />
                </div>
                <h3 className="text-2xl font-bold text-gray-900">{activeFeatureData.title}</h3>
              </div>
              
              <div className="space-y-4">
                <p className="text-gray-700 text-lg">
                  {activeFeatureData.description}
                </p>
                
                {activeFeatureData.id === 1 && (
                  <ul className="space-y-3">
                    <li className="flex items-center text-gray-600">
                      <CheckCircle className="w-5 h-5 text-green-500 mr-3" />
                      蔬菜每日从当地市场采购
                    </li>
                    <li className="flex items-center text-gray-600">
                      <CheckCircle className="w-5 h-5 text-green-500 mr-3" />
                      肉类供应商经过严格筛选
                    </li>
                    <li className="flex items-center text-gray-600">
                      <CheckCircle className="w-5 h-5 text-green-500 mr-3" />
                      调味料使用传统配方
                    </li>
                  </ul>
                )}
                
                {activeFeatureData.id === 2 && (
                  <ul className="space-y-3">
                    <li className="flex items-center text-gray-600">
                      <CheckCircle className="w-5 h-5 text-blue-500 mr-3" />
                      厨房设备每日消毒清洁
                    </li>
                    <li className="flex items-center text-gray-600">
                      <CheckCircle className="w-5 h-5 text-blue-500 mr-3" />
                      员工定期健康检查
                    </li>
                    <li className="flex items-center text-gray-600">
                      <CheckCircle className="w-5 h-5 text-blue-500 mr-3" />
                      食材储存符合安全标准
                    </li>
                  </ul>
                )}
                
                {activeFeatureData.id === 3 && (
                  <ul className="space-y-3">
                    <li className="flex items-center text-gray-600">
                      <CheckCircle className="w-5 h-5 text-amber-500 mr-3" />
                      手工制作，保留传统口感
                    </li>
                    <li className="flex items-center text-gray-600">
                      <CheckCircle className="w-5 h-5 text-amber-500 mr-3" />
                      秘制配方，代代相传
                    </li>
                    <li className="flex items-center text-gray-600">
                      <CheckCircle className="w-5 h-5 text-amber-500 mr-3" />
                      慢火炖煮，味道醇厚
                    </li>
                  </ul>
                )}
                
                {activeFeatureData.id === 4 && (
                  <ul className="space-y-3">
                    <li className="flex items-center text-gray-600">
                      <CheckCircle className="w-5 h-5 text-purple-500 mr-3" />
                      标准化制作流程
                    </li>
                    <li className="flex items-center text-gray-600">
                      <CheckCircle className="w-5 h-5 text-purple-500 mr-3" />
                      高效团队协作
                    </li>
                    <li className="flex items-center text-gray-600">
                      <CheckCircle className="w-5 h-5 text-purple-500 mr-3" />
                      外卖配送准时送达
                    </li>
                  </ul>
                )}
              </div>
              
              <div className="mt-8 pt-6 border-t border-gray-200">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-gray-500">特色 {activeFeatureData.id} / {features.length}</span>
                  <div className="flex space-x-2">
                    {features.map((_, index) => (
                      <button
                        key={index}
                        onClick={() => setActiveFeature(index + 1)}
                        className={`w-3 h-3 rounded-full transition-colors ${
                          activeFeature === index + 1 ? 'bg-amber-600' : 'bg-gray-300'
                        }`}
                        aria-label={`查看特色 ${index + 1}`}
                      />
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}