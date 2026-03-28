// API client for fetching cherry blossom data
// This is a mock implementation for the cherry blossom static webpage
// In a real application, replace with actual backend endpoints

export interface CherryBlossomFact {
  id: number;
  title: string;
  description: string;
  category: 'biology' | 'culture' | 'history';
}

export interface CherryBlossomImage {
  id: number;
  url: string;
  alt: string;
  caption: string;
}

export interface PageContent {
  title: string;
  introduction: string;
  sections: Array<{
    id: number;
    title: string;
    content: string;
  }>;
}

export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

class CherryBlossomApi {
  private baseUrl: string;
  
  constructor(baseUrl: string = '') {
    this.baseUrl = baseUrl;
  }
  
  // Mock data for cherry blossom facts
  private mockFacts: CherryBlossomFact[] = [
    {
      id: 1,
      title: 'Symbol of Spring',
      description: 'Cherry blossoms, known as "sakura" in Japan, are celebrated as a symbol of spring and the fleeting nature of life.',
      category: 'culture'
    },
    {
      id: 2,
      title: 'Short Blooming Period',
      description: 'Cherry blossoms typically bloom for only one to two weeks each year, depending on weather conditions.',
      category: 'biology'
    },
    {
      id: 3,
      title: 'Hanami Tradition',
      description: 'The Japanese tradition of "hanami" involves picnicking under blooming cherry blossom trees.',
      category: 'culture'
    },
    {
      id: 4,
      title: 'Varieties',
      description: 'There are over 200 varieties of cherry blossoms, with Somei Yoshino being the most popular in Japan.',
      category: 'biology'
    },
    {
      id: 5,
      title: 'National Cherry Blossom Festival',
      description: 'Washington D.C. hosts an annual National Cherry Blossom Festival to celebrate the gift of trees from Japan in 1912.',
      category: 'history'
    }
  ];
  
  // Mock data for images
  private mockImages: CherryBlossomImage[] = [
    {
      id: 1,
      url: '/images/cherry-blossom.jpg',
      alt: 'Beautiful pink cherry blossoms in full bloom',
      caption: 'Cherry blossoms in spring'
    },
    {
      id: 2,
      url: '/images/cherry-blossom-2.jpg',
      alt: 'White cherry blossoms against blue sky',
      caption: 'White sakura flowers'
    },
    {
      id: 3,
      url: '/images/cherry-blossom-3.jpg',
      alt: 'Cherry blossom petals falling like snow',
      caption: 'Falling cherry blossom petals'
    }
  ];
  
  // Mock page content
  private mockPageContent: PageContent = {
    title: 'Cherry Blossoms Introduction',
    introduction: 'Cherry blossoms are one of the most beautiful and culturally significant flowers in the world. These delicate pink and white flowers symbolize the transient nature of life and are celebrated in many cultures, particularly in Japan.',
    sections: [
      {
        id: 1,
        title: 'Cultural Significance',
        content: 'In Japanese culture, cherry blossoms represent the beauty and fragility of life. The concept of "mono no aware" - the awareness of impermanence - is deeply connected to the brief blooming period of sakura.'
      },
      {
        id: 2,
        title: 'Historical Background',
        content: 'Cherry blossoms have been celebrated in Japan for centuries. The practice of hanami (flower viewing) dates back to the Nara period (710-794), though it originally focused on plum blossoms before shifting to cherry blossoms.'
      },
      {
        id: 3,
        title: 'Global Appreciation',
        content: 'Today, cherry blossoms are celebrated worldwide. Many countries have received cherry trees as gifts from Japan and hold annual festivals to celebrate their bloom.'
      }
    ]
  };
  
  /**
   * Fetch cherry blossom facts
   * @param category Optional filter by category
   * @returns Promise with cherry blossom facts
   */
  async getFacts(category?: CherryBlossomFact['category']): Promise<ApiResponse<CherryBlossomFact[]>> {
    // Simulate API delay
    await this.simulateDelay();
    
    let facts = this.mockFacts;
    if (category) {
      facts = facts.filter(fact => fact.category === category);
    }
    
    return {
      success: true,
      data: facts
    };
  }
  
  /**
   * Fetch cherry blossom images
   * @param limit Optional limit for number of images
   * @returns Promise with cherry blossom images
   */
  async getImages(limit?: number): Promise<ApiResponse<CherryBlossomImage[]>> {
    // Simulate API delay
    await this.simulateDelay();
    
    let images = this.mockImages;
    if (limit && limit > 0) {
      images = images.slice(0, limit);
    }
    
    return {
      success: true,
      data: images
    };
  }
  
  /**
   * Fetch page content
   * @returns Promise with page content
   */
  async getPageContent(): Promise<ApiResponse<PageContent>> {
    // Simulate API delay
    await this.simulateDelay();
    
    return {
      success: true,
      data: this.mockPageContent
    };
  }
  
  /**
   * Submit contact form
   * @param name User's name
   * @param email User's email
   * @param message User's message
   * @returns Promise with submission result
   */
  async submitContactForm(name: string, email: string, message: string): Promise<ApiResponse<{ id: string }>> {
    // Simulate API delay
    await this.simulateDelay();
    
    // In a real implementation, this would send data to a backend
    console.log('Contact form submission:', { name, email, message });
    
    return {
      success: true,
      data: { id: `contact-${Date.now()}` },
      message: 'Thank you for your message! We will get back to you soon.'
    };
  }
  
  /**
   * Simulate network delay
   * @param ms Delay in milliseconds
   */
  private simulateDelay(ms: number = 300): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Create and export a singleton instance
export const cherryBlossomApi = new CherryBlossomApi();

// Export types for convenience
export type { CherryBlossomApi };