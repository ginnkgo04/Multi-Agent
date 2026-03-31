// API client for forum platform
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

// Types
export interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
  avatar_url?: string;
}

export interface Category {
  id: number;
  name: string;
  description: string;
  slug: string;
  thread_count: number;
  post_count: number;
  created_at: string;
}

export interface Thread {
  id: number;
  title: string;
  content: string;
  category_id: number;
  author_id: number;
  author: User;
  post_count: number;
  view_count: number;
  is_pinned: boolean;
  is_locked: boolean;
  created_at: string;
  updated_at: string;
  last_post_at?: string;
  last_post_by?: User;
}

export interface Post {
  id: number;
  content: string;
  thread_id: number;
  author_id: number;
  author: User;
  created_at: string;
  updated_at: string;
  parent_id?: number;
  reply_count: number;
  upvote_count: number;
  downvote_count: number;
  user_vote?: 'up' | 'down' | null;
}

export interface Vote {
  id: number;
  post_id: number;
  user_id: number;
  vote_type: 'up' | 'down';
  created_at: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface CreateThreadRequest {
  title: string;
  content: string;
  category_id: number;
}

export interface CreatePostRequest {
  content: string;
  thread_id: number;
  parent_id?: number;
}

export interface UpdatePostRequest {
  content: string;
}

export interface ApiError {
  detail: string;
  status_code: number;
}

// Auth API
export const authApi = {
  login: async (data: LoginRequest): Promise<{ access_token: string; token_type: string }> => {
    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Login failed');
    }
    
    return response.json();
  },

  register: async (data: RegisterRequest): Promise<{ message: string }> => {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }
    
    return response.json();
  },

  logout: async (): Promise<void> => {
    // In JWT, logout is client-side by removing token
    // This endpoint might be used for token blacklisting if implemented
    await fetch(`${API_BASE_URL}/auth/logout`, {
      method: 'POST',
      headers: await getAuthHeaders(),
    });
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: await getAuthHeaders(),
    });
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Failed to fetch user');
    }
    
    return response.json();
  },
};

// Categories API
export const categoriesApi = {
  getAll: async (): Promise<Category[]> => {
    const response = await fetch(`${API_BASE_URL}/api/categories`);
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Failed to fetch categories');
    }
    
    return response.json();
  },

  getBySlug: async (slug: string): Promise<Category> => {
    const response = await fetch(`${API_BASE_URL}/api/categories/${slug}`);
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Failed to fetch category');
    }
    
    return response.json();
  },
};

// Threads API
export const threadsApi = {
  getByCategory: async (
    categoryId: number, 
    page: number = 1, 
    perPage: number = 20
  ): Promise<PaginatedResponse<Thread>> => {
    const response = await fetch(
      `${API_BASE_URL}/api/categories/${categoryId}/threads?page=${page}&per_page=${perPage}`
    );
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Failed to fetch threads');
    }
    
    return response.json();
  },

  getById: async (threadId: number): Promise<Thread> => {
    const response = await fetch(`${API_BASE_URL}/api/threads/${threadId}`);
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Failed to fetch thread');
    }
    
    return response.json();
  },

  create: async (data: CreateThreadRequest): Promise<Thread> => {
    const response = await fetch(`${API_BASE_URL}/api/threads`, {
      method: 'POST',
      headers: await getAuthHeaders(),
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Failed to create thread');
    }
    
    return response.json();
  },

  update: async (threadId: number, data: Partial<CreateThreadRequest>): Promise<Thread> => {
    const response = await fetch(`${API_BASE_URL}/api/threads/${threadId}`, {
      method: 'PUT',
      headers: await getAuthHeaders(),
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Failed to update thread');
    }
    
    return response.json();
  },

  delete: async (threadId: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/api/threads/${threadId}`, {
      method: 'DELETE',
      headers: await getAuthHeaders(),
    });
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Failed to delete thread');
    }
  },
};

// Posts API
export const postsApi = {
  getByThread: async (
    threadId: number, 
    page: number = 1, 
    perPage: number = 50
  ): Promise<PaginatedResponse<Post>> => {
    const response = await fetch(
      `${API_BASE_URL}/api/threads/${threadId}/posts?page=${page}&per_page=${perPage}`
    );
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Failed to fetch posts');
    }
    
    return response.json();
  },

  getReplies: async (postId: number): Promise<Post[]> => {
    const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/replies`);
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Failed to fetch replies');
    }
    
    return response.json();
  },

  create: async (data: CreatePostRequest): Promise<Post> => {
    const response = await fetch(`${API_BASE_URL}/api/posts`, {
      method: 'POST',
      headers: await getAuthHeaders(),
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Failed to create post');
    }
    
    return response.json();
  },

  update: async (postId: number, data: UpdatePostRequest): Promise<Post> => {
    const response = await fetch(`${API_BASE_URL}/api/posts/${postId}`, {
      method: 'PUT',
      headers: await getAuthHeaders(),
      body: JSON.stringify(data),
    });
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Failed to update post');
    }
    
    return response.json();
  },

  delete: async (postId: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/api/posts/${postId}`, {
      method: 'DELETE',
      headers: await getAuthHeaders(),
    });
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Failed to delete post');
    }
  },
};

// Votes API
export const votesApi = {
  votePost: async (postId: number, voteType: 'up' | 'down'): Promise<Vote> => {
    const response = await fetch(`${API_BASE_URL}/api/posts/${postId}/vote`, {
      method: 'POST',
      headers: await getAuthHeaders(),
      body: JSON.stringify({ vote_type: voteType }),
    });
    
    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || 'Failed to vote');
    }
    
    return response.json();
  },

  removeVote: async (postId: number): Promise<void> => {