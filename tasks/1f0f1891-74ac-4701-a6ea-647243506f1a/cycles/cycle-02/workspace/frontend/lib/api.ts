// API client for Wuhan snacks static webpage
// Note: This is a placeholder since the project uses static HTML/CSS only
// This file exists for potential future API integrations

export interface SnackItem {
  id: string;
  name: string;
  chineseName: string;
  description: string;
  imageUrl: string;
  category: string;
  priceRange?: string;
  popularity: number;
}

export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
}

// Mock data for Wuhan specialty snacks
export const mockSnacks: SnackItem[] = [
  {
    id: '1',
    name: 'Hot Dry Noodles',
    chineseName: '热干面',
    description: 'Wuhan\'s most famous breakfast noodle dish with sesame paste and pickled vegetables',
    imageUrl: '/images/hot-dry-noodles.jpg',
    category: 'Noodles',
    priceRange: '¥8-15',
    popularity: 5
  },
  {
    id: '2',
    name: 'Doupi',
    chineseName: '豆皮',
    description: 'Savory soybean skin filled with glutinous rice, meat, and mushrooms',
    imageUrl: '/images/doupi.jpg',
    category: 'Breakfast',
    priceRange: '¥6-12',
    popularity: 4
  },
  {
    id: '3',
    name: 'Mianwo',
    chineseName: '面窝',
    description: 'Crispy fried dough rings made from rice and soybean milk',
    imageUrl: '/images/mianwo.jpg',
    category: 'Breakfast',
    priceRange: '¥2-5',
    popularity: 4
  },
  {
    id: '4',
    name: 'Tangbao',
    chineseName: '汤包',
    description: 'Steamed soup dumplings filled with pork and rich broth',
    imageUrl: '/images/tangbao.jpg',
    category: 'Dumplings',
    priceRange: '¥15-25',
    popularity: 4
  },
  {
    id: '5',
    name: 'Lotus Root Soup',
    chineseName: '藕汤',
    description: 'Hearty pork rib soup with lotus root, a Wuhan winter specialty',
    imageUrl: '/images/lotus-root-soup.jpg',
    category: 'Soup',
    priceRange: '¥20-35',
    popularity: 3
  },
  {
    id: '6',
    name: 'Fried Bean Skin Rolls',
    chineseName: '炸豆皮卷',
    description: 'Crispy fried rolls filled with vegetables and sometimes meat',
    imageUrl: '/images/fried-bean-skin-rolls.jpg',
    category: 'Snacks',
    priceRange: '¥10-18',
    popularity: 3
  }
];

// Mock API functions for potential future use
export class SnacksApi {
  static async getAllSnacks(): Promise<ApiResponse<SnackItem[]>> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 100));
    
    return {
      success: true,
      data: mockSnacks
    };
  }

  static async getSnackById(id: string): Promise<ApiResponse<SnackItem>> {
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const snack = mockSnacks.find(s => s.id === id);
    
    if (!snack) {
      return {
        success: false,
        error: 'Snack not found'
      };
    }
    
    return {
      success: true,
      data: snack
    };
  }

  static async getSnacksByCategory(category: string): Promise<ApiResponse<SnackItem[]>> {
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const filteredSnacks = mockSnacks.filter(s => s.category === category);
    
    return {
      success: true,
      data: filteredSnacks
    };
  }

  static async getPopularSnacks(limit: number = 5): Promise<ApiResponse<SnackItem[]>> {
    await new Promise(resolve => setTimeout(resolve, 100));
    
    const popularSnacks = [...mockSnacks]
      .sort((a, b) => b.popularity - a.popularity)
      .slice(0, limit);
    
    return {
      success: true,
      data: popularSnacks
    };
  }
}

// Utility functions for snack data
export function getSnackCategories(): string[] {
  const categories = new Set(mockSnacks.map(snack => snack.category));
  return Array.from(categories);
}

export function formatPrice(priceRange?: string): string {
  if (!priceRange) return 'Price varies';
  return `Price: ${priceRange}`;
}

export function getPopularityStars(popularity: number): string {
  return '★'.repeat(popularity) + '☆'.repeat(5 - popularity);
}

// Export types for use in other files
export type { SnackItem as Snack };
export type { ApiResponse };