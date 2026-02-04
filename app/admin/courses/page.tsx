'use client';

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import {
  coursesAPI,
  type CourseListItem,
  type CourseFilters
} from '@/lib/api/admin/courses';
import { useAdminAuthStore } from '@/stores/admin/useAdminAuthStore';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

// 权限不足弹窗
function PermissionDeniedAlert({ message, onClose }: { message: string; onClose: () => void }) {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl w-[400px] shadow-2xl p-6">
        <div className="flex items-center justify-center w-16 h-16 mx-auto mb-4 bg-red-100 rounded-full">
          <svg className="w-8 h-8 text-red-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <line x1="12" y1="8" x2="12" y2="12" />
            <line x1="12" y1="16" x2="12.01" y2="16" />
          </svg>
        </div>
        <h3 className="text-xl font-bold text-slate-900 text-center mb-2">权限不足</h3>
        <p className="text-slate-500 text-center mb-6">{message}</p>
        <button
          onClick={onClose}
          className="w-full px-4 py-3 text-sm font-medium text-white bg-red-500 rounded-xl hover:bg-red-600 transition-colors"
        >
          我知道了
        </button>
      </div>
    </div>
  );
}

// 状态徽章组件
function StatusBadge({ status }: { status: string }) {
  const statusConfig: Record<string, { bg: string; text: string; label: string }> = {
    published: { bg: 'bg-emerald-50', text: 'text-emerald-600', label: '已发布' },
    draft: { bg: 'bg-slate-100', text: 'text-slate-600', label: '草稿' },
    pending: { bg: 'bg-orange-50', text: 'text-orange-600', label: '待审阅' },
  };

  const config = statusConfig[status] || statusConfig.draft;

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
      {config.label}
    </span>
  );
}

// 难度徽章
function DifficultyBadge({ difficulty }: { difficulty: string }) {
  const config: Record<string, { bg: string; text: string; label: string }> = {
    beginner: { bg: 'bg-green-50', text: 'text-green-600', label: '初级' },
    intermediate: { bg: 'bg-blue-50', text: 'text-blue-600', label: '中级' },
    advanced: { bg: 'bg-orange-50', text: 'text-orange-600', label: '高级' },
    expert: { bg: 'bg-red-50', text: 'text-red-600', label: '专家' },
  };

  const c = config[difficulty] || { bg: 'bg-slate-100', text: 'text-slate-600', label: difficulty };

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${c.bg} ${c.text}`}>
      {c.label}
    </span>
  );
}

export default function AdminCoursesPage() {
  const router = useRouter();
  const { hasPermission } = useAdminAuthStore();
  const [courses, setCourses] = useState<CourseListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [importing, setImporting] = useState(false);
  const [permissionAlert, setPermissionAlert] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 权限检查
  const canDeleteCourse = hasPermission('courses.delete');
  const canPublishCourse = hasPermission('courses.publish');

  // Filters
  const [search, setSearch] = useState('');
  const [difficulty, setDifficulty] = useState<string>('');
  const [publishedFilter, setPublishedFilter] = useState<string>('');

  // Load courses
  const loadCourses = async () => {
    setLoading(true);
    try {
      const filters: CourseFilters = {
        page: currentPage,
        page_size: 20,
        sort_by: 'created_at',
        sort_order: 'desc'
      };

      if (search) filters.search = search;
      if (difficulty) filters.difficulty = difficulty as any;
      if (publishedFilter !== '') filters.is_published = publishedFilter === 'true';

      const response = await coursesAPI.getCourses(filters);
      setCourses(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (error) {
      console.error('Failed to load courses:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCourses();
  }, [currentPage]);

  // Handle search
  const handleSearch = () => {
    setCurrentPage(1);
    loadCourses();
  };

  // Handle delete
  const handleDelete = async (courseId: number, courseName: string) => {
    if (!canDeleteCourse) {
      setPermissionAlert('您没有删除课程的权限');
      return;
    }

    if (!confirm(`确定要删除课程 "${courseName}" 吗？此操作不可撤销。`)) {
      return;
    }

    try {
      await coursesAPI.deleteCourse(courseId);
      loadCourses();
    } catch (error) {
      console.error('Failed to delete course:', error);
      alert('删除失败，请重试');
    }
  };

  // Handle import JSON file
  const handleImportClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.json')) {
      alert('只支持 JSON 文件');
      return;
    }

    setImporting(true);
    try {
      const formData = new FormData();
      formData.append('file', file);

      const token = localStorage.getItem('auth_token');
      const response = await fetch(`${API_BASE_URL}/internal/import-package-file`, {
        method: 'POST',
        headers: token ? { 'Authorization': `Bearer ${token}` } : {},
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || '导入失败');
      }

      const result = await response.json();
      alert(`导入成功！创建了 ${result.nodes_created} 个节点`);
      loadCourses();
    } catch (error) {
      console.error('Failed to import course:', error);
      alert(error instanceof Error ? error.message : '导入失败，请重试');
    } finally {
      setImporting(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  // Handle edit - 跳转到课程编辑器
  const handleEdit = (courseId: number) => {
    router.push(`/admin/editor/${courseId}`);
  };

  // Handle publish/unpublish toggle
  const handleTogglePublish = async (courseId: number, currentlyPublished: boolean, courseName: string) => {
    if (!canPublishCourse) {
      setPermissionAlert('您没有上架/下架课程的权限');
      return;
    }

    const action = currentlyPublished ? '下架' : '上架';
    if (!confirm(`确定要${action}课程 "${courseName}" 吗？`)) {
      return;
    }

    try {
      await coursesAPI.publishCourse(courseId, !currentlyPublished);
      loadCourses();
    } catch (error) {
      console.error(`Failed to ${action} course:`, error);
      alert(`${action}失败，请重试`);
    }
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileChange}
        accept=".json"
        className="hidden"
      />

      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 italic">Content Editor.</h1>
          <p className="text-slate-500 mt-1">
            选择课程进入内容编辑器，管理课程节点和教学内容。
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleImportClick}
            disabled={importing}
            className="flex items-center gap-2 px-5 py-3 bg-white border border-slate-200 text-slate-700 rounded-xl hover:bg-slate-50 transition-colors font-medium disabled:opacity-50"
          >
            {importing ? (
              <div className="w-5 h-5 border-2 border-slate-300 border-t-slate-600 rounded-full animate-spin"></div>
            ) : (
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                <polyline points="17 8 12 3 7 8" />
                <line x1="12" y1="3" x2="12" y2="15" />
              </svg>
            )}
            {importing ? '导入中...' : '导入课程'}
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6 mb-6">
        <div className="flex flex-wrap items-end gap-4">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-slate-700 mb-2">搜索课程</label>
            <div className="relative">
              <svg
                className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.35-4.35" />
              </svg>
              <input
                type="text"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                placeholder="课程名称或描述..."
                className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500"
              />
            </div>
          </div>

          <div className="w-40">
            <label className="block text-sm font-medium text-slate-700 mb-2">难度</label>
            <select
              value={difficulty}
              onChange={(e) => setDifficulty(e.target.value)}
              className="w-full px-3 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 bg-white"
            >
              <option value="">全部</option>
              <option value="beginner">初级</option>
              <option value="intermediate">中级</option>
              <option value="advanced">高级</option>
              <option value="expert">专家</option>
            </select>
          </div>

          <div className="w-40">
            <label className="block text-sm font-medium text-slate-700 mb-2">状态</label>
            <select
              value={publishedFilter}
              onChange={(e) => setPublishedFilter(e.target.value)}
              className="w-full px-3 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 bg-white"
            >
              <option value="">全部</option>
              <option value="true">已发布</option>
              <option value="false">未发布</option>
            </select>
          </div>

          <button
            onClick={handleSearch}
            className="px-5 py-2.5 bg-red-500 text-white rounded-xl hover:bg-red-600 transition-colors font-medium"
          >
            筛选
          </button>
        </div>
      </div>

      {/* Course Grid */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-10 h-10 border-4 border-red-200 border-t-red-500 rounded-full animate-spin"></div>
          </div>
        ) : courses.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-500">
            <svg className="w-16 h-16 text-slate-300 mb-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
            </svg>
            <p className="text-lg font-medium mb-2">暂无课程</p>
            <p className="text-sm mb-4">使用 AI Studio 创建您的第一个课程</p>
            <button
              onClick={() => router.push('/admin/studio')}
              className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-sm font-medium"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 5v14M5 12h14" />
              </svg>
              创建课程
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 p-6">
            {courses.map((course) => (
              <div
                key={course.id}
                className={`bg-slate-50 rounded-xl overflow-hidden transition-all border border-transparent ${
                  !course.is_published
                    ? 'hover:shadow-md cursor-pointer group hover:border-red-200'
                    : 'opacity-80'
                }`}
                onClick={() => !course.is_published && handleEdit(course.id)}
              >
                {/* Course Thumbnail */}
                <div className="aspect-video bg-gradient-to-br from-slate-200 to-slate-300 relative overflow-hidden">
                  {course.thumbnail_url ? (
                    <img
                      src={course.thumbnail_url}
                      alt={course.name}
                      className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <svg className="w-12 h-12 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                      </svg>
                    </div>
                  )}
                  {/* Status Badge on Thumbnail */}
                  <div className="absolute top-2 left-2">
                    <StatusBadge status={course.is_published ? 'published' : 'draft'} />
                  </div>
                </div>

                <div className="p-4">
                {/* Course Header */}
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h3 className="font-semibold text-slate-900 group-hover:text-red-500 transition-colors line-clamp-1">
                      {course.name}
                    </h3>
                    <p className="text-xs text-red-500 font-mono">
                      CSCS-{String(course.id).padStart(3, '0')}
                    </p>
                  </div>
                  {canDeleteCourse && (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(course.id, course.name);
                      }}
                      className="px-2 py-1 text-xs font-medium text-red-600 bg-red-50 hover:bg-red-100 rounded-lg transition-colors flex items-center gap-1"
                    >
                      <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <polyline points="3 6 5 6 21 6" />
                        <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                      </svg>
                    </button>
                  )}
                </div>

                {/* Description */}
                <p className="text-sm text-slate-500 line-clamp-2 mb-3 min-h-[40px]">
                  {course.description || '暂无描述'}
                </p>

                {/* Stats */}
                <div className="flex items-center gap-3 text-xs text-slate-600 mb-3">
                  <div className="flex items-center gap-1">
                    <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="3" y="3" width="18" height="18" rx="2" />
                      <path d="M3 9h18" />
                      <path d="M9 21V9" />
                    </svg>
                    <span>{course.total_nodes}节</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <circle cx="12" cy="12" r="10" />
                      <polyline points="12 6 12 12 16 14" />
                    </svg>
                    <span>{course.duration_hours || 0}h</span>
                  </div>
                  <div className="flex items-center gap-1">
                    <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
                      <circle cx="9" cy="7" r="4" />
                    </svg>
                    <span>{course.enrolled_users}</span>
                  </div>
                </div>

                {/* Footer */}
                <div className="flex items-center justify-between pt-3 border-t border-slate-200">
                  <div className="flex items-center gap-1.5 flex-wrap">
                    <DifficultyBadge difficulty={course.difficulty} />
                    {/* 显示标签（最多2个） */}
                    {course.tags && (Array.isArray(course.tags) ? course.tags : (typeof course.tags === 'string' ? JSON.parse(course.tags) : [])).slice(0, 2).map((tag: string, idx: number) => (
                      <span
                        key={idx}
                        className="inline-flex items-center px-1.5 py-0.5 rounded text-xs font-medium bg-purple-50 text-purple-600"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                  <div className="flex items-center gap-1.5">
                    {/* 只有下架状态的课程可以编辑 */}
                    {!course.is_published ? (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleEdit(course.id);
                        }}
                        className="px-2 py-1 text-xs font-medium text-slate-600 bg-slate-100 hover:bg-slate-200 rounded-lg transition-colors"
                      >
                        编辑
                      </button>
                    ) : (
                      <span className="px-2 py-1 text-xs font-medium text-slate-400 bg-slate-50 rounded-lg">
                        已锁定
                      </span>
                    )}
                    {canPublishCourse && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleTogglePublish(course.id, course.is_published, course.name);
                        }}
                        className={`px-2 py-1 text-xs font-medium rounded-lg transition-colors ${
                          course.is_published
                            ? 'text-orange-600 bg-orange-50 hover:bg-orange-100'
                            : 'text-emerald-600 bg-emerald-50 hover:bg-emerald-100'
                        }`}
                      >
                        {course.is_published ? '下架' : '上架'}
                      </button>
                    )}
                  </div>
                </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-slate-100 flex items-center justify-between">
            <div className="text-sm text-slate-500">
              共 {total} 个课程，第 {currentPage} / {totalPages} 页
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 border border-slate-200 rounded-xl hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                上一页
              </button>
              <button
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="px-4 py-2 border border-slate-200 rounded-xl hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                下一页
              </button>
            </div>
          </div>
        )}
      </div>

      {/* 权限不足提示 */}
      {permissionAlert && (
        <PermissionDeniedAlert
          message={permissionAlert}
          onClose={() => setPermissionAlert(null)}
        />
      )}
    </div>
  );
}
