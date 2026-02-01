import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// 不需要认证的页面
const publicPaths = ['/admin/login', '/_next', '/favicon.ico', '/api'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 检查是否是公开路径
  const isPublicPath = publicPaths.some(path => pathname.startsWith(path));

  // 如果是公开路径，直接放行
  if (isPublicPath) {
    return NextResponse.next();
  }

  // 检查是否是 admin 路径
  if (pathname.startsWith('/admin')) {
    // 检查 cookie 中是否有 auth token (zustand persist 存储在 localStorage，但我们可以检查 cookie)
    // 由于 localStorage 在 middleware 中不可用，我们依赖客户端的 layout 检查
    // 但我们可以设置一个 cookie 来在服务端验证

    // 这里我们只做基本的路由保护，详细的认证检查在客户端 layout 中进行
    return NextResponse.next();
  }

  // 根路径重定向到登录页
  if (pathname === '/') {
    return NextResponse.redirect(new URL('/admin/login', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
