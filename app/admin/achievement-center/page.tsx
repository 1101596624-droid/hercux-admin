'use client';

import { useState, useEffect } from 'react';
import { achievementCenterAPI, BadgeConfig, SkillTreeConfig, AchievementStats, BadgeCategory, BadgeRarity } from '@/lib/api/admin/achievement-center';

type TabType = 'badges' | 'skill-trees' | 'pending-domains';

const CATEGORY_LABELS: Record<BadgeCategory, string> = {
  learning: '学习',
  persistence: '坚持',
  practice: '练习',
  quiz: '测验',
  special: '特殊',
};

const RARITY_LABELS: Record<BadgeRarity, string> = {
  common: '普通',
  rare: '稀有',
  epic: '史诗',
  legendary: '传说',
};

const RARITY_COLORS: Record<BadgeRarity, string> = {
  common: 'bg-gray-100 text-gray-700',
  rare: 'bg-blue-100 text-blue-700',
  epic: 'bg-purple-100 text-purple-700',
  legendary: 'bg-yellow-100 text-yellow-700',
};

export default function AchievementCenterPage() {
  const [activeTab, setActiveTab] = useState<TabType>('badges');
  const [stats, setStats] = useState<AchievementStats | null>(null);
  const [badges, setBadges] = useState<BadgeConfig[]>([]);
  const [skillTrees, setSkillTrees] = useState<SkillTreeConfig[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modal states
  const [showBadgeModal, setShowBadgeModal] = useState(false);
  const [editingBadge, setEditingBadge] = useState<BadgeConfig | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsData, badgesData, skillTreesData] = await Promise.all([
        achievementCenterAPI.getStats(),
        achievementCenterAPI.getBadges(),
        achievementCenterAPI.getSkillTrees(),
      ]);
      setStats(statsData);
      setBadges(badgesData);
      setSkillTrees(skillTreesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteBadge = async (id: string) => {
    if (!confirm('确定要删除这个勋章吗？')) return;
    try {
      await achievementCenterAPI.deleteBadge(id);
      setBadges(badges.filter(b => b.id !== id));
    } catch (err) {
      alert(err instanceof Error ? err.message : '删除失败');
    }
  };

  const handleToggleBadgeActive = async (badge: BadgeConfig) => {
    try {
      await achievementCenterAPI.updateBadge(badge.id, {
        is_active: badge.is_active ? 0 : 1,
      });
      // Reload badges to get updated data
      const badgesData = await achievementCenterAPI.getBadges();
      setBadges(badgesData);
    } catch (err) {
      alert(err instanceof Error ? err.message : '更新失败');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-red-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-6">
        <div className="bg-red-50 text-red-600 p-4 rounded-lg">
          {error}
          <button onClick={loadData} className="ml-4 underline">重试</button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">勋章中心管理</h1>
          <p className="text-gray-500 mt-1">管理勋章、技能树和成就配置</p>
        </div>
        <button
          onClick={() => {
            setEditingBadge(null);
            setShowBadgeModal(true);
          }}
          className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
        >
          + 新建勋章
        </button>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
            <div className="text-3xl font-bold text-gray-900">{stats.total_badges}</div>
            <div className="text-sm text-gray-500">勋章总数</div>
            <div className="text-xs text-green-600 mt-1">{stats.active_badges} 个启用</div>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
            <div className="text-3xl font-bold text-gray-900">{stats.total_skill_trees}</div>
            <div className="text-sm text-gray-500">技能树</div>
            <div className="text-xs text-green-600 mt-1">{stats.active_skill_trees} 个启用</div>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
            <div className="text-3xl font-bold text-gray-900">{stats.total_badge_unlocks}</div>
            <div className="text-sm text-gray-500">勋章解锁次数</div>
          </div>
          <div className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
            <div className="text-3xl font-bold text-gray-900">{stats.pending_domains}</div>
            <div className="text-sm text-gray-500">待审核领域</div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          {[
            { id: 'badges', label: '勋章管理' },
            { id: 'skill-trees', label: '技能树' },
            { id: 'pending-domains', label: '待审核领域' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as TabType)}
              className={`py-3 px-1 border-b-2 font-medium text-sm transition-colors ${
                activeTab === tab.id
                  ? 'border-red-500 text-red-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'badges' && (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">勋章</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">分类</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">稀有度</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">积分</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">解锁数</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100">
              {badges.map(badge => (
                <tr key={badge.id} className="hover:bg-gray-50">
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{badge.icon}</span>
                      <div>
                        <div className="font-medium text-gray-900">{badge.name}</div>
                        <div className="text-xs text-gray-500">{badge.id}</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {CATEGORY_LABELS[badge.category]}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${RARITY_COLORS[badge.rarity]}`}>
                      {RARITY_LABELS[badge.rarity]}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">{badge.points}</td>
                  <td className="px-4 py-3 text-sm text-gray-600">{badge.unlock_count || 0}</td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        badge.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-500'
                      }`}>
                        {badge.is_active ? '已启用' : '已停用'}
                      </span>
                      <button
                        onClick={() => handleToggleBadgeActive(badge)}
                        className={`px-2 py-1 rounded text-xs font-medium transition-colors ${
                          badge.is_active
                            ? 'text-red-600 hover:bg-red-50'
                            : 'text-green-600 hover:bg-green-50'
                        }`}
                      >
                        {badge.is_active ? '停用' : '启用'}
                      </button>
                    </div>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => {
                          setEditingBadge(badge);
                          setShowBadgeModal(true);
                        }}
                        className="text-blue-600 hover:text-blue-800 text-sm"
                      >
                        编辑
                      </button>
                      <button
                        onClick={() => handleDeleteBadge(badge.id)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        删除
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {badges.length === 0 && (
                <tr>
                  <td colSpan={7} className="px-4 py-8 text-center text-gray-500">
                    暂无勋章数据
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}

      {activeTab === 'skill-trees' && (
        <div className="grid grid-cols-3 gap-4">
          {skillTrees.map(tree => (
            <div key={tree.id} className="bg-white rounded-xl p-4 shadow-sm border border-gray-100">
              <div className="flex items-center gap-3 mb-3">
                <div
                  className="w-10 h-10 rounded-lg flex items-center justify-center text-xl"
                  style={{ backgroundColor: tree.color + '20', color: tree.color }}
                >
                  {tree.icon}
                </div>
                <div>
                  <div className="font-medium text-gray-900">{tree.name}</div>
                  <div className="text-xs text-gray-500">{tree.id}</div>
                </div>
              </div>
              <p className="text-sm text-gray-600 mb-3">{tree.description}</p>
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">{tree.active_users || 0} 用户学习中</span>
                <span className={tree.is_active ? 'text-green-600' : 'text-gray-400'}>
                  {tree.is_active ? '启用' : '禁用'}
                </span>
              </div>
            </div>
          ))}
          {skillTrees.length === 0 && (
            <div className="col-span-3 text-center py-8 text-gray-500">
              暂无技能树数据
            </div>
          )}
        </div>
      )}

      {activeTab === 'pending-domains' && (
        <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-100">
          <p className="text-gray-500 text-center py-8">待审核领域功能开发中...</p>
        </div>
      )}

      {/* Badge Modal */}
      {showBadgeModal && (
        <BadgeModal
          badge={editingBadge}
          onClose={() => {
            setShowBadgeModal(false);
            setEditingBadge(null);
          }}
          onSave={async (data) => {
            try {
              if (editingBadge) {
                await achievementCenterAPI.updateBadge(editingBadge.id, data);
              } else {
                await achievementCenterAPI.createBadge(data as any);
              }
              // Reload badges to get updated data
              const badgesData = await achievementCenterAPI.getBadges();
              setBadges(badgesData);
              setShowBadgeModal(false);
              setEditingBadge(null);
            } catch (err) {
              alert(err instanceof Error ? err.message : '保存失败');
            }
          }}
        />
      )}
    </div>
  );
}

// Badge Modal Component
function BadgeModal({
  badge,
  onClose,
  onSave,
}: {
  badge: BadgeConfig | null;
  onClose: () => void;
  onSave: (data: any) => Promise<void>;
}) {
  const isEditing = !!badge;

  // Form data - used for both edit and create (after AI generation)
  const [formData, setFormData] = useState({
    id: badge?.id || '',
    name: badge?.name || '',
    name_en: badge?.name_en || '',
    icon: badge?.icon || '',
    description: badge?.description || '',
    category: badge?.category || 'learning',
    rarity: badge?.rarity || 'common',
    points: badge?.points || 10,
    condition: JSON.stringify(badge?.condition || { type: 'counter', metric: '', target: 1 }, null, 2),
  });

  // For create mode, use AI generation first
  const [unlockDescription, setUnlockDescription] = useState('');
  const [generating, setGenerating] = useState(false);
  const [showForm, setShowForm] = useState(isEditing); // Show form directly if editing
  const [aiError, setAiError] = useState<string | null>(null);

  const [saving, setSaving] = useState(false);

  const handleGenerate = async () => {
    if (!unlockDescription.trim()) {
      setAiError('请输入解锁方式描述');
      return;
    }

    setGenerating(true);
    setAiError(null);

    try {
      const result = await achievementCenterAPI.generateBadge(unlockDescription);
      if (result.success && result.badge) {
        // Load generated badge into form
        const generated = result.badge;
        setFormData({
          id: generated.id || '',
          name: generated.name || '',
          name_en: generated.name_en || '',
          icon: generated.icon || '',
          description: generated.description || '',
          category: generated.category || 'learning',
          rarity: generated.rarity || 'common',
          points: generated.points || 10,
          condition: JSON.stringify(generated.condition || {}, null, 2),
        });
        setShowForm(true); // Switch to edit form
      } else {
        setAiError(result.error || 'AI 生成失败');
      }
    } catch (err) {
      setAiError(err instanceof Error ? err.message : 'AI 生成失败');
    } finally {
      setGenerating(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await onSave({
        ...formData,
        condition: JSON.parse(formData.condition),
      });
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl w-[600px] max-h-[90vh] overflow-y-auto">
        <div className="p-6 border-b border-gray-100">
          <h2 className="text-lg font-semibold">{isEditing ? '编辑勋章' : '新建勋章'}</h2>
        </div>

        {!showForm ? (
          // Step 1: AI Generation (only for create mode)
          <div className="p-6 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                描述勋章的解锁方式
              </label>
              <textarea
                value={unlockDescription}
                onChange={e => setUnlockDescription(e.target.value)}
                placeholder="例如：用户连续学习30天可以解锁这个勋章"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                rows={4}
              />
              <p className="mt-2 text-sm text-gray-500">
                AI 会根据您的描述自动生成勋章配置，生成后可以编辑修改
              </p>
            </div>

            {aiError && (
              <div className="p-3 bg-red-50 text-red-600 rounded-lg text-sm">
                {aiError}
              </div>
            )}

            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={onClose}
                className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
              >
                取消
              </button>
              <button
                onClick={handleGenerate}
                disabled={generating || !unlockDescription.trim()}
                className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50 flex items-center gap-2"
              >
                {generating ? (
                  <>
                    <span className="animate-spin">⏳</span>
                    AI 生成中...
                  </>
                ) : (
                  <>
                    ✨ AI 生成勋章
                  </>
                )}
              </button>
            </div>
          </div>
        ) : (
          // Step 2: Edit Form (for both edit and after AI generation)
          <form onSubmit={handleSubmit} className="p-6 space-y-4">
            {/* Preview header for newly generated badge */}
            {!isEditing && (
              <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-xl p-4 mb-4 flex items-center gap-4">
                <span className="text-4xl">{formData.icon}</span>
                <div className="flex-1">
                  <div className="font-semibold text-gray-900">{formData.name || '勋章名称'}</div>
                  <div className="text-sm text-gray-500">{formData.description || '勋章描述'}</div>
                </div>
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${RARITY_COLORS[formData.rarity as BadgeRarity]}`}>
                  {RARITY_LABELS[formData.rarity as BadgeRarity]}
                </span>
              </div>
            )}

            {!isEditing && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ID</label>
                <input
                  type="text"
                  value={formData.id}
                  onChange={e => setFormData({ ...formData, id: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  placeholder="badge_id"
                  required
                />
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">名称</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={e => setFormData({ ...formData, name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">图标 (emoji)</label>
                <input
                  type="text"
                  value={formData.icon}
                  onChange={e => setFormData({ ...formData, icon: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">描述</label>
              <textarea
                value={formData.description}
                onChange={e => setFormData({ ...formData, description: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                rows={2}
              />
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">分类</label>
                <select
                  value={formData.category}
                  onChange={e => setFormData({ ...formData, category: e.target.value as BadgeCategory })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                >
                  {Object.entries(CATEGORY_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">稀有度</label>
                <select
                  value={formData.rarity}
                  onChange={e => setFormData({ ...formData, rarity: e.target.value as BadgeRarity })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                >
                  {Object.entries(RARITY_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>{label}</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">积分</label>
                <input
                  type="number"
                  value={formData.points}
                  onChange={e => setFormData({ ...formData, points: parseInt(e.target.value) || 0 })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">解锁条件 (JSON)</label>
              <textarea
                value={formData.condition}
                onChange={e => setFormData({ ...formData, condition: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent font-mono text-sm bg-gray-50"
                rows={4}
              />
            </div>

            <div className="flex justify-between pt-4">
              {!isEditing && (
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  ← 重新生成
                </button>
              )}
              <div className={`flex gap-3 ${isEditing ? 'ml-auto' : ''}`}>
                <button
                  type="button"
                  onClick={onClose}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  取消
                </button>
                <button
                  type="submit"
                  disabled={saving}
                  className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50"
                >
                  {saving ? '保存中...' : (isEditing ? '保存修改' : '确认上架')}
                </button>
              </div>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
