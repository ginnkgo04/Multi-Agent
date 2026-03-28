'use client';

import { useState } from 'react';
import { ChevronDown, ChevronUp, Sparkles, Volume2, VolumeX, Heart } from 'lucide-react';

export default function FeatureExperience() {
  const [showAllFacts, setShowAllFacts] = useState(false);
  const [soundEnabled, setSoundEnabled] = useState(false);
  const [likedFacts, setLikedFacts] = useState<number[]>([]);

  const funFacts = [
    {
      id: 1,
      title: "睡眠专家",
      description: "小猪每天要睡12-14个小时，是真正的睡眠冠军！",
      emoji: "💤",
      detail: "充足的睡眠让小猪保持粉嫩的皮肤和快乐的心情。研究表明，睡眠充足的小猪更聪明、更健康。"
    },
    {
      id: 2,
      title: "美食家",
      description: "小猪的嗅觉比人类灵敏1000倍，能找到最美味的美食！",
      emoji: "🍎",
      detail: "小猪的鼻子非常灵敏，能闻到地下深处的食物。它们最喜欢吃苹果、胡萝卜和玉米。"
    },
    {
      id: 3,
      title: "游泳健将",
      description: "别看小猪胖乎乎的，它们其实是天生的游泳高手！",
      emoji: "🏊",
      detail: "小猪天生就会游泳，它们的身体脂肪帮助浮在水面上。在炎热的夏天，小猪特别喜欢在水里玩耍。"
    },
    {
      id: 4,
      title: "社交达人",
      description: "小猪是非常社会化的动物，喜欢和朋友们一起玩耍！",
      emoji: "👫",
      detail: "小猪会通过不同的叫声和身体语言与同伴交流。它们建立深厚的友谊，甚至会互相按摩。"
    },
    {
      id: 5,
      title: "聪明绝顶",
      description: "小猪的智商相当于3岁的人类小孩，非常聪明！",
      emoji: "🧠",
      detail: "小猪能学会复杂的任务，记住路线，甚至能玩电子游戏。它们有很好的长期记忆能力。"
    },
    {
      id: 6,
      title: "爱干净",
      description: "小猪其实很爱干净，它们会在固定的地方上厕所！",
      emoji: "🛁",
      detail: "与普遍认知不同，小猪非常注重卫生。它们不会在自己睡觉和吃饭的地方排泄。"
    }
  ];

  const toggleLike = (factId: number) => {
    setLikedFacts(prev => 
      prev.includes(factId) 
        ? prev.filter(id => id !== factId)
        : [...prev, factId]
    );
  };

  const playSound = () => {
    if (soundEnabled) {
      // In a real app, this would play a cute pig sound
      console.log("Oink oink! 🐷");
    }
  };

  return (
    <section id="facts" className="mb-20">
      <div className="bg-gradient-to-br from-pink-50 to-rose-50 rounded-3xl p-8 md:p-12 border-2 border-pink-200">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-10">
          <div>
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-gradient-to-br from-pink-400 to-rose-400 rounded-full flex items-center justify-center">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <h2 className="text-3xl font-bold text-pink-700">趣味小知识</h2>
            </div>
            <p className="text-lg text-pink-600 max-w-2xl">
              发现粉色小猪不为人知的可爱秘密！点击爱心标记你喜欢的小知识。
            </p>
          </div>
          
          <div className="flex gap-4 mt-6 md:mt-0">
            <button
              onClick={() => setSoundEnabled(!soundEnabled)}
              className={`flex items-center gap-2 px-4 py-2 rounded-full transition-all duration-300 ${
                soundEnabled 
                  ? 'bg-pink-500 text-white' 
                  : 'bg-white text-pink-600 border border-pink-300'
              }`}
            >
              {soundEnabled ? (
                <>
                  <Volume2 className="w-4 h-4" />
                  <span>音效开启</span>
                </>
              ) : (
                <>
                  <VolumeX className="w-4 h-4" />
                  <span>音效关闭</span>
                </>
              )}
            </button>
            
            <button
              onClick={() => setShowAllFacts(!showAllFacts)}
              className="flex items-center gap-2 px-4 py-2 bg-white text-pink-600 border border-pink-300 rounded-full hover:bg-pink-50 transition-colors"
            >
              {showAllFacts ? (
                <>
                  <ChevronUp className="w-4 h-4" />
                  <span>收起全部</span>
                </>
              ) : (
                <>
                  <ChevronDown className="w-4 h-4" />
                  <span>展开全部</span>
                </>
              )}
            </button>
          </div>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {funFacts.slice(0, showAllFacts ? funFacts.length : 3).map((fact) => (
            <div 
              key={fact.id} 
              className="group relative bg-white rounded-2xl p-6 shadow-lg border border-pink-100 hover:shadow-xl transition-all duration-300 hover:-translate-y-1"
              onClick={() => playSound()}
            >
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  toggleLike(fact.id);
                }}
                className="absolute top-4 right-4 z-10"
              >
                <Heart 
                  className={`w-5 h-5 transition-all duration-300 ${
                    likedFacts.includes(fact.id) 
                      ? 'fill-red-500 text-red-500 heart-beat' 
                      : 'text-gray-300 hover:text-pink-400'
                  }`}
                />
              </button>
              
              <div className="flex items-start gap-4 mb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-pink-200 to-rose-200 rounded-2xl flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform duration-300">
                  <span className="text-3xl">{fact.emoji}</span>
                </div>
                <div>
                  <h3 className="text-xl font-bold text-pink-700 mb-2">{fact.title}</h3>
                  <p className="text-gray-600">{fact.description}</p>
                </div>
              </div>
              
              {showAllFacts && (
                <div className="mt-4 pt-4 border-t border-pink-100">
                  <p className="text-gray-700">{fact.detail}</p>
                </div>
              )}
              
              <div className="mt-4 flex items-center justify-between">
                <span className="text-sm text-pink-500 font-medium">
                  {likedFacts.includes(fact.id) ? '已喜欢 💖' : '点击爱心'}
                </span>
                <span className="text-xs text-gray-400">
                  点击卡片听小猪叫声
                </span>
              </div>
            </div>
          ))}
        </div>

        {!showAllFacts && (
          <div className="text-center mt-10">
            <div className="inline-flex items-center gap-2 text-pink-600 animate-pulse">
              <span className="text-2xl">🐷</span>
              <span>还有 {funFacts.length - 3} 个趣味小知识等待发现！</span>
              <span className="text-2xl">✨</span>
            </div>
          </div>
        )}

        {/* Interactive Pig Animation */}
        <div className="mt-12 pt-8 border-t border-pink-200">
          <div className="max-w-md mx-auto">
            <div className="bg-gradient-to-r from-pink-100 to-rose-100 rounded-2xl p-6 text-center">
              <div className="inline-block animate-float mb-4">
                <span className="text-6xl">🐽</span>
              </div>
              <h4 className="text-lg font-bold text-pink-700 mb-2">和小猪互动</h4>
              <p className="text-pink-600 mb-4">
                点击上面的趣味卡片，听听小猪可爱的叫声！
              </p>
              <div className="flex justify-center gap-4">
                <button 
                  onClick={() => setSoundEnabled(true)}
                  className="px-4 py-2 bg-pink-500 text-white rounded-full text-sm hover:bg-pink-600 transition-colors"
                >
                  开启音效
                </button>
                <button 
                  onClick={() => setLikedFacts([])}
                  className="px-4 py-2 bg-white text-pink-600 border border-pink-300 rounded-full text-sm hover:bg-pink-50 transition-colors"
                >
                  重置喜欢
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}