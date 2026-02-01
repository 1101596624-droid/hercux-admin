'use client';

import { useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
  createNode,
  type NodeCreateData
} from '@/lib/api/admin/nodes';

export default function NodeCreatePage() {
  const router = useRouter();
  const params = useParams();
  const courseId = parseInt(params.courseId as string);

  const [saving, setSaving] = useState(false);

  // Form state
  const [nodeId, setNodeId] = useState('');
  const [type, setType] = useState<'video' | 'simulator' | 'assessment' | 'reading' | 'practice'>('video');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [componentId, setComponentId] = useState('');
  const [sequence, setSequence] = useState(0);
  const [timelineConfigJson, setTimelineConfigJson] = useState('{}');
  const [unlockConditionJson, setUnlockConditionJson] = useState('{"type": "previous_complete"}');
  const [jsonError, setJsonError] = useState<string | null>(null);

  // Validate JSON
  const validateJson = (jsonString: string): boolean => {
    try {
      JSON.parse(jsonString);
      setJsonError(null);
      return true;
    } catch (error) {
      setJsonError('JSON 格式错误');
      return false;
    }
  };

  // Handle save
  const handleSave = async () => {
    // Validate required fields
    if (!nodeId || !title || !componentId) {
      alert('请填写所有必填字段');
      return;
    }

    // Validate JSON
    if (!validateJson(timelineConfigJson) || !validateJson(unlockConditionJson)) {
      alert('请检查 JSON 格式');
      return;
    }

    setSaving(true);
    try {
      const createData: NodeCreateData = {
        node_id: nodeId,
        type,
        title,
        description,
        component_id: componentId,
        sequence,
        timeline_config: JSON.parse(timelineConfigJson),
        unlock_condition: JSON.parse(unlockConditionJson)
      };

      await createNode(courseId, createData);
      alert('创建成功');
      router.push(`/admin/courses/${courseId}/nodes`);
    } catch (error) {
      console.error('Failed to create node:', error);
      alert('创建失败，请重试');
    } finally {
      setSaving(false);
    }
  };

  // Format JSON
  const handleFormatJson = (type: 'timeline' | 'unlock') => {
    try {
      if (type === 'timeline') {
        const parsed = JSON.parse(timelineConfigJson);
        setTimelineConfigJson(JSON.stringify(parsed, null, 2));
      } else {
        const parsed = JSON.parse(unlockConditionJson);
        setUnlockConditionJson(JSON.stringify(parsed, null, 2));
      }
      setJsonError(null);
    } catch (error) {
      setJsonError('JSON 格式错误，无法格式化');
    }
  };

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <button
            onClick={() => router.push(`/admin/courses/${courseId}/nodes`)}
            className="text-slate-600 hover:text-slate-900"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-slate-900">创建节点</h1>
            <p className="mt-2 text-slate-600">为课程添加新的学习节点</p>
          </div>
        </div>
      </div>

      {/* Form */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
        <div className="space-y-6">
          {/* Basic Info */}
          <div>
            <h2 className="text-lg font-semibold text-slate-900 mb-4">基本信息</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  节点ID * <span className="text-slate-500 font-normal">(唯一标识符)</span>
                </label>
                <input
                  type="text"
                  value={nodeId}
                  onChange={(e) => setNodeId(e.target.value)}
                  placeholder="例如: node-biomech-01"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  类型 *
                </label>
                <select
                  value={type}
                  onChange={(e) => setType(e.target.value as any)}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="video">视频</option>
                  <option value="simulator">模拟器</option>
                  <option value="assessment">测验</option>
                  <option value="reading">阅读</option>
                  <option value="practice">练习</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  标题 *
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="节点标题"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  组件ID *
                </label>
                <input
                  type="text"
                  value={componentId}
                  onChange={(e) => setComponentId(e.target.value)}
                  placeholder="例如: force-balance-sim"
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  描述
                </label>
                <textarea
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  placeholder="节点描述"
                  rows={3}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  序号
                </label>
                <input
                  type="number"
                  value={sequence}
                  onChange={(e) => setSequence(parseInt(e.target.value))}
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <p className="text-xs text-slate-500 mt-1">节点在课程中的显示顺序</p>
              </div>
            </div>
          </div>

          {/* Timeline Config */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-slate-900">Timeline 配置 (API调用配置)</h2>
              <button
                onClick={() => handleFormatJson('timeline')}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                格式化 JSON
              </button>
            </div>
            <div className="mb-2">
              <p className="text-sm text-slate-600 mb-2">
                配置教学模块调用的 API 端点、参数和步骤。例如:
              </p>
              <pre className="text-xs bg-slate-50 p-2 rounded border border-slate-200 overflow-x-auto">
{`{
  "steps": [
    {
      "type": "api_call",
      "endpoint": "/api/simulator/force-balance",
      "method": "POST",
      "params": {
        "mode": "interactive",
        "difficulty": "beginner"
      }
    },
    {
      "type": "video",
      "url": "https://example.com/video.mp4"
    }
  ]
}`}
              </pre>
            </div>
            <textarea
              value={timelineConfigJson}
              onChange={(e) => setTimelineConfigJson(e.target.value)}
              rows={15}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
            />
          </div>

          {/* Unlock Condition */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-slate-900">解锁条件</h2>
              <button
                onClick={() => handleFormatJson('unlock')}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                格式化 JSON
              </button>
            </div>
            <div className="mb-2">
              <p className="text-sm text-slate-600 mb-2">
                配置节点的解锁条件。例如:
              </p>
              <pre className="text-xs bg-slate-50 p-2 rounded border border-slate-200 overflow-x-auto">
{`{
  "type": "previous_complete",
  "required_nodes": ["node-1", "node-2"]
}`}
              </pre>
            </div>
            <textarea
              value={unlockConditionJson}
              onChange={(e) => setUnlockConditionJson(e.target.value)}
              rows={8}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
            />
          </div>

          {/* Error Message */}
          {jsonError && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800 text-sm">{jsonError}</p>
            </div>
          )}

          {/* Actions */}
          <div className="flex justify-end gap-4 pt-4 border-t border-slate-200">
            <button
              onClick={() => router.push(`/admin/courses/${courseId}/nodes`)}
              className="px-6 py-2 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
            >
              取消
            </button>
            <button
              onClick={handleSave}
              disabled={saving}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {saving ? '创建中...' : '创建节点'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
