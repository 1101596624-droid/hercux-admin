/**
 * API 统一导出
 */

export { apiClient } from './client';
export * from './badges';
export * from './users';
export * from './courses';
export * from './training';
export * from './progress';
export * from './ai';
export * from './achievements';
export * from './nodes';

// Re-export API objects for convenience
export { userAPI } from './users';
export { coursesAPI } from './courses';
export { trainingAPI } from './training';
export { progressAPI } from './progress';
export { aiAPI } from './ai';
export { achievementsAPI } from './achievements';

// Studio API
export * from './studio';
export {
  studioApiClient,
  studioPackagesApi,
  studioGenerateApi,
  studioProcessorsApi,
  studioUploadApi,
  studioHealthApi,
} from './studio';
