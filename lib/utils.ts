import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

/**
 * API 服务器基础 URL
 */
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://106.14.180.66:8001';

/**
 * Merge class names with Tailwind CSS support
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

/**
 * 获取服务器基础 URL（不含 /api 后缀）
 */
function getServerBaseUrl(): string {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://106.14.180.66:8001';
  // 移除 /api 或 /api/v1 后缀，获取纯服务器地址
  return apiUrl.replace(/\/api(\/v\d+)?$/, '');
}

/**
 * 获取完整的媒体文件 URL
 * 将相对路径转换为完整的服务器 URL
 *
 * 后端返回的 URL 格式：/upload/{category}/{filename}
 * 静态文件挂载路径：/upload -> uploads 目录
 *
 * @param url - 媒体文件 URL（可能是相对路径或完整 URL）
 * @returns 完整的 URL
 */
export function getMediaUrl(url: string | undefined | null): string {
  if (!url) return '';

  // 如果已经是完整 URL，直接返回
  if (url.startsWith('http://') || url.startsWith('https://') || url.startsWith('data:')) {
    return url;
  }

  const serverBaseUrl = getServerBaseUrl();

  // 移除开头的斜杠
  const cleanPath = url.startsWith('/') ? url.slice(1) : url;

  // 如果是旧的 media 路径格式，转换为 upload 路径
  // /media/diagrams/xxx.jpg -> /upload/diagrams/xxx.jpg
  if (cleanPath.startsWith('media/')) {
    const pathWithoutMedia = cleanPath.replace('media/', '');
    return `${serverBaseUrl}/upload/${pathWithoutMedia}`;
  }

  // 直接拼接服务器基础 URL
  return `${serverBaseUrl}/${cleanPath}`;
}

/**
 * Format duration in minutes to human-readable string
 * @param minutes - Duration in minutes
 * @returns Formatted string (e.g., "1h 30min")
 */
export function formatDuration(minutes: number): string {
  if (minutes < 60) {
    return `${minutes}分钟`
  }
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return mins > 0 ? `${hours}小时${mins}分钟` : `${hours}小时`
}

/**
 * Format number with thousands separator
 * @param num - Number to format
 * @returns Formatted string (e.g., "1,234")
 */
export function formatNumber(num: number): string {
  return num.toLocaleString('zh-CN')
}

/**
 * Calculate progress percentage
 * @param completed - Completed items
 * @param total - Total items
 * @returns Progress percentage (0-100)
 */
export function calculateProgress(completed: number, total: number): number {
  if (total === 0) return 0
  return Math.round((completed / total) * 100)
}

/**
 * Truncate text to specified length
 * @param text - Text to truncate
 * @param length - Maximum length
 * @returns Truncated text with ellipsis
 */
export function truncate(text: string, length: number): string {
  if (text.length <= length) return text
  return text.slice(0, length) + '...'
}
