/**
 * Simulator Icon Library API
 * 模拟器图标库 API - 供两个应用调用
 */

import { apiClient } from './admin/client';

// ============================================
// Types
// ============================================

export interface SimulatorIcon {
  id: string;
  name: string;
  name_en?: string;
  category: string;
  description?: string;
  keywords?: string[];
  default_color: string;
  default_scale: number;
  recommended_scenes?: string[];
  is_active: number;
  sort_order: number;
  usage_count: number;
}

export interface IconCategory {
  id: string;
  name: string;
  name_en: string;
  count: number;
}

export interface IconPreset {
  id: string;
  name: string;
  name_en?: string;
  description?: string;
  icons: Array<{
    id: string;
    x: number;
    y: number;
    scale?: number;
    tint?: string;
    rotation?: number;
  }>;
  canvas_config?: {
    width: number;
    height: number;
    background?: any;
  };
  category?: string;
  tags?: string[];
  is_official: number;
  is_active: number;
  usage_count: number;
}

export interface IconCreateData {
  id: string;
  name: string;
  name_en?: string;
  category: string;
  description?: string;
  keywords?: string[];
  default_color?: string;
  default_scale?: number;
  recommended_scenes?: string[];
}

export interface IconPresetCreateData {
  id: string;
  name: string;
  name_en?: string;
  description?: string;
  icons: Array<{
    id: string;
    x: number;
    y: number;
    scale?: number;
    tint?: string;
    rotation?: number;
  }>;
  canvas_config?: {
    width: number;
    height: number;
    background?: any;
  };
  category?: string;
  tags?: string[];
}

// ============================================
// Icon API
// ============================================

/**
 * 获取图标列表
 */
export async function getIcons(params?: {
  category?: string;
  search?: string;
  limit?: number;
  offset?: number;
}): Promise<SimulatorIcon[]> {
  const { data } = await apiClient.get<SimulatorIcon[]>('/icon-library/icons', { params });
  return data;
}

/**
 * 获取图标分类列表
 */
export async function getIconCategories(): Promise<IconCategory[]> {
  const { data } = await apiClient.get<IconCategory[]>('/icon-library/icons/categories');
  return data;
}

/**
 * 获取单个图标
 */
export async function getIcon(iconId: string): Promise<SimulatorIcon> {
  const { data } = await apiClient.get<SimulatorIcon>(`/icon-library/icons/${iconId}`);
  return data;
}

/**
 * 创建图标
 */
export async function createIcon(iconData: IconCreateData): Promise<SimulatorIcon> {
  const { data } = await apiClient.post<SimulatorIcon>('/icon-library/icons', iconData);
  return data;
}

/**
 * 批量创建图标
 */
export async function bulkCreateIcons(icons: IconCreateData[]): Promise<{
  created: number;
  skipped: number;
  total: number;
}> {
  const { data } = await apiClient.post('/icon-library/icons/bulk', { icons });
  return data;
}

/**
 * 更新图标
 */
export async function updateIcon(iconId: string, iconData: IconCreateData): Promise<SimulatorIcon> {
  const { data } = await apiClient.put<SimulatorIcon>(`/icon-library/icons/${iconId}`, iconData);
  return data;
}

/**
 * 删除图标
 */
export async function deleteIcon(iconId: string): Promise<{ message: string }> {
  const { data } = await apiClient.delete<{ message: string }>(`/icon-library/icons/${iconId}`);
  return data;
}

/**
 * 获取所有图标ID列表（轻量级）
 */
export async function getAllIconIds(): Promise<Array<{ id: string; name: string; category: string }>> {
  const { data } = await apiClient.get<Array<{ id: string; name: string; category: string }>>('/icon-library/icons/all/list');
  return data;
}

/**
 * 增加图标使用次数
 */
export async function incrementIconUsage(iconId: string): Promise<{ message: string }> {
  const { data } = await apiClient.post<{ message: string }>(`/icon-library/icons/${iconId}/usage`);
  return data;
}

// ============================================
// Preset API
// ============================================

/**
 * 获取预设列表
 */
export async function getPresets(params?: {
  category?: string;
  official_only?: boolean;
  limit?: number;
  offset?: number;
}): Promise<IconPreset[]> {
  const { data } = await apiClient.get<IconPreset[]>('/icon-library/presets', { params });
  return data;
}

/**
 * 获取单个预设
 */
export async function getPreset(presetId: string): Promise<IconPreset> {
  const { data } = await apiClient.get<IconPreset>(`/icon-library/presets/${presetId}`);
  return data;
}

/**
 * 创建预设
 */
export async function createPreset(presetData: IconPresetCreateData): Promise<IconPreset> {
  const { data } = await apiClient.post<IconPreset>('/icon-library/presets', presetData);
  return data;
}

/**
 * 更新预设
 */
export async function updatePreset(presetId: string, presetData: IconPresetCreateData): Promise<IconPreset> {
  const { data } = await apiClient.put<IconPreset>(`/icon-library/presets/${presetId}`, presetData);
  return data;
}

/**
 * 删除预设
 */
export async function deletePreset(presetId: string): Promise<{ message: string }> {
  const { data } = await apiClient.delete<{ message: string }>(`/icon-library/presets/${presetId}`);
  return data;
}

/**
 * 增加预设使用次数
 */
export async function incrementPresetUsage(presetId: string): Promise<{ message: string }> {
  const { data } = await apiClient.post<{ message: string }>(`/icon-library/presets/${presetId}/usage`);
  return data;
}

// ============================================
// Export all
// ============================================

export const iconLibraryApi = {
  // Icons
  getIcons,
  getIconCategories,
  getIcon,
  createIcon,
  bulkCreateIcons,
  updateIcon,
  deleteIcon,
  getAllIconIds,
  incrementIconUsage,
  // Presets
  getPresets,
  getPreset,
  createPreset,
  updatePreset,
  deletePreset,
  incrementPresetUsage,
};

export default iconLibraryApi;
