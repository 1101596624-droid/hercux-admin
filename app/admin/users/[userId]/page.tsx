'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
  getUserDetail,
  deleteUser,
  updateUser,
  type UserDetail
} from '@/lib/api/admin/users';

export default function UserDetailPage() {
  const router = useRouter();
  const params = useParams();
  const userId = parseInt(params.userId as string);

  const [user, setUser] = useState<UserDetail | null>(null);
  const [loading, setLoading] = useState(true);

  // Load user detail
  useEffect(() => {
    loadUser();
  }, [userId]);

  const loadUser = async () => {
    setLoading(true);
    try {
      const data = await getUserDetail(userId);
      setUser(data);
    } catch (error) {
      console.error('Failed to load user:', error);
      alert('加载用户失败');
      router.push('/admin/users');
    } finally {
      setLoading(false);
    }
  };

  // Handle delete
  const handleDelete = async () => {
    if (!user) return;

    if (!confirm(`确定要删除用户 "${user.username}" 吗？此操作不可撤销。`)) {
      return;
    }

    try {
      await deleteUser(userId);
      alert('用户已删除');
      router.push('/admin/users');
    } catch (error) {
      console.error('Failed to delete user:', error);
      alert('删除失败，请重试');
    }
  };

  // Handle toggle active
  const handleToggleActive = async () => {
    if (!user) return;

    try {
      await updateUser(userId, { is_active: !user.is_active });
      loadUser();
    } catch (error) {
      console.error('Failed to toggle active status:', error);
      alert('操作失败，请重试');
    }
  };

  // Handle toggle premium
  const handleTogglePremium = async () => {
    if (!user) return;

    try {
      await updateUser(userId, { is_premium: !user.is_premium });
      loadUser();
    } catch (error) {
      console.error('Failed to toggle premium status:', error);
      alert('操作失败，请重试');
    }
  };

  // Format date
  const formatDate = (dateString: string | null) => {
    if (!dateString) return '-';
    return new Date(dateString).toLocaleDateString('zh-CN');
  };

  // Format time
  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    if (hours > 0) return `${hours}小时${minutes}分钟`;
    return `${minutes}分钟`;
  };

  // Rarity color
  const getRarityColor = (rarity: string | null) => {
    const colors = {
      common: 'bg-gray-100 text-gray-800',
      rare: 'bg-blue-100 text-blue-800',
      epic: 'bg-purple-100 text-purple-800',
      legendary: 'bg-orange-100 text-orange-800'
    };
    return colors[rarity as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-slate-600">加载中...</div>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-slate-600">用户未找到</div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <button
            onClick={() => router.push('/admin/users')}
            className="text-slate-600 hover:text-slate-900"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div className="flex-1">
            <div className="flex items-center gap-3">
              {user.avatar_url ? (
                <img
                  src={user.avatar_url}
                  alt={user.username}
                  className="w-16 h-16 rounded-full"
                />
              ) : (
                <div className="w-16 h-16 rounded-full bg-blue-100 flex items-center justify-center">
                  <span className="text-blue-600 font-bold text-2xl">
                    {user.username.charAt(0).toUpperCase()}
                  </span>
                </div>
              )}
              <div>
                <h1 className="text-3xl font-bold text-slate-900">{user.username}</h1>
                <p className="mt-1 text-slate-600">{user.email}</p>
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleToggleActive}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                user.is_active
                  ? 'bg-green-100 text-green-800 hover:bg-green-200'
                  : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
              }`}
            >
              {user.is_active ? '活跃' : '已禁用'}
            </button>
            <button
              onClick={handleTogglePremium}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                user.is_premium
                  ? 'bg-purple-100 text-purple-800 hover:bg-purple-200'
                  : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
              }`}
            >
              {user.is_premium ? '高级会员' : '普通用户'}
            </button>
            <button
              onClick={handleDelete}
              className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
            >
              删除
            </button>
          </div>
        </div>
      </div>

      {/* User Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">基本信息</h2>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-slate-600">姓名</p>
              <p className="text-base font-medium text-slate-900">{user.full_name || '-'}</p>
            </div>
            <div>
              <p className="text-sm text-slate-600">注册时间</p>
              <p className="text-base font-medium text-slate-900">{formatDate(user.created_at)}</p>
            </div>
            <div>
              <p className="text-sm text-slate-600">最后更新</p>
              <p className="text-base font-medium text-slate-900">{formatDate(user.updated_at)}</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">学习统计</h2>
          <div className="space-y-3">
            <div>
              <p className="text-sm text-slate-600">连续学习天数</p>
              <p className="text-base font-medium text-slate-900">{user.statistics.current_streak} 天</p>
            </div>
            <div>
              <p className="text-sm text-slate-600">总学习时长</p>
              <p className="text-base font-medium text-slate-900">{user.statistics.total_time_hours} 小时</p>
            </div>
            <div>
              <p className="text-sm text-slate-600">成就数量</p>
              <p className="text-base font-medium text-slate-900">{user.statistics.achievements_count} 个</p>
            </div>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">已注册课程</p>
          <p className="mt-2 text-3xl font-bold text-blue-600">{user.statistics.enrolled_courses}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">完成节点</p>
          <p className="mt-2 text-3xl font-bold text-green-600">{user.statistics.completed_nodes}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">连续天数</p>
          <p className="mt-2 text-3xl font-bold text-orange-600">{user.statistics.current_streak}</p>
        </div>
      </div>

      {/* Enrolled Courses */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 mb-8">
        <div className="px-6 py-4 border-b border-slate-200">
          <h2 className="text-lg font-semibold text-slate-900">已注册课程</h2>
        </div>
        {user.enrolled_courses.length === 0 ? (
          <div className="p-12 text-center text-slate-600">暂无注册课程</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    课程名称
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    注册时间
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    最后访问
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    进度
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    完成率
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {user.enrolled_courses.map((course) => (
                  <tr key={course.course_id} className="hover:bg-slate-50">
                    <td className="px-6 py-4">
                      <div className="flex items-center">
                        <div className="text-sm font-medium text-slate-900">{course.course_name}</div>
                        {course.is_favorite && (
                          <svg className="w-4 h-4 text-yellow-500 ml-2" fill="currentColor" viewBox="0 0 20 20">
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                      {formatDate(course.enrolled_at)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-600">
                      {formatDate(course.last_accessed)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                      {course.completed_nodes} / {course.total_nodes}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="w-24 bg-gray-200 rounded-full h-2 mr-2">
                          <div
                            className="bg-blue-600 h-2 rounded-full"
                            style={{ width: `${course.completion_rate}%` }}
                          ></div>
                        </div>
                        <span className="text-sm text-slate-900">{course.completion_rate.toFixed(0)}%</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Achievements */}
      {user.achievements.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-slate-200 mb-8">
          <div className="px-6 py-4 border-b border-slate-200">
            <h2 className="text-lg font-semibold text-slate-900">成就徽章</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {user.achievements.map((achievement) => (
                <div
                  key={achievement.badge_id}
                  className="flex items-start gap-3 p-4 border border-slate-200 rounded-lg"
                >
                  {achievement.icon_url && (
                    <img
                      src={achievement.icon_url}
                      alt={achievement.badge_name}
                      className="w-12 h-12"
                    />
                  )}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-medium text-slate-900">{achievement.badge_name}</h3>
                      {achievement.rarity && (
                        <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${getRarityColor(achievement.rarity)}`}>
                          {achievement.rarity}
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-slate-600 mb-2">{achievement.badge_description}</p>
                    <p className="text-xs text-slate-500">
                      解锁于 {formatDate(achievement.unlocked_at)}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Daily Statistics Chart */}
      {user.daily_statistics.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border border-slate-200">
          <div className="px-6 py-4 border-b border-slate-200">
            <h2 className="text-lg font-semibold text-slate-900">最近30天学习统计</h2>
          </div>
          <div className="p-6">
            <div className="space-y-2">
              {user.daily_statistics.slice(-7).map((stat) => (
                <div key={stat.date} className="flex items-center gap-4">
                  <div className="w-24 text-sm text-slate-600">{stat.date}</div>
                  <div className="flex-1 bg-gray-200 rounded-full h-6 relative">
                    <div
                      className="bg-blue-600 h-6 rounded-full flex items-center justify-end pr-2"
                      style={{ width: `${Math.min((stat.total_time_seconds / 3600 / 8) * 100, 100)}%` }}
                    >
                      <span className="text-xs text-white font-medium">
                        {formatTime(stat.total_time_seconds)}
                      </span>
                    </div>
                  </div>
                  <div className="w-20 text-sm text-slate-600 text-right">
                    {stat.nodes_completed} 节点
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
