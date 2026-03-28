// API工具函数和类型定义

export interface MenuItem {
  id: number;
  name: string;
  description: string;
  price: string;
  category: string;
  popular: boolean;
  imageUrl?: string;
}

export interface StoreLocation {
  id: number;
  name: string;
  address: string;
  city: string;
  phone: string;
  openingHours: string;
  latitude: number;
  longitude: number;
}

export interface Testimonial {
  id: number;
  name: string;
  comment: string;
  rating: number;
  date: string;
}

// 模拟数据
export const mockMenuItems: MenuItem[] = [
  {
    id: 1,
    name: '扁肉',
    description: '传统手工制作的扁肉，皮薄馅嫩，汤鲜味美',
    price: '¥12',
    category: '汤类',
    popular: true,
    imageUrl: '/images/bian-rou.jpg'
  },
  {
    id: 2,
    name: '拌面',
    description: '特制花生酱拌面，香气浓郁，口感爽滑',
    price: '¥10',
    category: '面食',
    popular: true,
    imageUrl: '/images/ban-mian.jpg'
  },
  {
    id: 3,
    name: '蒸饺',
    description: '手工蒸饺，皮薄馅多，鲜香可口',
    price: '¥15',
    category: '点心',
    popular: false,
    imageUrl: '/images/zheng-jiao.jpg'
  },
  {
    id: 4,
    name: '炖罐',
    description: '多种药材炖制，营养丰富，滋补养生',
    price: '¥18',
    category: '汤类',
    popular: true,
    imageUrl: '/images/dun-guan.jpg'
  },
  {
    id: 5,
    name: '炒饭',
    description: '粒粒分明的炒饭，配料丰富，香气扑鼻',
    price: '¥14',
    category: '主食',
    popular: false,
    imageUrl: '/images/chao-fan.jpg'
  },
  {
    id: 6,
    name: '卤味拼盘',
    description: '多种卤味组合，味道醇厚，下酒佳品',
    price: '¥25',
    category: '小吃',
    popular: true,
    imageUrl: '/images/lu-wei.jpg'
  }
];

export const mockStoreLocations: StoreLocation[] = [
  {
    id: 1,
    name: '沙县小吃（北京总店）',
    address: '北京市东城区王府井大街138号',
    city: '北京',
    phone: '010-12345678',
    openingHours: '6:30 - 22:00',
    latitude: 39.9042,
    longitude: 116.4074
  },
  {
    id: 2,
    name: '沙县小吃（上海分店）',
    address: '上海市黄浦区南京东路123号',
    city: '上海',
    phone: '021-87654321',
    openingHours: '6:30 - 23:00',
    latitude: 31.2304,
    longitude: 121.4737
  },
  {
    id: 3,
    name: '沙县小吃（广州分店）',
    address: '广州市天河区体育西路456号',
    city: '广州',
    phone: '020-23456789',
    openingHours: '6:00 - 24:00',
    latitude: 23.1291,
    longitude: 113.2644
  },
  {
    id: 4,
    name: '沙县小吃（深圳分店）',
    address: '深圳市福田区华强北路789号',
    city: '深圳',
    phone: '0755-34567890',
    openingHours: '24小时营业',
    latitude: 22.5431,
    longitude: 114.0579
  }
];

export const mockTestimonials: Testimonial[] = [
  {
    id: 1,
    name: '张先生',
    comment: '吃了十几年的沙县小吃，味道始终如一，扁肉和拌面是我的最爱！',
    rating: 5,
    date: '2024-01-15'
  },
  {
    id: 2,
    name: '李女士',
    comment: '价格实惠，味道正宗，是工作午餐的最佳选择。',
    rating: 5,
    date: '2024-01-10'
  },
  {
    id: 3,
    name: '王同学',
    comment: '学生党的福音，分量足价格便宜，特别推荐蒸饺！',
    rating: 4,
    date: '2024-01-05'
  },
  {
    id: 4,
    name: '陈女士',
    comment: '带孩子来吃，孩子特别喜欢他们的炒饭，干净卫生，放心。',
    rating: 5,
    date: '2023-12-28'
  }
];

// API函数
export async function fetchMenuItems(): Promise<MenuItem[]> {
  // 模拟API延迟
  await new Promise(resolve => setTimeout(resolve, 300));
  return mockMenuItems;
}

export async function fetchPopularItems(): Promise<MenuItem[]> {
  await new Promise(resolve => setTimeout(resolve, 200));
  return mockMenuItems.filter(item => item.popular);
}

export async function fetchStoreLocations(city?: string): Promise<StoreLocation[]> {
  await new Promise(resolve => setTimeout(resolve, 400));
  if (city) {
    return mockStoreLocations.filter(store => store.city.includes(city));
  }
  return mockStoreLocations;
}

export async function fetchTestimonials(): Promise<Testimonial[]> {
  await new Promise(resolve => setTimeout(resolve, 250));
  return mockTestimonials;
}

export async function searchStores(query: string): Promise<StoreLocation[]> {
  await new Promise(resolve => setTimeout(resolve, 500));
  const normalizedQuery = query.toLowerCase().trim();
  
  return mockStoreLocations.filter(store => 
    store.name.toLowerCase().includes(normalizedQuery) ||
    store.address.toLowerCase().includes(normalizedQuery) ||
    store.city.toLowerCase().includes(normalizedQuery)
  );
}

export async function submitContactForm(data: {
  name: string;
  email: string;
  message: string;
  phone?: string;
}): Promise<{ success: boolean; message: string }> {
  await new Promise(resolve => setTimeout(resolve, 600));
  
  // 模拟表单验证
  if (!data.name || !data.email || !data.message) {
    return {
      success: false,
      message: '请填写所有必填字段'
    };
  }
  
  if (!data.email.includes('@')) {
    return {
      success: false,
      message: '请输入有效的邮箱地址'
    };
  }
  
  // 模拟成功提交
  console.log('Contact form submitted:', data);
  
  return {
    success: true,
    message: '感谢您的留言！我们会尽快与您联系。'
  };
}

// 工具函数
export function formatPrice(price: number): string {
  return `¥${price.toFixed(2)}`;
}

export function getRatingStars(rating: number): string {
  return '★'.repeat(rating) + '☆'.repeat(5 - rating);
}

export function calculateDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  // 简化的距离计算（实际应用中应使用更精确的算法）
  const R = 6371; // 地球半径（公里）
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) * 
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

// 缓存管理
const cache = new Map<string, { data: any; timestamp: number }>();
const CACHE_DURATION = 5 * 60 * 1000; // 5分钟

export async function fetchWithCache<T>(
  key: string,
  fetcher: () => Promise<T>
): Promise<T> {
  const cached = cache.get(key);
  const now = Date.now();
  
  if (cached && now - cached.timestamp < CACHE_DURATION) {
    return cached.data;
  }
  
  const data = await fetcher();
  cache.set(key, { data, timestamp: now });
  return data;
}

// 清除缓存
export function clearCache(key?: string) {
  if (key) {
    cache.delete(key);
  } else {
    cache.clear();
  }
}