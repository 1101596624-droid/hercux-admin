'use client';

/**
 * TriggerList - 触发器列表管理
 * 管理 AI 引导的触发条件
 */

import React, { useState } from 'react';
import { useEditorStore } from '@/stores/editor/useEditorStore';
import { createDefaultTrigger } from '@/types/editor';
import type { AITrigger, TriggerCondition } from '@/types/editor';
import { cn } from '@/lib/cn';

const triggerTypeLabels: Record<TriggerCondition['type'], string> = {
  on_enter: '进入时',
  on_complete: '完成时',
  on_error: '出错时',
  on_idle: '空闲时',
  custom: '自定义',
};

const triggerTypeDescriptions: Record<TriggerCondition['type'], string> = {
  on_enter: '学生进入此小节时触发',
  on_complete: '学生完成此小节时触发',
  on_error: '学生遇到错误时触发',
  on_idle: '学生空闲一段时间后触发',
  custom: '自定义触发条件',
};

export function TriggerList() {
  const { aiGuidance, addTrigger, updateTrigger, deleteTrigger } = useEditorStore();
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const handleAddTrigger = () => {
    const newTrigger = createDefaultTrigger();
    addTrigger(newTrigger);
    setExpandedId(newTrigger.id);
  };

  const handleConditionTypeChange = (trigger: AITrigger, type: TriggerCondition['type']) => {
    let newCondition: TriggerCondition;
    switch (type) {
      case 'on_idle':
        newCondition = { type: 'on_idle', seconds: 30 };
        break;
      case 'on_error':
        newCondition = { type: 'on_error' };
        break;
      case 'custom':
        newCondition = { type: 'custom', expression: '' };
        break;
      default:
        newCondition = { type };
        break;
    }
    updateTrigger(trigger.id, { condition: newCondition });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-dark-700">
          触发器 ({aiGuidance.triggers.length})
        </label>
        <button
          onClick={handleAddTrigger}
          className="text-sm text-primary-600 hover:text-primary-700"
        >
          + 添加触发器
        </button>
      </div>

      <div className="space-y-3">
        {aiGuidance.triggers.map((trigger) => (
          <TriggerItem
            key={trigger.id}
            trigger={trigger}
            expanded={expandedId === trigger.id}
            onToggle={() => setExpandedId(expandedId === trigger.id ? null : trigger.id)}
            onUpdate={(updates) => updateTrigger(trigger.id, updates)}
            onDelete={() => deleteTrigger(trigger.id)}
            onConditionTypeChange={(type) => handleConditionTypeChange(trigger, type)}
          />
        ))}

        {aiGuidance.triggers.length === 0 && (
          <div className="text-center py-8 text-dark-400 text-sm border border-dashed border-dark-200 rounded-lg">
            暂无触发器，点击上方按钮添加
          </div>
        )}
      </div>

      <div className="p-3 rounded-lg bg-amber-50 border border-amber-100">
        <h4 className="text-xs font-medium text-amber-800 mb-1">关于触发器</h4>
        <p className="text-xs text-amber-700">
          触发器定义了 AI 导师何时主动介入。合理配置触发器可以在学生需要帮助时提供及时的引导。
        </p>
      </div>
    </div>
  );
}

interface TriggerItemProps {
  trigger: AITrigger;
  expanded: boolean;
  onToggle: () => void;
  onUpdate: (updates: Partial<AITrigger>) => void;
  onDelete: () => void;
  onConditionTypeChange: (type: TriggerCondition['type']) => void;
}

function TriggerItem({
  trigger,
  expanded,
  onToggle,
  onUpdate,
  onDelete,
  onConditionTypeChange,
}: TriggerItemProps) {
  return (
    <div className="border border-dark-200 rounded-lg overflow-hidden">
      <div
        className={cn(
          'flex items-center gap-3 px-3 py-2 cursor-pointer hover:bg-dark-50',
          expanded && 'bg-dark-50'
        )}
        onClick={onToggle}
      >
        <button
          onClick={(e) => {
            e.stopPropagation();
            onUpdate({ enabled: !trigger.enabled });
          }}
          className={cn(
            'w-8 h-5 rounded-full transition-colors relative',
            trigger.enabled ? 'bg-primary-500' : 'bg-dark-300'
          )}
        >
          <span
            className={cn(
              'absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform',
              trigger.enabled ? 'left-3.5' : 'left-0.5'
            )}
          />
        </button>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-medium text-dark-800 truncate">
            {trigger.name || '未命名触发器'}
          </p>
          <p className="text-xs text-dark-500">
            {triggerTypeLabels[trigger.condition.type]}
          </p>
        </div>
        <svg
          className={cn('w-4 h-4 text-dark-400 transition-transform', expanded && 'rotate-180')}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>

      {expanded && (
        <div className="px-3 py-3 border-t border-dark-100 space-y-3">
          <div>
            <label className="block text-xs font-medium text-dark-600 mb-1">
              触发器名称
            </label>
            <input
              type="text"
              value={trigger.name}
              onChange={(e) => onUpdate({ name: e.target.value })}
              placeholder="输入名称..."
              className="w-full rounded border border-dark-200 px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-dark-600 mb-1">
              触发条件
            </label>
            <select
              value={trigger.condition.type}
              onChange={(e) => onConditionTypeChange(e.target.value as TriggerCondition['type'])}
              className="w-full rounded border border-dark-200 px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary-500"
            >
              {Object.entries(triggerTypeLabels).map(([type, label]) => (
                <option key={type} value={type}>
                  {label}
                </option>
              ))}
            </select>
            <p className="mt-1 text-xs text-dark-500">
              {triggerTypeDescriptions[trigger.condition.type]}
            </p>
          </div>

          {trigger.condition.type === 'on_idle' && (
            <div>
              <label className="block text-xs font-medium text-dark-600 mb-1">
                空闲时间（秒）
              </label>
              <input
                type="number"
                min={5}
                max={300}
                value={trigger.condition.seconds}
                onChange={(e) =>
                  onUpdate({
                    condition: { type: 'on_idle', seconds: parseInt(e.target.value) || 30 },
                  })
                }
                className="w-full rounded border border-dark-200 px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
          )}

          {trigger.condition.type === 'on_error' && (
            <div>
              <label className="block text-xs font-medium text-dark-600 mb-1">
                错误类型（可选）
              </label>
              <input
                type="text"
                value={trigger.condition.errorType || ''}
                onChange={(e) =>
                  onUpdate({
                    condition: { type: 'on_error', errorType: e.target.value || undefined },
                  })
                }
                placeholder="留空表示所有错误"
                className="w-full rounded border border-dark-200 px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
          )}

          {trigger.condition.type === 'custom' && (
            <div>
              <label className="block text-xs font-medium text-dark-600 mb-1">
                自定义表达式
              </label>
              <input
                type="text"
                value={trigger.condition.expression}
                onChange={(e) =>
                  onUpdate({
                    condition: { type: 'custom', expression: e.target.value },
                  })
                }
                placeholder="例如: progress > 50 && !completed"
                className="w-full rounded border border-dark-200 px-2 py-1.5 text-sm font-mono focus:outline-none focus:ring-1 focus:ring-primary-500"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-medium text-dark-600 mb-1">
              触发提示词
            </label>
            <textarea
              value={trigger.prompt}
              onChange={(e) => onUpdate({ prompt: e.target.value })}
              placeholder="当触发条件满足时，AI 将使用此提示词..."
              rows={4}
              className="w-full rounded border border-dark-200 px-2 py-1.5 text-sm focus:outline-none focus:ring-1 focus:ring-primary-500"
            />
          </div>

          <div className="flex justify-end">
            <button
              onClick={onDelete}
              className="text-sm text-red-500 hover:text-red-600"
            >
              删除触发器
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
