// API client for fetching Wuhan snack data
// This file provides functions to fetch snack data from a backend API
// Currently uses mock data but can be extended to make real API calls

export interface Snack {
  id: string;
  name: string;
  description: string;
  imageUrl: string;
  origin: string;
  ingredients: string[];
  popularity: number;
  category: string;
}

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
}

// Mock data for Wuhan snacks
const MOCK_SNACKS: Snack[] = [
  {
    id: '1',
    name: 'Hot Dry Noodles (热干面)',
    description: 'A signature Wuhan breakfast noodle dish with sesame paste and spices.',
    imageUrl: '/images/hot-dry-noodles.jpg',
    origin: 'Wuhan, Hubei',
    ingredients: ['Wheat noodles', 'Sesame paste', 'Soy sauce', 'Pickled vegetables', 'Chili oil'],
    popularity: 5,
    category: 'Noodles'
  },
  {
    id: '2',
    name: 'Doupi (豆皮)',
    description: 'A savory snack made of glutinous rice, tofu skin, and various fillings.',
    imageUrl: '/images/doupi.jpg',
    origin: 'Wuhan, Hubei',
    ingredients: ['Glutinous rice', 'Tofu skin', 'Mushrooms', 'Bamboo shoots', 'Pork'],
    popularity: 4,
    category: 'Rice Dishes'
  },
  {
    id: '3',
    name: 'Mianwo (面窝)',
    description: 'A deep-fried dough ring made from rice and soybean milk.',
    imageUrl: '/images/mianwo.jpg',
    origin: 'Wuhan, Hubei',
    ingredients: ['Rice flour', 'Soybean milk', 'Green onions', 'Sesame seeds'],
    popularity: 4,
    category: 'Fried Snacks'
  },
  {
    id: '4',
    name: 'Tangbao (汤包)',
    description: 'Soup-filled dumplings that are a Wuhan specialty.',
    imageUrl: '/images/tangbao.jpg',
    origin: 'Wuhan, Hubei',
    ingredients: ['Flour', 'Pork', 'Gelatin broth', 'Ginger', 'Green onions'],
    popularity: 5,
    category: 'Dumplings'
  },
  {
    id: '5',
    name: 'Lotus Root Soup (莲藕汤)',
    description: 'A nourishing soup made with lotus root and pork ribs.',
    imageUrl: '/images/lotus-root-soup.jpg',
    origin: 'Wuhan, Hubei',
    ingredients: ['Lotus root', 'Pork ribs', 'Ginger', 'Green onions', 'Goji berries'],
    popularity: 4,
    category: 'Soups'
  },
  {
    id: '6',
    name: 'Fried Tofu Skin (炸豆皮)',
    description: 'Crispy fried tofu skin often served as a street food snack.',
    imageUrl: '/images/fried-tofu-skin.jpg',
    origin: 'Wuhan, Hubei',
    ingredients: ['Tofu skin', 'Five-spice powder', 'Salt', 'Oil'],
    popularity: 3,
    category: 'Fried Snacks'
  }
];

// Simulate API delay
const simulateDelay = (ms: number = 300): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

/**
 * Fetch all Wuhan snacks
 * @returns Promise with snack data
 */
export async function fetchAllSnacks(): Promise<ApiResponse<Snack[]>> {
  await simulateDelay();
  
  return {
    data: MOCK_SNACKS,
    success: true,
    message: 'Successfully fetched all snacks'
  };
}

/**
 * Fetch a single snack by ID
 * @param id - The snack ID
 * @returns Promise with snack data
 */
export async function fetchSnackById(id: string): Promise<ApiResponse<Snack | null>> {
  await simulateDelay();
  
  const snack = MOCK_SNACKS.find(s => s.id === id);
  
  if (!snack) {
    return {
      data: null,
      success: false,
      message: `Snack with ID ${id} not found`
    };
  }
  
  return {
    data: snack,
    success: true,
    message: 'Successfully fetched snack'
  };
}

/**
 * Fetch snacks by category
 * @param category - The snack category
 * @returns Promise with filtered snack data
 */
export async function fetchSnacksByCategory(category: string): Promise<ApiResponse<Snack[]>> {
  await simulateDelay();
  
  const filteredSnacks = MOCK_SNACKS.filter(s => 
    s.category.toLowerCase() === category.toLowerCase()
  );
  
  return {
    data: filteredSnacks,
    success: true,
    message: `Successfully fetched ${filteredSnacks.length} snacks in category: ${category}`
  };
}

/**
 * Fetch popular snacks (popularity >= 4)
 * @returns Promise with popular snack data
 */
export async function fetchPopularSnacks(): Promise<ApiResponse<Snack[]>> {
  await simulateDelay();
  
  const popularSnacks = MOCK_SNACKS.filter(s => s.popularity >= 4);
  
  return {
    data: popularSnacks,
    success: true,
    message: `Successfully fetched ${popularSnacks.length} popular snacks`
  };
}

/**
 * Search snacks by name or description
 * @param query - Search query
 * @returns Promise with matching snack data
 */
export async function searchSnacks(query: string): Promise<ApiResponse<Snack[]>> {
  await simulateDelay();
  
  if (!query.trim()) {
    return {
      data: MOCK_SNACKS,
      success: true,
      message: 'Empty query, returning all snacks'
    };
  }
  
  const searchTerm = query.toLowerCase();
  const matchingSnacks = MOCK_SNACKS.filter(s => 
    s.name.toLowerCase().includes(searchTerm) ||
    s.description.toLowerCase().includes(searchTerm) ||
    s.ingredients.some(ingredient => ingredient.toLowerCase().includes(searchTerm))
  );
  
  return {
    data: matchingSnacks,
    success: true,
    message: `Found ${matchingSnacks.length} snacks matching "${query}"`
  };
}

/**
 * Get all available snack categories
 * @returns Promise with unique categories
 */
export async function fetchCategories(): Promise<ApiResponse<string[]>> {
  await simulateDelay();
  
  const categories = Array.from(new Set(MOCK_SNACKS.map(s => s.category)));
  
  return {
    data: categories,
    success: true,
    message: `Found ${categories.length} categories`
  };
}

// Real API configuration (for future integration)
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api';

/**
 * Real API client for production (commented out for now)
 * Uncomment and configure when backend API is available
 */
/*
export async function fetchSnacksFromAPI(): Promise<ApiResponse<Snack[]>> {
  try {
    const response = await fetch(`${API_BASE_URL}/snacks`);
    
    if (!response.ok) {
      throw new Error(`API error: ${response.status}`);
    }
    
    const data = await response.json();
    
    return {
      data,
      success: true,
      message: 'Successfully fetched snacks from API'
    };
  } catch (error) {
    console.error('Failed to fetch snacks:', error);
    
    return {
      data: [],
      success: false,
      message: error instanceof Error ? error.message : 'Unknown error occurred'
    };
  }
}
*/