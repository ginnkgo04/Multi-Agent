// API integration layer for fetching Wuhan snack data
// This module provides functions to retrieve snack information for the static webpage

export interface Snack {
  id: string;
  name: string;
  chineseName: string;
  pinyin: string;
  description: string;
  imageUrl: string;
  category: 'breakfast' | 'street-food' | 'dessert' | 'savory';
  popularity: number;
  ingredients: string[];
  bestTimeToEat: string;
  priceRange: string;
}

// Mock data for Wuhan specialty snacks
const wuhanSnacks: Snack[] = [
  {
    id: '1',
    name: 'Hot Dry Noodles',
    chineseName: '热干面',
    pinyin: 'règānmiàn',
    description: 'A signature Wuhan breakfast noodle dish featuring wheat noodles tossed in a savory sesame paste sauce with pickled vegetables and chili oil.',
    imageUrl: '/images/hot-dry-noodles.jpg',
    category: 'breakfast',
    popularity: 5,
    ingredients: ['wheat noodles', 'sesame paste', 'pickled vegetables', 'chili oil', 'green onions', 'soy sauce'],
    bestTimeToEat: 'Breakfast',
    priceRange: '¥5-¥15'
  },
  {
    id: '2',
    name: 'Doupi',
    chineseName: '豆皮',
    pinyin: 'dòupí',
    description: 'A savory snack consisting of a crispy outer layer made from mung bean and rice flour, filled with glutinous rice, mushrooms, bamboo shoots, and pork.',
    imageUrl: '/images/doupi.jpg',
    category: 'breakfast',
    popularity: 4,
    ingredients: ['mung bean flour', 'rice flour', 'glutinous rice', 'mushrooms', 'bamboo shoots', 'pork'],
    bestTimeToEat: 'Breakfast or Snack',
    priceRange: '¥8-¥20'
  },
  {
    id: '3',
    name: 'Mianwo',
    chineseName: '面窝',
    pinyin: 'miànwō',
    description: 'A deep-fried dough ring made from rice and soybean batter, crispy on the outside and soft on the inside, often eaten for breakfast.',
    imageUrl: '/images/mianwo.jpg',
    category: 'breakfast',
    popularity: 4,
    ingredients: ['rice flour', 'soybean flour', 'green onions', 'sesame seeds', 'salt'],
    bestTimeToEat: 'Breakfast',
    priceRange: '¥2-¥5'
  },
  {
    id: '4',
    name: 'Tangbao',
    chineseName: '汤包',
    pinyin: 'tāngbāo',
    description: 'Soup dumplings with thin wrappers filled with pork and hot, flavorful broth, a popular snack throughout the day.',
    imageUrl: '/images/tangbao.jpg',
    category: 'savory',
    popularity: 4,
    ingredients: ['wheat flour', 'pork', 'pork broth', 'ginger', 'green onions'],
    bestTimeToEat: 'Any time',
    priceRange: '¥15-¥30'
  },
  {
    id: '5',
    name: 'Lotus Root and Pork Rib Soup',
    chineseName: '莲藕排骨汤',
    pinyin: 'liánǒu páigǔ tāng',
    description: 'A nourishing soup made with lotus root, pork ribs, and various herbs, representing Wuhan\'s culinary tradition of soup-making.',
    imageUrl: '/images/lotus-root-soup.jpg',
    category: 'savory',
    popularity: 4,
    ingredients: ['lotus root', 'pork ribs', 'ginger', 'green onions', 'goji berries', 'salt'],
    bestTimeToEat: 'Lunch or Dinner',
    priceRange: '¥25-¥50'
  },
  {
    id: '6',
    name: 'Fried Sticky Rice Balls',
    chineseName: '炸糍粑',
    pinyin: 'zhá cíbā',
    description: 'Crispy fried glutinous rice cakes, often served with a sweet soybean powder or sugar coating, popular as a dessert or snack.',
    imageUrl: '/images/fried-sticky-rice.jpg',
    category: 'dessert',
    popularity: 3,
    ingredients: ['glutinous rice', 'sugar', 'soybean powder', 'oil'],
    bestTimeToEat: 'Dessert or Snack',
    priceRange: '¥8-¥15'
  }
];

/**
 * Fetches all Wuhan specialty snacks
 * @returns Promise resolving to an array of Snack objects
 */
export async function getAllSnacks(): Promise<Snack[]> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 100));
  
  return [...wuhanSnacks];
}

/**
 * Fetches a specific snack by ID
 * @param id - The snack ID to retrieve
 * @returns Promise resolving to a Snack object or null if not found
 */
export async function getSnackById(id: string): Promise<Snack | null> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 50));
  
  const snack = wuhanSnacks.find(s => s.id === id);
  return snack || null;
}

/**
 * Fetches snacks by category
 * @param category - The category to filter by
 * @returns Promise resolving to an array of Snack objects in the specified category
 */
export async function getSnacksByCategory(category: Snack['category']): Promise<Snack[]> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 80));
  
  return wuhanSnacks.filter(snack => snack.category === category);
}

/**
 * Fetches the most popular snacks
 * @param limit - Maximum number of snacks to return (default: 3)
 * @returns Promise resolving to an array of the most popular Snack objects
 */
export async function getPopularSnacks(limit: number = 3): Promise<Snack[]> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 60));
  
  return [...wuhanSnacks]
    .sort((a, b) => b.popularity - a.popularity)
    .slice(0, limit);
}

/**
 * Searches snacks by name or description
 * @param query - The search query string
 * @returns Promise resolving to an array of Snack objects matching the query
 */
export async function searchSnacks(query: string): Promise<Snack[]> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 120));
  
  if (!query.trim()) {
    return [];
  }
  
  const searchTerm = query.toLowerCase();
  return wuhanSnacks.filter(snack => 
    snack.name.toLowerCase().includes(searchTerm) ||
    snack.chineseName.toLowerCase().includes(searchTerm) ||
    snack.description.toLowerCase().includes(searchTerm) ||
    snack.ingredients.some(ingredient => ingredient.toLowerCase().includes(searchTerm))
  );
}

/**
 * Gets all available snack categories
 * @returns Promise resolving to an array of unique category strings
 */
export async function getSnackCategories(): Promise<Snack['category'][]> {
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 40));
  
  const categories = wuhanSnacks.map(snack => snack.category);
  return Array.from(new Set(categories));
}

// Export the mock data for direct use if needed
export { wuhanSnacks };