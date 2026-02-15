import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'HERCU Manager - 后台管理系统',
  description: 'HERCU 深度认知学习系统管理后台',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh-CN">
      <body className="font-sans antialiased bg-slate-50" style={{ fontFamily: "'Inter', 'Noto Sans SC', 'Poppins', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif" }}>
        {children}
      </body>
    </html>
  )
}
