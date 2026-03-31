/**
 * Polar Bear Conservation API Client
 * 
 * This module provides functions for interacting with conservation APIs.
 * Currently implemented as mock functions for demonstration purposes.
 */

export interface ConservationOrganization {
  id: string;
  name: string;
  description: string;
  website: string;
  donationUrl: string;
}

export interface ConservationFact {
  id: string;
  title: string;
  content: string;
  source: string;
  category: 'habitat' | 'threats' | 'conservation' | 'biology';
}

export interface DonationOption {
  id: string;
  amount: number;
  description: string;
  impact: string;
}

export interface NewsletterSubscription {
  email: string;
  name?: string;
  interests: string[];
}

/**
 * Mock function to fetch conservation organizations
 * In a real implementation, this would call a backend API
 */
export async function fetchConservationOrganizations(): Promise<ConservationOrganization[]> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 300));
  
  return [
    {
      id: '1',
      name: '世界自然基金会 (WWF)',
      description: '全球最大的独立性非政府环境保护组织之一，致力于北极熊保护项目。',
      website: 'https://www.worldwildlife.org/species/polar-bear',
      donationUrl: 'https://www.worldwildlife.org/species/polar-bear#donate'
    },
    {
      id: '2',
      name: '北极熊国际 (Polar Bears International)',
      description: '专注于北极熊研究和保护的非营利组织，通过科学研究和教育推动保护工作。',
      website: 'https://polarbearsinternational.org',
      donationUrl: 'https://polarbearsinternational.org/donate'
    },
    {
      id: '3',
      name: '国际自然保护联盟 (IUCN)',
      description: '全球最大的自然保护网络，负责评估北极熊的保护状况并制定保护策略。',
      website: 'https://www.iucn.org',
      donationUrl: 'https://www.iucn.org/support/donate'
    }
  ];
}

/**
 * Mock function to fetch conservation facts
 * In a real implementation, this would call a backend API
 */
export async function fetchConservationFacts(): Promise<ConservationFact[]> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 200));
  
  return [
    {
      id: '1',
      title: '海冰减少速度',
      content: '北极海冰面积每十年减少约13%，严重影响了北极熊的狩猎和繁殖。',
      source: 'NASA气候研究中心',
      category: 'habitat'
    },
    {
      id: '2',
      title: '种群数量趋势',
      content: '全球北极熊数量估计在22,000-31,000只之间，其中19个亚群中有3个正在减少。',
      source: 'IUCN北极熊专家组',
      category: 'biology'
    },
    {
      id: '3',
      title: '主要威胁',
      content: '气候变化导致的栖息地丧失是北极熊面临的最大威胁，其次是污染和人类活动干扰。',
      source: '世界自然基金会',
      category: 'threats'
    },
    {
      id: '4',
      title: '保护成功案例',
      content: '通过国际保护协议，北极熊的国际贸易受到严格限制，有效减少了非法狩猎。',
      source: 'CITES公约',
      category: 'conservation'
    }
  ];
}

/**
 * Mock function to get donation options
 * In a real implementation, this would call a backend API
 */
export async function getDonationOptions(): Promise<DonationOption[]> {
  return [
    {
      id: 'basic',
      amount: 50,
      description: '基础支持',
      impact: '支持一天的野外监测工作'
    },
    {
      id: 'standard',
      amount: 100,
      description: '标准支持',
      impact: '保护100平方米的北极熊栖息地'
    },
    {
      id: 'premium',
      amount: 500,
      description: '深度支持',
      impact: '资助一个月的科学研究项目'
    },
    {
      id: 'custom',
      amount: 0,
      description: '自定义金额',
      impact: '根据金额产生相应影响'
    }
  ];
}

/**
 * Mock function to submit a donation
 * In a real implementation, this would call a payment processing API
 */
export async function submitDonation(
  amount: number,
  donorInfo: {
    name: string;
    email: string;
    message?: string;
  }
): Promise<{ success: boolean; transactionId?: string; message: string }> {
  // Simulate API processing
  await new Promise(resolve => setTimeout(resolve, 500));
  
  // Generate mock transaction ID
  const transactionId = 'TX-' + Math.random().toString(36).substr(2, 9).toUpperCase();
  
  return {
    success: true,
    transactionId,
    message: `感谢您捐赠 ¥${amount} 支持北极熊保护！您的交易ID是：${transactionId}`
  };
}

/**
 * Mock function to subscribe to newsletter
 * In a real implementation, this would call a backend API
 */
export async function subscribeToNewsletter(
  subscription: NewsletterSubscription
): Promise<{ success: boolean; message: string }> {
  // Simulate API processing
  await new Promise(resolve => setTimeout(resolve, 300));
  
  return {
    success: true,
    message: `感谢订阅！我们已经向 ${subscription.email} 发送了确认邮件。`
  };
}

/**
 * Mock function to calculate carbon footprint reduction
 * In a real implementation, this would call a calculation service
 */
export async function calculateCarbonReduction(
  actions: {
    usePublicTransport: boolean;
    reduceEnergy: boolean;
    recycle: boolean;
    eatLessMeat: boolean;
  }
): Promise<{ totalReduction: number; breakdown: Record<string, number> }> {
  // Simple calculation logic
  const breakdown: Record<string, number> = {};
  let total = 0;
  
  if (actions.usePublicTransport) {
    breakdown.publicTransport = 0.5;
    total += 0.5;
  }
  
  if (actions.reduceEnergy) {
    breakdown.energyReduction = 0.8;
    total += 0.8;
  }
  
  if (actions.recycle) {
    breakdown.recycling = 0.3;
    total += 0.3;
  }
  
  if (actions.eatLessMeat) {
    breakdown.diet = 0.4;
    total += 0.4;
  }
  
  return {
    totalReduction: total,
    breakdown
  };
}

/**
 * Utility function to format currency
 */
export function formatCurrency(amount: number, currency: string = 'CNY'): string {
  return new Intl.NumberFormat('zh-CN', {
    style: 'currency',
    currency,
    minimumFractionDigits: 0
  }).format(amount);
}

/**
 * Utility function to format large numbers
 */
export function formatNumber(num: number): string {
  if (num >= 1000000) {
    return (num / 1000000).toFixed(1) + '百万';
  }
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + '万';
  }
  return num.toString();
}