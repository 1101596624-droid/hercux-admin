'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAdminAuthStore } from '@/stores/admin/useAdminAuthStore';
import {
  getAdmins,
  createAdmin,
  deleteAdmin,
  type AdminListItem,
  type CreateAdminRequest,
} from '@/lib/api/admin/admins';
import { ADMIN_LEVEL_NAMES, ADMIN_LEVEL_DESCRIPTIONS, type AdminLevel } from '@/types';

// 等级徽章组件
function LevelBadge({ level }: { level: AdminLevel }) {
  const config: Record<AdminLevel, { bg: string; text: string; border: string }> = {
    1: { bg: 'bg-red-50', text: 'text-red-600', border: 'border-red-200' },
    2: { bg: 'bg-blue-50', text: 'text-blue-600', border: 'border-blue-200' },
    3: { bg: 'bg-slate-50', text: 'text-slate-600', border: 'border-slate-200' },
  };

  const c = config[level];

  return (
    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${c.bg} ${c.text} border ${c.border}`}>
      {ADMIN_LEVEL_NAMES[level]}
    </span>
  );
}

// 创建管理员弹窗
function CreateAdminModal({
  isOpen,
  onClose,
  onSubmit,
  isSubmitting,
}: {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: CreateAdminRequest) => void;
  isSubmitting: boolean;
}) {
  const [formData, setFormData] = useState<CreateAdminRequest>({
    username: '',
    email: '',
    password: '',
    level: 3,
  });

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl w-[500px] shadow-2xl">
        <div className="p-6 border-b border-slate-200">
          <h3 className="text-xl font-bold text-slate-900">创建管理员账号</h3>
          <p className="text-sm text-slate-500 mt-1">添加新的管理员到系统中</p>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">用户名</label>
            <input
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              placeholder="输入用户名"
              required
              className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">邮箱</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({ ...formData, email: e.target.value })}
              placeholder="输入邮箱地址"
              required
              className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">密码</label>
            <input
              type="password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              placeholder="设置登录密码"
              required
              minLength={6}
              className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">管理员等级</label>
            <div className="space-y-3">
              {([2, 3] as AdminLevel[]).map((level) => (
                <label
                  key={level}
                  className={`flex items-start gap-3 p-4 rounded-xl border-2 cursor-pointer transition-all ${
                    formData.level === level
                      ? 'border-red-500 bg-red-50'
                      : 'border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <input
                    type="radio"
                    name="level"
                    value={level}
                    checked={formData.level === level}
                    onChange={() => setFormData({ ...formData, level })}
                    className="mt-1"
                  />
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-slate-900">{ADMIN_LEVEL_NAMES[level]}</span>
                      <span className="text-xs text-slate-500">Level {level}</span>
                    </div>
                    <p className="text-sm text-slate-500 mt-1">{ADMIN_LEVEL_DESCRIPTIONS[level]}</p>
                  </div>
                </label>
              ))}
            </div>
          </div>

          <div className="flex gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-3 text-sm font-medium text-slate-700 bg-slate-100 rounded-xl hover:bg-slate-200 transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 px-4 py-3 text-sm font-medium text-white bg-red-500 rounded-xl hover:bg-red-600 disabled:opacity-50 transition-colors"
            >
              {isSubmitting ? '创建中...' : '创建管理员'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// 权限不足弹窗
function PermissionDeniedModal({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) {
  if (!isOpen) return null;

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
        <p className="text-slate-500 text-center mb-6">
          您没有访问此页面的权限。只有超级管理员（1级）可以管理其他管理员账号。
        </p>
        <button
          onClick={onClose}
          className="w-full px-4 py-3 text-sm font-medium text-white bg-red-500 rounded-xl hover:bg-red-600 transition-colors"
        >
          返回
        </button>
      </div>
    </div>
  );
}

export default function AdminPermissionsPage() {
  const router = useRouter();
  const { user, canAccessAdminManagement, getAdminLevelName } = useAdminAuthStore();

  const [admins, setAdmins] = useState<AdminListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showPermissionDenied, setShowPermissionDenied] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [levelFilter, setLevelFilter] = useState<AdminLevel | ''>('');

  // 检查权限
  useEffect(() => {
    if (!canAccessAdminManagement()) {
      setShowPermissionDenied(true);
    }
  }, [canAccessAdminManagement]);

  // 加载管理员列表
  const loadAdmins = async () => {
    try {
      setLoading(true);
      const response = await getAdmins({
        search: searchQuery || undefined,
        level: levelFilter || undefined,
      });
      setAdmins(response.items);
    } catch (error) {
      console.error('Failed to load admins:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (canAccessAdminManagement()) {
      loadAdmins();
    }
  }, [searchQuery, levelFilter]);

  // 创建管理员
  const handleCreateAdmin = async (data: CreateAdminRequest) => {
    setIsSubmitting(true);
    try {
      await createAdmin(data);
      setShowCreateModal(false);
      loadAdmins();
    } catch (error) {
      alert(error instanceof Error ? error.message : '创建失败');
    } finally {
      setIsSubmitting(false);
    }
  };

  // 删除管理员
  const handleDeleteAdmin = async (admin: AdminListItem) => {
    if (admin.level === 1) {
      alert('不能删除超级管理员');
      return;
    }

    if (!confirm(`确定要删除管理员 "${admin.username}" 吗？此操作不可撤销。`)) {
      return;
    }

    try {
      await deleteAdmin(admin.id);
      loadAdmins();
    } catch (error) {
      alert(error instanceof Error ? error.message : '删除失败');
    }
  };

  // 格式化日期
  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  // 权限不足时显示弹窗
  if (showPermissionDenied) {
    return (
      <PermissionDeniedModal
        isOpen={true}
        onClose={() => router.push('/admin/dashboard')}
      />
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 italic">Permissions.</h1>
          <p className="text-slate-500 mt-1">
            管理系统管理员账号，当前共有 <span className="text-red-500 font-medium">{admins.length}</span> 个管理员
          </p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center gap-2 px-5 py-3 bg-slate-900 text-white rounded-xl hover:bg-slate-800 transition-colors font-medium"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 5v14M5 12h14" />
          </svg>
          添加管理员
        </button>
      </div>

      {/* 当前用户信息 */}
      <div className="bg-gradient-to-r from-red-500 to-red-600 rounded-2xl p-6 mb-8 text-white">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center text-2xl font-bold">
            {user?.name?.charAt(0).toUpperCase() || 'A'}
          </div>
          <div>
            <h2 className="text-xl font-bold">{user?.name || 'Admin'}</h2>
            <p className="text-red-100">{user?.email}</p>
            <div className="flex items-center gap-2 mt-2">
              <span className="px-3 py-1 bg-white/20 rounded-full text-sm font-medium">
                {getAdminLevelName()}
              </span>
              <span className="text-red-100 text-sm">Level {user?.level}</span>
            </div>
          </div>
        </div>
      </div>

      {/* 权限等级说明 */}
      <div className="grid grid-cols-3 gap-4 mb-8">
        {([1, 2, 3] as AdminLevel[]).map((level) => (
          <div
            key={level}
            className={`p-4 rounded-xl border-2 ${
              level === 1
                ? 'border-red-200 bg-red-50'
                : level === 2
                ? 'border-blue-200 bg-blue-50'
                : 'border-slate-200 bg-slate-50'
            }`}
          >
            <div className="flex items-center gap-2 mb-2">
              <span className={`text-lg font-bold ${
                level === 1 ? 'text-red-600' : level === 2 ? 'text-blue-600' : 'text-slate-600'
              }`}>
                Level {level}
              </span>
              <span className={`text-sm font-medium ${
                level === 1 ? 'text-red-500' : level === 2 ? 'text-blue-500' : 'text-slate-500'
              }`}>
                {ADMIN_LEVEL_NAMES[level]}
              </span>
            </div>
            <p className="text-sm text-slate-600">{ADMIN_LEVEL_DESCRIPTIONS[level]}</p>
          </div>
        ))}
      </div>

      {/* 筛选栏 */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-6 mb-6">
        <div className="flex items-center gap-4">
          <div className="flex-1">
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
                placeholder="搜索管理员..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500"
              />
            </div>
          </div>
          <select
            value={levelFilter}
            onChange={(e) => setLevelFilter(e.target.value as AdminLevel | '')}
            className="px-4 py-2.5 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 bg-white"
          >
            <option value="">全部等级</option>
            <option value="1">超级管理员</option>
            <option value="2">高级管理员</option>
            <option value="3">普通管理员</option>
          </select>
        </div>
      </div>

      {/* 管理员列表 */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100">
          <h2 className="text-lg font-semibold text-slate-900">
            <span className="text-red-500">管理员列表</span>
          </h2>
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="w-10 h-10 border-4 border-red-200 border-t-red-500 rounded-full animate-spin"></div>
          </div>
        ) : admins.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-20 text-slate-500">
            <svg className="w-16 h-16 text-slate-300 mb-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
              <circle cx="9" cy="7" r="4" />
              <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
              <path d="M16 3.13a4 4 0 0 1 0 7.75" />
            </svg>
            <p className="text-lg font-medium mb-2">暂无管理员</p>
            <p className="text-sm">点击"添加管理员"按钮创建新的管理员账号</p>
          </div>
        ) : (
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-100 text-left">
                <th className="py-3 px-6 text-sm font-medium text-slate-500">管理员</th>
                <th className="py-3 px-6 text-sm font-medium text-slate-500">等级</th>
                <th className="py-3 px-6 text-sm font-medium text-slate-500">状态</th>
                <th className="py-3 px-6 text-sm font-medium text-slate-500">创建时间</th>
                <th className="py-3 px-6 text-sm font-medium text-slate-500">更新时间</th>
                <th className="py-3 px-6 text-sm font-medium text-slate-500">操作</th>
              </tr>
            </thead>
            <tbody>
              {admins.map((admin) => (
                <tr key={admin.id} className="border-b border-slate-100 hover:bg-slate-50/50 transition-colors">
                  <td className="py-4 px-6">
                    <div className="flex items-center gap-3">
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center text-white font-semibold ${
                        admin.level === 1 ? 'bg-red-500' : admin.level === 2 ? 'bg-blue-500' : 'bg-slate-500'
                      }`}>
                        {admin.username.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <div className="font-semibold text-slate-900">{admin.username}</div>
                        <div className="text-sm text-slate-500">{admin.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="py-4 px-6">
                    <LevelBadge level={admin.level} />
                  </td>
                  <td className="py-4 px-6">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-medium ${
                      admin.is_active
                        ? 'bg-emerald-50 text-emerald-600 border border-emerald-200'
                        : 'bg-slate-100 text-slate-600 border border-slate-200'
                    }`}>
                      {admin.is_active ? '活跃' : '已禁用'}
                    </span>
                  </td>
                  <td className="py-4 px-6 text-sm text-slate-600">
                    {formatDate(admin.created_at)}
                  </td>
                  <td className="py-4 px-6 text-sm text-slate-600">
                    {formatDate(admin.updated_at)}
                  </td>
                  <td className="py-4 px-6">
                    {admin.level !== 1 && (
                      <button
                        onClick={() => handleDeleteAdmin(admin)}
                        className="w-10 h-10 rounded-xl border border-red-200 flex items-center justify-center hover:bg-red-50 transition-colors"
                        title="删除管理员"
                      >
                        <svg className="w-5 h-5 text-red-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <polyline points="3 6 5 6 21 6" />
                          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                          <line x1="10" y1="11" x2="10" y2="17" />
                          <line x1="14" y1="11" x2="14" y2="17" />
                        </svg>
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* 创建管理员弹窗 */}
      <CreateAdminModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onSubmit={handleCreateAdmin}
        isSubmitting={isSubmitting}
      />
    </div>
  );
}
