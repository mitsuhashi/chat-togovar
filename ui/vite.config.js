import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  base: '/chat-togovar/', // ← リポジトリ名に合わせる
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './'),
    },
  },
});
