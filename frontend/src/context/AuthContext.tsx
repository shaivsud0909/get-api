import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import type { ReactNode } from 'react';
import type { AuthUser } from '../types';
import * as authService from '../services/authService';
import { setUnauthorizedListener } from '../services/apiClient';
import { userFromToken } from '../utils/jwt';

interface AuthContextValue {
  user: AuthUser | null;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<AuthUser>;
  signup: (input: authService.SignupInput) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(() => {
    const token = authService.getStoredToken();
    if (!token) return null;
    const existing = userFromToken(token);
    if (!existing) authService.clearToken();
    return existing;
  });

  const logout = useCallback(() => {
    authService.clearToken();
    setUser(null);
  }, []);

  // Any 401 response (expired/invalid token) logs the user out.
  useEffect(() => {
    setUnauthorizedListener(() => {
      if (authService.getStoredToken()) logout();
    });
    return () => setUnauthorizedListener(null);
  }, [logout]);

  const login = useCallback(async (email: string, password: string): Promise<AuthUser> => {
    const { access_token } = await authService.login({ email, password });
    const nextUser = userFromToken(access_token);
    if (!nextUser) {
      throw new Error('Received an invalid token from the server.');
    }
    authService.storeToken(access_token);
    setUser(nextUser);
    return nextUser;
  }, []);

  const signup = useCallback(async (input: authService.SignupInput) => {
    // The backend's signup does not return a token; callers log in afterwards.
    await authService.signup(input);
  }, []);

  const value = useMemo(
    () => ({ user, isAuthenticated: user !== null, login, signup, logout }),
    [user, login, signup, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
