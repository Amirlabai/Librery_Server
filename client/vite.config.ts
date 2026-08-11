import { defineConfig, type ProxyOptions } from 'vite';
import react from '@vitejs/plugin-react';

const flask: ProxyOptions = {
  target: 'http://localhost:8000',
  changeOrigin: true,
};

/**
 * Vite matches proxy keys as prefixes. `/upload` would also steal `/uploads`
 * (the React admin tab). Bypass SPA document routes so the React app loads.
 */
const uploadProxy: ProxyOptions = {
  ...flask,
  bypass(req) {
    const path = (req.url || '').split('?')[0];
    if (path === '/uploads' || path.startsWith('/uploads/')) {
      return req.url;
    }
    return undefined;
  },
};

const authPageProxy: ProxyOptions = {
  ...flask,
  bypass(req) {
    const path = (req.url || '').split('?')[0];
    const accept = String(req.headers.accept || '');
    if (
      accept.includes('text/html') &&
      (path === '/login' ||
        path === '/register' ||
        path === '/forgot-password' ||
        path.startsWith('/reset-password'))
    ) {
      return req.url;
    }
    return undefined;
  },
};

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': flask,
      '/login': authPageProxy,
      '/register': authPageProxy,
      '/logout': flask,
      '/forgot-password': authPageProxy,
      '/reset-password': authPageProxy,
      '/refresh-session': flask,
      '/browse': flask,
      '/search': flask,
      '/download': flask,
      '/delete': flask,
      '/create_folder': flask,
      '/suggest': flask,
      '/my_uploads': flask,
      '/upload': uploadProxy,
      '/admin': flask,
      '/preview': flask,
      '/useful_links': flask,
      '/heartbeat': flask,
    },
  },
  build: {
    outDir: 'dist',
  },
});
