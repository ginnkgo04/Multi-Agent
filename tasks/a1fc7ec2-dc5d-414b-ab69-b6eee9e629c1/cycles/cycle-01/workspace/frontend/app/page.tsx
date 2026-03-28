import FeatureExperience from '@/components/FeatureExperience';
import { MapPin, Phone, Clock, Utensils, Star, Users } from 'lucide-react';

export default function Home() {
  const menuItems = [
    {
      id: 1,
      name: '扁肉',
      description: '传统手工制作的扁肉，皮薄馅嫩，汤鲜味美',
      price: '¥12',
      popular: true
    },
    {
      id: 2,
      name: '拌面',
      description: '特制花生酱拌面，香气浓郁，口感爽滑',
      price: '¥10',
      popular: true
    },
    {
      id: 3,
      name: '蒸饺',
      description: '手工蒸饺，皮薄馅多，鲜香可口',
      price: '¥15',
      popular: false
    },
    {
      id: 4,
      name: '炖罐',
      description: '多种药材炖制，营养丰富，滋补养生',
      price: '¥18',
      popular: true
    },
    {
      id: 5,
      name: '炒饭',
      description: '粒粒分明的炒饭，配料丰富，香气扑鼻',
      price: '¥14',
      popular: false
    }
  ];

  const testimonials = [
    {
      id: 1,
      name: '张先生',
      comment: '吃了十几年的沙县小吃，味道始终如一，扁肉和拌面是我的最爱！',
      rating: 5
    },
    {
      id: 2,
      name: '李女士',
      comment: '价格实惠，味道正宗，是工作午餐的最佳选择。',
      rating: 5
    },
    {
      id: 3,
      name: '王同学',
      comment: '学生党的福音，分量足价格便宜，特别推荐蒸饺！',
      rating: 4
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <section className="relative bg-gradient-to-r from-amber-50 to-orange-50 py-20 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-bold text-gray-900 mb-6">
              沙县小吃
            </h1>
            <p className="text-xl md:text-2xl text-gray-700 mb-8 max-w-3xl mx-auto">
              源自福建沙县的经典美食，传承百年制作工艺，为您带来地道的中国街头小吃体验
            </p>
            <div className="flex flex-wrap justify-center gap-4">
              <button className="bg-amber-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-amber-700 transition-colors">
                查看菜单
              </button>
              <button className="border-2 border-amber-600 text-amber-600 px-8 py-3 rounded-lg font-semibold hover:bg-amber-50 transition-colors">
                查找门店
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Introduction Section */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-6">关于沙县小吃</h2>
              <div className="space-y-4 text-gray-700">
                <p>
                  沙县小吃起源于福建省三明市沙县，是中国著名的传统小吃品牌。自1990年代以来，
                  沙县小吃以其独特的口味、实惠的价格和便捷的服务，迅速在全国范围内发展壮大。
                </p>
                <p>
                  我们坚持使用新鲜食材，传承百年制作工艺，每一道菜品都经过精心烹制，
                  力求为顾客提供最地道的沙县美食体验。
                </p>
                <p>
                  目前，沙县小吃已在全国开设超过8万家门店，成为最受欢迎的中式快餐品牌之一，
                  并成功走向国际市场。
                </p>
              </div>
            </div>
            <div className="bg-gray-100 rounded-2xl p-8">
              <div className="grid grid-cols-2 gap-6">
                <div className="text-center">
                  <div className="text-4xl font-bold text-amber-600 mb-2">30+</div>
                  <div className="text-gray-600">年历史传承</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-amber-600 mb-2">80k+</div>
                  <div className="text-gray-600">全国门店</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-amber-600 mb-2">50+</div>
                  <div className="text-gray-600">特色菜品</div>
                </div>
                <div className="text-center">
                  <div className="text-4xl font-bold text-amber-600 mb-2">24/7</div>
                  <div className="text-gray-600">部分门店营业</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Menu Highlights */}
      <section className="py-16 px-4 bg-gray-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">招牌菜品</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              精选最受欢迎的沙县小吃菜品，每一道都承载着传统的味道
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {menuItems.map((item) => (
              <div 
                key={item.id} 
                className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-6"
              >
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900">{item.name}</h3>
                    <div className="text-amber-600 font-bold text-lg mt-1">{item.price}</div>
                  </div>
                  {item.popular && (
                    <span className="bg-amber-100 text-amber-800 text-xs font-semibold px-3 py-1 rounded-full">
                      热门
                    </span>
                  )}
                </div>
                <p className="text-gray-600 mb-4">{item.description}</p>
                <div className="flex items-center text-gray-500">
                  <Utensils className="w-4 h-4 mr-2" />
                  <span className="text-sm">传统工艺制作</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Experience Component */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <FeatureExperience />
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-16 px-4 bg-amber-50">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">顾客评价</h2>
            <p className="text-gray-600">听听我们的顾客怎么说</p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial) => (
              <div key={testimonial.id} className="bg-white rounded-xl p-6 shadow-sm">
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 bg-amber-100 rounded-full flex items-center justify-center mr-4">
                    <Users className="w-6 h-6 text-amber-600" />
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900">{testimonial.name}</h4>
                    <div className="flex">
                      {[...Array(5)].map((_, i) => (
                        <Star 
                          key={i} 
                          className={`w-4 h-4 ${i < testimonial.rating ? 'text-amber-500 fill-amber-500' : 'text-gray-300'}`}
                        />
                      ))}
                    </div>
                  </div>
                </div>
                <p className="text-gray-600 italic">"{testimonial.comment}"</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Contact & Location */}
      <section className="py-16 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 mb-8">联系我们</h2>
              
              <div className="space-y-6">
                <div className="flex items-start">
                  <MapPin className="w-6 h-6 text-amber-600 mr-4 mt-1" />
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">门店地址</h3>
                    <p className="text-gray-600">
                      全国各大城市均有分店<br />
                      查找离您最近的门店
                    </p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <Phone className="w-6 h-6 text-amber-600 mr-4 mt-1" />
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">客服热线</h3>
                    <p className="text-gray-600">400-123-4567</p>
                    <p className="text-gray-600 text-sm">周一至周日 9:00-21:00</p>
                  </div>
                </div>
                
                <div className="flex items-start">
                  <Clock className="w-6 h-6 text-amber-600 mr-4 mt-1" />
                  <div>
                    <h3 className="font-semibold text-gray-900 mb-1">营业时间</h3>
                    <p className="text-gray-600">
                      大部分门店：6:30 - 22:00<br />
                      部分24小时营业门店请查询具体位置
                    </p>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-gray-100 rounded-2xl p-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-6">查找附近门店</h3>
              <div className="space-y-4">
                <input 
                  type="text" 
                  placeholder="输入城市或区域" 
                  className="w-full px-4 py-3 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-amber-500"
                />
                <button className="w-full bg-amber-600 text-white py-3 rounded-lg font-semibold hover:bg-amber-700 transition-colors">
                  搜索门店
                </button>
              </div>
              <div className="mt-8 p-4 bg-white rounded-lg">
                <p className="text-gray-600 text-sm">
                  💡 提示：您也可以使用地图应用搜索"沙县小吃"查找最近的门店
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}