'use client';

import { useState, useEffect, useCallback } from 'react';
import { studioProcessorsApi } from '@/lib/api/studio';
import { cn } from '@/lib/utils';
import type { ProcessorWithConfig, CreateProcessorRequest } from '@/types/studio';

// Icon mapping for processors
const ICON_MAP: Record<string, string> = {
  sparkles: '✨',
  Sparkles: '✨',
  book: '📖',
  brain: '🧠',
  rocket: '🚀',
  star: '⭐',
  zap: '⚡',
  target: '🎯',
  lightbulb: '💡',
};

export default function ProcessorsPage() {
  const [processors, setProcessors] = useState<ProcessorWithConfig[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [updatingId, setUpdatingId] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingProcessor, setEditingProcessor] = useState<ProcessorWithConfig | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  // Show message
  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 3000);
  };

  // Load all processors (including disabled)
  const loadProcessors = useCallback(async () => {
    try {
      setIsLoading(true);
      const { processors: data } = await studioProcessorsApi.list(true);
      setProcessors(data);
    } catch (error) {
      console.error('Failed to load processors:', error);
      showMessage('error', '加载处理器列表失败');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    loadProcessors();
  }, [loadProcessors]);

  // Toggle processor enabled state
  const toggleEnabled = async (processor: ProcessorWithConfig) => {
    setUpdatingId(processor.id);
    try {
      if (processor.enabled) {
        await studioProcessorsApi.disable(processor.id);
        showMessage('success', `已禁用 ${processor.name}`);
      } else {
        await studioProcessorsApi.enable(processor.id);
        showMessage('success', `已启用 ${processor.name}`);
      }
      await loadProcessors();
    } catch (error) {
      console.error('Failed to toggle processor:', error);
      showMessage('error', '操作失败');
    } finally {
      setUpdatingId(null);
    }
  };

  // Delete custom processor
  const deleteProcessor = async (processor: ProcessorWithConfig) => {
    if (processor.is_official) {
      showMessage('error', '官方处理器不能删除');
      return;
    }

    setDeletingId(processor.id);
    try {
      await studioProcessorsApi.delete(processor.id);
      showMessage('success', `已删除 ${processor.name}`);
      await loadProcessors();
    } catch (error) {
      console.error('Failed to delete processor:', error);
      showMessage('error', '删除失败');
    } finally {
      setDeletingId(null);
    }
  };

  // Handle create/edit modal close
  const handleModalClose = () => {
    setShowCreateModal(false);
    setEditingProcessor(null);
  };

  // Handle create/edit success
  const handleSaveSuccess = async () => {
    handleModalClose();
    await loadProcessors();
  };

  // Count enabled processors
  const enabledCount = processors.filter(p => p.enabled).length;
  const officialCount = processors.filter(p => p.is_official).length;
  const customCount = processors.filter(p => p.is_custom).length;

  return (
    <div className="space-y-6">
      {/* Message Toast */}
      {message && (
        <div className={cn(
          'fixed top-4 right-4 z-50 px-4 py-3 rounded-lg shadow-lg transition-all',
          message.type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
        )}>
          {message.text}
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">处理器管理</h1>
          <p className="text-slate-500 mt-1">管理课程讲解风格插件</p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors flex items-center gap-2"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 5v14M5 12h14" />
            </svg>
            添加处理器
          </button>
          <button
            onClick={loadProcessors}
            disabled={isLoading}
            className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors flex items-center gap-2"
          >
            <svg className={cn("w-5 h-5", isLoading && "animate-spin")} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M23 4v6h-6M1 20v-6h6" />
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
            </svg>
            刷新
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-slate-600">
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
          </svg>
          <span>共 {processors.length} 个处理器</span>
        </div>
        <span className="px-2 py-1 bg-green-100 text-green-700 text-sm rounded-md">
          {enabledCount} 个已启用
        </span>
        {officialCount > 0 && (
          <span className="px-2 py-1 bg-blue-100 text-blue-700 text-sm rounded-md flex items-center gap-1">
            <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
            </svg>
            {officialCount} 个官方
          </span>
        )}
        {customCount > 0 && (
          <span className="px-2 py-1 bg-purple-100 text-purple-700 text-sm rounded-md flex items-center gap-1">
            ✨ {customCount} 个自定义
          </span>
        )}
      </div>

      {/* Info Card */}
      <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-700">
          <strong>提示：</strong>启用的处理器会显示在 Studio 的「讲解风格」选择器中。
          禁用后将不会在 Studio 显示，但已生成的课程不受影响。
        </p>
      </div>

      {/* Processor List */}
      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <svg className="animate-spin text-slate-400 w-8 h-8" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M23 4v6h-6M1 20v-6h6" />
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
          </svg>
        </div>
      ) : (
        <div className="space-y-4">
          {processors.map((processor) => (
            <ProcessorCard
              key={processor.id}
              processor={processor}
              isUpdating={updatingId === processor.id}
              isDeleting={deletingId === processor.id}
              onToggle={() => toggleEnabled(processor)}
              onEdit={() => setEditingProcessor(processor)}
              onDelete={() => deleteProcessor(processor)}
            />
          ))}

          {processors.length === 0 && (
            <div className="bg-white rounded-xl border border-slate-200 p-12 text-center">
              <svg className="mx-auto mb-4 text-slate-300 w-12 h-12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z" />
              </svg>
              <p className="text-slate-500">暂无可用的处理器</p>
              <button
                onClick={() => setShowCreateModal(true)}
                className="mt-4 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
              >
                添加第一个处理器
              </button>
            </div>
          )}
        </div>
      )}

      {/* Create/Edit Modal */}
      {(showCreateModal || editingProcessor) && (
        <ProcessorModal
          processor={editingProcessor}
          onClose={handleModalClose}
          onSuccess={handleSaveSuccess}
          showMessage={showMessage}
        />
      )}
    </div>
  );
}

// Processor Card Component
interface ProcessorCardProps {
  processor: ProcessorWithConfig;
  isUpdating: boolean;
  isDeleting: boolean;
  onToggle: () => void;
  onEdit: () => void;
  onDelete: () => void;
}

function ProcessorCard({ processor, isUpdating, isDeleting, onToggle, onEdit, onDelete }: ProcessorCardProps) {
  const iconEmoji = ICON_MAP[processor.icon] || '📦';

  return (
    <div
      className={cn(
        'bg-white rounded-xl border p-4 transition-all',
        processor.enabled
          ? 'border-green-200'
          : 'border-slate-200 opacity-75'
      )}
    >
      <div className="flex items-center gap-4">
        {/* Drag Handle */}
        <div className="text-slate-300 cursor-grab">
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="9" cy="5" r="1" />
            <circle cx="9" cy="12" r="1" />
            <circle cx="9" cy="19" r="1" />
            <circle cx="15" cy="5" r="1" />
            <circle cx="15" cy="12" r="1" />
            <circle cx="15" cy="19" r="1" />
          </svg>
        </div>

        {/* Icon */}
        <div
          className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl"
          style={{ backgroundColor: `${processor.color}20` }}
        >
          {iconEmoji}
        </div>

        {/* Info */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-bold text-slate-900">{processor.name}</h3>
            {processor.is_official && (
              <span className="px-2 py-0.5 text-xs border border-blue-200 text-blue-600 rounded-md flex items-center gap-1">
                <svg className="w-3 h-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
                </svg>
                官方
              </span>
            )}
            {processor.is_custom && (
              <span className="px-2 py-0.5 text-xs border border-purple-200 text-purple-600 rounded-md">
                ✨ 自定义
              </span>
            )}
            <span
              className={cn(
                'px-2 py-0.5 text-xs rounded-md',
                processor.enabled ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'
              )}
            >
              {processor.enabled ? '已启用' : '已禁用'}
            </span>
          </div>
          <p className="text-sm text-slate-500 truncate">{processor.description}</p>
          <div className="flex items-center gap-2 mt-1">
            <span className="text-xs text-slate-400">ID: {processor.id}</span>
            {processor.version && (
              <span className="text-xs text-slate-400">v{processor.version}</span>
            )}
            {processor.tags?.map((tag) => (
              <span key={tag} className="px-1.5 py-0.5 text-xs border border-slate-200 text-slate-500 rounded">
                {tag}
              </span>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2">
          {/* Edit Button (only for custom processors) */}
          {processor.is_custom && (
            <button
              onClick={onEdit}
              className="p-2 border border-slate-200 text-slate-500 rounded-lg hover:bg-slate-50 transition-colors"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
              </svg>
            </button>
          )}

          {/* Delete Button (only for custom processors) */}
          {processor.is_custom && (
            <button
              onClick={onDelete}
              disabled={isDeleting}
              className="p-2 border border-red-200 text-red-500 rounded-lg hover:bg-red-50 transition-colors disabled:opacity-50"
            >
              {isDeleting ? (
                <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M23 4v6h-6M1 20v-6h6" />
                  <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
                </svg>
              ) : (
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                </svg>
              )}
            </button>
          )}

          {/* Toggle Button */}
          <button
            onClick={onToggle}
            disabled={isUpdating}
            className={cn(
              'px-3 py-2 rounded-lg transition-colors flex items-center gap-2 text-sm font-medium disabled:opacity-50',
              processor.enabled
                ? 'border border-red-200 text-red-500 hover:bg-red-50'
                : 'bg-green-500 text-white hover:bg-green-600'
            )}
          >
            {isUpdating ? (
              <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M23 4v6h-6M1 20v-6h6" />
                <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
              </svg>
            ) : processor.enabled ? (
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18.36 6.64a9 9 0 1 1-12.73 0M12 2v10" />
              </svg>
            ) : (
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M18.36 6.64A9 9 0 1 1 5.64 6.64M12 2v10" />
              </svg>
            )}
            {processor.enabled ? '禁用' : '启用'}
          </button>
        </div>
      </div>
    </div>
  );
}

// Processor Create/Edit Modal Component
interface ProcessorModalProps {
  processor: ProcessorWithConfig | null;
  onClose: () => void;
  onSuccess: () => void;
  showMessage: (type: 'success' | 'error', text: string) => void;
}

function ProcessorModal({ processor, onClose, onSuccess, showMessage }: ProcessorModalProps) {
  const isEditing = !!processor;
  const [isSaving, setIsSaving] = useState(false);
  const [formData, setFormData] = useState<CreateProcessorRequest>({
    name: processor?.name || '',
    description: processor?.description || '',
    color: processor?.color || '#6366f1',
    icon: processor?.icon || 'Sparkles',
    system_prompt: processor?.system_prompt || '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (!formData.name.trim()) {
      showMessage('error', '请输入处理器名称');
      return;
    }
    if (!formData.description.trim()) {
      showMessage('error', '请输入处理器描述');
      return;
    }
    if (!formData.system_prompt.trim()) {
      showMessage('error', '请输入系统提示词');
      return;
    }

    setIsSaving(true);
    try {
      if (isEditing && processor) {
        await studioProcessorsApi.update(processor.id, formData);
        showMessage('success', '处理器更新成功');
      } else {
        await studioProcessorsApi.create(formData);
        showMessage('success', '处理器创建成功');
      }
      onSuccess();
    } catch (error) {
      console.error('Failed to save processor:', error);
      showMessage('error', isEditing ? '更新失败' : '创建失败');
    } finally {
      setIsSaving(false);
    }
  };

  // Available colors
  const colors = [
    '#6366f1', '#8b5cf6', '#ec4899', '#ef4444', '#f97316',
    '#eab308', '#22c55e', '#14b8a6', '#06b6d4', '#3b82f6',
  ];

  // Available icons
  const icons = [
    { id: 'Sparkles', emoji: '✨' },
    { id: 'book', emoji: '📖' },
    { id: 'brain', emoji: '🧠' },
    { id: 'rocket', emoji: '🚀' },
    { id: 'star', emoji: '⭐' },
    { id: 'zap', emoji: '⚡' },
    { id: 'target', emoji: '🎯' },
    { id: 'lightbulb', emoji: '💡' },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />

      {/* Modal */}
      <div className="relative bg-white rounded-xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto m-4">
        {/* Header */}
        <div className="sticky top-0 bg-white border-b px-6 py-4 flex items-center justify-between">
          <h2 className="text-xl font-bold text-slate-900">
            {isEditing ? '编辑处理器' : '创建新处理器'}
          </h2>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-slate-600 transition-colors"
          >
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M18 6L6 18M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Name */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              处理器名称 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="例如：故事化讲解"
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
            />
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              描述 <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="简短描述这个处理器的特点"
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500"
            />
          </div>

          {/* Color */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              主题颜色
            </label>
            <div className="flex gap-2 flex-wrap">
              {colors.map((color) => (
                <button
                  key={color}
                  type="button"
                  onClick={() => setFormData({ ...formData, color })}
                  className={cn(
                    'w-8 h-8 rounded-full transition-all',
                    formData.color === color
                      ? 'ring-2 ring-offset-2 ring-slate-400 scale-110'
                      : 'hover:scale-105'
                  )}
                  style={{ backgroundColor: color }}
                />
              ))}
            </div>
          </div>

          {/* Icon */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              图标
            </label>
            <div className="flex gap-2 flex-wrap">
              {icons.map((icon) => (
                <button
                  key={icon.id}
                  type="button"
                  onClick={() => setFormData({ ...formData, icon: icon.id })}
                  className={cn(
                    'w-10 h-10 rounded-lg flex items-center justify-center text-xl transition-all',
                    formData.icon === icon.id
                      ? 'bg-red-100 ring-2 ring-red-500'
                      : 'bg-slate-100 hover:bg-slate-200'
                  )}
                >
                  {icon.emoji}
                </button>
              ))}
            </div>
          </div>

          {/* System Prompt */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              系统提示词 <span className="text-red-500">*</span>
            </label>
            <textarea
              value={formData.system_prompt}
              onChange={(e) => setFormData({ ...formData, system_prompt: e.target.value })}
              placeholder="定义这个处理器的行为和风格..."
              rows={8}
              className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-red-500 font-mono text-sm"
            />
            <p className="mt-2 text-xs text-slate-500">
              系统提示词定义了AI如何生成课程内容。可以包含角色设定、输出格式要求、风格指导等。
            </p>
          </div>

          {/* Preview */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              预览
            </label>
            <div className="p-4 bg-slate-50 rounded-lg flex items-center gap-4">
              <div
                className="w-12 h-12 rounded-xl flex items-center justify-center text-2xl"
                style={{ backgroundColor: `${formData.color}20` }}
              >
                {icons.find(i => i.id === formData.icon)?.emoji || '📦'}
              </div>
              <div>
                <h3 className="font-bold text-slate-900">
                  {formData.name || '处理器名称'}
                </h3>
                <p className="text-sm text-slate-500">
                  {formData.description || '处理器描述'}
                </p>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={isSaving}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {isSaving && (
                <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M23 4v6h-6M1 20v-6h6" />
                  <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
                </svg>
              )}
              {isEditing ? '保存修改' : '创建处理器'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
