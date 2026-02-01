'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import {
  getSettings,
  updatePlatformSettings,
  updateCourseSettings,
  updateUserSettings,
  updateStorageSettings,
  updateLogSettings,
  getSystemInfo,
  getSystemStats,
  getCacheInfo,
  clearCache,
  resetSettings,
  type AllSettings,
  type SystemInfo,
  type SystemStats,
  type CacheInfo,
} from '@/lib/api/admin/settings';

type TabType = 'platform' | 'course' | 'user' | 'storage' | 'log' | 'system';

function Toggle({ enabled, onChange }: { enabled: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      type="button"
      onClick={() => onChange(!enabled)}
      className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
        enabled ? 'bg-red-500' : 'bg-slate-200'
      }`}
    >
      <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
        enabled ? 'translate-x-6' : 'translate-x-1'
      }`} />
    </button>
  );
}

function Input({ label, value, onChange, type = 'text', placeholder, description }: {
  label: string; value: string | number; onChange: (v: string) => void;
  type?: string; placeholder?: string; description?: string;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-2">{label}</label>
      <input type={type} value={value} onChange={(e) => onChange(e.target.value)} placeholder={placeholder}
        className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500" />
      {description && <p className="mt-1 text-xs text-slate-500">{description}</p>}
    </div>
  );
}

function Select({ label, value, onChange, options, description }: {
  label: string; value: string; onChange: (v: string) => void;
  options: { value: string; label: string }[]; description?: string;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-2">{label}</label>
      <select value={value} onChange={(e) => onChange(e.target.value)}
        className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500 bg-white">
        {options.map((opt) => (<option key={opt.value} value={opt.value}>{opt.label}</option>))}
      </select>
      {description && <p className="mt-1 text-xs text-slate-500">{description}</p>}
    </div>
  );
}

function TagsInput({ label, value, onChange, description }: {
  label: string; value: string[]; onChange: (v: string[]) => void; description?: string;
}) {
  const [inputValue, setInputValue] = useState('');
  const addTag = () => {
    if (inputValue.trim() && !value.includes(inputValue.trim())) {
      onChange([...value, inputValue.trim()]);
      setInputValue('');
    }
  };
  const removeTag = (tag: string) => onChange(value.filter((t) => t !== tag));
  return (
    <div>
      <label className="block text-sm font-medium text-slate-700 mb-2">{label}</label>
      <div className="flex flex-wrap gap-2 mb-2">
        {value.map((tag) => (
          <span key={tag} className="inline-flex items-center gap-1 px-3 py-1 bg-red-50 text-red-600 rounded-full text-sm">
            {tag}
            <button onClick={() => removeTag(tag)} className="hover:text-red-800">
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6L6 18M6 6l12 12" /></svg>
            </button>
          </span>
        ))}
      </div>
      <div className="flex gap-2">
        <input type="text" value={inputValue} onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())} placeholder="输入标签后按回车"
          className="flex-1 px-4 py-2 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500" />
        <button type="button" onClick={addTag} className="px-4 py-2 bg-slate-100 text-slate-700 rounded-xl hover:bg-slate-200">添加</button>
      </div>
      {description && <p className="mt-1 text-xs text-slate-500">{description}</p>}
    </div>
  );
}// 统计卡片组件
function StatCard({ label, value, icon, color = 'red' }: { label: string; value: string | number; icon: React.ReactNode; color?: string }) {
  const colorClasses: Record<string, string> = {
    red: 'bg-red-50 text-red-500',
    blue: 'bg-blue-50 text-blue-500',
    green: 'bg-emerald-50 text-emerald-500',
    purple: 'bg-purple-50 text-purple-500',
    amber: 'bg-amber-50 text-amber-500',
  };
  return (
    <div className="bg-white rounded-xl border border-slate-100 p-4">
      <div className="flex items-center gap-3">
        <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${colorClasses[color]}`}>{icon}</div>
        <div>
          <div className="text-2xl font-bold text-slate-900">{value}</div>
          <div className="text-sm text-slate-500">{label}</div>
        </div>
      </div>
    </div>
  );
}

export default function SettingsPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<TabType>('platform');
  const [settings, setSettings] = useState<AllSettings | null>(null);
  const [systemInfo, setSystemInfo] = useState<SystemInfo | null>(null);
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null);
  const [cacheInfo, setCacheInfo] = useState<CacheInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [clearingCache, setClearingCache] = useState(false);

  // 加载数据
  const loadData = async () => {
    try {
      setLoading(true);
      const [settingsData, infoData, statsData, cacheData] = await Promise.all([
        getSettings(),
        getSystemInfo(),
        getSystemStats(),
        getCacheInfo(),
      ]);
      setSettings(settingsData);
      setSystemInfo(infoData);
      setSystemStats(statsData);
      setCacheInfo(cacheData);
    } catch (error) {
      console.error('Failed to load settings:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadData(); }, []);

  // 保存设置
  const handleSave = async (section: string) => {
    if (!settings) return;
    setSaving(true);
    try {
      switch (section) {
        case 'platform': await updatePlatformSettings(settings.platform); break;
        case 'course': await updateCourseSettings(settings.course); break;
        case 'user': await updateUserSettings(settings.user); break;
        case 'storage': await updateStorageSettings(settings.storage); break;
        case 'log': await updateLogSettings(settings.log); break;
      }
      alert('设置已保存');
    } catch (error) {
      alert(error instanceof Error ? error.message : '保存失败');
    } finally {
      setSaving(false);
    }
  };

  // 清除缓存
  const handleClearCache = async () => {
    if (!confirm('确定要清除所有缓存吗？')) return;
    setClearingCache(true);
    try {
      await clearCache();
      alert('缓存已清除');
      loadData();
    } catch (error) {
      alert(error instanceof Error ? error.message : '清除失败');
    } finally {
      setClearingCache(false);
    }
  };

  // 重置设置
  const handleReset = async () => {
    if (!confirm('确定要重置所有设置为默认值吗？此操作不可撤销。')) return;
    try {
      await resetSettings();
      alert('设置已重置');
      loadData();
    } catch (error) {
      alert(error instanceof Error ? error.message : '重置失败');
    }
  };

  // 更新设置
  const updateSetting = <K extends keyof AllSettings>(section: K, key: keyof AllSettings[K], value: any) => {
    if (!settings) return;
    setSettings({
      ...settings,
      [section]: { ...settings[section], [key]: value },
    });
  };

  const tabs = [
    { id: 'platform' as TabType, label: '平台设置', icon: <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="18" height="18" rx="2" /><path d="M3 9h18M9 21V9" /></svg> },
    { id: 'course' as TabType, label: '课程设置', icon: <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" /><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" /></svg> },
    { id: 'user' as TabType, label: '用户设置', icon: <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /><path d="M23 21v-2a4 4 0 0 0-3-3.87" /><path d="M16 3.13a4 4 0 0 1 0 7.75" /></svg> },
    { id: 'storage' as TabType, label: '存储设置', icon: <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" /></svg> },
    { id: 'log' as TabType, label: '日志设置', icon: <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /><polyline points="10 9 9 9 8 9" /></svg> },
    { id: 'system' as TabType, label: '系统信息', icon: <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><line x1="12" y1="16" x2="12" y2="12" /><line x1="12" y1="8" x2="12.01" y2="8" /></svg> },
  ];if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-10 h-10 border-4 border-red-200 border-t-red-500 rounded-full animate-spin"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-start justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold text-slate-900 italic">Settings.</h1>
          <p className="text-slate-500 mt-1">系统设置与配置管理</p>
        </div>
        <button onClick={handleReset} className="flex items-center gap-2 px-5 py-3 bg-slate-100 text-slate-700 rounded-xl hover:bg-slate-200 transition-colors font-medium">
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M23 4v6h-6M1 20v-6h6" /><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" /></svg>
          重置为默认
        </button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
        {tabs.map((tab) => (
          <button key={tab.id} onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium transition-colors whitespace-nowrap ${
              activeTab === tab.id ? 'bg-red-500 text-white' : 'bg-white text-slate-600 hover:bg-slate-50 border border-slate-200'
            }`}>
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm">
        {/* 平台设置 */}
        {activeTab === 'platform' && settings && (
          <div className="p-6 space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">平台基础设置</h2>
                <p className="text-sm text-slate-500">配置平台名称、公告和维护模式</p>
              </div>
              <button onClick={() => handleSave('platform')} disabled={saving}
                className="px-5 py-2.5 bg-red-500 text-white rounded-xl hover:bg-red-600 disabled:opacity-50 font-medium">
                {saving ? '保存中...' : '保存设置'}
              </button>
            </div>
            <div className="grid grid-cols-2 gap-6">
              <Input label="平台名称" value={settings.platform.platform_name}
                onChange={(v) => updateSetting('platform', 'platform_name', v)} />
              <Input label="Logo URL" value={settings.platform.logo_url || ''}
                onChange={(v) => updateSetting('platform', 'logo_url', v)} placeholder="https://..." />
            </div>
            <Input label="平台描述" value={settings.platform.platform_description}
              onChange={(v) => updateSetting('platform', 'platform_description', v)} />
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                <div>
                  <div className="font-medium text-slate-900">系统公告</div>
                  <div className="text-sm text-slate-500">启用后将在用户端显示公告</div>
                </div>
                <Toggle enabled={settings.platform.announcement_enabled}
                  onChange={(v) => updateSetting('platform', 'announcement_enabled', v)} />
              </div>
              {settings.platform.announcement_enabled && (
                <textarea value={settings.platform.announcement || ''}
                  onChange={(e) => updateSetting('platform', 'announcement', e.target.value)}
                  placeholder="输入公告内容..." rows={3}
                  className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500/20 focus:border-red-500" />
              )}
              <div className="flex items-center justify-between p-4 bg-amber-50 rounded-xl border border-amber-200">
                <div>
                  <div className="font-medium text-amber-900">维护模式</div>
                  <div className="text-sm text-amber-700">启用后用户将无法访问系统</div>
                </div>
                <Toggle enabled={settings.platform.maintenance_mode}
                  onChange={(v) => updateSetting('platform', 'maintenance_mode', v)} />
              </div>
              {settings.platform.maintenance_mode && (
                <Input label="维护提示信息" value={settings.platform.maintenance_message}
                  onChange={(v) => updateSetting('platform', 'maintenance_message', v)} />
              )}
            </div>
          </div>
        )}{/* 课程设置 */}
        {activeTab === 'course' && settings && (
          <div className="p-6 space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">课程默认设置</h2>
                <p className="text-sm text-slate-500">配置新课程的默认参数和 AI 生成选项</p>
              </div>
              <button onClick={() => handleSave('course')} disabled={saving}
                className="px-5 py-2.5 bg-red-500 text-white rounded-xl hover:bg-red-600 disabled:opacity-50 font-medium">
                {saving ? '保存中...' : '保存设置'}
              </button>
            </div>
            <div className="grid grid-cols-2 gap-6">
              <Select label="默认难度" value={settings.course.default_difficulty}
                onChange={(v) => updateSetting('course', 'default_difficulty', v)}
                options={[
                  { value: 'beginner', label: '入门' },
                  { value: 'intermediate', label: '中级' },
                  { value: 'advanced', label: '高级' },
                  { value: 'expert', label: '专家' },
                ]} />
              <Input label="AI 生成步骤数" type="number" value={settings.course.ai_generation_steps}
                onChange={(v) => updateSetting('course', 'ai_generation_steps', parseInt(v) || 8)}
                description="每个课时生成的步骤数量" />
            </div>
            <Input label="AI 内容最小长度" type="number" value={settings.course.ai_content_min_length}
              onChange={(v) => updateSetting('course', 'ai_content_min_length', parseInt(v) || 100)}
              description="AI 生成内容的最小字符数" />
            <TagsInput label="默认标签" value={settings.course.default_tags}
              onChange={(v) => updateSetting('course', 'default_tags', v)}
              description="新课程的默认标签选项" />
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                <div>
                  <div className="font-medium text-slate-900">自动发布</div>
                  <div className="text-sm text-slate-500">新课程创建后自动发布</div>
                </div>
                <Toggle enabled={settings.course.auto_publish}
                  onChange={(v) => updateSetting('course', 'auto_publish', v)} />
              </div>
              <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                <div>
                  <div className="font-medium text-slate-900">需要审核</div>
                  <div className="text-sm text-slate-500">课程发布前需要管理员审核</div>
                </div>
                <Toggle enabled={settings.course.require_review}
                  onChange={(v) => updateSetting('course', 'require_review', v)} />
              </div>
            </div>
          </div>
        )}

        {/* 用户设置 */}
        {activeTab === 'user' && settings && (
          <div className="p-6 space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">用户设置</h2>
                <p className="text-sm text-slate-500">配置用户注册、登录和权限</p>
              </div>
              <button onClick={() => handleSave('user')} disabled={saving}
                className="px-5 py-2.5 bg-red-500 text-white rounded-xl hover:bg-red-600 disabled:opacity-50 font-medium">
                {saving ? '保存中...' : '保存设置'}
              </button>
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                <div>
                  <div className="font-medium text-slate-900">开放注册</div>
                  <div className="text-sm text-slate-500">允许新用户注册账号</div>
                </div>
                <Toggle enabled={settings.user.allow_registration}
                  onChange={(v) => updateSetting('user', 'allow_registration', v)} />
              </div>
              <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                <div>
                  <div className="font-medium text-slate-900">邮箱验证</div>
                  <div className="text-sm text-slate-500">注册时需要验证邮箱</div>
                </div>
                <Toggle enabled={settings.user.require_email_verification}
                  onChange={(v) => updateSetting('user', 'require_email_verification', v)} />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-6">
              <Input label="登录失败锁定阈值" type="number" value={settings.user.login_fail_lock_threshold}
                onChange={(v) => updateSetting('user', 'login_fail_lock_threshold', parseInt(v) || 5)}
                description="连续失败次数后锁定账号" />
              <Input label="锁定时间（分钟）" type="number" value={settings.user.login_fail_lock_minutes}
                onChange={(v) => updateSetting('user', 'login_fail_lock_minutes', parseInt(v) || 30)} />
            </div>
            <Input label="会话超时（分钟）" type="number" value={settings.user.session_timeout_minutes}
              onChange={(v) => updateSetting('user', 'session_timeout_minutes', parseInt(v) || 1440)}
              description="用户无操作后自动登出的时间" />
          </div>
        )}{/* 存储设置 */}
        {activeTab === 'storage' && settings && (
          <div className="p-6 space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">存储设置</h2>
                <p className="text-sm text-slate-500">配置文件上传和存储选项</p>
              </div>
              <button onClick={() => handleSave('storage')} disabled={saving}
                className="px-5 py-2.5 bg-red-500 text-white rounded-xl hover:bg-red-600 disabled:opacity-50 font-medium">
                {saving ? '保存中...' : '保存设置'}
              </button>
            </div>
            <div className="grid grid-cols-2 gap-6">
              <Input label="最大上传大小 (MB)" type="number" value={settings.storage.max_upload_size_mb}
                onChange={(v) => updateSetting('storage', 'max_upload_size_mb', parseInt(v) || 100)} />
              <Input label="自动清理天数" type="number" value={settings.storage.auto_cleanup_days}
                onChange={(v) => updateSetting('storage', 'auto_cleanup_days', parseInt(v) || 30)}
                description="超过此天数的临时文件将被清理" />
            </div>
            <Input label="存储路径" value={settings.storage.storage_path}
              onChange={(v) => updateSetting('storage', 'storage_path', v)} />
            <TagsInput label="允许的图片类型" value={settings.storage.allowed_image_types}
              onChange={(v) => updateSetting('storage', 'allowed_image_types', v)} />
            <TagsInput label="允许的视频类型" value={settings.storage.allowed_video_types}
              onChange={(v) => updateSetting('storage', 'allowed_video_types', v)} />
            <TagsInput label="允许的文档类型" value={settings.storage.allowed_document_types}
              onChange={(v) => updateSetting('storage', 'allowed_document_types', v)} />
          </div>
        )}

        {/* 日志设置 */}
        {activeTab === 'log' && settings && (
          <div className="p-6 space-y-6">
            <div className="flex items-center justify-between pb-4 border-b border-slate-100">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">日志设置</h2>
                <p className="text-sm text-slate-500">配置系统日志记录选项</p>
              </div>
              <button onClick={() => handleSave('log')} disabled={saving}
                className="px-5 py-2.5 bg-red-500 text-white rounded-xl hover:bg-red-600 disabled:opacity-50 font-medium">
                {saving ? '保存中...' : '保存设置'}
              </button>
            </div>
            <div className="grid grid-cols-2 gap-6">
              <Select label="日志级别" value={settings.log.log_level}
                onChange={(v) => updateSetting('log', 'log_level', v)}
                options={[
                  { value: 'DEBUG', label: 'DEBUG - 调试' },
                  { value: 'INFO', label: 'INFO - 信息' },
                  { value: 'WARNING', label: 'WARNING - 警告' },
                  { value: 'ERROR', label: 'ERROR - 错误' },
                ]} />
              <Input label="日志保留天数" type="number" value={settings.log.log_retention_days}
                onChange={(v) => updateSetting('log', 'log_retention_days', parseInt(v) || 30)} />
            </div>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                <div>
                  <div className="font-medium text-slate-900">访问日志</div>
                  <div className="text-sm text-slate-500">记录所有 API 访问请求</div>
                </div>
                <Toggle enabled={settings.log.enable_access_log}
                  onChange={(v) => updateSetting('log', 'enable_access_log', v)} />
              </div>
              <div className="flex items-center justify-between p-4 bg-slate-50 rounded-xl">
                <div>
                  <div className="font-medium text-slate-900">错误日志</div>
                  <div className="text-sm text-slate-500">记录系统错误和异常</div>
                </div>
                <Toggle enabled={settings.log.enable_error_log}
                  onChange={(v) => updateSetting('log', 'enable_error_log', v)} />
              </div>
            </div>
          </div>
        )}{/* 系统信息 */}
        {activeTab === 'system' && (
          <div className="p-6 space-y-6">
            <div className="pb-4 border-b border-slate-100">
              <h2 className="text-lg font-semibold text-slate-900">系统信息</h2>
              <p className="text-sm text-slate-500">查看系统状态和统计数据</p>
            </div>

            {/* 系统信息卡片 */}
            {systemInfo && (
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-slate-50 rounded-xl p-4">
                  <div className="text-sm text-slate-500">系统版本</div>
                  <div className="text-lg font-semibold text-slate-900">{systemInfo.version}</div>
                </div>
                <div className="bg-slate-50 rounded-xl p-4">
                  <div className="text-sm text-slate-500">运行环境</div>
                  <div className="text-lg font-semibold text-slate-900">{systemInfo.environment}</div>
                </div>
                <div className="bg-slate-50 rounded-xl p-4">
                  <div className="text-sm text-slate-500">Python 版本</div>
                  <div className="text-lg font-semibold text-slate-900">{systemInfo.python_version}</div>
                </div>
                <div className="bg-slate-50 rounded-xl p-4">
                  <div className="text-sm text-slate-500">数据库类型</div>
                  <div className="text-lg font-semibold text-slate-900">{systemInfo.database_type}</div>
                </div>
              </div>
            )}

            {/* 统计数据 */}
            {systemStats && (
              <div>
                <h3 className="text-md font-semibold text-slate-900 mb-4">数据统计</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <StatCard label="总用户数" value={systemStats.total_users} color="blue"
                    icon={<svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" /><circle cx="9" cy="7" r="4" /></svg>} />
                  <StatCard label="管理员数" value={systemStats.total_admins} color="purple"
                    icon={<svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="3" y="11" width="18" height="11" rx="2" /><path d="M7 11V7a5 5 0 0 1 10 0v4" /></svg>} />
                  <StatCard label="总课程数" value={systemStats.total_courses} color="green"
                    icon={<svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" /><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" /></svg>} />
                  <StatCard label="已发布" value={systemStats.published_courses} color="amber"
                    icon={<svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="20 6 9 17 4 12" /></svg>} />
                  <StatCard label="总节点数" value={systemStats.total_nodes} color="red"
                    icon={<svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="3" /></svg>} />
                  <StatCard label="学习记录" value={systemStats.total_progress_records} color="blue"
                    icon={<svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 20V10" /><path d="M12 20V4" /><path d="M6 20v-6" /></svg>} />
                  <StatCard label="存储使用" value={`${systemStats.storage_used_mb} MB`} color="purple"
                    icon={<svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z" /></svg>} />
                  {systemInfo?.database_size_mb && (
                    <StatCard label="数据库大小" value={`${systemInfo.database_size_mb} MB`} color="green"
                      icon={<svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><ellipse cx="12" cy="5" rx="9" ry="3" /><path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3" /><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5" /></svg>} />
                  )}
                </div>
              </div>
            )}

            {/* 缓存管理 */}
            {cacheInfo && (
              <div>
                <h3 className="text-md font-semibold text-slate-900 mb-4">缓存管理</h3>
                <div className="bg-slate-50 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className={`w-3 h-3 rounded-full ${cacheInfo.redis_connected ? 'bg-emerald-500' : 'bg-red-500'}`}></div>
                      <span className="font-medium text-slate-900">Redis {cacheInfo.redis_connected ? '已连接' : '未连接'}</span>
                    </div>
                    <button onClick={handleClearCache} disabled={clearingCache || !cacheInfo.redis_connected}
                      className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 disabled:opacity-50 text-sm font-medium">
                      {clearingCache ? '清除中...' : '清除缓存'}
                    </button>
                  </div>
                  <div className="grid grid-cols-3 gap-4 text-sm">
                    <div>
                      <div className="text-slate-500">连接地址</div>
                      <div className="font-mono text-slate-700">{cacheInfo.redis_url}</div>
                    </div>
                    <div>
                      <div className="text-slate-500">缓存键数</div>
                      <div className="font-semibold text-slate-900">{cacheInfo.keys_count ?? '-'}</div>
                    </div>
                    <div>
                      <div className="text-slate-500">内存使用</div>
                      <div className="font-semibold text-slate-900">{cacheInfo.memory_used_mb ? `${cacheInfo.memory_used_mb} MB` : '-'}</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}