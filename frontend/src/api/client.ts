import axios, { AxiosError } from 'axios';
import { config } from '@/config';
import { useAuthStore } from '@/store/authStore';
import { tr } from '@/i18n/tr';
import type { ApiErrorBody } from '@/types/common';

/**
 * Merkezi Axios instance. Tüm API çağrıları bu client üzerinden yapılır
 * (bkz. ARCHITECTURE.md §8.2).
 */
export const apiClient = axios.create({
  baseURL: config.apiBaseUrl,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: Bearer token ekle
apiClient.interceptors.request.use((requestConfig) => {
  const { accessToken } = useAuthStore.getState();
  if (accessToken) {
    requestConfig.headers.Authorization = `Bearer ${accessToken}`;
  }
  return requestConfig;
});

/**
 * `responseType: 'blob'` ile yapılan istekler (ör. PDF indirme) hata durumunda
 * da gövdeyi bir `Blob` olarak döndürür — backend'in Türkçe JSON hata mesajı
 * ayrıştırılamadan kaybolur. Burada blob içeriği JSON ise senkron hale getirilir.
 */
async function normalizeBlobError(error: AxiosError<ApiErrorBody>): Promise<AxiosError<ApiErrorBody>> {
  const data = error.response?.data as unknown;
  if (data instanceof Blob && data.type.includes('json')) {
    try {
      const text = await data.text();
      error.response!.data = JSON.parse(text) as ApiErrorBody;
    } catch {
      // Ayrıştırılamıyorsa orijinal Blob'u bırak, getApiErrorMessage genel mesaja düşer.
    }
  }
  return error;
}

// Response interceptor: 401 → logout + /login yönlendirme, blob hata gövdesini normalize et
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError<ApiErrorBody>) => {
    if (error.response?.status === 401) {
      const { isAuthenticated, logout } = useAuthStore.getState();
      if (isAuthenticated) {
        logout();
        if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
          window.location.assign('/login');
        }
      }
    }
    return Promise.reject(await normalizeBlobError(error));
  },
);

/**
 * Backend olmadan sayfalarda gezinebilmek için geçici mock-auth modunda
 * (bkz. `api/mockAuth.ts`) fırlatılan hata. `getApiErrorMessage`/`getApiErrorCode`
 * gerçek `AxiosError` ile aynı şekilde ele alınmasını sağlar.
 */
export class MockAuthError extends Error {
  code: string;

  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

/**
 * Axios hatasından kullanıcıya gösterilecek Türkçe mesajı çıkarır.
 * Backend `{"error": {"code", "message"}}` şemasında döner.
 */
export function getApiErrorMessage(error: unknown): string {
  if (error instanceof MockAuthError) return error.message;

  if (axios.isAxiosError<ApiErrorBody>(error)) {
    const backendMessage = error.response?.data?.error?.message;
    if (backendMessage) return backendMessage;

    if (!error.response) return tr.common.networkError;

    const code = error.response.data?.error?.code;
    if (code && code in tr.errors) {
      return tr.errors[code as keyof typeof tr.errors];
    }
  }
  return tr.common.genericError;
}

export function getApiErrorCode(error: unknown): string | undefined {
  if (error instanceof MockAuthError) return error.code;

  if (axios.isAxiosError<ApiErrorBody>(error)) {
    return error.response?.data?.error?.code;
  }
  return undefined;
}
