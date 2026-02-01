'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import {
  getCourseNodes,
  deleteNode,
  type NodeListItem,
  type CourseNodesResponse
} from '@/lib/api/admin/nodes';

export default function CourseNodesPage() {
  const router = useRouter();
  const params = useParams();
  const courseId = parseInt(params.courseId as string);

  const [data, setData] = useState<CourseNodesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<NodeListItem | null>(null);
  const [showConfigModal, setShowConfigModal] = useState(false);

  // Load nodes
  useEffect(() => {
    loadNodes();
  }, [courseId]);

  const loadNodes = async () => {
    setLoading(true);
    try {
      const response = await getCourseNodes(courseId);
      setData(response);
    } catch (error) {
      console.error('Failed to load nodes:', error);
      alert('加载节点失败');
      router.push(`/admin/courses/${courseId}`);
    } finally {
      setLoading(false);
    }
  };

  // Handle delete
  const handleDelete = async (node: NodeListItem) => {
    if (!confirm(`确定要删除节点 "${node.title}" 吗？此操作不可撤销。`)) {
      return;
    }

    try {
      await deleteNode(node.id);
      loadNodes();
    } catch (error) {
      console.error('Failed to delete node:', error);
      alert('删除失败，请重试');
    }
  };

  // Handle view config
  const handleViewConfig = (node: NodeListItem) => {
    setSelectedNode(node);
    setShowConfigModal(true);
  };

  // Node type label
  const getNodeTypeLabel = (type: string) => {
    const labels = {
      video: '视频',
      simulator: '模拟器',
      assessment: '测验',
      reading: '阅读',
      practice: '练习'
    };
    return labels[type as keyof typeof labels] || type;
  };

  // Node type color
  const getNodeTypeColor = (type: string) => {
    const colors = {
      video: 'bg-blue-100 text-blue-800',
      simulator: 'bg-purple-100 text-purple-800',
      assessment: 'bg-green-100 text-green-800',
      reading: 'bg-yellow-100 text-yellow-800',
      practice: 'bg-orange-100 text-orange-800'
    };
    return colors[type as keyof typeof colors] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-slate-600">加载中...</div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-slate-600">数据未找到</div>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-4 mb-4">
          <button
            onClick={() => router.push(`/admin/courses/${courseId}`)}
            className="text-slate-600 hover:text-slate-900"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-slate-900">节点管理</h1>
            <p className="mt-2 text-slate-600">课程: {data.course_name}</p>
          </div>
          <button
            onClick={() => router.push(`/admin/courses/${courseId}/nodes/create`)}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            添加节点
          </button>
        </div>
      </div>

      {/* Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">总节点数</p>
          <p className="mt-2 text-3xl font-bold text-slate-900">{data.nodes.length}</p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">视频节点</p>
          <p className="mt-2 text-3xl font-bold text-blue-600">
            {data.nodes.filter((n) => n.type === 'video').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">模拟器节点</p>
          <p className="mt-2 text-3xl font-bold text-purple-600">
            {data.nodes.filter((n) => n.type === 'simulator').length}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow-sm p-6 border border-slate-200">
          <p className="text-sm font-medium text-slate-600">测验节点</p>
          <p className="mt-2 text-3xl font-bold text-green-600">
            {data.nodes.filter((n) => n.type === 'assessment').length}
          </p>
        </div>
      </div>

      {/* Nodes List */}
      <div className="bg-white rounded-lg shadow-sm border border-slate-200">
        {data.nodes.length === 0 ? (
          <div className="p-12 text-center text-slate-600">
            <p className="mb-4">该课程还没有添加节点</p>
            <button
              onClick={() => router.push(`/admin/courses/${courseId}/nodes/create`)}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              添加第一个节点
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-slate-50 border-b border-slate-200">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    序号
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    节点ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    标题
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    类型
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    组件ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">
                    配置
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-slate-500 uppercase tracking-wider">
                    操作
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-slate-200">
                {data.nodes.map((node) => (
                  <tr key={node.id} className="hover:bg-slate-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                      {node.sequence}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-mono text-slate-900">{node.node_id}</div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm font-medium text-slate-900">{node.title}</div>
                      {node.description && (
                        <div className="text-sm text-slate-500 truncate max-w-xs">
                          {node.description}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${getNodeTypeColor(node.type)}`}>
                        {getNodeTypeLabel(node.type)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-slate-600">
                      {node.component_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <button
                        onClick={() => handleViewConfig(node)}
                        className="text-blue-600 hover:text-blue-900 text-sm"
                      >
                        {node.timeline_config ? '查看配置' : '无配置'}
                      </button>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => router.push(`/admin/courses/${courseId}/nodes/${node.id}/edit`)}
                        className="text-blue-600 hover:text-blue-900 mr-4"
                      >
                        编辑
                      </button>
                      <button
                        onClick={() => handleDelete(node)}
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
      </div>

      {/* Config Modal */}
      {showConfigModal && selectedNode && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-4xl w-full mx-4 max-h-[80vh] overflow-hidden flex flex-col">
            <div className="px-6 py-4 border-b border-slate-200 flex items-center justify-between">
              <h2 className="text-xl font-bold text-slate-900">节点配置</h2>
              <button
                onClick={() => setShowConfigModal(false)}
                className="text-slate-400 hover:text-slate-600"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            <div className="px-6 py-4 overflow-y-auto flex-1">
              <div className="mb-4">
                <h3 className="text-sm font-medium text-slate-700 mb-2">节点信息</h3>
                <div className="bg-slate-50 rounded-lg p-4 space-y-2">
                  <div><span className="font-medium">节点ID:</span> {selectedNode.node_id}</div>
                  <div><span className="font-medium">标题:</span> {selectedNode.title}</div>
                  <div><span className="font-medium">类型:</span> {getNodeTypeLabel(selectedNode.type)}</div>
                  <div><span className="font-medium">组件ID:</span> {selectedNode.component_id}</div>
                </div>
              </div>
              <div className="mb-4">
                <h3 className="text-sm font-medium text-slate-700 mb-2">Timeline 配置 (API调用配置)</h3>
                <pre className="bg-slate-900 text-slate-100 rounded-lg p-4 overflow-x-auto text-sm">
                  {JSON.stringify(selectedNode.timeline_config, null, 2)}
                </pre>
              </div>
              <div>
                <h3 className="text-sm font-medium text-slate-700 mb-2">解锁条件</h3>
                <pre className="bg-slate-900 text-slate-100 rounded-lg p-4 overflow-x-auto text-sm">
                  {JSON.stringify(selectedNode.unlock_condition, null, 2)}
                </pre>
              </div>
            </div>
            <div className="px-6 py-4 border-t border-slate-200 flex justify-end gap-2">
              <button
                onClick={() => setShowConfigModal(false)}
                className="px-4 py-2 border border-slate-300 rounded-lg hover:bg-slate-50 transition-colors"
              >
                关闭
              </button>
              <button
                onClick={() => {
                  setShowConfigModal(false);
                  router.push(`/admin/courses/${courseId}/nodes/${selectedNode.id}/edit`);
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                编辑配置
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
