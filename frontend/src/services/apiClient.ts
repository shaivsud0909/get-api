import axios, { AxiosError } from 'axios';
import { TOKEN_STORAGE_KEY } from '../constants';

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000',
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

/** Attach the JWT access token to every request when present. */
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_STORAGE_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

type UnauthorizedListener = () => void;
let onUnauthorized: UnauthorizedListener | null = null;

/** AuthContext registers a callback so a 401 anywhere logs the user out. */
export function setUnauthorizedListener(listener: UnauthorizedListener | null) {
  onUnauthorized = listener;
}

apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      onUnauthorized?.();
    }
    return Promise.reject(error);
  }
);

interface FastApiValidationError {
  loc: (string | number)[];
  msg: string;
}

/** Turn any failed request into a human-readable message. */
export function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (error.code === 'ECONNABORTED') {
      return 'The request timed out. Please try again.';
    }
    if (!error.response) {
      return 'Cannot reach the server. Please check that the backend is running.';
    }
    const detail = (error.response.data as { detail?: unknown })?.detail;
    if (typeof detail === 'string') {
      return detail;
    }
    if (Array.isArray(detail)) {
      // FastAPI 422 validation errors
      return (detail as FastApiValidationError[])
        .map((d) => `${d.loc[d.loc.length - 1]}: ${d.msg}`)
        .join('; ');
    }
    if (detail && typeof detail === 'object' && 'message' in detail) {
      return String((detail as { message: unknown }).message);
    }
    if (error.response.status === 403) {
      return 'You do not have permission to perform this action.';
    }
    return `Request failed (${error.response.status}). Please try again.`;
  }
  return error instanceof Error ? error.message : 'Something went wrong. Please try again.';
}
