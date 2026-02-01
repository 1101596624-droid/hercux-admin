'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
  getNodeDetail,
  updateNode,
  type NodeDetail,
  type NodeUpdateData
} from '@/lib/api/admin/nodes';

export default function NodeEditPage() {
  const router = useRouter();
  const params = useParams();
  const courseId = parseInt(params.courseId as string);
  const nodeId = parseInt(params.nodeId as string);

  const [node, setNode] = useState<NodeDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  // Form state
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [componentId, setComponentId] = useState('');
  const [sequence, setSequence] = useState(0);
  const [timelineConfigJson, setTimelineConfigJson] = useState('');
  const [unlockConditionJson, setUnlockConditionJson] = useState('');
  const [jsonError, setJsonError] = useState<string | null>(null);

  // Load node detail
  useEffect(() => {
    loadNode();
  }, [nodeId]);

  const loadNode = async () => {
    setLoading(true);
    try {
      const data = await getNodeDetail(nodeId);
      setNode(data);
      setTitle(data.title);
      setDescription(data.description || '');
      setComponentId(data.component_id);
      setSequence(data.sequence);
      setTimelineConfigJson(JSON.stringify(data.timeline_config, null, 2));
      setUnlockConditionJson(JSON.stringify(data.unlock_condition, null, 2));
    } catch (error) {
      console.error('Failed to load node:', error);
      alert('加载节点失败');
      router.push(`/admin/courses/${courseId}/nodes`);
    } finally {
      setLoading(false);
    }
  };

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
    // Validate JSON
    if (!validateJson(timelineConfigJson) || !validateJson(unlockConditionJson)) {
      alert('请检查 JSON 格式');
      return;
    }

    setSaving(true);
    try {
      const updateData: NodeUpdateData = {
        title,
        description,
        component_id: componentId,
        sequence,
        timeline_config: JSON.parse(timelineConfigJson),
        unlock_condition: JSON.parse(unlockConditionJson)
      };

      await updateNode(nodeId, updateData);
      alert('保存成功');
      router.push(`/admin/courses/${courseId}/nodes`);
    } catch (error) {
      console.error('Failed to update node:', error);
      alert('保存失败，请重试');
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

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-slate-600">加载中...</div>
      </div>
    );
  }

  if (!node) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-slate-600">节点未找到</div>
      </div>
    );
  }

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
            <h1 className="text-3xl font-bold text-slate-900">编辑节点</h1>
            <p className="mt-2 text-slate-600">课程: {node.course.name}</p>
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">已开始学习</p>
          <p className="mt-2 text-3xl font-bold text-blue-600">{node.statistics.total_started}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">已完成</p>
          <p className="mt-2 text-3xl font-bold text-green-600">{node.statistics.total_completed}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">完成率</p>
          <p className="mt-2 text-3xl font-bold text-orange-600">{node.statistics.completion_rate}%</p>
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
                  节点ID (只读)
                </label>
                <input
                  type="text"
                  value={node.node_id}
                  disabled
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-slate-50 text-slate-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  类型 (只读)
                </label>
                <input
                  type="text"
                  value={node.type}
                  disabled
                  className="w-full px-3 py-2 border border-slate-300 rounded-lg bg-slate-50 text-slate-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  标题 *
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
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
      "params": { "mode": "interactive" }
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
              {saving ? '保存中...' : '保存'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
