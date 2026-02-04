/**
 * InputView - 输入视图组件 (三栏布局)
 */

import { PenLine, Sparkles, PlayCircle, FileText, Eye, X, Trash2 } from 'lucide-react';
import { cn } from '@/lib/utils';
import { FileUploadZone } from '@/components/studio/upload/FileUploadZone';
import { getTotalCharCount } from '@/stores/studio/useStudioStore';
import type { ProcessorWithConfig, UploadedSource } from '@/types/studio';

interface InputViewProps {
  sources: UploadedSource[];
  setSources: (sources: UploadedSource[]) => void;
  showPasteInput: boolean;
  setShowPasteInput: (show: boolean) => void;
  pastedText: string;
  setPastedText: (text: string) => void;
  handleAddPastedText: () => void;
  setPreviewSource: (source: UploadedSource | null) => void;
  courseTitle: string;
  setCourseTitle: (title: string) => void;
  sourceInfo: string;
  setSourceInfo: (info: string) => void;
  processors: ProcessorWithConfig[];
  selectedProcessorId: string;
  setSelectedProcessorId: (id: string) => void;
  canGenerate: () => boolean;
  handleGenerate: () => void;
}

export function InputView({
  sources,
  setSources,
  showPasteInput,
  setShowPasteInput,
  pastedText,
  setPastedText,
  handleAddPastedText,
  setPreviewSource,
  courseTitle,
  setCourseTitle,
  sourceInfo,
  setSourceInfo,
  processors,
  selectedProcessorId,
  setSelectedProcessorId,
  canGenerate,
  handleGenerate,
}: InputViewProps) {
  const totalChars = getTotalCharCount(sources);

  return (
    <div className="flex-1 flex overflow-hidden">
      {/* Left Panel - Sources */}
      <div className="w-80 bg-slate-50 border-r border-slate-200 flex flex-col">
        <div className="p-4 border-b border-slate-200">
          <h2 className="text-sm font-bold text-slate-700 uppercase tracking-wider">素材来源</h2>
          <p className="text-xs text-slate-500 mt-1">
            {sources.length > 0 ? `${sources.length} 个文件，${totalChars.toLocaleString()} 字符` : '上传文件或粘贴文本'}
          </p>
        </div>

        <div className="flex-1 overflow-auto p-4">
          <FileUploadZone
            sources={sources}
            onSourcesChange={setSources}
          />

          {/* Source List */}
          {sources.length > 0 && (
            <div className="mt-4 space-y-2">
              {sources.map((source) => (
                <div
                  key={source.id}
                  className="flex items-center justify-between p-3 bg-white rounded-xl border border-slate-200 hover:border-slate-300 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className={cn(
                      'w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0',
                      source.type === 'paste' ? 'bg-purple-100' : 'bg-blue-100'
                    )}>
                      {source.type === 'paste' ? (
                        <PenLine size={16} className="text-purple-600" />
                      ) : (
                        <FileText size={16} className="text-blue-600" />
                      )}
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-slate-900 truncate">{source.name}</p>
                      <p className="text-xs text-slate-500">{source.charCount.toLocaleString()} 字符</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-1 flex-shrink-0">
                    <button
                      onClick={() => setPreviewSource(source)}
                      className="p-1.5 hover:bg-slate-100 rounded-lg transition-colors"
                      title="预览"
                    >
                      <Eye size={14} className="text-slate-500" />
                    </button>
                    <button
                      onClick={() => setSources(sources.filter(s => s.id !== source.id))}
                      className="p-1.5 hover:bg-red-100 rounded-lg transition-colors"
                      title="删除"
                    >
                      <Trash2 size={14} className="text-red-500" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Add Text Button */}
        <div className="p-4 border-t border-slate-200">
          {showPasteInput ? (
            <div className="space-y-3">
              <textarea
                value={pastedText}
                onChange={(e) => setPastedText(e.target.value)}
                placeholder="粘贴文本内容..."
                rows={4}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
                autoFocus
              />
              <div className="flex gap-2">
                <button
                  onClick={handleAddPastedText}
                  disabled={!pastedText.trim()}
                  className="flex-1 px-4 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  添加
                </button>
                <button
                  onClick={() => {
                    setShowPasteInput(false);
                    setPastedText('');
                  }}
                  className="px-4 py-2 text-sm text-slate-600 hover:bg-slate-100 rounded-lg transition-colors"
                >
                  取消
                </button>
              </div>
            </div>
          ) : (
            <button
              onClick={() => setShowPasteInput(true)}
              className="w-full flex items-center justify-center gap-2 px-4 py-2 text-sm text-slate-600 hover:text-slate-900 hover:bg-slate-100 rounded-lg transition-colors"
            >
              <PenLine size={16} />
              <span>粘贴文本</span>
            </button>
          )}
        </div>
      </div>

      {/* Center Panel - Configuration */}
      <div className="flex-1 flex flex-col bg-white overflow-hidden">
        <div className="flex-1 overflow-auto p-8">
          <div className="max-w-xl w-full space-y-8 mx-auto">
            {/* Hero */}
            <div className="text-center space-y-4">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-red-50 border border-red-200 rounded-full">
                <Sparkles size={16} className="text-red-600" />
                <span className="text-xs font-bold text-red-600 uppercase tracking-wider">
                  AI 课程生成
                </span>
              </div>
              <h1 className="text-3xl font-black text-slate-900">HERCU Studio</h1>
              <p className="text-slate-600">
                上传素材，AI 自动生成结构化课程包
              </p>
            </div>

            {/* Course Title */}
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700">课程标题</label>
              <input
                type="text"
                value={courseTitle}
                onChange={(e) => setCourseTitle(e.target.value)}
                placeholder="例如：力量训练基础原理"
                className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all text-lg"
              />
            </div>

            {/* Source Info */}
            <div className="space-y-2">
              <label className="text-sm font-bold text-slate-700">来源说明（可选）</label>
              <input
                type="text"
                value={sourceInfo}
                onChange={(e) => setSourceInfo(e.target.value)}
                placeholder="例如：CSCS 教材第三章"
                className="w-full px-4 py-3 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent transition-all"
              />
            </div>

            {/* Processor Selection */}
            <div className="space-y-3">
              <label className="text-sm font-bold text-slate-700">讲解风格</label>
              <div className="grid grid-cols-2 gap-3">
                {processors.map((processor) => (
                  <button
                    key={processor.id}
                    onClick={() => setSelectedProcessorId(processor.id)}
                    className={cn(
                      'p-4 rounded-xl border-2 transition-all text-left',
                      selectedProcessorId === processor.id
                        ? 'border-red-500 bg-red-50'
                        : 'border-slate-200 hover:border-slate-300'
                    )}
                  >
                    <div className="flex items-center gap-2 mb-1">
                      <div
                        className="w-3 h-3 rounded-full"
                        style={{ backgroundColor: processor.color || '#ef4444' }}
                      />
                      <p
                        className={cn(
                          'text-sm font-bold',
                          selectedProcessorId === processor.id ? 'text-red-600' : 'text-slate-700'
                        )}
                      >
                        {processor.name}
                      </p>
                    </div>
                    <p className="text-xs text-slate-500">{processor.description}</p>
                    {processor.tags && (Array.isArray(processor.tags) ? processor.tags : []).length > 0 && (
                      <div className="flex flex-wrap gap-1 mt-2">
                        {(Array.isArray(processor.tags) ? processor.tags : (typeof processor.tags === 'string' ? JSON.parse(processor.tags) : [])).map((tag: string) => (
                          <span
                            key={tag}
                            className="text-xs px-1.5 py-0.5 bg-slate-100 text-slate-500 rounded"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Generate Button */}
            <button
              onClick={handleGenerate}
              disabled={!canGenerate()}
              className={cn(
                'w-full py-4 text-lg font-bold rounded-xl transition-all flex items-center justify-center gap-2',
                canGenerate()
                  ? 'bg-red-600 text-white hover:bg-red-700 shadow-lg hover:shadow-xl'
                  : 'bg-slate-200 text-slate-400 cursor-not-allowed'
              )}
            >
              <PlayCircle size={24} />
              生成课程包
            </button>

            {/* Status */}
            {sources.length === 0 && (
              <p className="text-center text-sm text-slate-500">
                请先在左侧添加素材
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Right Panel - Preview */}
      <div className="w-80 bg-slate-50 border-l border-slate-200 flex flex-col">
        <div className="p-4 border-b border-slate-200">
          <h2 className="text-sm font-bold text-slate-700 uppercase tracking-wider">素材预览</h2>
        </div>
        <div className="flex-1 overflow-auto p-4">
          {sources.length > 0 ? (
            <div className="space-y-4">
              {sources.map((source) => (
                <button
                  key={source.id}
                  onClick={() => setPreviewSource(source)}
                  className="w-full bg-white rounded-lg p-3 border border-slate-200 hover:border-red-300 hover:shadow-sm transition-all text-left group"
                >
                  <div className="flex items-center justify-between mb-2">
                    <p className="text-xs font-medium text-slate-700">{source.name}</p>
                    <Eye size={14} className="text-slate-400 group-hover:text-red-500 transition-colors" />
                  </div>
                  <p className="text-xs text-slate-500 line-clamp-6 whitespace-pre-wrap">
                    {source.text.slice(0, 500)}...
                  </p>
                  <p className="text-xs text-red-500 mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                    点击查看完整内容
                  </p>
                </button>
              ))}
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-slate-400">
              <FileText size={48} className="mb-4 opacity-50" />
              <p className="text-sm text-center">
                上传文件后<br />可在此预览内容
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
