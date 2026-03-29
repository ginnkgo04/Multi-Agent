// API utilities for Red Panda website

export interface RedPandaFact {
  id: number;
  category: 'biology' | 'habitat' | 'diet' | 'conservation' | 'behavior';
  title: string;
  description: string;
  source?: string;
}

export interface ConservationOrganization {
  id: number;
  name: string;
  description: string;
  website: string;
  focus: string[];
}

export interface ImageData {
  id: number;
  url: string;
  alt: string;
  caption: string;
  photographer?: string;
  license?: string;
}

// Mock data for development
export const redPandaFacts: RedPandaFact[] = [
  {
    id: 1,
    category: 'biology',
    title: '独特的分类地位',
    description: '小熊猫是小熊猫科的唯一现存物种，与大熊猫的亲缘关系并不近。它们有自己独特的科属分类。',
    source: 'IUCN Red List'
  },
  {
    id: 2,
    category: 'habitat',
    title: '高山栖息地',
    description: '小熊猫生活在海拔2000-4800米的温带森林中，主要分布在喜马拉雅山脉东部地区。',
    source: 'WWF'
  },
  {
    id: 3,
    category: 'diet',
    title: '竹食专家',
    description: '虽然主要以竹子为食，但小熊猫也吃水果、橡子、根茎，偶尔捕食小型动物和鸟蛋。',
    source: 'Smithsonian National Zoo'
  },
  {
    id: 4,
    category: 'behavior',
    title: '夜行性动物',
    description: '小熊猫主要在黄昏和黎明活动，白天大部分时间在树上休息睡觉。',
    source: 'Red Panda Network'
  },
  {
    id: 5,
    category: 'conservation',
    title: '濒危状态',
    description: '被世界自然保护联盟列为濒危物种，野外数量估计不足10,000只，且持续下降。',
    source: 'IUCN'
  }
];

export const conservationOrganizations: ConservationOrganization[] = [
  {
    id: 1,
    name: 'Red Panda Network',
    description: '致力于通过社区参与、研究和教育来保护野生小熊猫及其栖息地。',
    website: 'https://redpandanetwork.org',
    focus: ['栖息地保护', '社区教育', '科学研究']
  },
  {
    id: 2,
    name: 'World Wildlife Fund',
    description: '全球最大的自然保护组织之一，在多个国家开展小熊猫保护项目。',
    website: 'https://www.worldwildlife.org',
    focus: ['栖息地恢复', '反盗猎', '政策倡导']
  },
  {
    id: 3,
    name: 'IUCN SSC Red Panda Specialist Group',
    description: '国际自然保护联盟的小熊猫专家组，负责制定保护策略和行动计划。',
    website: 'https://www.iucnredlist.org',
    focus: ['科学研究', '保护规划', '国际协作']
  }
];

export const redPandaImages: ImageData[] = [
  {
    id: 1,
    url: 'https://images.unsplash.com/photo-1599236449652-f2a5d0a5c5c9',
    alt: 'Red panda sitting on a tree branch',
    caption: '小熊猫在树枝上休息',
    photographer: 'Wildlife Photographer',
    license: 'Unsplash License'
  },
  {
    id: 2,
    url: 'https://images.unsplash.com/photo-1564349683136-77e08dba1ef7',
    alt: 'Red panda looking at camera',
    caption: '好奇的小熊猫',
    photographer: 'Nature Enthusiast',
    license: 'Unsplash License'
  },
  {
    id: 3,
    url: 'https://images.unsplash.com/photo-1548681525-41a8e2c5f2f5',
    alt: 'Red panda eating bamboo',
    caption: '进食的小熊猫',
    photographer: 'Conservationist',
    license: 'Unsplash License'
  }
];

// API functions
export async function fetchRedPandaFacts(category?: string): Promise<RedPandaFact[]> {
  // Simulate API call
  return new Promise((resolve) => {
    setTimeout(() => {
      if (category) {
        resolve(redPandaFacts.filter(fact => fact.category === category));
      } else {
        resolve(redPandaFacts);
      }
    }, 300);
  });
}

export async function fetchConservationOrganizations(): Promise<ConservationOrganization[]> {
  // Simulate API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(conservationOrganizations);
    }, 300);
  });
}

export async function fetchRandomFact(): Promise<RedPandaFact> {
  // Simulate API call
  return new Promise((resolve) => {
    setTimeout(() => {
      const randomIndex = Math.floor(Math.random() * redPandaFacts.length);
      resolve(redPandaFacts[randomIndex]);
    }, 300);
  });
}

export async function fetchImageGallery(): Promise<ImageData[]> {
  // Simulate API call
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve(redPandaImages);
    }, 300);
  });
}

// Utility functions
export function formatCategory(category: string): string {
  const categoryMap: Record<string, string> = {
    'biology': '生物学',
    'habitat': '栖息地',
    'diet': '饮食',
    'conservation': '保护',
    'behavior': '行为'
  };
  return categoryMap[category] || category;
}

export function getConservationStatus(): {
  status: string;
  color: string;
  description: string;
} {
  return {
    status: '濒危 (EN)',
    color: 'text-red-600',
    description: '野外数量持续下降，面临栖息地丧失和非法捕猎的严重威胁'
  };
}

export function calculatePopulationTrend(): {
  trend: '下降' | '稳定' | '增长';
  percentage: number;
  years: number;
} {
  return {
    trend: '下降',
    percentage: -50,
    years: 20
  };
}

// Local storage utilities for user preferences
const STORAGE_KEY = 'red_panda_preferences';

export interface UserPreferences {
  language: 'zh' | 'en';
  theme: 'light' | 'dark' | 'auto';
  notifications: boolean;
  lastVisit?: string;
}

export function getUserPreferences(): UserPreferences {
  if (typeof window === 'undefined') {
    return {
      language: 'zh',
      theme: 'auto',
      notifications: true
    };
  }

  const stored = localStorage.getItem(STORAGE_KEY);
  if (stored) {
    return JSON.parse(stored);
  }

  return {
    language: 'zh',
    theme: 'auto',
    notifications: true
  };
}

export function saveUserPreferences(prefs: UserPreferences): void {
  if (typeof window === 'undefined') return;
  
  const preferences = {
    ...prefs,
    lastVisit: new Date().toISOString()
  };
  
  localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
}

// Analytics utilities
export function trackEvent(eventName: string, data?: Record<string, any>): void {
  if (typeof window === 'undefined') return;
  
  console.log('Analytics Event:', {
    event: eventName,
    timestamp: new Date().toISOString(),
    url: window.location.href,
    ...data
  });
  
  // In a real application, this would send data to your analytics service
  // Example: sendToAnalytics({ event: eventName, ...data });
}

export function trackPageView(pageName: string): void {
  trackEvent('page_view', { page: pageName });
}

export function trackFactView(factId: number): void {
  trackEvent('fact_view', { factId });
}

export function trackImageClick(imageId: number): void {
  trackEvent('image_click', { imageId });
}