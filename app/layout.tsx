import type { Metadata } from 'next'
import { Inter, Noto_Sans_SC, Poppins } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter' })
const notoSansSC = Noto_Sans_SC({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-noto-sans-sc'
})
const poppins = Poppins({
  subsets: ['latin'],
  weight: ['400', '600', '700'],
  style: ['normal', 'italic'],
  variable: '--font-poppins'
})

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
      <body className={`${inter.variable} ${notoSansSC.variable} ${poppins.variable} font-sans antialiased bg-slate-50`}>
        {children}
      </body>
    </html>
  )
}
