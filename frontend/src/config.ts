/**
 * Merkezi ortam değişkeni erişimi. Tüm `import.meta.env` erişimleri
 * bu dosya üzerinden yapılır.
 */
export const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
  appName: import.meta.env.VITE_APP_NAME ?? 'CareerCopilot AI',
  /**
   * Backend hazır olmadan sayfalarda gezinebilmek için geçici mod.
   * true iken auth çağrıları gerçek API yerine tarayıcı localStorage'ını kullanır.
   */
  useMockAuth: import.meta.env.VITE_USE_MOCK_AUTH === 'true',
} as const;
