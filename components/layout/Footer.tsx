'use client';

import Link from 'next/link';

export function Footer() {
  const currentYear = new Date().getFullYear();

  const footerLinks = {
    product: [
      { label: '课程中心', href: '/courses' },
      { label: 'AI 训练计划', href: '/training' },
      { label: '学习路径', href: '/dashboard' },
      { label: '成就系统', href: '/profile' },
    ],
    resources: [
      { label: '帮助中心', href: '/help' },
      { label: '使用指南', href: '/guide' },
      { label: 'API 文档', href: '/docs' },
      { label: '开发者', href: '/developers' },
    ],
    company: [
      { label: '关于我们', href: '/about' },
      { label: '联系我们', href: '/contact' },
      { label: '加入我们', href: '/careers' },
      { label: '博客', href: '/blog' },
    ],
    legal: [
      { label: '服务条款', href: '/terms' },
      { label: '隐私政策', href: '/privacy' },
      { label: 'Cookie 政策', href: '/cookies' },
      { label: '许可协议', href: '/license' },
    ],
  };

  const socialLinks = [
    { name: 'GitHub', icon: '💻', href: 'https://github.com' },
    { name: 'Twitter', icon: '🐦', href: 'https://twitter.com' },
    { name: 'WeChat', icon: '💬', href: '#' },
    { name: 'Weibo', icon: '📱', href: '#' },
  ];

  return (
    <footer className="bg-dark-900 text-dark-100 mt-auto">
      <div className="container mx-auto px-6 py-12">
        {/* Main Footer Content */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-8 mb-8">
          {/* Brand */}
          <div className="lg:col-span-1">
            <div className="flex items-center gap-3 mb-4">
              <div className="text-3xl">🏋️</div>
              <div className="flex flex-col">
                <span className="text-xl font-bold text-white">HERCU</span>
                <span className="text-xs text-dark-400">运动科学学习</span>
              </div>
            </div>
            <p className="text-sm text-dark-400 mb-4">
              通过 AI 驱动的个性化学习，掌握运动科学核心知识，成就更好的自己。
            </p>
            <div className="flex items-center gap-3">
              {socialLinks.map((social) => (
                <a
                  key={social.name}
                  href={social.href}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="w-10 h-10 rounded-lg bg-dark-800 hover:bg-dark-700 flex items-center justify-center text-lg transition-colors"
                  title={social.name}
                >
                  {social.icon}
                </a>
              ))}
            </div>
          </div>

          {/* Links Sections */}
          <div>
            <h3 className="text-white font-semibold mb-4">产品</h3>
            <ul className="space-y-2">
              {footerLinks.product.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-dark-400 hover:text-white transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-white font-semibold mb-4">资源</h3>
            <ul className="space-y-2">
              {footerLinks.resources.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-dark-400 hover:text-white transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-white font-semibold mb-4">公司</h3>
            <ul className="space-y-2">
              {footerLinks.company.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-dark-400 hover:text-white transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="text-white font-semibold mb-4">法律</h3>
            <ul className="space-y-2">
              {footerLinks.legal.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="text-sm text-dark-400 hover:text-white transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="pt-8 border-t border-dark-800">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-dark-400">
              © {currentYear} HERCU. All rights reserved.
            </p>
            <div className="flex items-center gap-6 text-sm text-dark-400">
              <span>由 ❤️ 和 ☕ 打造</span>
              <span>•</span>
              <span>Made with Next.js & Tailwind CSS</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
