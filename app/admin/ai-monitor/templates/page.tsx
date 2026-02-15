'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://106.14.180.66:8001';

interface Template {
  id: number;
  subject: string;
  topic: string;
  qualityScore: number;
  lineCount: number;
  visualElements: number | null;
  createdAt: string | null;
}

interface TemplateDetail extends Template {
  code: string;
}

const SUBJECT_LABELS: Record<string, string> = {
  physics: '物理', mathematics: '数学', chemistry: '化学',
  biology: '生物', medicine: '医学', geography: '地理',
  history: '历史', computer_science: '计算机',
};

const SUBJECT_COLORS: Record<string, string> = {
  physics: 'bg-blue-100 text-blue-700',
  mathematics: 'bg-purple-100 text-purple-700',
  chemistry: 'bg-orange-100 text-orange-700',
  biology: 'bg-green-100 text-green-700',
  medicine: 'bg-red-100 text-red-700',
  geography: 'bg-cyan-100 text-cyan-700',
  history: 'bg-amber-100 text-amber-700',
  computer_science: 'bg-indigo-100 text-indigo-700',
};

function ScoreBadge({ score }: { score: number }) {
  const color = score >= 85 ? 'bg-green-100 text-green-700'
    : score >= 75 ? 'bg-blue-100 text-blue-700'
    : score >= 60 ? 'bg-yellow-100 text-yellow-700'
    : 'bg-red-100 text-red-700';
  const grade = score >= 90 ? 'S' : score >= 85 ? 'A' : score >= 75 ? 'B' : score >= 60 ? 'C' : 'D';
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold ${color}`}>
      {grade} · {score.toFixed(0)}
    </span>
  );
}

function PreviewModal({ template, onClose }: { template: TemplateDetail; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onClose}>
      <div className="bg-white rounded-2xl shadow-2xl w-[90vw] max-w-[1200px] h-[85vh] flex flex-col" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <div className="flex items-center gap-3">
            <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${SUBJECT_COLORS[template.subject] || 'bg-slate-100 text-slate-600'}`}>
              {SUBJECT_LABELS[template.subject] || template.subject}
            </span>
            <h2 className="text-lg font-bold text-slate-900">{template.topic}</h2>
            <ScoreBadge score={template.qualityScore} />
          </div>
          <button onClick={onClose} className="p-2 text-slate-400 hover:text-slate-600 hover:bg-slate-100 rounded-lg transition-colors">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6L6 18M6 6l12 12"/></svg>
          </button>
        </div>
        {/* Preview iframe */}
        <div className="flex-1 bg-slate-900 rounded-b-2xl overflow-hidden">
          <iframe
            srcDoc={template.code}
            className="w-full h-full border-0"
            sandbox="allow-scripts"
            title={template.topic}
          />
        </div>
      </div>
    </div>
  );
}

function DeleteConfirmModal({ template, onConfirm, onCancel }: {
  template: Template; onConfirm: () => void; onCancel: () => void;
}) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50" onClick={onCancel}>
      <div className="bg-white rounded-2xl shadow-2xl p-6 w-[400px]" onClick={e => e.stopPropagation()}>
        <h3 className="text-lg font-bold text-slate-900 mb-2">确认删除</h3>
        <p className="text-slate-600 text-sm mb-4">
          确定要删除模板 <span className="font-medium text-slate-900">{template.topic}</span> 吗？此操作不可撤销。
        </p>
        <div className="flex justify-end gap-3">
          <button onClick={onCancel} className="px-4 py-2 text-sm text-slate-600 bg-slate-100 rounded-lg hover:bg-slate-200 transition-colors">
            取消
          </button>
          <button onClick={onConfirm} className="px-4 py-2 text-sm text-white bg-red-600 rounded-lg hover:bg-red-700 transition-colors">
            删除
          </button>
        </div>
      </div>
    </div>
  );
}

export default function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [subjectFilter, setSubjectFilter] = useState('');
  const [subjects, setSubjects] = useState<{ subject: string; count: number }[]>([]);
  const [previewTemplate, setPreviewTemplate] = useState<TemplateDetail | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<Template | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);

  const loadTemplates = useCallback(async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({ page: String(page), page_size: '12' });
      if (subjectFilter) params.set('subject', subjectFilter);
      const res = await fetch(`${API_BASE}/api/v1/agent/templates?${params}`);
      const data = await res.json();
      setTemplates(data.templates || []);
      setTotal(data.total || 0);
    } catch (err) {
      console.error('Failed to load templates:', err);
    } finally {
      setLoading(false);
    }
  }, [page, subjectFilter]);

  const loadSubjects = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/agent/templates/subjects/list`);
      const data = await res.json();
      setSubjects(data || []);
    } catch (err) {
      console.error('Failed to load subjects:', err);
    }
  };

  useEffect(() => { loadSubjects(); }, []);
  useEffect(() => { loadTemplates(); }, [loadTemplates]);

  const handlePreview = async (id: number) => {
    try {
      setPreviewLoading(true);
      const res = await fetch(`${API_BASE}/api/v1/agent/templates/${id}`);
      const data = await res.json();
      setPreviewTemplate(data);
    } catch (err) {
      console.error('Failed to load template:', err);
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await fetch(`${API_BASE}/api/v1/agent/templates/${deleteTarget.id}`, { method: 'DELETE' });
      setDeleteTarget(null);
      loadTemplates();
    } catch (err) {
      console.error('Failed to delete template:', err);
    }
  };

  const totalPages = Math.ceil(total / 12);

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2 text-sm text-slate-500 mb-1">
            <Link href="/admin/ai-monitor" className="hover:text-slate-700">AI 监控</Link>
            <span>/</span>
            <span className="text-slate-900">模拟器模板库</span>
          </div>
          <h1 className="text-3xl font-bold text-slate-900">模拟器模板库</h1>
          <p className="text-slate-500 mt-1">浏览、预览和管理所有模拟器模板 · 共 {total} 个模板</p>
        </div>
        <Link
          href="/admin/ai-monitor"
          className="px-4 py-2 text-sm font-medium text-slate-600 bg-white border border-slate-200 rounded-xl hover:bg-slate-50 transition-colors"
        >
          返回监控
        </Link>
      </div>

      {/* Subject Filter */}
      <div className="bg-white rounded-2xl p-4 shadow-sm border border-slate-100">
        <div className="flex items-center gap-2 flex-wrap">
          <span className="text-sm text-slate-500 mr-2">学科筛选:</span>
          <button
            onClick={() => { setSubjectFilter(''); setPage(1); }}
            className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${!subjectFilter ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
          >
            全部
          </button>
          {subjects.map(s => (
            <button
              key={s.subject}
              onClick={() => { setSubjectFilter(s.subject); setPage(1); }}
              className={`px-3 py-1.5 text-sm rounded-lg transition-colors ${subjectFilter === s.subject ? 'bg-slate-900 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}`}
            >
              {SUBJECT_LABELS[s.subject] || s.subject} ({s.count})
            </button>
          ))}
        </div>
      </div>

      {/* Template Grid */}
      {loading ? (
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="w-10 h-10 border-4 border-red-200 border-t-red-500 rounded-full animate-spin"></div>
        </div>
      ) : templates.length === 0 ? (
        <div className="bg-white rounded-2xl p-12 shadow-sm border border-slate-100 text-center">
          <p className="text-slate-400 text-lg">暂无模板</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {templates.map(t => (
            <div key={t.id} className="bg-white rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow overflow-hidden group">
              {/* Card Header */}
              <div className="p-4 pb-3">
                <div className="flex items-start justify-between mb-2">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${SUBJECT_COLORS[t.subject] || 'bg-slate-100 text-slate-600'}`}>
                    {SUBJECT_LABELS[t.subject] || t.subject}
                  </span>
                  <ScoreBadge score={t.qualityScore} />
                </div>
                <h3 className="text-base font-semibold text-slate-900 mb-1 line-clamp-1">{t.topic}</h3>
                <div className="flex items-center gap-3 text-xs text-slate-400">
                  <span>{t.lineCount} 行</span>
                  {t.visualElements && <span>{t.visualElements} 个视觉元素</span>}
                  <span>#{t.id}</span>
                </div>
              </div>
              {/* Actions */}
              <div className="flex border-t border-slate-100">
                <button
                  onClick={() => handlePreview(t.id)}
                  className="flex-1 py-2.5 text-sm font-medium text-blue-600 hover:bg-blue-50 transition-colors text-center"
                >
                  预览
                </button>
                <div className="w-px bg-slate-100"></div>
                <button
                  onClick={() => setDeleteTarget(t)}
                  className="flex-1 py-2.5 text-sm font-medium text-red-500 hover:bg-red-50 transition-colors text-center"
                >
                  删除
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2">
          <button
            onClick={() => setPage(p => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-3 py-1.5 text-sm rounded-lg bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            上一页
          </button>
          <span className="text-sm text-slate-500">
            {page} / {totalPages}
          </span>
          <button
            onClick={() => setPage(p => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-3 py-1.5 text-sm rounded-lg bg-white border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            下一页
          </button>
        </div>
      )}

      {/* Preview Modal */}
      {previewTemplate && <PreviewModal template={previewTemplate} onClose={() => setPreviewTemplate(null)} />}

      {/* Delete Confirm Modal */}
      {deleteTarget && <DeleteConfirmModal template={deleteTarget} onConfirm={handleDelete} onCancel={() => setDeleteTarget(null)} />}

      {/* Preview Loading Overlay */}
      {previewLoading && (
        <div className="fixed inset-0 z-40 flex items-center justify-center bg-black/30">
          <div className="w-10 h-10 border-4 border-white/30 border-t-white rounded-full animate-spin"></div>
        </div>
      )}
    </div>
  );
}
