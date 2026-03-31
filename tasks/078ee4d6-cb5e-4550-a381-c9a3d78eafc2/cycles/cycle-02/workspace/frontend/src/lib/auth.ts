import { jwtDecode } from 'jwt-decode';

export interface User {
  id: number;
  username: string;
  email: string;
  avatar_url?: string;
  created_at: string;
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
}

export interface DecodedToken {
  user_id: number;
  username: string;
  email: string;
  exp: number;
  iat: number;
}

const TOKEN_KEY = 'forum_auth_tokens';
const USER_KEY = 'forum_user';

export class AuthError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AuthError';
  }
}

export const auth = {
  // Store tokens in localStorage
  setTokens(tokens: AuthTokens): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(TOKEN_KEY, JSON.stringify(tokens));
  },

  // Get tokens from localStorage
  getTokens(): AuthTokens | null {
    if (typeof window === 'undefined') return null;
    const tokens = localStorage.getItem(TOKEN_KEY);
    return tokens ? JSON.parse(tokens) : null;
  },

  // Get access token
  getAccessToken(): string | null {
    const tokens = this.getTokens();
    return tokens?.access_token || null;
  },

  // Get refresh token
  getRefreshToken(): string | null {
    const tokens = this.getTokens();
    return tokens?.refresh_token || null;
  },

  // Store user data
  setUser(user: User): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  },

  // Get user data
  getUser(): User | null {
    if (typeof window === 'undefined') return null;
    const user = localStorage.getItem(USER_KEY);
    return user ? JSON.parse(user) : null;
  },

  // Decode JWT token
  decodeToken(token: string): DecodedToken | null {
    try {
      return jwtDecode<DecodedToken>(token);
    } catch (error) {
      console.error('Failed to decode token:', error);
      return null;
    }
  },

  // Check if token is expired
  isTokenExpired(token: string): boolean {
    const decoded = this.decodeToken(token);
    if (!decoded) return true;
    
    const currentTime = Date.now() / 1000;
    return decoded.exp < currentTime;
  },

  // Check if user is authenticated
  isAuthenticated(): boolean {
    const accessToken = this.getAccessToken();
    if (!accessToken) return false;
    
    return !this.isTokenExpired(accessToken);
  },

  // Get current user ID
  getCurrentUserId(): number | null {
    const user = this.getUser();
    return user?.id || null;
  },

  // Get current username
  getCurrentUsername(): string | null {
    const user = this.getUser();
    return user?.username || null;
  },

  // Clear authentication data
  clearAuth(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
  },

  // Refresh token
  async refreshToken(): Promise<AuthTokens | null> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      this.clearAuth();
      return null;
    }

    try {
      const response = await fetch('http://localhost:8000/api/auth/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${refreshToken}`,
        },
      });

      if (!response.ok) {
        throw new AuthError('Failed to refresh token');
      }

      const tokens: AuthTokens = await response.json();
      this.setTokens(tokens);
      return tokens;
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.clearAuth();
      return null;
    }
  },

  // Get authorization header for API requests
  async getAuthHeader(): Promise<Record<string, string>> {
    let accessToken = this.getAccessToken();
    
    // Refresh token if expired
    if (accessToken && this.isTokenExpired(accessToken)) {
      const newTokens = await this.refreshToken();
      accessToken = newTokens?.access_token || null;
    }

    if (!accessToken) {
      return {};
    }

    return {
      'Authorization': `Bearer ${accessToken}`,
    };
  },

  // Login user
  async login(username: string, password: string): Promise<{ user: User; tokens: AuthTokens }> {
    const response = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Login failed' }));
      throw new AuthError(error.detail || 'Login failed');
    }

    const data = await response.json();
    this.setTokens(data.tokens);
    this.setUser(data.user);
    
    return data;
  },

  // Register user
  async register(username: string, email: string, password: string): Promise<{ user: User; tokens: AuthTokens }> {
    const response = await fetch('http://localhost:8000/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, email, password }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Registration failed' }));
      throw new AuthError(error.detail || 'Registration failed');
    }

    const data = await response.json();
    this.setTokens(data.tokens);
    this.setUser(data.user);
    
    return data;
  },

  // Logout user
  async logout(): Promise<void> {
    const accessToken = this.getAccessToken();
    
    if (accessToken) {
      try {
        await fetch('http://localhost:8000/api/auth/logout', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
        });
      } catch (error) {
        console.error('Logout API call failed:', error);
      }
    }

    this.clearAuth();
  },

  // Update user profile
  async updateProfile(updates: Partial<User>): Promise<User> {
    const authHeader = await this.getAuthHeader();
    
    const response = await fetch('http://localhost:8000/api/users/me', {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...authHeader,
      },
      body: JSON.stringify(updates),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Profile update failed' }));
      throw new AuthError(error.detail || 'Profile update failed');
    }

    const user: User = await response.json();
    this.setUser(user);
    
    return user;
  },

  // Change password
  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    const authHeader = await this.getAuthHeader();
    
    const response = await fetch('http://localhost:8000/api/auth/change-password', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...authHeader,
      },
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Password change failed' }));
      throw new AuthError(error.detail || 'Password change failed');
    }
  },
};