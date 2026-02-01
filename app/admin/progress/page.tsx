'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  getProgress,
  deleteProgress,
  updateProgress,
  type ProgressListItem,
  type ProgressFilters
} from '@/lib/api/admin/progress';

export default function AdminProgressPage() {
  const router = useRouter();
  const [progress, setProgress] = useState<ProgressListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Filters
  const [userIdFilter, setUserIdFilter] = useState('');
  const [courseIdFilter, setCourseIdFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [sortBy, setSortBy] = useState<'last_accessed' | 'created_at' | 'completion_percentage'>('last_accessed');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Load progress
  const loadProgress = async () => {
    setLoading(true);
    try {
      const filters: ProgressFilters = {
        page: currentPage,
        page_size: 20,
        sort_by: sortBy,
        sort_order: sortOrder
      };

      if (userIdFilter) filters.user_id = parseInt(userIdFilter);
      if (courseIdFilter) filters.course_id = parseInt(courseIdFilter);
      if (statusFilter) filters.status = statusFilter as any;

      const response = await getProgress(filters);
      setProgress(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (error) {
      console.error('Failed to load progress:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProgress();
  }, [currentPage, sortBy, sortOrder]);

  // Handle search
  const handleSearch = () => {
    setCurrentPage(1);
    loadProgress();
  };

  // Handle delete
  const handleDelete = async (progressId: number, nodeTitle: string) => {
    if (!confirm(`确定要删除进度记录 "${nodeTitle}" 吗？此操作不可撤销。`)) {
      return;
    }

    try {
      await deleteProgress(progressId);
      loadProgress();
    } catch (error) {
      console.error('Failed to delete progress:', error);
      alert('删除失败，请重试');
    }
  };

  // Handle status update
  const handleUpdateStatus = async (progressId: number, newStatus: string) => {
    try {
      await updateProgress(progressId, { status: newStatus as any });
      loadProgress();
    } catch (error) {
      console.error('Failed to update status:', error);
      alert('更新失败，请重试');
    }
  };

  // Status badge color
  const getStatusColor = (status: string) => {
    const colors = {
      locked: 'bg-gray-100 text-gray-800',
      unlocked: 'bg-blue-100 text-blue-800',
      in_progress: 'bg-yellow-100 text-yellow-800',
      completed: 'bg-green-100 text-green-800'
    };
    return colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  // Status label
  const getStatusLabel = (status: string) => {
    const labels = {
      locked: '锁定',
      unlocked: '已解锁',
      in_progress: '进行中',
      completed: '已完成'
    };
    return labels[status as keyof typeof labels] || status;
  };

  // Node type label
  const getNodeTypeLabel = (type: string) => {
    const labels = {
      video: '视频',
      simulator: '模拟器',
      quiz: '测验',
      reading: '阅读',
      practice: '练习'
    };
    return labels[type as keyof typeof labels] || type;
  };

  // Format date
  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('zh-CN');
  };

  // Format time
  const formatTime = (hours: number) => {
    if (hours < 1) return `${Math.round(hours * 60)}分钟`;
    return `${hours.toFixed(1)}小时`;
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">学习进度管理</h1>
          <p className="mt-2 text-slate-600">管理所有用户的学习进度</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">用户ID</label>
            <input
              type="number"
              value={userIdFilter}
              onChange={(e) => setUserIdFilter(e.target.value)}
              placeholder="输入用户ID"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">课程ID</label>
            <input
              type="number"
              value={courseIdFilter}
              onChange={(e) => setCourseIdFilter(e.target.value)}
              placeholder="输入课程ID"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">状态</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">全部</option>
              <option value="locked">锁定</option>
              <option value="unlocked">已解锁</option>
              <option value="in_progress">进行中</option>
              <option value="completed">已完成</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">排序</label>
            <select
              value={`${sortBy}-${sortOrder}`}
              onChange={(e) => {
                const [field, order] = e.target.value.split('-');
                setSortBy(field as any);
                setSortOrder(order as any);
              }}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="last_accessed-desc">最近访问</option>
              <option value="last_accessed-asc">最早访问</option>
              <option value="created_at-desc">最新创建</option>
              <option value="created_at-asc">最早创建</option>
              <option value="completion_percentage-desc">完成度高</option>
              <option value="completion_percentage-asc">完成度低</option>
            </select>
          </div>
        </div>

        <button
          onClick={handleSearch}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          应用筛选
        </button>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">总进度记录</p>
          <p className="mt-2 text-3xl font-bold text-slate-900">{total}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">已完成</p>
          <p className="mt-2 text-3xl font-bold text-green-600">
            {progress.filter((p) => p.status === 'completed').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">进行中</p>
          <p className="mt-2 text-3xl font-bold text-yellow-600">
            {progress.filter((p) => p.status === 'in_progress').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">总学习时长</p>
          <p className="mt-2 text-3xl font-bold text-blue-600">
            {progress.reduce((sum, p) => sum + p.time_spent_hours, 0).toFixed(0)}h
          </p>
        </div>
      </div>

      {/* Progress List */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200">
        {loading ? (
          <div className="p-12 text-center text-slate-600">加载中...</div>
        ) : progress.length === 0 ? (
          <div className="p-12 text-center text-slate-600">没有找到进度记录</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    用户
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    课程
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    节点
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    类型
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    状态
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    完成度
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    学习时长
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    最后访问
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {progress.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50">
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm font-medium text-slate-900">{item.username}</div>
                        <div className="text-sm text-slate-500">{item.user_email}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 text-sm text-slate-900">
                      {item.course_name}
                    </td>
                    <td className="px-6 py-4">
                      <div>
                        <div className="text-sm font-medium text-slate-900">{item.node_title}</div>
                        <div className="text-sm text-slate-500 font-mono">{item.node_id}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                      {getNodeTypeLabel(item.node_type)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(item.status)}`}>
                        {getStatusLabel(item.status)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${item.completion_percentage}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-slate-900">{item.completion_percentage.toFixed(0)}%</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                      {formatTime(item.time_spent_hours)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                      {formatDate(item.last_accessed)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => router.push(`/admin/progress/${item.id}`)}
                        className="text-blue-600 hover:text-blue-900 mr-4"
                      >
                        查看
                      </button>
                      <button
                        onClick={() => handleDelete(item.id, item.node_title)}
                        className="text-red-600 hover:text-red-900"
                      >
                        删除
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="px-6 py-4 border-t border-slate-200 flex items-center justify-between">
            <div className="text-sm text-slate-600">
              共 {total} 条记录，第 {currentPage} / {totalPages} 页
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                上一页
              </button>
              <button
                onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-1 border border-slate-300 rounded-lg hover:bg-slate-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                下一页
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
