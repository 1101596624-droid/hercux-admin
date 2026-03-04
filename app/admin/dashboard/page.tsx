'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { coursesAPI, CourseListItem } from '@/lib/api/admin/courses';
import { analyticsAPI, OverviewData, mockOverviewData } from '@/lib/api/admin/analytics';
import { useAdminAuthStore } from '@/stores/admin/useAdminAuthStore';

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

// 统计卡片组件
function StatCard({
  icon,
  iconBg,
  iconColor,
  value,
  label
}: {
  icon: React.ReactNode;
  iconBg: string;
  iconColor: string;
  value: string | number;
  label: string;
}) {
  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-100 shadow-sm">
      <div className="flex items-center gap-4">
        <div className={`w-14 h-14 ${iconBg} rounded-2xl flex items-center justify-center`}>
          <div className={iconColor}>{icon}</div>
        </div>
        <div>
          <div className="text-sm text-slate-500 mb-1">{label}</div>
          <div className="text-3xl font-bold text-slate-900">{value}</div>
        </div>
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

// 课程行组件
function CourseRow({ course, onEdit, onDelete, onTogglePublish, canDelete, canPublish }: {
  course: CourseListItem;
  onEdit: (id: number) => void;
  onDelete: (id: number, name: string) => void;
  onTogglePublish: (id: number, isPublished: boolean, name: string) => void;
  canDelete: boolean;
  canPublish: boolean;
}) {
  return (
    <tr className="border-b border-slate-100 hover:bg-slate-50/50 transition-colors">
      <td className="py-4 px-4">
        <div>
          <div className="font-semibold text-slate-900">{course.name}</div>
          <div className="text-sm text-red-500 font-mono">{course.id ? `CSCS-${String(course.id).padStart(3, '0')}` : '-'}</div>
        </div>
      </td>
      <td className="py-4 px-4">
        <StatusBadge status={course.is_published ? 'published' : 'draft'} />
      </td>
      <td className="py-4 px-4">
        <div>
          <div className="font-semibold text-red-500">{course.total_nodes} 节点</div>
          <div className="text-sm text-slate-500">{course.duration_hours || 0} 小时教研量</div>
        </div>
      </td>
      <td className="py-4 px-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-slate-800 rounded-full flex items-center justify-center text-white text-sm font-medium">
            {course.instructor?.charAt(0) || 'A'}
          </div>
          <span className="text-slate-700">{course.instructor || '未指定'}</span>
        </div>
      </td>
      <td className="py-4 px-4">
        <div className="flex items-center gap-2">
          <button
            onClick={() => onEdit(course.id)}
            className="w-10 h-10 rounded-xl border border-slate-200 flex items-center justify-center hover:bg-slate-100 transition-colors"
            title="编辑课程"
          >
            <svg className="w-5 h-5 text-slate-600" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
            </svg>
          </button>
          {canPublish && (
            <button
              onClick={() => onTogglePublish(course.id, course.is_published, course.name)}
              className={`w-10 h-10 rounded-xl border flex items-center justify-center transition-colors ${
                course.is_published
                  ? 'border-orange-200 hover:bg-orange-50'
                  : 'border-emerald-200 hover:bg-emerald-50'
              }`}
              title={course.is_published ? '下架课程' : '上架课程'}
            >
              {course.is_published ? (
                <svg className="w-5 h-5 text-orange-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                  <line x1="1" y1="1" x2="23" y2="23" />
                </svg>
              ) : (
                <svg className="w-5 h-5 text-emerald-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                  <circle cx="12" cy="12" r="3" />
                </svg>
            )}
          </button>
          )}
          {canDelete && (
            <button
              onClick={() => onDelete(course.id, course.name)}
              className="w-10 h-10 rounded-xl border border-red-200 flex items-center justify-center hover:bg-red-50 transition-colors"
              title="删除课程"
            >
              <svg className="w-5 h-5 text-red-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <polyline points="3 6 5 6 21 6" />
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                <line x1="10" y1="11" x2="10" y2="17" />
                <line x1="14" y1="11" x2="14" y2="17" />
              </svg>
            </button>
          )}
        </div>
      </td>
    </tr>
  );
}

export default function AdminDashboardPage() {
  const router = useRouter();
  const { hasPermission } = useAdminAuthStore();
  const [courses, setCourses] = useState<CourseListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [permissionAlert, setPermissionAlert] = useState<string | null>(null);
  const [stats, setStats] = useState({
    totalCourses: 0,
    publishedCourses: 0,
    totalStudents: 0,
    avgCompletion: 0,
  });
  const [analyticsData, setAnalyticsData] = useState<OverviewData>(mockOverviewData);

  // 权限检查
  const canDeleteCourse = hasPermission('courses.delete');
  const canPublishCourse = hasPermission('courses.publish');

  useEffect(() => {
    loadCourses();
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      const data = await analyticsAPI.getOverview();
      setAnalyticsData(data);
    } catch (error) {
      console.error('Failed to load analytics:', error);
    }
  };

  const loadCourses = async () => {
    try {
      setLoading(true);
      const response = await coursesAPI.getCourses({ page: 1, page_size: 50 });
      setCourses(response.items);

      // 计算统计数据
      const published = response.items.filter(c => c.is_published).length;
      const totalStudents = response.items.reduce((sum, c) => sum + (c.enrolled_users || 0), 0);

      setStats({
        totalCourses: response.total,
        publishedCourses: published,
        totalStudents: totalStudents,
        avgCompletion: 72, // 这个需要从后端获取真实数据
      });
    } catch (error) {
      console.error('Failed to load courses:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = (courseId: number) => {
    router.push(`/admin/editor/${courseId}`);
  };

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

  const handleCreateCourse = () => {
    router.push('/admin/studio');
  };

  const filteredCourses = courses.filter(course =>
    course.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    course.description?.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const pendingCount = courses.filter(c => !c.is_published).length;
  const totalUsers = analyticsData.totalUsers;
  const activeUsers = analyticsData.activeUsers;
  const todayLearningHours = analyticsData.todayLearningHours;
  const activeUserRate = totalUsers > 0 ? ((activeUsers / totalUsers) * 100).toFixed(1) : '0.0';
  const avgLearningMinutes = activeUsers > 0 ? ((todayLearningHours / activeUsers) * 60).toFixed(0) : '0';

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 italic">Workstation.</h1>
          <p className="text-slate-500 mt-1">
            欢迎回来，今日有 <span className="text-red-500 font-medium">{pendingCount}</span> 项教研任务待处理。
          </p>
        </div>
        <button
          onClick={handleCreateCourse}
          className="flex items-center gap-2 px-5 py-3 bg-slate-900 text-white rounded-xl hover:bg-slate-800 transition-colors font-medium"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 5v14M5 12h14" />
          </svg>
          创建课程
        </button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
            </svg>
          }
          iconBg="bg-blue-50"
          iconColor="text-blue-500"
          value={stats.totalCourses}
          label="总课程数"
        />
        <StatCard
          icon={
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
              <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
          }
          iconBg="bg-emerald-50"
          iconColor="text-emerald-500"
          value={stats.publishedCourses}
          label="已发布"
        />
        <StatCard
          icon={
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
          }
          iconBg="bg-amber-50"
          iconColor="text-amber-500"
          value={stats.totalStudents.toLocaleString()}
          label="总学员"
        />
        <StatCard
          icon={
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="12" y1="20" x2="12" y2="10" />
              <line x1="18" y1="20" x2="18" y2="4" />
              <line x1="6" y1="20" x2="6" y2="16" />
            </svg>
          }
          iconBg="bg-rose-50"
          iconColor="text-rose-500"
          value={`${stats.avgCompletion}%`}
          label="平均完成率"
        />
      </div>

      {/* Analytics Quick View */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6 mb-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-50 rounded-xl flex items-center justify-center">
              <svg className="w-5 h-5 text-red-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="20" x2="18" y2="10" />
                <line x1="12" y1="20" x2="12" y2="4" />
                <line x1="6" y1="20" x2="6" y2="14" />
              </svg>
            </div>
            <div>
              <h2 className="text-lg font-semibold text-slate-900">教研数据统计</h2>
              <p className="text-sm text-slate-500">实时监控平台运营数据</p>
            </div>
          </div>
          <Link
            href="/admin/analytics"
            className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-red-500 hover:text-red-600 hover:bg-red-50 rounded-xl transition-colors"
          >
            查看详情
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </Link>
        </div>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-slate-50 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-blue-500" />
              <span className="text-sm text-slate-500">总用户数</span>
            </div>
            <p className="text-2xl font-bold text-slate-900">{analyticsData.totalUsers.toLocaleString()}</p>
            <p className="text-xs text-green-500 mt-1">
              +{analyticsData.newUsersToday} 今日新增
            </p>
          </div>
          <div className="bg-slate-50 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-green-500" />
              <span className="text-sm text-slate-500">活跃用户</span>
            </div>
            <p className="text-2xl font-bold text-slate-900">{analyticsData.activeUsers.toLocaleString()}</p>
            <p className="text-xs text-slate-400 mt-1">
              {activeUserRate}% 活跃率
            </p>
          </div>
          <div className="bg-slate-50 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-amber-500" />
              <span className="text-sm text-slate-500">今日学习时长</span>
            </div>
            <p className="text-2xl font-bold text-slate-900">{analyticsData.todayLearningHours.toLocaleString()}h</p>
            <p className="text-xs text-slate-400 mt-1">
              人均 {avgLearningMinutes} 分钟
            </p>
          </div>
          <div className="bg-slate-50 rounded-xl p-4">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full bg-purple-500" />
              <span className="text-sm text-slate-500">AI 对话次数</span>
            </div>
            <p className="text-2xl font-bold text-slate-900">{analyticsData.aiConversations.toLocaleString()}</p>
            <p className="text-xs text-slate-400 mt-1">
              今日累计
            </p>
          </div>
        </div>

        {/* Quick Links */}
        <div className="flex items-center gap-3 mt-4 pt-4 border-t border-slate-100">
          <Link
            href="/admin/analytics/learning"
            className="flex items-center gap-2 px-3 py-1.5 text-sm text-slate-600 hover:text-red-500 hover:bg-slate-50 rounded-lg transition-colors"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z" />
              <path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 1 3-3h7z" />
            </svg>
            学习行为分析
          </Link>
          <Link
            href="/admin/analytics/retention"
            className="flex items-center gap-2 px-3 py-1.5 text-sm text-slate-600 hover:text-red-500 hover:bg-slate-50 rounded-lg transition-colors"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
            留存分析
          </Link>
          <Link
            href="/admin/ai-monitor"
            className="flex items-center gap-2 px-3 py-1.5 text-sm text-slate-600 hover:text-red-500 hover:bg-slate-50 rounded-lg transition-colors"
          >
            <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 2a10 10 0 1 0 10 10H12V2z" />
              <path d="M12 2a10 10 0 0 1 10 10" />
              <circle cx="12" cy="12" r="6" />
            </svg>
            AI API 监控
          </Link>
        </div>
      </div>

      {/* Course Table */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
        {/* Table Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-100">
          <h2 className="text-lg font-semibold text-slate-900 flex items-center gap-2">
            <span className="text-red-500">课程教研库</span>
          </h2>
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
              placeholder="搜索课程..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10 pr-4 py-2 w-64 border border-slate-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500"
            />
          </div>
        </div>

        {/* Table */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-10 h-10 border-4 border-red-200 border-t-red-500 rounded-full animate-spin"></div>
          </div>
        ) : filteredCourses.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-500">
            <svg className="w-16 h-16 text-slate-300 mb-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" />
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" />
            </svg>
            <p className="text-lg font-medium mb-2">暂无课程</p>
            <p className="text-sm mb-4">点击"创建课程"按钮开始创建您的第一个课程</p>
            <button
              onClick={handleCreateCourse}
              className="flex items-center gap-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors text-sm font-medium"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 5v14M5 12h14" />
              </svg>
              创建课程
            </button>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-100 text-left">
                <th className="py-3 px-4 text-sm font-medium text-slate-500">课程标识/名称</th>
                <th className="py-3 px-4 text-sm font-medium text-slate-500">教研状态</th>
                <th className="py-3 px-4 text-sm font-medium text-slate-500">节点/时长</th>
                <th className="py-3 px-4 text-sm font-medium text-slate-500">负责人</th>
                <th className="py-3 px-4 text-sm font-medium text-slate-500">管理</th>
              </tr>
            </thead>
            <tbody>
              {filteredCourses.map((course) => (
                <CourseRow
                  key={course.id}
                  course={course}
                  onEdit={handleEdit}
                  onDelete={handleDelete}
                  onTogglePublish={handleTogglePublish}
                  canDelete={canDeleteCourse}
                  canPublish={canPublishCourse}
                />
              ))}
            </tbody>
          </table>
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
