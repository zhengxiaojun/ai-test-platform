import { defineConfig } from 'umi';

export default defineConfig({
  routes: [
    {
      path: '/',
      component: '@/pages/Home',
    },
    {
      path: '/interface',
      component: '@/pages/Interface',
    },
    {
      path: '/testcase',
      component: '@/pages/TestCase',
    },
    {
      path: '/execution',
      component: '@/pages/Execution',
    },
    {
      path: '/report',
      component: '@/pages/Report',
    },
  ],
  npmClient: 'npm',
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
  title: 'AI Test Platform',
  // 使用 antd 插件
  plugins: ['@umijs/plugins/dist/antd'],
  antd: {},
});

