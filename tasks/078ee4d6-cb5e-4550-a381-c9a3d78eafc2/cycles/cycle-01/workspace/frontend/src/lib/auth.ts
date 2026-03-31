import { jwtDecode } from 'jwt-decode';

export interface User {
  id: number;
  username: string;
  email: string;
  avatar?: string;
  role: 'user' | 'moderator' | 'admin';
  createdAt: string;
}

export interface AuthTokens {
  accessToken: string;
  refreshToken: string;
}

export interface DecodedToken {
  sub: string;
  userId: number;
  username: string;
  role: string;
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
    return tokens?.accessToken || null;
  },

  // Get refresh token
  getRefreshToken(): string | null {
    const tokens = this.getTokens();
    return tokens?.refreshToken || null;
  },

  // Clear tokens (logout)
  clearTokens(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
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

  // Clear user data
  clearUser(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(USER_KEY);
  },

  // Check if user is authenticated
  isAuthenticated(): boolean {
    const token = this.getAccessToken();
    if (!token) return false;

    try {
      const decoded = jwtDecode<DecodedToken>(token);
      const now = Date.now() / 1000;
      return decoded.exp > now;
    } catch {
      return false;
    }
  },

  // Check if token is expired
  isTokenExpired(token: string): boolean {
    try {
      const decoded = jwtDecode<DecodedToken>(token);
      const now = Date.now() / 1000;
      return decoded.exp <= now;
    } catch {
      return true;
    }
  },

  // Get decoded token data
  getDecodedToken(): DecodedToken | null {
    const token = this.getAccessToken();
    if (!token) return null;

    try {
      return jwtDecode<DecodedToken>(token);
    } catch {
      return null;
    }
  },

  // Get current user role
  getUserRole(): string | null {
    const decoded = this.getDecodedToken();
    return decoded?.role || null;
  },

  // Check if user has required role
  hasRole(requiredRole: string): boolean {
    const userRole = this.getUserRole();
    if (!userRole) return false;

    const roleHierarchy = ['user', 'moderator', 'admin'];
    const userRoleIndex = roleHierarchy.indexOf(userRole);
    const requiredRoleIndex = roleHierarchy.indexOf(requiredRole);

    return userRoleIndex >= requiredRoleIndex;
  },

  // Refresh token (placeholder - should be implemented with API call)
  async refreshToken(): Promise<AuthTokens | null> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      this.clearTokens();
      return null;
    }

    try {
      // In a real implementation, this would call the backend refresh endpoint
      // For now, we'll return null and let the API layer handle it
      return null;
    } catch (error) {
      this.clearTokens();
      throw new AuthError('Failed to refresh token');
    }
  },

  // Initialize auth state from localStorage
  initialize(): { user: User | null; isAuthenticated: boolean } {
    const user = this.getUser();
    const isAuthenticated = this.isAuthenticated();

    // Clear invalid auth state
    if (!isAuthenticated && user) {
      this.clearUser();
    }

    return { user: isAuthenticated ? user : null, isAuthenticated };
  },
};

// Export default instance
export default auth;