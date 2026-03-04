'use client';

import { useState, useEffect, useRef } from 'react';
import { achievementCenterAPI, BadgeConfig, SkillTreeConfig, AchievementStats, BadgeCategory, BadgeRarity, BadgeCreateInput, BadgeUpdateInput } from '@/lib/api/admin/achievement-center';

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

  // Pagination states
  const [currentPage, setCurrentPage] = useState(1);
  const [totalBadges, setTotalBadges] = useState(0);
  const pageSize = 40;

  // Modal states
  const [showBadgeModal, setShowBadgeModal] = useState(false);
  const [editingBadge, setEditingBadge] = useState<BadgeConfig | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  // Load badges when page changes
  useEffect(() => {
    loadBadges(currentPage);
  }, [currentPage]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsData, badgesResult, skillTreesData] = await Promise.all([
        achievementCenterAPI.getStats(),
        achievementCenterAPI.getBadges({ page: 1, page_size: pageSize }),
        achievementCenterAPI.getSkillTrees(),
      ]);
      setStats(statsData);
      setBadges(badgesResult.badges);
      setTotalBadges(badgesResult.pagination.total);
      setSkillTrees(skillTreesData);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载数据失败');
    } finally {
      setLoading(false);
    }
  };

  const loadBadges = async (page: number) => {
    try {
      const result = await achievementCenterAPI.getBadges({ page, page_size: pageSize });
      setBadges(result.badges);
      setTotalBadges(result.pagination.total);
    } catch (err) {
      console.error('Failed to load badges:', err);
    }
  };

  const handleDeleteBadge = async (id: string) => {
    if (!confirm('确定要删除这个勋章吗？')) return;
    try {
      await achievementCenterAPI.deleteBadge(id);
      loadBadges(currentPage);
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
      loadBadges(currentPage);
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
                      {badge.icon_url ? (
                        <img src={badge.icon_url} alt={badge.name} className="w-8 h-8 rounded-lg object-cover" />
                      ) : (
                        <span className="text-2xl">{badge.icon}</span>
                      )}
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

          {/* 分页控件 */}
          {totalBadges > pageSize && (
            <div className="flex items-center justify-between px-4 py-4 border-t border-gray-100">
              <div className="text-sm text-gray-500">
                共 {totalBadges} 个勋章，第 {currentPage} / {Math.ceil(totalBadges / pageSize)} 页
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed bg-gray-100 text-gray-700 hover:bg-gray-200"
                >
                  上一页
                </button>
                {Array.from({ length: Math.ceil(totalBadges / pageSize) }, (_, i) => i + 1).map((page) => {
                  const totalPages = Math.ceil(totalBadges / pageSize);
                  const showPage = page === 1 ||
                                   page === totalPages ||
                                   Math.abs(page - currentPage) <= 1;
                  const showEllipsisBefore = page === currentPage - 2 && currentPage > 3;
                  const showEllipsisAfter = page === currentPage + 2 && currentPage < totalPages - 2;

                  if (showEllipsisBefore || showEllipsisAfter) {
                    return <span key={page} className="px-2 text-gray-400">...</span>;
                  }
                  if (!showPage) return null;

                  return (
                    <button
                      key={page}
                      onClick={() => setCurrentPage(page)}
                      className={`w-8 h-8 rounded-lg text-sm font-medium transition-colors ${
                        currentPage === page
                          ? 'bg-red-500 text-white'
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {page}
                    </button>
                  );
                })}
                <button
                  onClick={() => setCurrentPage(p => Math.min(Math.ceil(totalBadges / pageSize), p + 1))}
                  disabled={currentPage === Math.ceil(totalBadges / pageSize)}
                  className="px-3 py-1.5 rounded-lg text-sm font-medium transition-colors disabled:opacity-40 disabled:cursor-not-allowed bg-gray-100 text-gray-700 hover:bg-gray-200"
                >
                  下一页
                </button>
              </div>
            </div>
          )}
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
              loadBadges(currentPage);
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
  onSave: (data: BadgeCreateInput | BadgeUpdateInput) => Promise<void>;
}) {
  const isEditing = !!badge;

  // Form data - used for both edit and create (after AI generation)
  const [formData, setFormData] = useState({
    id: badge?.id || '',
    name: badge?.name || '',
    name_en: badge?.name_en || '',
    icon: badge?.icon || '',
    icon_url: badge?.icon_url || '',
    description: badge?.description || '',
    category: badge?.category || 'learning',
    rarity: badge?.rarity || 'common',
    points: badge?.points || 10,
    condition: JSON.stringify(badge?.condition || { type: 'counter', metric: '', target: 1 }, null, 2),
    unlock_animation: badge?.unlock_animation || '',
  });

  // For create mode, use AI generation first
  const [unlockDescription, setUnlockDescription] = useState('');
  const [generating, setGenerating] = useState(false);
  const [showForm, setShowForm] = useState(isEditing); // Show form directly if editing
  const [aiError, setAiError] = useState<string | null>(null);

  const [saving, setSaving] = useState(false);
  const [uploadingIcon, setUploadingIcon] = useState(false);
  const [showAnimationDialog, setShowAnimationDialog] = useState(false);
  const [showAnimationPreview, setShowAnimationPreview] = useState(false);
  const [animationPrompt, setAnimationPrompt] = useState('');
  const [generatingAnimation, setGeneratingAnimation] = useState(false);

  // 是否可以有解锁动画（只有史诗和传说级别）
  const canHaveAnimation = formData.rarity === 'epic' || formData.rarity === 'legendary';

  // 处理图标图片上传
  const handleIconUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (!file.type.startsWith('image/')) {
      alert('请选择图片文件');
      return;
    }

    if (file.size > 2 * 1024 * 1024) {
      alert('图片大小不能超过 2MB');
      return;
    }

    setUploadingIcon(true);
    try {
      const reader = new FileReader();
      reader.onload = (event) => {
        const base64 = event.target?.result as string;
        setFormData({ ...formData, icon_url: base64 });
        setUploadingIcon(false);
      };
      reader.onerror = () => {
        alert('读取图片失败');
        setUploadingIcon(false);
      };
      reader.readAsDataURL(file);
    } catch (error) {
      alert('上传失败');
      setUploadingIcon(false);
    }
  };

  // 生成解锁动画
  const handleGenerateAnimation = async () => {
    if (!animationPrompt.trim()) {
      alert('请描述你想要的动画效果');
      return;
    }

    setGeneratingAnimation(true);
    try {
      const result = await achievementCenterAPI.generateUnlockAnimation(
        formData.name,
        animationPrompt,
        formData.rarity as BadgeRarity
      );
      if (result.success && result.animation_code) {
        setFormData({ ...formData, unlock_animation: result.animation_code });
        setShowAnimationDialog(false);
        setAnimationPrompt('');
      } else {
        alert(result.error || '生成动画失败');
      }
    } catch (err) {
      alert(err instanceof Error ? err.message : '生成动画失败');
    } finally {
      setGeneratingAnimation(false);
    }
  };

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
          icon_url: '',
          description: generated.description || '',
          category: generated.category || 'learning',
          rarity: generated.rarity || 'common',
          points: generated.points || 10,
          condition: JSON.stringify(generated.condition || {}, null, 2),
          unlock_animation: '',
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
        // 只有史诗和传说级别才保存动画
        unlock_animation: canHaveAnimation ? formData.unlock_animation : undefined,
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
                {formData.icon_url ? (
                  <img src={formData.icon_url} alt={formData.name} className="w-12 h-12 rounded-lg object-cover" />
                ) : (
                  <span className="text-4xl">{formData.icon}</span>
                )}
                <div className="flex-1">
                  <div className="font-semibold text-gray-900">{formData.name || '勋章名称'}</div>
                  <div className="text-sm text-gray-500">{formData.description || '勋章描述'}</div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${RARITY_COLORS[formData.rarity as BadgeRarity]}`}>
                    {RARITY_LABELS[formData.rarity as BadgeRarity]}
                  </span>
                  <button
                    type="button"
                    onClick={() => setShowAnimationPreview(true)}
                    className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
                    title="预览解锁动画"
                  >
                    ▶️
                  </button>
                </div>
              </div>
            )}

            {/* Preview header for editing mode */}
            {isEditing && (
              <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-4 mb-4 flex items-center gap-4">
                {formData.icon_url ? (
                  <img src={formData.icon_url} alt={formData.name} className="w-12 h-12 rounded-lg object-cover" />
                ) : (
                  <span className="text-4xl">{formData.icon}</span>
                )}
                <div className="flex-1">
                  <div className="font-semibold text-gray-900">{formData.name || '勋章名称'}</div>
                  <div className="text-xs text-gray-400">ID: {formData.id}</div>
                </div>
                <div className="flex items-center gap-2">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${RARITY_COLORS[formData.rarity as BadgeRarity]}`}>
                    {RARITY_LABELS[formData.rarity as BadgeRarity]}
                  </span>
                  <button
                    type="button"
                    onClick={() => setShowAnimationPreview(true)}
                    className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors"
                    title="预览解锁动画"
                  >
                    ▶️ 预览
                  </button>
                </div>
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
                <label className="block text-sm font-medium text-gray-700 mb-1">图标</label>
                <div className="flex items-center gap-2">
                  <input
                    type="text"
                    value={formData.icon}
                    onChange={e => setFormData({ ...formData, icon: e.target.value })}
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                    placeholder="emoji 或留空使用图片"
                  />
                  <label className="cursor-pointer">
                    <input
                      type="file"
                      accept="image/*"
                      onChange={handleIconUpload}
                      className="hidden"
                    />
                    <div className={`w-10 h-10 rounded-lg border-2 border-dashed border-gray-300 hover:border-red-400 flex items-center justify-center transition-colors ${uploadingIcon ? 'opacity-50' : ''}`}>
                      {formData.icon_url ? (
                        <img src={formData.icon_url} alt="icon" className="w-full h-full object-cover rounded-lg" />
                      ) : uploadingIcon ? (
                        <div className="w-4 h-4 border-2 border-gray-300 border-t-red-500 rounded-full animate-spin" />
                      ) : (
                        <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                      )}
                    </div>
                  </label>
                  {formData.icon_url && (
                    <button
                      type="button"
                      onClick={() => setFormData({ ...formData, icon_url: '' })}
                      className="text-red-500 hover:text-red-700 text-sm"
                    >
                      清除
                    </button>
                  )}
                </div>
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

            {/* 解锁动画区域 - 只有史诗和传说级别显示 */}
            {canHaveAnimation && (
              <div className="border-t border-gray-200 pt-4">
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-gray-700">
                    解锁动画 <span className="text-purple-600">(史诗/传说专属)</span>
                  </label>
                  <div className="flex items-center gap-2">
                    {formData.unlock_animation && (
                      <button
                        type="button"
                        onClick={() => setShowAnimationPreview(true)}
                        className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors flex items-center gap-1"
                      >
                        <span>▶️</span> 预览动画
                      </button>
                    )}
                    <button
                      type="button"
                      onClick={() => setShowAnimationDialog(true)}
                      className="px-3 py-1 text-sm bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors flex items-center gap-1"
                    >
                      <span>✨</span> AI 生成动画
                    </button>
                  </div>
                </div>
                {formData.unlock_animation ? (
                  <div className="relative">
                    <textarea
                      value={formData.unlock_animation}
                      onChange={e => setFormData({ ...formData, unlock_animation: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent font-mono text-xs bg-gray-900 text-green-400"
                      rows={6}
                      placeholder="// 动画代码..."
                    />
                    <button
                      type="button"
                      onClick={() => setFormData({ ...formData, unlock_animation: '' })}
                      className="absolute top-2 right-2 text-gray-400 hover:text-red-400"
                    >
                      清除
                    </button>
                  </div>
                ) : (
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center text-gray-500">
                    <p className="mb-2">暂无解锁动画</p>
                    <p className="text-sm">点击上方按钮让 AI 为你生成炫酷的解锁动画</p>
                  </div>
                )}
              </div>
            )}

            {/* 普通/稀有级别 - 也可以预览默认动画 */}
            {!canHaveAnimation && (
              <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-600 flex items-center justify-between">
                <div>
                  <span className="font-medium">提示：</span> 普通和稀有级别的勋章解锁时会显示默认的粒子动画效果。
                </div>
                <button
                  type="button"
                  onClick={() => setShowAnimationPreview(true)}
                  className="px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors flex items-center gap-1"
                >
                  <span>▶️</span> 预览动画
                </button>
              </div>
            )}

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

        {/* AI 动画生成对话框 */}
        {showAnimationDialog && (
          <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-10">
            <div className="bg-white rounded-xl w-[500px] p-6 shadow-2xl">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <span className="text-2xl">✨</span> AI 生成解锁动画
              </h3>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  描述你想要的动画效果
                </label>
                <textarea
                  value={animationPrompt}
                  onChange={e => setAnimationPrompt(e.target.value)}
                  placeholder={`例如：\n- 金色光芒从中心向外扩散，勋章旋转出现\n- 粒子特效环绕，然后汇聚成勋章形状\n- 闪电效果，勋章从天而降`}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  rows={5}
                />
              </div>
              <div className="bg-purple-50 rounded-lg p-3 mb-4 text-sm text-purple-700">
                <p className="font-medium mb-1">当前勋章信息：</p>
                <p>名称：{formData.name || '未命名'}</p>
                <p>稀有度：{RARITY_LABELS[formData.rarity as BadgeRarity]}</p>
              </div>
              <div className="flex justify-end gap-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowAnimationDialog(false);
                    setAnimationPrompt('');
                  }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
                >
                  取消
                </button>
                <button
                  onClick={handleGenerateAnimation}
                  disabled={generatingAnimation || !animationPrompt.trim()}
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {generatingAnimation ? (
                    <>
                      <span className="animate-spin">⏳</span>
                      生成中...
                    </>
                  ) : (
                    <>
                      ✨ 生成动画
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* 动画预览对话框 */}
        {showAnimationPreview && (
          <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50">
            <div className="relative w-full h-full flex items-center justify-center">
              {/* 关闭按钮 */}
              <button
                onClick={() => setShowAnimationPreview(false)}
                className="absolute top-4 right-4 text-white/80 hover:text-white text-lg z-10 bg-black/50 rounded-full w-10 h-10 flex items-center justify-center"
              >
                ✕
              </button>

              {/* 动画预览区域 */}
              <AnimationPreview
                badgeName={formData.name || '勋章名称'}
                badgeIcon={formData.icon || '🏆'}
                badgeIconUrl={formData.icon_url}
                badgeDescription={formData.description || '勋章描述'}
                rarity={formData.rarity as BadgeRarity}
                customAnimation={formData.unlock_animation}
                onClose={() => setShowAnimationPreview(false)}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// 动画预览组件 - 根据勋章内容渲染不同效果
function AnimationPreview({
  badgeName,
  badgeIcon,
  badgeIconUrl,
  badgeDescription,
  rarity,
  customAnimation,
  onClose,
}: {
  badgeName: string;
  badgeIcon: string;
  badgeIconUrl?: string;
  badgeDescription: string;
  rarity: BadgeRarity;
  customAnimation?: string;
  onClose: () => void;
}) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [phase, setPhase] = useState<'particles' | 'reveal' | 'done'>('particles');
  const [animKey, setAnimKey] = useState(0);

  // 解析自定义动画配置
  const animConfig = customAnimation ? (() => {
    try {
      return JSON.parse(customAnimation);
    } catch {
      return null;
    }
  })() : null;

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    canvas.width = 500;
    canvas.height = 400;

    const centerX = canvas.width / 2;
    const centerY = canvas.height / 2;

    // 从配置获取颜色，或使用默认颜色
    let particleColors: string[] = [];
    let glowColor = '';

    if (animConfig?.colors) {
      particleColors = animConfig.colors.map((c: string) => {
        if (c.startsWith('#')) {
          const r = parseInt(c.slice(1, 3), 16);
          const g = parseInt(c.slice(3, 5), 16);
          const b = parseInt(c.slice(5, 7), 16);
          return `rgba(${r}, ${g}, ${b}, 1)`;
        }
        return c;
      });
      glowColor = particleColors[0];
    } else {
      const defaultColors = {
        common: ['rgba(100, 150, 255, 1)', 'rgba(150, 100, 255, 1)'],
        rare: ['rgba(80, 180, 255, 1)', 'rgba(120, 80, 255, 1)'],
        epic: ['rgba(180, 80, 255, 1)', 'rgba(255, 100, 180, 1)'],
        legendary: ['rgba(255, 200, 50, 1)', 'rgba(255, 100, 50, 1)'],
      };
      particleColors = defaultColors[rarity] || defaultColors.common;
      glowColor = rarity === 'legendary' ? 'rgba(255, 180, 50, 1)' :
                  rarity === 'epic' ? 'rgba(180, 80, 255, 1)' :
                  rarity === 'rare' ? 'rgba(80, 180, 255, 1)' : 'rgba(255, 80, 80, 1)';
    }

    // 获取动画类型
    const animType = animConfig?.type || 'default';
    const effect = animConfig?.effect || 'converge';

    // 粒子数组
    interface ParticleObj {
      x: number; y: number; vx: number; vy: number;
      size: number; color: string; alpha: number;
      life: number; maxLife: number; shape?: string;
      rotation?: number; rotationSpeed?: number;
    }
    const particles: ParticleObj[] = [];

    // 特效元素数组
    interface EffectObj {
      x: number; y: number; radius: number;
      alpha: number; color: string; type: string;
      angle?: number; scale?: number;
    }
    const effects: EffectObj[] = [];

    let frame = 0;
    let animationId: number;

    // 根据动画类型创建粒子
    const createParticle = () => {
      const color = particleColors[Math.floor(Math.random() * particleColors.length)];
      let particle: ParticleObj;

      switch (animType) {
        case 'target_lock':
        case 'perfect_aim':
          // 十字准星效果 - 从四个方向射入
          const dir = Math.floor(Math.random() * 4);
          const startPos = [
            { x: 0, y: centerY }, { x: canvas.width, y: centerY },
            { x: centerX, y: 0 }, { x: centerX, y: canvas.height }
          ][dir];
          particle = {
            x: startPos.x, y: startPos.y,
            vx: (centerX - startPos.x) * 0.03,
            vy: (centerY - startPos.y) * 0.03,
            size: 3, color, alpha: 1, life: 0, maxLife: 60, shape: 'line'
          };
          break;

        case 'data_stream':
        case 'matrix_code':
          // 数据流效果 - 从上方落下
          particle = {
            x: Math.random() * canvas.width, y: -20,
            vx: 0, vy: 3 + Math.random() * 4,
            size: 2, color, alpha: 0.8, life: 0, maxLife: 120, shape: 'rect'
          };
          break;

        case 'medal_shower':
        case 'coronation':
          // 奖章/王冠从上方落下
          particle = {
            x: centerX + (Math.random() - 0.5) * 200, y: -30,
            vx: (Math.random() - 0.5) * 2, vy: 2 + Math.random() * 2,
            size: 8 + Math.random() * 8, color, alpha: 1, life: 0, maxLife: 150,
            shape: 'star', rotation: 0, rotationSpeed: 0.05 + Math.random() * 0.1
          };
          break;

        case 'phoenix_rise':
        case 'eternal_flame':
        case 'sun_rise':
        case 'streak_fire':
          // 火焰上升效果
          particle = {
            x: centerX + (Math.random() - 0.5) * 100, y: canvas.height,
            vx: (Math.random() - 0.5) * 2, vy: -3 - Math.random() * 3,
            size: 4 + Math.random() * 6, color, alpha: 1, life: 0, maxLife: 80, shape: 'flame'
          };
          break;

        case 'gear_system':
        case 'hologram':
        case 'vr_world':
          // 齿轮/全息效果 - 环绕旋转
          const gearAngle = Math.random() * Math.PI * 2;
          const gearDist = 80 + Math.random() * 60;
          particle = {
            x: centerX + Math.cos(gearAngle) * gearDist, y: centerY + Math.sin(gearAngle) * gearDist,
            vx: 0, vy: 0, size: 3, color, alpha: 0.8, life: 0, maxLife: 100,
            shape: 'gear', rotation: gearAngle, rotationSpeed: 0.02
          };
          break;

        case 'big_bang':
        case 'nebula_form':
          // 宇宙大爆炸 - 从中心爆发
          const explosionAngle = Math.random() * Math.PI * 2;
          const speed = 2 + Math.random() * 5;
          particle = {
            x: centerX, y: centerY,
            vx: Math.cos(explosionAngle) * speed, vy: Math.sin(explosionAngle) * speed,
            size: 2 + Math.random() * 4, color, alpha: 1, life: 0, maxLife: 100, shape: 'star'
          };
          break;

        case 'butterfly_emerge':
          // 蝴蝶效果 - 翅膀形状
          particle = {
            x: centerX + (Math.random() - 0.5) * 60, y: centerY + (Math.random() - 0.5) * 60,
            vx: (Math.random() - 0.5) * 3, vy: -1 - Math.random() * 2,
            size: 3 + Math.random() * 4, color, alpha: 1, life: 0, maxLife: 100, shape: 'wing'
          };
          break;

        case 'dragon_treasure':
        case 'treasure_chest':
          // 金龙宝库 - 金币喷涌
          particle = {
            x: centerX, y: centerY + 50,
            vx: (Math.random() - 0.5) * 8, vy: -5 - Math.random() * 5,
            size: 6 + Math.random() * 4, color: 'rgba(255, 215, 0, 1)', alpha: 1,
            life: 0, maxLife: 80, shape: 'coin', rotation: 0, rotationSpeed: 0.15
          };
          break;

        case 'calendar_flip':
        case 'seasons_cycle':
        case 'time_lord':
        case 'hourglass':
          // 时间/日历效果 - 旋转的时间碎片
          const timeAngle = Math.random() * Math.PI * 2;
          const timeDist = 50 + Math.random() * 100;
          particle = {
            x: centerX + Math.cos(timeAngle) * timeDist, y: centerY + Math.sin(timeAngle) * timeDist,
            vx: Math.cos(timeAngle + Math.PI/2) * 2, vy: Math.sin(timeAngle + Math.PI/2) * 2,
            size: 4 + Math.random() * 4, color, alpha: 0.9, life: 0, maxLife: 100,
            shape: 'rect', rotation: timeAngle, rotationSpeed: 0.08
          };
          break;

        case 'chain_link':
          // 链条效果 - 连接的环
          const chainAngle = Math.random() * Math.PI * 2;
          particle = {
            x: centerX + Math.cos(chainAngle) * 120, y: centerY + Math.sin(chainAngle) * 120,
            vx: (centerX - (centerX + Math.cos(chainAngle) * 120)) * 0.02,
            vy: (centerY - (centerY + Math.sin(chainAngle) * 120)) * 0.02,
            size: 5, color, alpha: 1, life: 0, maxLife: 80, shape: 'ring'
          };
          break;

        case 'check_cascade':
          // 勾选瀑布效果
          particle = {
            x: Math.random() * canvas.width, y: -20,
            vx: (Math.random() - 0.5) * 2, vy: 2 + Math.random() * 3,
            size: 6 + Math.random() * 4, color, alpha: 1, life: 0, maxLife: 120,
            shape: 'check', rotation: 0
          };
          break;

        case 'conquest':
        case 'grand_hall':
        case 'temple_ascend':
          // 征服/殿堂效果 - 从下方升起的柱子
          particle = {
            x: centerX + (Math.random() - 0.5) * 200, y: canvas.height + 20,
            vx: 0, vy: -2 - Math.random() * 2,
            size: 8 + Math.random() * 8, color, alpha: 1, life: 0, maxLife: 100, shape: 'pillar'
          };
          break;

        case 'diamond_form':
          // 钻石形成效果
          const diamondAngle = Math.random() * Math.PI * 2;
          const diamondDist = 100 + Math.random() * 50;
          particle = {
            x: centerX + Math.cos(diamondAngle) * diamondDist, y: centerY + Math.sin(diamondAngle) * diamondDist,
            vx: (centerX - (centerX + Math.cos(diamondAngle) * diamondDist)) * 0.025,
            vy: (centerY - (centerY + Math.sin(diamondAngle) * diamondDist)) * 0.025,
            size: 5 + Math.random() * 5, color, alpha: 1, life: 0, maxLife: 80, shape: 'diamond'
          };
          break;

        case 'enlightenment':
        case 'graduation':
          // 启蒙/毕业效果 - 光芒四射
          const lightAngle = Math.random() * Math.PI * 2;
          particle = {
            x: centerX, y: centerY,
            vx: Math.cos(lightAngle) * (2 + Math.random() * 3), vy: Math.sin(lightAngle) * (2 + Math.random() * 3),
            size: 3 + Math.random() * 4, color, alpha: 1, life: 0, maxLife: 70, shape: 'ray'
          };
          break;

        case 'error_fix':
        case 'transformation':
          // 错误修复/转化效果 - X变成勾
          particle = {
            x: centerX + (Math.random() - 0.5) * 150, y: centerY + (Math.random() - 0.5) * 150,
            vx: (centerX - (centerX + (Math.random() - 0.5) * 150)) * 0.02,
            vy: (centerY - (centerY + (Math.random() - 0.5) * 150)) * 0.02,
            size: 4, color, alpha: 1, life: 0, maxLife: 80, shape: Math.random() > 0.5 ? 'x' : 'check'
          };
          break;

        case 'knowledge_galaxy':
        case 'starship_launch':
          // 知识星系/星舰效果 - 星星轨迹
          const starAngle = Math.random() * Math.PI * 2;
          const starDist = 30 + Math.random() * 120;
          particle = {
            x: centerX + Math.cos(starAngle) * starDist, y: centerY + Math.sin(starAngle) * starDist,
            vx: Math.cos(starAngle + Math.PI/2) * 3, vy: Math.sin(starAngle + Math.PI/2) * 3,
            size: 2 + Math.random() * 3, color, alpha: 1, life: 0, maxLife: 100, shape: 'star'
          };
          break;

        case 'knowledge_tree':
          // 知识树效果 - 叶子飘落
          particle = {
            x: centerX + (Math.random() - 0.5) * 100, y: centerY - 80,
            vx: (Math.random() - 0.5) * 2, vy: 1 + Math.random() * 2,
            size: 4 + Math.random() * 4, color, alpha: 1, life: 0, maxLife: 100,
            shape: 'leaf', rotation: Math.random() * Math.PI * 2, rotationSpeed: 0.05
          };
          break;

        case 'lightbulb_array':
        case 'question_burst':
        case 'wisdom_eye':
          // 灯泡/问号效果 - 闪烁的光点
          const bulbAngle = Math.random() * Math.PI * 2;
          const bulbDist = 40 + Math.random() * 80;
          particle = {
            x: centerX + Math.cos(bulbAngle) * bulbDist, y: centerY + Math.sin(bulbAngle) * bulbDist,
            vx: 0, vy: -0.5 - Math.random(),
            size: 5 + Math.random() * 5, color, alpha: 0.5 + Math.random() * 0.5, life: 0, maxLife: 80, shape: 'glow'
          };
          break;

        case 'marathon':
          // 马拉松效果 - 速度线
          particle = {
            x: 0, y: centerY + (Math.random() - 0.5) * 100,
            vx: 8 + Math.random() * 6, vy: 0,
            size: 2, color, alpha: 1, life: 0, maxLife: 60, shape: 'speedline'
          };
          break;

        case 'neural_network':
          // 神经网络效果 - 连接的节点
          const nodeAngle = Math.random() * Math.PI * 2;
          const nodeDist = 40 + Math.random() * 100;
          particle = {
            x: centerX + Math.cos(nodeAngle) * nodeDist, y: centerY + Math.sin(nodeAngle) * nodeDist,
            vx: (Math.random() - 0.5) * 2, vy: (Math.random() - 0.5) * 2,
            size: 4 + Math.random() * 4, color, alpha: 0.8, life: 0, maxLife: 100, shape: 'node'
          };
          break;

        case 'progress_bar':
          // 进度条效果 - 水平填充
          particle = {
            x: centerX - 100 + Math.random() * 50, y: centerY + (Math.random() - 0.5) * 20,
            vx: 3 + Math.random() * 2, vy: 0,
            size: 4 + Math.random() * 4, color, alpha: 1, life: 0, maxLife: 80, shape: 'square'
          };
          break;

        case 'world_map':
          // 世界地图效果 - 定位点
          particle = {
            x: centerX + (Math.random() - 0.5) * 200, y: centerY + (Math.random() - 0.5) * 150,
            vx: 0, vy: -1,
            size: 4 + Math.random() * 4, color, alpha: 0, life: 0, maxLife: 60, shape: 'pin'
          };
          break;

        case 'writing_flow':
          // 书写效果 - 墨水飞溅
          particle = {
            x: centerX + (Math.random() - 0.5) * 60, y: centerY,
            vx: (Math.random() - 0.5) * 4, vy: (Math.random() - 0.5) * 4,
            size: 2 + Math.random() * 4, color, alpha: 1, life: 0, maxLife: 60, shape: 'ink'
          };
          break;

        default:
          // 默认汇聚效果
          const defaultAngle = Math.random() * Math.PI * 2;
          const defaultDist = 80 + Math.random() * 150;
          particle = {
            x: centerX + Math.cos(defaultAngle) * defaultDist,
            y: centerY + Math.sin(defaultAngle) * defaultDist,
            vx: 0, vy: 0, size: 2 + Math.random() * 5, color, alpha: 0.8, life: 0, maxLife: 80
          };
          const dx = centerX - particle.x;
          const dy = centerY - particle.y;
          const spd = 1.5 + Math.random() * 2.5;
          particle.vx = dx * 0.015 * spd;
          particle.vy = dy * 0.015 * spd;
      }

      return particle;
    };

    // 绘制粒子
    const drawParticle = (p: ParticleObj) => {
      ctx.save();
      ctx.globalAlpha = p.alpha;

      switch (p.shape) {
        case 'star':
          ctx.translate(p.x, p.y);
          ctx.rotate(p.rotation || 0);
          ctx.beginPath();
          for (let i = 0; i < 5; i++) {
            const outerAngle = (i * 4 * Math.PI) / 5 - Math.PI / 2;
            const innerAngle = outerAngle + Math.PI / 5;
            ctx.lineTo(Math.cos(outerAngle) * p.size, Math.sin(outerAngle) * p.size);
            ctx.lineTo(Math.cos(innerAngle) * p.size * 0.5, Math.sin(innerAngle) * p.size * 0.5);
          }
          ctx.closePath();
          ctx.fillStyle = p.color;
          ctx.fill();
          break;

        case 'flame':
          const flameGradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size);
          flameGradient.addColorStop(0, p.color);
          flameGradient.addColorStop(0.5, p.color.replace('1)', '0.5)'));
          flameGradient.addColorStop(1, 'rgba(0,0,0,0)');
          ctx.fillStyle = flameGradient;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
          ctx.fill();
          break;

        case 'rect':
          ctx.translate(p.x, p.y);
          ctx.rotate(p.rotation || 0);
          ctx.fillStyle = p.color;
          ctx.fillRect(-1, 0, 2, 10 + Math.random() * 10);
          break;

        case 'coin':
          ctx.translate(p.x, p.y);
          ctx.rotate(p.rotation || 0);
          ctx.beginPath();
          ctx.ellipse(0, 0, p.size, p.size * 0.6, 0, 0, Math.PI * 2);
          ctx.fillStyle = p.color;
          ctx.fill();
          ctx.strokeStyle = 'rgba(255, 180, 0, 0.8)';
          ctx.lineWidth = 2;
          ctx.stroke();
          break;

        case 'gear':
          ctx.translate(p.x, p.y);
          ctx.rotate(p.rotation || 0);
          ctx.beginPath();
          for (let i = 0; i < 8; i++) {
            const gearAngle = (i * Math.PI) / 4;
            const r = i % 2 === 0 ? p.size : p.size * 0.6;
            ctx.lineTo(Math.cos(gearAngle) * r, Math.sin(gearAngle) * r);
          }
          ctx.closePath();
          ctx.fillStyle = p.color;
          ctx.fill();
          break;

        case 'ring':
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
          ctx.strokeStyle = p.color;
          ctx.lineWidth = 2;
          ctx.stroke();
          break;

        case 'check':
          ctx.translate(p.x, p.y);
          ctx.strokeStyle = p.color;
          ctx.lineWidth = 3;
          ctx.lineCap = 'round';
          ctx.beginPath();
          ctx.moveTo(-p.size * 0.5, 0);
          ctx.lineTo(-p.size * 0.1, p.size * 0.4);
          ctx.lineTo(p.size * 0.5, -p.size * 0.4);
          ctx.stroke();
          break;

        case 'x':
          ctx.translate(p.x, p.y);
          ctx.strokeStyle = p.color;
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.moveTo(-p.size * 0.4, -p.size * 0.4);
          ctx.lineTo(p.size * 0.4, p.size * 0.4);
          ctx.moveTo(p.size * 0.4, -p.size * 0.4);
          ctx.lineTo(-p.size * 0.4, p.size * 0.4);
          ctx.stroke();
          break;

        case 'pillar':
          ctx.fillStyle = p.color;
          ctx.fillRect(p.x - p.size / 4, p.y, p.size / 2, p.size * 2);
          // 柱头
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size / 2, Math.PI, 0);
          ctx.fill();
          break;

        case 'diamond':
          ctx.translate(p.x, p.y);
          ctx.rotate(Math.PI / 4);
          ctx.fillStyle = p.color;
          ctx.fillRect(-p.size / 2, -p.size / 2, p.size, p.size);
          // 高光
          ctx.fillStyle = 'rgba(255,255,255,0.4)';
          ctx.fillRect(-p.size / 4, -p.size / 2, p.size / 4, p.size / 2);
          break;

        case 'ray':
          ctx.strokeStyle = p.color;
          ctx.lineWidth = 2;
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          const rayLen = p.size * 3;
          const rayAngle = Math.atan2(p.vy, p.vx);
          ctx.lineTo(p.x + Math.cos(rayAngle) * rayLen, p.y + Math.sin(rayAngle) * rayLen);
          ctx.stroke();
          break;

        case 'leaf':
          ctx.translate(p.x, p.y);
          ctx.rotate(p.rotation || 0);
          ctx.fillStyle = p.color;
          ctx.beginPath();
          ctx.ellipse(0, 0, p.size, p.size * 0.5, 0, 0, Math.PI * 2);
          ctx.fill();
          // 叶脉
          ctx.strokeStyle = 'rgba(255,255,255,0.3)';
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(-p.size, 0);
          ctx.lineTo(p.size, 0);
          ctx.stroke();
          break;

        case 'glow':
          const glowGradient = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, p.size);
          glowGradient.addColorStop(0, p.color);
          glowGradient.addColorStop(0.5, p.color.replace('1)', '0.3)'));
          glowGradient.addColorStop(1, 'rgba(0,0,0,0)');
          ctx.fillStyle = glowGradient;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size * 1.5, 0, Math.PI * 2);
          ctx.fill();
          break;

        case 'speedline':
          ctx.strokeStyle = p.color;
          ctx.lineWidth = p.size;
          ctx.lineCap = 'round';
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(p.x + 30, p.y);
          ctx.stroke();
          break;

        case 'node':
          // 节点
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
          ctx.fillStyle = p.color;
          ctx.fill();
          // 连接线
          ctx.strokeStyle = p.color.replace('1)', '0.3)');
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(p.x, p.y);
          ctx.lineTo(centerX, centerY);
          ctx.stroke();
          break;

        case 'square':
          ctx.fillStyle = p.color;
          ctx.fillRect(p.x - p.size / 2, p.y - p.size / 2, p.size, p.size);
          break;

        case 'pin':
          // 定位图钉
          ctx.fillStyle = p.color;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
          ctx.fill();
          ctx.beginPath();
          ctx.moveTo(p.x, p.y + p.size);
          ctx.lineTo(p.x, p.y + p.size * 2);
          ctx.strokeStyle = p.color;
          ctx.lineWidth = 2;
          ctx.stroke();
          break;

        case 'ink':
          // 墨水滴
          ctx.fillStyle = p.color;
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
          ctx.fill();
          // 飞溅效果
          for (let i = 0; i < 3; i++) {
            const splashAngle = Math.random() * Math.PI * 2;
            const splashDist = p.size * (1 + Math.random());
            ctx.beginPath();
            ctx.arc(p.x + Math.cos(splashAngle) * splashDist, p.y + Math.sin(splashAngle) * splashDist, p.size * 0.3, 0, Math.PI * 2);
            ctx.fill();
          }
          break;

        case 'wing':
          ctx.translate(p.x, p.y);
          ctx.fillStyle = p.color;
          // 左翅
          ctx.beginPath();
          ctx.ellipse(-p.size, 0, p.size * 1.2, p.size * 0.6, -0.3, 0, Math.PI * 2);
          ctx.fill();
          // 右翅
          ctx.beginPath();
          ctx.ellipse(p.size, 0, p.size * 1.2, p.size * 0.6, 0.3, 0, Math.PI * 2);
          ctx.fill();
          break;

        default:
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
          ctx.fillStyle = p.color;
          ctx.fill();
      }

      ctx.restore();
    };

    // 创建特效
    const createEffect = () => {
      effects.push({
        x: centerX, y: centerY, radius: 0, alpha: 0.8, color: glowColor, type: 'ring'
      });
    };

    // 绘制主体动画元素
    const drawMainElement = (progress: number) => {
      ctx.save();
      const alpha = Math.min(progress * 2, 1);
      ctx.globalAlpha = alpha;

      switch (animType) {
        case 'coronation':
        case 'medal_shower': {
          // 皇冠动画 - 从上方降落
          const crownY = centerY - 150 + progress * 80;
          const scale = 0.5 + progress * 0.5;
          ctx.translate(centerX, crownY);
          ctx.scale(scale, scale);

          // 皇冠主体
          const size = 60;
          const gradient = ctx.createLinearGradient(-size, -size, size, size);
          gradient.addColorStop(0, '#FFD700');
          gradient.addColorStop(0.5, '#FFA500');
          gradient.addColorStop(1, '#FFD700');
          ctx.fillStyle = gradient;
          ctx.shadowColor = '#FFD700';
          ctx.shadowBlur = 30;

          ctx.beginPath();
          ctx.moveTo(-size, size * 0.4);
          ctx.lineTo(-size * 0.7, -size * 0.3);
          ctx.lineTo(-size * 0.4, size * 0.1);
          ctx.lineTo(0, -size);
          ctx.lineTo(size * 0.4, size * 0.1);
          ctx.lineTo(size * 0.7, -size * 0.3);
          ctx.lineTo(size, size * 0.4);
          ctx.closePath();
          ctx.fill();
          ctx.fillRect(-size, size * 0.4, size * 2, size * 0.25);

          // 宝石
          const gems = [[-size * 0.7, -size * 0.1, '#FF0000'], [0, -size * 0.7, '#00FF00'], [size * 0.7, -size * 0.1, '#0000FF']];
          gems.forEach(([x, y, color]) => {
            ctx.fillStyle = color as string;
            ctx.shadowColor = color as string;
            ctx.beginPath();
            ctx.arc(x as number, y as number, 10, 0, Math.PI * 2);
            ctx.fill();
          });
          break;
        }

        case 'phoenix_rise':
        case 'eternal_flame':
        case 'streak_fire': {
          // 火焰/凤凰动画
          const flameHeight = 120 * progress;
          ctx.translate(centerX, centerY + 50);

          // 多层火焰
          for (let layer = 0; layer < 5; layer++) {
            const layerProgress = Math.max(0, progress - layer * 0.1);
            if (layerProgress <= 0) continue;

            const layerHeight = flameHeight * (1 - layer * 0.15);
            const layerWidth = 40 - layer * 5;
            const hue = 30 + layer * 10;

            ctx.fillStyle = `hsla(${hue}, 100%, ${60 - layer * 5}%, ${0.8 - layer * 0.1})`;
            ctx.beginPath();
            ctx.moveTo(-layerWidth, 0);
            ctx.quadraticCurveTo(-layerWidth * 0.5, -layerHeight * 0.5, 0, -layerHeight);
            ctx.quadraticCurveTo(layerWidth * 0.5, -layerHeight * 0.5, layerWidth, 0);
            ctx.closePath();
            ctx.fill();
          }

          // 凤凰翅膀（仅 phoenix_rise）
          if (animType === 'phoenix_rise' && progress > 0.5) {
            const wingProgress = (progress - 0.5) * 2;
            ctx.globalAlpha = wingProgress;
            ctx.fillStyle = 'rgba(255, 100, 50, 0.6)';
            // 左翅
            ctx.beginPath();
            ctx.ellipse(-60, -40, 50 * wingProgress, 25, -0.5, 0, Math.PI * 2);
            ctx.fill();
            // 右翅
            ctx.beginPath();
            ctx.ellipse(60, -40, 50 * wingProgress, 25, 0.5, 0, Math.PI * 2);
            ctx.fill();
          }
          break;
        }

        case 'diamond_form': {
          // 钻石形成动画
          const diamondSize = 80 * progress;
          ctx.translate(centerX, centerY);
          ctx.rotate(Math.PI / 4 + frame * 0.01);

          // 钻石主体
          const gradient = ctx.createLinearGradient(-diamondSize, -diamondSize, diamondSize, diamondSize);
          gradient.addColorStop(0, 'rgba(100, 200, 255, 0.9)');
          gradient.addColorStop(0.5, 'rgba(200, 230, 255, 1)');
          gradient.addColorStop(1, 'rgba(100, 200, 255, 0.9)');
          ctx.fillStyle = gradient;
          ctx.shadowColor = '#00BFFF';
          ctx.shadowBlur = 40;

          ctx.beginPath();
          ctx.moveTo(0, -diamondSize);
          ctx.lineTo(diamondSize, 0);
          ctx.lineTo(0, diamondSize);
          ctx.lineTo(-diamondSize, 0);
          ctx.closePath();
          ctx.fill();

          // 高光
          ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
          ctx.beginPath();
          ctx.moveTo(0, -diamondSize * 0.8);
          ctx.lineTo(diamondSize * 0.3, -diamondSize * 0.2);
          ctx.lineTo(0, 0);
          ctx.lineTo(-diamondSize * 0.3, -diamondSize * 0.2);
          ctx.closePath();
          ctx.fill();
          break;
        }

        case 'gear_system':
        case 'hologram': {
          // 齿轮系统动画
          const gearSize = 50;
          const rotation = frame * 0.03;

          // 主齿轮
          ctx.translate(centerX, centerY);
          ctx.rotate(rotation);
          drawGear(ctx, 0, 0, gearSize, 12, particleColors[0]);

          // 副齿轮
          ctx.rotate(-rotation * 2);
          drawGear(ctx, gearSize * 1.8, 0, gearSize * 0.7, 8, particleColors[1] || particleColors[0]);
          ctx.rotate(rotation * 2);
          drawGear(ctx, -gearSize * 1.8, 0, gearSize * 0.7, 8, particleColors[1] || particleColors[0]);

          // 全息效果
          if (animType === 'hologram') {
            ctx.globalAlpha = 0.3 + Math.sin(frame * 0.1) * 0.2;
            ctx.strokeStyle = particleColors[0];
            ctx.lineWidth = 2;
            for (let r = 30; r < 120; r += 20) {
              ctx.beginPath();
              ctx.arc(0, 0, r, 0, Math.PI * 2);
              ctx.stroke();
            }
          }
          break;
        }

        case 'target_lock':
        case 'perfect_aim': {
          // 瞄准镜动画
          ctx.translate(centerX, centerY);
          const targetSize = 80 * progress;

          ctx.strokeStyle = particleColors[0];
          ctx.lineWidth = 3;
          ctx.shadowColor = particleColors[0];
          ctx.shadowBlur = 15;

          // 外圈
          ctx.beginPath();
          ctx.arc(0, 0, targetSize, 0, Math.PI * 2);
          ctx.stroke();

          // 内圈
          ctx.beginPath();
          ctx.arc(0, 0, targetSize * 0.6, 0, Math.PI * 2);
          ctx.stroke();

          // 十字线
          ctx.beginPath();
          ctx.moveTo(-targetSize * 1.2, 0);
          ctx.lineTo(-targetSize * 0.3, 0);
          ctx.moveTo(targetSize * 0.3, 0);
          ctx.lineTo(targetSize * 1.2, 0);
          ctx.moveTo(0, -targetSize * 1.2);
          ctx.lineTo(0, -targetSize * 0.3);
          ctx.moveTo(0, targetSize * 0.3);
          ctx.lineTo(0, targetSize * 1.2);
          ctx.stroke();

          // 中心点
          ctx.fillStyle = '#FF0000';
          ctx.beginPath();
          ctx.arc(0, 0, 5, 0, Math.PI * 2);
          ctx.fill();
          break;
        }

        case 'time_lord':
        case 'hourglass': {
          // 沙漏动画
          ctx.translate(centerX, centerY);
          const hourglassHeight = 100 * progress;
          const hourglassWidth = 40;

          ctx.strokeStyle = particleColors[0];
          ctx.fillStyle = particleColors[1] || '#FFD700';
          ctx.lineWidth = 3;
          ctx.shadowColor = particleColors[0];
          ctx.shadowBlur = 20;

          // 上半部分
          ctx.beginPath();
          ctx.moveTo(-hourglassWidth, -hourglassHeight);
          ctx.lineTo(-hourglassWidth, -hourglassHeight * 0.3);
          ctx.lineTo(0, 0);
          ctx.lineTo(hourglassWidth, -hourglassHeight * 0.3);
          ctx.lineTo(hourglassWidth, -hourglassHeight);
          ctx.closePath();
          ctx.stroke();

          // 下半部分
          ctx.beginPath();
          ctx.moveTo(-hourglassWidth, hourglassHeight);
          ctx.lineTo(-hourglassWidth, hourglassHeight * 0.3);
          ctx.lineTo(0, 0);
          ctx.lineTo(hourglassWidth, hourglassHeight * 0.3);
          ctx.lineTo(hourglassWidth, hourglassHeight);
          ctx.closePath();
          ctx.stroke();

          // 沙子
          const sandLevel = (frame % 100) / 100;
          ctx.fillStyle = '#FFD700';
          ctx.globalAlpha = 0.7;
          // 上部沙子
          ctx.beginPath();
          ctx.moveTo(-hourglassWidth * (1 - sandLevel), -hourglassHeight * (1 - sandLevel * 0.7));
          ctx.lineTo(0, 0);
          ctx.lineTo(hourglassWidth * (1 - sandLevel), -hourglassHeight * (1 - sandLevel * 0.7));
          ctx.closePath();
          ctx.fill();
          // 下部沙子
          ctx.beginPath();
          ctx.moveTo(-hourglassWidth * sandLevel, hourglassHeight);
          ctx.lineTo(-hourglassWidth * sandLevel * 0.3, hourglassHeight * (1 - sandLevel * 0.5));
          ctx.lineTo(hourglassWidth * sandLevel * 0.3, hourglassHeight * (1 - sandLevel * 0.5));
          ctx.lineTo(hourglassWidth * sandLevel, hourglassHeight);
          ctx.closePath();
          ctx.fill();
          break;
        }

        case 'sun_rise':
        case 'enlightenment': {
          // 太阳升起动画
          const sunY = centerY + 50 - progress * 100;
          const sunSize = 50 * progress;

          // 光芒
          ctx.translate(centerX, sunY);
          const rayCount = 12;
          for (let i = 0; i < rayCount; i++) {
            const angle = (i / rayCount) * Math.PI * 2 + frame * 0.02;
            const rayLength = sunSize * 1.5 + Math.sin(frame * 0.1 + i) * 20;

            const gradient = ctx.createLinearGradient(0, 0, Math.cos(angle) * rayLength, Math.sin(angle) * rayLength);
            gradient.addColorStop(0, 'rgba(255, 200, 50, 0.8)');
            gradient.addColorStop(1, 'rgba(255, 200, 50, 0)');

            ctx.strokeStyle = gradient;
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.moveTo(0, 0);
            ctx.lineTo(Math.cos(angle) * rayLength, Math.sin(angle) * rayLength);
            ctx.stroke();
          }

          // 太阳主体
          const sunGradient = ctx.createRadialGradient(0, 0, 0, 0, 0, sunSize);
          sunGradient.addColorStop(0, '#FFFF00');
          sunGradient.addColorStop(0.5, '#FFA500');
          sunGradient.addColorStop(1, '#FF6600');
          ctx.fillStyle = sunGradient;
          ctx.shadowColor = '#FFD700';
          ctx.shadowBlur = 40;
          ctx.beginPath();
          ctx.arc(0, 0, sunSize, 0, Math.PI * 2);
          ctx.fill();
          break;
        }

        case 'check_cascade':
        case 'transformation': {
          // 大勾号动画
          ctx.translate(centerX, centerY);
          const checkSize = 80 * progress;

          ctx.strokeStyle = '#00FF00';
          ctx.lineWidth = 10;
          ctx.lineCap = 'round';
          ctx.lineJoin = 'round';
          ctx.shadowColor = '#00FF00';
          ctx.shadowBlur = 30;

          ctx.beginPath();
          ctx.moveTo(-checkSize * 0.5, 0);
          ctx.lineTo(-checkSize * 0.1, checkSize * 0.4);
          ctx.lineTo(checkSize * 0.5, -checkSize * 0.4);
          ctx.stroke();
          break;
        }

        case 'graduation': {
          // 毕业帽动画
          ctx.translate(centerX, centerY - 30);
          const capSize = 60 * progress;

          ctx.fillStyle = '#1a1a2e';
          ctx.shadowColor = particleColors[0];
          ctx.shadowBlur = 20;

          // 帽顶
          ctx.beginPath();
          ctx.moveTo(-capSize, 0);
          ctx.lineTo(0, -capSize * 0.4);
          ctx.lineTo(capSize, 0);
          ctx.lineTo(0, capSize * 0.4);
          ctx.closePath();
          ctx.fill();

          // 帽身
          ctx.fillStyle = '#1a1a2e';
          ctx.fillRect(-capSize * 0.4, 0, capSize * 0.8, capSize * 0.5);

          // 流苏
          ctx.strokeStyle = '#FFD700';
          ctx.lineWidth = 3;
          ctx.beginPath();
          ctx.moveTo(0, -capSize * 0.4);
          ctx.lineTo(capSize * 0.8, capSize * 0.3);
          ctx.stroke();
          ctx.fillStyle = '#FFD700';
          ctx.beginPath();
          ctx.arc(capSize * 0.8, capSize * 0.3, 8, 0, Math.PI * 2);
          ctx.fill();
          break;
        }

        default: {
          // 默认：发光圆环
          ctx.translate(centerX, centerY);
          const ringSize = 60 * progress;

          ctx.strokeStyle = particleColors[0];
          ctx.lineWidth = 4;
          ctx.shadowColor = particleColors[0];
          ctx.shadowBlur = 30;

          ctx.beginPath();
          ctx.arc(0, 0, ringSize, 0, Math.PI * 2);
          ctx.stroke();

          ctx.beginPath();
          ctx.arc(0, 0, ringSize * 0.6, 0, Math.PI * 2);
          ctx.stroke();
        }
      }
      ctx.restore();
    };

    // 辅助函数：绘制齿轮
    const drawGear = (ctx: CanvasRenderingContext2D, x: number, y: number, size: number, teeth: number, color: string) => {
      ctx.save();
      ctx.translate(x, y);
      ctx.fillStyle = color;
      ctx.shadowColor = color;
      ctx.shadowBlur = 15;

      ctx.beginPath();
      for (let i = 0; i < teeth * 2; i++) {
        const angle = (i * Math.PI) / teeth;
        const r = i % 2 === 0 ? size : size * 0.7;
        ctx.lineTo(Math.cos(angle) * r, Math.sin(angle) * r);
      }
      ctx.closePath();
      ctx.fill();

      // 中心孔
      ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
      ctx.beginPath();
      ctx.arc(0, 0, size * 0.25, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();
    };

    const animate = () => {
      // 清除画布（带拖尾效果）
      ctx.fillStyle = 'rgba(0, 0, 0, 0.15)';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      frame++;
      const progress = Math.min(frame / 80, 1);

      // 绘制主体动画元素
      drawMainElement(progress);

      // 生成粒子
      if (frame < 70 && frame % 2 === 0) {
        for (let i = 0; i < 4; i++) {
          particles.push(createParticle());
        }
      }

      // 生成光环特效
      if (frame % 25 === 0 && frame < 90) {
        createEffect();
      }

      // 更新和绘制特效
      for (let i = effects.length - 1; i >= 0; i--) {
        const e = effects[i];
        e.radius += 4;
        e.alpha *= 0.94;
        if (e.alpha < 0.01) {
          effects.splice(i, 1);
        } else {
          ctx.beginPath();
          ctx.arc(e.x, e.y, e.radius, 0, Math.PI * 2);
          ctx.strokeStyle = e.color.replace('1)', `${e.alpha})`);
          ctx.lineWidth = 3;
          ctx.stroke();
        }
      }

      // 更新和绘制粒子
      for (let i = particles.length - 1; i >= 0; i--) {
        const p = particles[i];
        p.x += p.vx;
        p.y += p.vy;
        p.life++;
        if (p.rotation !== undefined && p.rotationSpeed) {
          p.rotation += p.rotationSpeed;
        }

        // 重力效果（某些动画类型）
        if (['medal_shower', 'coronation', 'dragon_treasure', 'treasure_chest', 'check_cascade', 'knowledge_tree'].includes(animType)) {
          p.vy += 0.1;
        }

        // 淡入效果（某些动画类型）
        if (['world_map', 'pin'].includes(animType) || p.shape === 'pin') {
          if (p.life < 20) p.alpha = p.life / 20;
        }

        // 淡出
        if (p.life > p.maxLife * 0.7) {
          p.alpha *= 0.92;
        }

        if (p.alpha < 0.01 || p.life > p.maxLife || p.y > canvas.height + 50) {
          particles.splice(i, 1);
        } else {
          drawParticle(p);
        }
      }

      // 中心发光
      const glowIntensity = Math.sin(frame * 0.08) * 0.3 + 0.7;
      const centerGlow = ctx.createRadialGradient(centerX, centerY, 0, centerX, centerY, 100);
      centerGlow.addColorStop(0, glowColor.replace('1)', `${0.4 * glowIntensity})`));
      centerGlow.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = centerGlow;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // 切换到显示阶段
      if (frame > 85) {
        setPhase('reveal');
      }

      if (frame < 160) {
        animationId = requestAnimationFrame(animate);
      } else {
        setPhase('done');
      }
    };

    animate();

    return () => {
      if (animationId) cancelAnimationFrame(animationId);
    };
  }, [rarity, animKey, customAnimation]);

  return (
    <div className="relative flex flex-col items-center justify-center" style={{ width: 500, height: 450 }}>
      {/* Canvas 动画 */}
      <canvas
        ref={canvasRef}
        className="absolute top-0 left-0"
        style={{ opacity: phase === 'done' ? 0 : 1, transition: 'opacity 0.5s' }}
      />

      {/* 勋章卡片 */}
      <div
        className={`relative z-10 bg-gradient-to-br rounded-2xl p-8 shadow-2xl transform transition-all duration-700 ${
          phase === 'particles' ? 'scale-0 opacity-0' : 'scale-100 opacity-100'
        } ${
          rarity === 'legendary' ? 'from-yellow-500/20 to-orange-500/20 border-2 border-yellow-400/50' :
          rarity === 'epic' ? 'from-purple-500/20 to-pink-500/20 border-2 border-purple-400/50' :
          rarity === 'rare' ? 'from-blue-500/20 to-cyan-500/20 border-2 border-blue-400/50' :
          'from-gray-500/20 to-slate-500/20 border-2 border-gray-400/50'
        }`}
        style={{ minWidth: 280 }}
      >
        {/* 稀有度标签 */}
        <div className={`absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full text-xs font-bold ${
          rarity === 'legendary' ? 'bg-yellow-500 text-yellow-900' :
          rarity === 'epic' ? 'bg-purple-500 text-white' :
          rarity === 'rare' ? 'bg-blue-500 text-white' :
          'bg-gray-500 text-white'
        }`}>
          {RARITY_LABELS[rarity]}
        </div>

        {/* 图标 */}
        <div className="flex justify-center mb-4">
          {badgeIconUrl ? (
            <img src={badgeIconUrl} alt={badgeName} className="w-20 h-20 rounded-xl object-cover" />
          ) : (
            <span className="text-6xl">{badgeIcon}</span>
          )}
        </div>

        {/* 名称 */}
        <h3 className="text-xl font-bold text-white text-center mb-2">{badgeName}</h3>

        {/* 描述 */}
        <p className="text-sm text-white/70 text-center">{badgeDescription}</p>

        {/* 解锁提示 */}
        <div className="mt-4 pt-4 border-t border-white/20 text-center">
          <span className="text-green-400 text-sm font-medium">🎉 成就解锁！</span>
        </div>

        {/* 重播按钮 - 放在卡片内部 */}
        {phase === 'done' && (
          <button
            onClick={() => {
              setPhase('particles');
              setAnimKey(k => k + 1);
            }}
            className="mt-4 w-full px-4 py-2 bg-white/10 text-white/80 rounded-lg hover:bg-white/20 transition-colors text-sm"
          >
            🔄 重播动画
          </button>
        )}
      </div>
    </div>
  );
}
