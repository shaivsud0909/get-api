import type { AuthUser, TokenPayload } from '../types';

/** Decode a JWT payload without verifying the signature (verification happens server-side). */
export function decodeToken(token: string): TokenPayload | null {
  try {
    const payload = token.split('.')[1];
    if (!payload) return null;
    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/');
    const json = decodeURIComponent(
      atob(normalized)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(json) as TokenPayload;
  } catch {
    return null;
  }
}

export function isTokenExpired(payload: TokenPayload): boolean {
  return payload.exp * 1000 <= Date.now();
}

export function userFromToken(token: string): AuthUser | null {
  const payload = decodeToken(token);
  if (!payload || isTokenExpired(payload)) return null;
  return {
    id: Number(payload.sub),
    email: payload.email,
    role: payload.role,
  };
}
