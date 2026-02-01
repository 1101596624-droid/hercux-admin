/**
 * SDL 场景模板库
 * 前端版本 - 通过后端 API 获取模板
 */

import type { SDLScene } from '@/types/editor';

// 本地缓存
const templateCache: Record<string, SDLScene> = {};

// Studio API base URL
const getStudioApiUrl = () => {
  return process.env.NEXT_PUBLIC_STUDIO_API_URL || 'http://localhost:8001';
};

/**
 * 获取模板 - 从后端 API 获取并缓存
 */
export async function getTemplate(templateId: string): Promise<SDLScene | null> {
  // 先检查本地缓存
  if (templateCache[templateId]) {
    return templateCache[templateId];
  }

  // 从后端 API 获取
  try {
    const response = await fetch(`${getStudioApiUrl()}/api/v1/studio/templates/${templateId}`);
    if (response.ok) {
      const template = await response.json();
      // 缓存到本地
      templateCache[templateId] = template;
      return template;
    } else {
      console.error(`Template ${templateId} not found: ${response.status}`);
    }
  } catch (error) {
    console.error(`Failed to fetch template ${templateId}:`, error);
  }

  return null;
}

/**
 * 获取所有模板列表
 */
export async function getTemplateList(): Promise<Array<{id: string; name: string; description: string; category: string}>> {
  try {
    const response = await fetch(`${getStudioApiUrl()}/api/v1/studio/templates`);
    if (response.ok) {
      const data = await response.json();
      return data.templates || [];
    }
  } catch (error) {
    console.error('Failed to fetch template list:', error);
  }
  return [];
}

/**
 * 按分类获取模板列表
 */
export async function getTemplatesByCategory(category: string): Promise<Array<{id: string; name: string; description: string; category: string}>> {
  const templates = await getTemplateList();
  return templates.filter(t => t.category === category);
}

/**
 * 预加载模板到缓存
 */
export async function preloadTemplate(templateId: string): Promise<void> {
  await getTemplate(templateId);
}

/**
 * 清除模板缓存
 */
export function clearTemplateCache(): void {
  Object.keys(templateCache).forEach(key => delete templateCache[key]);
}

export default {
  getTemplate,
  getTemplateList,
  getTemplatesByCategory,
  preloadTemplate,
  clearTemplateCache,
};
