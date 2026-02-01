/** @type {import('next').NextConfig} */
const nextConfig = {
  // 使用 standalone 输出模式，生成独立的服务器
  output: 'standalone',

  // 跳过类型检查（打包时）
  typescript: {
    ignoreBuildErrors: true,
  },

  // 跳过 ESLint 检查（打包时）
  eslint: {
    ignoreDuringBuilds: true,
  },

  // 性能优化配置

  // 1. 编译器优化
  compiler: {
    // 移除 console.log (生产环境)
    removeConsole: process.env.NODE_ENV === 'production' ? {
      exclude: ['error', 'warn'],
    } : false,
  },

  // 2. 实验性功能
  experimental: {
    // 优化包导入
    optimizePackageImports: [
      '@/components/ui',
      '@/components/courses',
      '@/components/workstation',
      '@/components/dashboard',
      '@/components/profile',
      '@/components/training',
      '@/components/admin',
    ],
  },

  // 3. Webpack 配置优化
  webpack: (config, { dev, isServer }) => {
    // 生产环境优化
    if (!dev && !isServer) {
      // 代码分割优化
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            // 将 React 相关库打包在一起
            react: {
              test: /[\\/]node_modules[\\/](react|react-dom|scheduler)[\\/]/,
              name: 'react-vendor',
              priority: 40,
            },
            // Zustand 状态管理
            zustand: {
              test: /[\\/]node_modules[\\/]zustand[\\/]/,
              name: 'zustand',
              priority: 35,
            },
            // UI 组件库
            ui: {
              test: /[\\/]components[\\/]ui[\\/]/,
              name: 'ui-components',
              priority: 30,
            },
            // 其他 node_modules
            defaultVendors: {
              test: /[\\/]node_modules[\\/]/,
              name: 'vendors',
              priority: 20,
            },
            // 通用组件
            commons: {
              minChunks: 2,
              priority: 10,
              reuseExistingChunk: true,
            },
          },
        },
      };
    }

    return config;
  },

  // 4. 图片优化
  images: {
    unoptimized: true,
    formats: ['image/avif', 'image/webp'],
    deviceSizes: [640, 750, 828, 1080, 1200, 1920, 2048, 3840],
    imageSizes: [16, 32, 48, 64, 96, 128, 256, 384],
    minimumCacheTTL: 60,
  },

  // 5. 压缩
  compress: true,

  // 6. 生产环境优化
  productionBrowserSourceMaps: false,

  // 7. 输出优化
  poweredByHeader: false,
  generateEtags: true,

  // 8. SWC 压缩
  swcMinify: true,
};

module.exports = nextConfig;
