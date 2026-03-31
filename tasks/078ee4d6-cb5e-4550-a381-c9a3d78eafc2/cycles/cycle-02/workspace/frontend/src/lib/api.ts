// API client for forum backend services
// Base URL for backend API
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Common headers for API requests
const getHeaders = (includeAuth = true): HeadersInit => {
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
  };

  if (includeAuth && typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  return headers;
};

// Generic API request handler
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      ...getHeaders(),
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API request failed: ${response.status}`);
  }

  // Handle 204 No Content responses
  if (response.status === 204) {
    return null as T;
  }

  return response.json() as Promise<T>;
}

// Authentication API
export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  display_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface User {
  id: number;
  username: string;
  email: string;
  display_name: string | null;
  created_at: string;
  is_active: boolean;
}

export const authApi = {
  login: (data: LoginRequest): Promise<AuthResponse> =>
    apiRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  register: (data: RegisterRequest): Promise<AuthResponse> =>
    apiRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  logout: (): Promise<void> =>
    apiRequest('/auth/logout', {
      method: 'POST',
    }),

  refreshToken: (refreshToken: string): Promise<{ access_token: string }> =>
    apiRequest('/auth/refresh', {
      method: 'POST',
      body: JSON.stringify({ refresh_token: refreshToken }),
    }),

  getCurrentUser: (): Promise<User> =>
    apiRequest('/users/me'),
};

// Categories API
export interface Category {
  id: number;
  name: string;
  description: string | null;
  slug: string;
  thread_count: number;
  post_count: number;
  created_at: string;
  updated_at: string;
}

export interface CategoryCreateRequest {
  name: string;
  description?: string;
}

export const categoriesApi = {
  getAll: (): Promise<Category[]> =>
    apiRequest('/categories'),

  getBySlug: (slug: string): Promise<Category> =>
    apiRequest(`/categories/${slug}`),

  create: (data: CategoryCreateRequest): Promise<Category> =>
    apiRequest('/categories', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  update: (id: number, data: Partial<CategoryCreateRequest>): Promise<Category> =>
    apiRequest(`/categories/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: (id: number): Promise<void> =>
    apiRequest(`/categories/${id}`, {
      method: 'DELETE',
    }),
};

// Threads API
export interface Thread {
  id: number;
  title: string;
  content: string;
  category_id: number;
  author_id: number;
  author: User;
  post_count: number;
  view_count: number;
  is_locked: boolean;
  is_pinned: boolean;
  last_post_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface ThreadCreateRequest {
  title: string;
  content: string;
  category_id: number;
}

export interface ThreadUpdateRequest {
  title?: string;
  content?: string;
  is_locked?: boolean;
  is_pinned?: boolean;
}

export interface PaginatedThreads {
  items: Thread[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export const threadsApi = {
  getByCategory: (
    categorySlug: string,
    page = 1,
    perPage = 20
  ): Promise<PaginatedThreads> =>
    apiRequest(`/categories/${categorySlug}/threads?page=${page}&per_page=${perPage}`),

  getById: (threadId: number): Promise<Thread> =>
    apiRequest(`/threads/${threadId}`),

  create: (data: ThreadCreateRequest): Promise<Thread> =>
    apiRequest('/threads', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  update: (threadId: number, data: ThreadUpdateRequest): Promise<Thread> =>
    apiRequest(`/threads/${threadId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: (threadId: number): Promise<void> =>
    apiRequest(`/threads/${threadId}`, {
      method: 'DELETE',
    }),

  search: (
    query: string,
    page = 1,
    perPage = 20
  ): Promise<PaginatedThreads> =>
    apiRequest(`/threads/search?q=${encodeURIComponent(query)}&page=${page}&per_page=${perPage}`),
};

// Posts API
export interface Post {
  id: number;
  content: string;
  thread_id: number;
  author_id: number;
  author: User;
  parent_id: number | null;
  reply_count: number;
  upvote_count: number;
  downvote_count: number;
  created_at: string;
  updated_at: string;
}

export interface PostCreateRequest {
  content: string;
  thread_id: number;
  parent_id?: number;
}

export interface PostUpdateRequest {
  content: string;
}

export interface PaginatedPosts {
  items: Post[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export const postsApi = {
  getByThread: (
    threadId: number,
    page = 1,
    perPage = 50
  ): Promise<PaginatedPosts> =>
    apiRequest(`/threads/${threadId}/posts?page=${page}&per_page=${perPage}`),

  getById: (postId: number): Promise<Post> =>
    apiRequest(`/posts/${postId}`),

  create: (data: PostCreateRequest): Promise<Post> =>
    apiRequest('/posts', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  update: (postId: number, data: PostUpdateRequest): Promise<Post> =>
    apiRequest(`/posts/${postId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: (postId: number): Promise<void> =>
    apiRequest(`/posts/${postId}`, {
      method: 'DELETE',
    }),

  getReplies: (
    postId: number,
    page = 1,
    perPage = 20
  ): Promise<PaginatedPosts> =>
    apiRequest(`/posts/${postId}/replies?page=${page}&per_page=${perPage}`),
};

// Votes API
export interface VoteRequest {
  post_id: number;
  value: 1 | -1; // 1 for upvote, -1 for downvote
}

export interface VoteResponse {
  post_id: number;
  user_id: number;
  value: number;
  total_score: number;
}

export const votesApi = {
  vote: (data: VoteRequest): Promise<VoteResponse> =>
    apiRequest('/votes', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  removeVote: (postId: number): Promise<void> =>
    apiRequest(`/votes/${postId}`, {
      method: 'DELETE',
    }),

  getUserVote: (postId: number): Promise<{ value: number } | null> =>
    apiRequest(`/votes/${postId}/user`),
};

// Notifications API
export interface Notification {
  id: number;
  type: 'new_reply' | 'thread_update' | 'mention' | 'system';
  title: string;
  message: string;
  data: Record<string, any>;
  is_read: boolean;
  created_at: string;
}

export interface PaginatedNotifications {
  items: Notification[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
  unread_count: number;
}

export const notificationsApi = {
  getAll: (page = 1, perPage = 20): Promise<PaginatedNotifications> =>
    apiRequest(`/notifications?page=${page}&per_page=${perPage}`),

  getUnread: (page = 1, perPage = 20): Promise<PaginatedNotifications> =>
    apiRequest(`/notifications/unread?page=${page}&per_page=${perPage}`),

  markAsRead: (notificationId: number): Promise<void> =>
    apiRequest(`/notifications/${notificationId}/read`, {
      method: 'POST',
    }),

  markAllAsRead: (): Promise<void> =>
    apiRequest('/notifications/read-all', {
      method: 'POST',
    }),

  delete: (notificationId: number): Promise<void> =>
    apiRequest(`/notifications/${notificationId}`, {
      method: 'DELETE',
    }),
};

// Search API
export interface SearchResult {
  threads: Thread[];
  posts: Post[];
  users