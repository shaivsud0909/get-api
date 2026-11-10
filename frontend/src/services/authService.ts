import { apiClient } from './apiClient';
import { TOKEN_STORAGE_KEY } from '../constants';
import type { LoginResponse, SignupResponse } from '../types';

export interface SignupInput {
  email: string;
  password: string;
  phone_number?: string | null;
  country_code?: string | null;
}

export interface LoginInput {
  email: string;
  password: string;
}

/** POST /signup — returns the created user (does NOT log in). */
export async function signup(input: SignupInput): Promise<SignupResponse> {
  const { data } = await apiClient.post<SignupResponse>('/signup', input);
  return data;
}

/** POST /login — returns a bearer token. */
export async function login(input: LoginInput): Promise<LoginResponse> {
  const { data } = await apiClient.post<LoginResponse>('/login', input);
  return data;
}

export function storeToken(token: string) {
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
}

export function getStoredToken(): string | null {
  return localStorage.getItem(TOKEN_STORAGE_KEY);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_STORAGE_KEY);
}
