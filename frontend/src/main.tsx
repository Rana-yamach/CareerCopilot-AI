import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './styles/globals.css';
import App from './App.tsx';
import { config } from './config';

if (config.useMockAuth) {
  // eslint-disable-next-line no-console
  console.warn(
    '[CareerCopilot AI] VITE_USE_MOCK_AUTH=true — auth çağrıları gerçek backend yerine ' +
      'localStorage tabanlı mock veriyi kullanıyor. Bu ortam prod ise .env değerini kontrol edin.',
  );
}

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
