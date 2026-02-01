'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  getUsers,
  deleteUser,
  updateUser,
  type UserListItem,
  type UserFilters
} from '@/lib/api/admin/users';

export default function AdminUsersPage() {
  const router = useRouter();
  const [users, setUsers] = useState<UserListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  // Filters
  const [search, setSearch] = useState('');
  const [activeFilter, setActiveFilter] = useState<string>('');
  const [premiumFilter, setPremiumFilter] = useState<string>('');
  const [sortBy, setSortBy] = useState<'created_at' | 'username' | 'email'>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  // Load users
  const loadUsers = async () => {
    setLoading(true);
    try {
      const filters: UserFilters = {
        page: currentPage,
        page_size: 20,
        sort_by: sortBy,
        sort_order: sortOrder
      };

      if (search) filters.search = search;
      if (activeFilter !== '') filters.is_active = activeFilter === 'true';
      if (premiumFilter !== '') filters.is_premium = premiumFilter === 'true';

      const response = await getUsers(filters);
      setUsers(response.items);
      setTotal(response.total);
      setTotalPages(response.total_pages);
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUsers();
  }, [currentPage, sortBy, sortOrder]);

  // Handle search
  const handleSearch = () => {
    setCurrentPage(1);
    loadUsers();
  };

  // Handle delete
  const handleDelete = async (userId: number, username: string) => {
    if (!confirm(`确定要删除用户 "${username}" 吗？此操作不可撤销。`)) {
      return;
    }

    try {
      await deleteUser(userId);
      loadUsers();
    } catch (error) {
      console.error('Failed to delete user:', error);
      alert('删除失败，请重试');
    }
  };

  // Handle toggle active
  const handleToggleActive = async (userId: number, currentStatus: boolean) => {
    try {
      await updateUser(userId, { is_active: !currentStatus });
      loadUsers();
    } catch (error) {
      console.error('Failed to toggle active status:', error);
      alert('操作失败，请重试');
    }
  };

  // Handle toggle premium
  const handleTogglePremium = async (userId: number, currentStatus: boolean) => {
    try {
      await updateUser(userId, { is_premium: !currentStatus });
      loadUsers();
    } catch (error) {
      console.error('Failed to toggle premium status:', error);
      alert('操作失败，请重试');
    }
  };

  // Format time
  const formatTime = (hours: number) => {
    if (hours < 1) return `${Math.round(hours * 60)}分钟`;
    return `${hours.toFixed(1)}小时`;
  };

  // Format date
  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('zh-CN');
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">用户管理</h1>
          <p className="mt-2 text-slate-600">管理所有用户账户</p>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">搜索</label>
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="用户名、邮箱或姓名"
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">账户状态</label>
            <select
              value={activeFilter}
              onChange={(e) => setActiveFilter(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">全部</option>
              <option value="true">活跃</option>
              <option value="false">已禁用</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">会员状态</label>
            <select
              value={premiumFilter}
              onChange={(e) => setPremiumFilter(e.target.value)}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">全部</option>
              <option value="true">高级会员</option>
              <option value="false">普通用户</option>
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
              <option value="created_at-desc">最新注册</option>
              <option value="created_at-asc">最早注册</option>
              <option value="username-asc">用户名 A-Z</option>
              <option value="username-desc">用户名 Z-A</option>
              <option value="email-asc">邮箱 A-Z</option>
              <option value="email-desc">邮箱 Z-A</option>
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
          <p className="text-sm font-medium text-slate-600">总用户数</p>
          <p className="mt-2 text-3xl font-bold text-slate-900">{total}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">活跃用户</p>
          <p className="mt-2 text-3xl font-bold text-green-600">
            {users.filter((u) => u.is_active).length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">高级会员</p>
          <p className="mt-2 text-3xl font-bold text-purple-600">
            {users.filter((u) => u.is_premium).length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">总学习时长</p>
          <p className="mt-2 text-3xl font-bold text-blue-600">
            {users.reduce((sum, u) => sum + u.total_time_hours, 0).toFixed(0)}h
          </p>
        </div>
      </div>

      {/* User List */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200">
        {loading ? (
          <div className="p-12 text-center text-slate-600">加载中...</div>
        ) : users.length === 0 ? (
          <div className="p-12 text-center text-slate-600">没有找到用户</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    用户
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    邮箱
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    课程数
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    完成节点
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    学习时长
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    最后活动
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    状态
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-slate-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        {user.avatar_url ? (
                          <img
                            src={user.avatar_url}
                            alt={user.username}
                            className="w-10 h-10 rounded-full mr-3"
                          />
                        ) : (
                          <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center mr-3">
                            <span className="text-blue-600 font-medium">
                              {user.username.charAt(0).toUpperCase()}
                            </span>
                          </div>
                        )}
                        <div>
                          <div className="text-sm font-medium text-slate-900">{user.username}</div>
                          <div className="text-sm text-slate-500">{user.full_name || '-'}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                      {user.email}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                      {user.enrolled_courses}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                      {user.completed_nodes}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                      {formatTime(user.total_time_hours)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                      {formatDate(user.last_activity)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleToggleActive(user.id, user.is_active)}
                          className={`px-2 py-1 text-xs font-medium rounded-full ${
                            user.is_active
                              ? 'bg-green-100 text-green-800 hover:bg-green-200'
                              : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
                          }`}
                        >
                          {user.is_active ? '活跃' : '禁用'}
                        </button>
                        {user.is_premium && (
                          <span className="px-2 py-1 text-xs font-medium rounded-full bg-purple-100 text-purple-800">
                            会员
                          </span>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => router.push(`/admin/users/${user.id}`)}
                        className="text-blue-600 hover:text-blue-900 mr-4"
                      >
                        查看
                      </button>
                      <button
                        onClick={() => handleTogglePremium(user.id, user.is_premium)}
                        className="text-purple-600 hover:text-purple-900 mr-4"
                      >
                        {user.is_premium ? '取消会员' : '设为会员'}
                      </button>
                      <button
                        onClick={() => handleDelete(user.id, user.username)}
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
              共 {total} 个用户，第 {currentPage} / {totalPages} 页
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
