// API utilities for Red Panda informational website
// Currently a static site, but prepared for potential future API integrations

/**
 * Base API configuration
 */
export const API_CONFIG = {
  baseUrl: process.env.NEXT_PUBLIC_API_URL || 'https://api.example.com',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
} as const;

/**
 * API endpoints for potential future features
 */
export const ENDPOINTS = {
  // Conservation status data
  conservationStatus: '/api/conservation-status',
  
  // Red panda facts
  facts: '/api/facts',
  
  // Habitat information
  habitats: '/api/habitats',
  
  // Image gallery
  images: '/api/images',
  
  // Conservation organizations
  organizations: '/api/organizations',
} as const;

/**
 * Error types for API responses
 */
export type ApiError = {
  message: string;
  code?: string;
  status?: number;
};

/**
 * Standard API response wrapper
 */
export type ApiResponse<T = unknown> = {
  data?: T;
  error?: ApiError;
  success: boolean;
  timestamp: string;
};

/**
 * Conservation status data structure
 */
export interface ConservationStatus {
  status: 'Endangered' | 'Vulnerable' | 'Near Threatened' | 'Least Concern';
  populationTrend: 'Decreasing' | 'Stable' | 'Increasing';
  lastAssessed: string;
  iucnLink: string;
}

/**
 * Red panda fact
 */
export interface RedPandaFact {
  id: string;
  title: string;
  description: string;
  category: 'biology' | 'behavior' | 'habitat' | 'conservation';
  source?: string;
}

/**
 * Habitat information
 */
export interface HabitatInfo {
  region: string;
  countries: string[];
  elevationRange: string;
  vegetationType: string;
  threats: string[];
}

/**
 * Image metadata
 */
export interface RedPandaImage {
  id: string;
  url: string;
  alt: string;
  caption?: string;
  photographer?: string;
  license?: string;
  width: number;
  height: number;
}

/**
 * Conservation organization
 */
export interface ConservationOrg {
  id: string;
  name: string;
  website: string;
  description: string;
  focusAreas: string[];
}

/**
 * Mock data for development and fallback
 */
export const MOCK_DATA = {
  conservationStatus: {
    status: 'Endangered' as const,
    populationTrend: 'Decreasing' as const,
    lastAssessed: '2015-04-10',
    iucnLink: 'https://www.iucnredlist.org/species/714/110023718',
  },
  
  facts: [
    {
      id: 'fact-1',
      title: 'Not Actually a Panda',
      description: 'Red pandas are not closely related to giant pandas. They were given the name "panda" first, about 50 years before the giant panda was discovered.',
      category: 'biology' as const,
      source: 'Smithsonian\'s National Zoo',
    },
    {
      id: 'fact-2',
      title: 'Bamboo Specialists',
      description: 'Red pandas primarily eat bamboo, but unlike giant pandas, they also eat fruits, acorns, roots, and eggs.',
      category: 'biology' as const,
    },
    {
      id: 'fact-3',
      title: 'Thermoregulation',
      description: 'Red pandas have thick fur on the soles of their feet to keep them warm and provide traction on slippery branches.',
      category: 'biology' as const,
    },
  ] as RedPandaFact[],
  
  habitats: [
    {
      region: 'Eastern Himalayas',
      countries: ['Nepal', 'Bhutan', 'India'],
      elevationRange: '2,200-4,800 meters',
      vegetationType: 'Temperate forests with bamboo understories',
      threats: ['Habitat loss', 'Poaching', 'Climate change'],
    },
  ] as HabitatInfo[],
  
  images: [
    {
      id: 'img-1',
      url: '/images/red-panda-1.jpg',
      alt: 'Red panda resting on a tree branch',
      caption: 'A red panda taking a nap in its natural habitat',
      photographer: 'John Doe',
      license: 'CC BY 2.0',
      width: 800,
      height: 600,
    },
    {
      id: 'img-2',
      url: '/images/red-panda-2.jpg',
      alt: 'Red panda eating bamboo',
      caption: 'Red panda enjoying a bamboo meal',
      photographer: 'Jane Smith',
      license: 'CC BY-SA 3.0',
      width: 1024,
      height: 768,
    },
  ] as RedPandaImage[],
  
  organizations: [
    {
      id: 'org-1',
      name: 'Red Panda Network',
      website: 'https://redpandanetwork.org',
      description: 'Dedicated to the conservation of wild red pandas and their habitat.',
      focusAreas: ['Habitat protection', 'Community conservation', 'Research'],
    },
    {
      id: 'org-2',
      name: 'World Wildlife Fund',
      website: 'https://www.worldwildlife.org',
      description: 'Works to conserve nature and reduce the most pressing threats to biodiversity.',
      focusAreas: ['Species conservation', 'Habitat protection', 'Climate change'],
    },
  ] as ConservationOrg[],
};

/**
 * Generic API client with error handling
 */
export class ApiClient {
  private baseUrl: string;
  private timeout: number;

  constructor(config: { baseUrl?: string; timeout?: number } = {}) {
    this.baseUrl = config.baseUrl || API_CONFIG.baseUrl;
    this.timeout = config.timeout || API_CONFIG.timeout;
  }

  /**
   * Make a GET request to the API
   */
  async get<T>(endpoint: string, options?: RequestInit): Promise<ApiResponse<T>> {
    return this.request<T>('GET', endpoint, undefined, options);
  }

  /**
   * Make a POST request to the API
   */
  async post<T>(endpoint: string, data?: unknown, options?: RequestInit): Promise<ApiResponse<T>> {
    return this.request<T>('POST', endpoint, data, options);
  }

  /**
   * Generic request method
   */
  private async request<T>(
    method: string,
    endpoint: string,
    data?: unknown,
    options?: RequestInit
  ): Promise<ApiResponse<T>> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const url = `${this.baseUrl}${endpoint}`;
      const headers = {
        ...API_CONFIG.headers,
        ...options?.headers,
      };

      const response = await fetch(url, {
        method,
        headers,
        body: data ? JSON.stringify(data) : undefined,
        signal: controller.signal,
        ...options,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const responseData = await response.json();

      return {
        data: responseData as T,
        success: true,
        timestamp: new Date().toISOString(),
      };
    } catch (error) {
      clearTimeout(timeoutId);

      const apiError: ApiError = {
        message: error instanceof Error ? error.message : 'Unknown error occurred',
        code: error instanceof DOMException ? error.name : undefined,
      };

      return {
        error: apiError,
        success: false,
        timestamp: new Date().toISOString(),
      };
    }
  }
}

/**
 * Factory function to create an API client instance
 */
export function createApiClient(config?: { baseUrl?: string; timeout?: number }) {
  return new ApiClient(config);
}

/**
 * Default API client instance
 */
export const apiClient = createApiClient();

/**
 * Utility function to fetch conservation status
 * Falls back to mock data if API is unavailable
 */
export async function fetchConservationStatus(): Promise<ConservationStatus> {
  try {
    const response = await apiClient.get<ConservationStatus>(ENDPOINTS.conservationStatus);
    
    if (response.success && response.data) {
      return response.data;
    }
    
    // Fallback to mock data
    return MOCK_DATA.conservationStatus;
  } catch {
    return MOCK_DATA.conservationStatus;
  }
}

/**
 * Utility function to fetch red panda facts
 * Falls back to mock data if API is unavailable
 */
export async function fetchRedPandaFacts(): Promise<RedPandaFact[]> {
  try {
    const response = await apiClient.get<RedPandaFact[]>(ENDPOINTS.facts);
    
    if (response.success && response.data) {
      return response.data;
    }
    
    // Fallback to mock data
    return MOCK_DATA.facts;
  } catch {
    return MOCK_DATA.facts;
  }
}

/**
 * Utility function to fetch habitat information
 * Falls back to mock data if API is unavailable
 */
export async function fetchHabitatInfo(): Promise<HabitatInfo[]> {
  try {
    const response = await apiClient.get<HabitatInfo[]>(ENDPOINTS.habitats);
    
    if (response.success && response.data) {
      return response.data;
    }
    
    // Fallback to mock data
    return MOCK_DATA.habitats;
  } catch {
    return MOCK_DATA.habitats;
  }
}

/**
 * Utility function to fetch red panda images
 * Falls back to mock data if API is unavailable
 */
export async function fetchRedPandaImages(): Promise<RedPandaImage[]> {
  try {
    const response = await apiClient.get<RedPandaImage[]>(ENDPOINTS.images);
    
    if (response.success && response.data) {
      return response.data;
    }
    
    // Fallback to mock data
    return MOCK_DATA.images;
  } catch {
    return MOCK_DATA