'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAdminAuthStore } from '@/stores/admin/useAdminAuthStore';
import {
  getAPIConfig,
  updateAPIConfig,
  testAPIConnection,
  type APIConfigCategory,
  type APIConfigItem,
} from '@/lib/api/admin/api-config';

// 分类图标映射
const categoryIcons: Record<string, React.ReactNode> = {
  '服务器配置': (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="2" y="3" width="20" height="14" rx="2" />
      <path d="M8 21h8M12 17v4" />
    </svg>
  ),
  '数据库配置': (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <ellipse cx="12" cy="5" rx="9" ry="3" />
      <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" />
      <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" />
    </svg>
  ),
  'JWT 认证': (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="11" width="18" height="11" rx="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </svg>
  ),
  'Claude AI (Anthropic)': (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M12 2a2 2 0 0 1 2 2c0 .74-.4 1.39-1 1.73V7h1a7 7 0 0 1 7 7h1a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1h-1v1a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-1H2a1 1 0 0 1-1-1v-3a1 1 0 0 1 1-1h1a7 7 0 0 1 7-7h1V5.73c-.6-.34-1-.99-1-1.73a2 2 0 0 1 2-2z" />
      <circle cx="7.5" cy="14.5" r="1.5" />
      <circle cx="16.5" cy="14.5" r="1.5" />
    </svg>
  ),
  'DeepSeek AI': (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="10" />
      <path d="M12 16v-4M12 8h.01" />
    </svg>
  ),
  '图片生成 (Gemini/DALL-E)': (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="3" width="18" height="18" rx="2" />
      <circle cx="8.5" cy="8.5" r="1.5" />
      <path d="m21 15-5-5L5 21" />
    </svg>
  ),
  'AWS S3 存储': (
    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
      <path d="M22 6l-10 7L2 6" />
    </svg>
  ),
};

// 状态徽章组件
function StatusBadge({ configured }: { configured: boolean }) {
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
      configured
        ? 'bg-emerald-50 text-emerald-600 border border-emerald-200'
        : 'bg-amber-50 text-amber-600 border border-amber-200'
    }`}>
      {configured ? '已配置' : '未配置'}
    </span>
  );
}

// 编辑弹窗组件
function EditModal({
  isOpen,
  item,
  onClose,
  onSave,
  isSaving,
}: {
  isOpen: boolean;
  item: APIConfigItem | null;
  onClose: () => void;
  onSave: (key: string, value: string) => void;
  isSaving: boolean;
}) {
  const [value, setValue] = useState('');

  useEffect(() => {
    if (item) {
      setValue(item.is_secret ? '' : item.value);
    }
  }, [item]);

  if (!isOpen || !item) return null;

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-2xl w-[500px] shadow-2xl">
        <div className="p-6 border-b border-slate-200">
          <h3 className="text-xl font-bold text-slate-900">编辑配置</h3>
          <p className="text-sm text-slate-500 mt-1">{item.name}</p>
        </div>

        <div className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">配置键</label>
            <input
              type="text"
              value={item.key}
              disabled
              className="w-full px-4 py-3 border border-slate-200 rounded-xl bg-slate-50 text-slate-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">描述</label>
            <p className="text-sm text-slate-600 bg-slate-50 px-4 py-3 rounded-xl">{item.description}</p>
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              当前值 {item.is_secret && <span className="text-amber-500">(敏感信息已脱敏)</span>}
            </label>
            <input
              type="text"
              value={item.masked_value}
              disabled
              className="w-full px-4 py-3 border border-slate-200 rounded-xl bg-slate-50 text-slate-500 font-mono text-sm"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              新值 {item.is_secret && <span className="text-red-500">*</span>}
            </label>
            <input
              type={item.is_secret ? 'password' : 'text'}
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder={item.is_secret ? '输入新的密钥值' : '输入新值'}
              className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 font-mono text-sm"
            />
          </div>

          <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
            <div className="flex items-start gap-2">
              <svg className="w-5 h-5 text-amber-500 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
                <line x1="12" y1="9" x2="12" y2="13" />
                <line x1="12" y1="17" x2="12.01" y2="17" />
              </svg>
              <p className="text-sm text-amber-700">
                修改配置后需要<strong>重启服务</strong>才能生效
              </p>
            </div>
          </div>
        </div>

        <div className="p-6 border-t border-slate-200 flex gap-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-3 text-sm font-medium text-slate-700 bg-slate-100 rounded-xl hover:bg-slate-200 transition-colors"
          >
            取消
          </button>
          <button
            onClick={() => onSave(item.key, value)}
            disabled={isSaving || !value}
            className="flex-1 px-4 py-3 text-sm font-medium text-white bg-red-500 rounded-xl hover:bg-red-600 disabled:opacity-50 transition-colors"
          >
            {isSaving ? '保存中...' : '保存配置'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function APIConfigPage() {
  const router = useRouter();
  const { canAccessAdminManagement } = useAdminAuthStore();

  const [categories, setCategories] = useState<APIConfigCategory[]>([]);
  const [envFilePath, setEnvFilePath] = useState('');
  const [loading, setLoading] = useState(true);
  const [editItem, setEditItem] = useState<APIConfigItem | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [testingCategory, setTestingCategory] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<Record<string, { success: boolean; message: string }>>({});
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());

  // 加载配置
  const loadConfig = async () => {
    try {
      setLoading(true);
      const data = await getAPIConfig();
      setCategories(data.categories);
      setEnvFilePath(data.env_file_path);
      // 默认展开所有分类
      setExpandedCategories(new Set(data.categories.map(c => c.name)));
    } catch (error) {
      console.error('Failed to load API config:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadConfig();
  }, []);

  // 保存配置
  const handleSave = async (key: string, value: string) => {
    setIsSaving(true);
    try {
      await updateAPIConfig({ key, value });
      setEditItem(null);
      loadConfig();
      alert('配置已保存，需要重启服务才能生效');
    } catch (error) {
      alert(error instanceof Error ? error.message : '保存失败');
    } finally {
      setIsSaving(false);
    }
  };

  // 测试 API 连接
  const handleTest = async (categoryName: string) => {
    // 映射分类名到测试类别
    const categoryMap: Record<string, string> = {
      'Claude AI (Anthropic)': 'claude',
      'DeepSeek AI': 'deepseek',
      '图片生成 (Gemini/DALL-E)': 'gemini',
      '数据库配置': 'database',
    };

    const testCategory = categoryMap[categoryName];
    if (!testCategory) {
      alert('该分类不支持连接测试');
      return;
    }

    setTestingCategory(categoryName);
    try {
      const result = await testAPIConnection(testCategory);
      setTestResults(prev => ({ ...prev, [categoryName]: result }));
    } catch (error) {
      setTestResults(prev => ({
        ...prev,
        [categoryName]: { success: false, message: error instanceof Error ? error.message : '测试失败' }
      }));
    } finally {
      setTestingCategory(null);
    }
  };

  // 切换分类展开状态
  const toggleCategory = (name: string) => {
    setExpandedCategories(prev => {
      const next = new Set(prev);
      if (next.has(name)) {
        next.delete(name);
      } else {
        next.add(name);
      }
      return next;
    });
  };

  // 统计配置状态
  const getConfigStats = () => {
    let total = 0;
    let configured = 0;
    categories.forEach(cat => {
      cat.items.forEach(item => {
        total++;
        if (item.is_configured) configured++;
      });
    });
    return { total, configured };
  };

  const stats = getConfigStats();

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 italic">API Config.</h1>
          <p className="text-slate-500 mt-1">
            管理所有 API 配置，共 <span className="text-red-500 font-medium">{stats.configured}/{stats.total}</span> 项已配置
          </p>
        </div>
        <button
          onClick={loadConfig}
          className="flex items-center gap-2 px-5 py-3 bg-slate-100 text-slate-700 rounded-xl hover:bg-slate-200 transition-colors font-medium"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M23 4v6h-6M1 20v-6h6" />
            <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
          </svg>
          刷新配置
        </button>
      </div>

      {/* 环境文件路径 */}
      <div className="bg-slate-900 rounded-2xl p-4 mb-8 flex items-center gap-3">
        <svg className="w-5 h-5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
        </svg>
        <span className="text-slate-400 text-sm">配置文件路径:</span>
        <code className="text-emerald-400 font-mono text-sm">{envFilePath}</code>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="w-10 h-10 border-4 border-red-200 border-t-red-500 rounded-full animate-spin"></div>
        </div>
      ) : (
        <div className="space-y-4">
          {categories.map((category) => {
            const isExpanded = expandedCategories.has(category.name);
            const testResult = testResults[category.name];
            const canTest = ['Claude AI (Anthropic)', 'DeepSeek AI', '图片生成 (Gemini/DALL-E)', '数据库配置'].includes(category.name);

            return (
              <div key={category.name} className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
                {/* 分类头部 */}
                <div
                  className="px-6 py-4 flex items-center justify-between cursor-pointer hover:bg-slate-50 transition-colors"
                  onClick={() => toggleCategory(category.name)}
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-red-50 rounded-xl flex items-center justify-center text-red-500">
                      {categoryIcons[category.name] || (
                        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <circle cx="12" cy="12" r="3" />
                          <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z" />
                        </svg>
                      )}
                    </div>
                    <div>
                      <h2 className="text-lg font-semibold text-slate-900">{category.name}</h2>
                      <p className="text-sm text-slate-500">{category.description}</p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    {/* 测试结果 */}
                    {testResult && (
                      <span className={`text-sm font-medium ${testResult.success ? 'text-emerald-600' : 'text-red-500'}`}>
                        {testResult.success ? '连接正常' : '连接失败'}
                      </span>
                    )}

                    {/* 测试按钮 */}
                    {canTest && (
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleTest(category.name);
                        }}
                        disabled={testingCategory === category.name}
                        className="px-3 py-1.5 text-xs font-medium text-slate-600 bg-slate-100 rounded-lg hover:bg-slate-200 transition-colors disabled:opacity-50"
                      >
                        {testingCategory === category.name ? '测试中...' : '测试连接'}
                      </button>
                    )}

                    {/* 配置数量 */}
                    <span className="text-sm text-slate-400">
                      {category.items.filter(i => i.is_configured).length}/{category.items.length}
                    </span>

                    {/* 展开/收起图标 */}
                    <svg
                      className={`w-5 h-5 text-slate-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                    >
                      <polyline points="6 9 12 15 18 9" />
                    </svg>
                  </div>
                </div>

                {/* 配置项列表 */}
                {isExpanded && (
                  <div className="border-t border-slate-100">
                    <table className="w-full">
                      <thead>
                        <tr className="border-b border-slate-100 text-left bg-slate-50">
                          <th className="py-3 px-6 text-xs font-medium text-slate-500 uppercase">配置项</th>
                          <th className="py-3 px-6 text-xs font-medium text-slate-500 uppercase">值</th>
                          <th className="py-3 px-6 text-xs font-medium text-slate-500 uppercase">状态</th>
                          <th className="py-3 px-6 text-xs font-medium text-slate-500 uppercase">操作</th>
                        </tr>
                      </thead>
                      <tbody>
                        {category.items.map((item) => (
                          <tr key={item.key} className="border-b border-slate-100 hover:bg-slate-50/50 transition-colors">
                            <td className="py-4 px-6">
                              <div>
                                <div className="font-medium text-slate-900">{item.name}</div>
                                <div className="text-xs text-slate-400 font-mono">{item.key}</div>
                              </div>
                            </td>
                            <td className="py-4 px-6">
                              <code className="text-sm text-slate-600 bg-slate-100 px-2 py-1 rounded font-mono">
                                {item.masked_value}
                              </code>
                            </td>
                            <td className="py-4 px-6">
                              <StatusBadge configured={item.is_configured} />
                            </td>
                            <td className="py-4 px-6">
                              <button
                                onClick={() => setEditItem(item)}
                                className="w-9 h-9 rounded-lg border border-slate-200 flex items-center justify-center hover:bg-slate-100 transition-colors"
                                title="编辑配置"
                              >
                                <svg className="w-4 h-4 text-slate-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                                  <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                                  <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                                </svg>
                              </button>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* 编辑弹窗 */}
      <EditModal
        isOpen={!!editItem}
        item={editItem}
        onClose={() => setEditItem(null)}
        onSave={handleSave}
        isSaving={isSaving}
      />
    </div>
  );
}
