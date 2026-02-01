/**
 * Studio - 文件上传区域组件
 */

'use client';

import { useState, useRef, useCallback } from 'react';
import { cn } from '@/lib/utils';
import { studioUploadApi, getStudioErrorMessage } from '@/lib/api/studio';
import type { UploadedSource } from '@/types/studio';

interface FileUploadZoneProps {
  sources: UploadedSource[];
  onSourcesChange: (sources: UploadedSource[]) => void;
  className?: string;
}

const ALLOWED_EXTENSIONS = ['.pdf', '.doc', '.docx', '.txt', '.md', '.markdown', '.epub', '.html', '.htm'];
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

const getFileIcon = (filename: string) => {
  const ext = filename.split('.').pop()?.toLowerCase();
  switch (ext) {
    case 'pdf':
      return (
        <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      );
    case 'doc':
    case 'docx':
      return (
        <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
      );
    case 'epub':
      return (
        <svg className="w-5 h-5 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
        </svg>
      );
    default:
      return (
        <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
      );
  }
};

export function FileUploadZone({ sources, onSourcesChange, className }: FileUploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const validateFile = (file: File): string | null => {
    const ext = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!ALLOWED_EXTENSIONS.includes(ext)) {
      return `不支持的文件类型: ${ext}`;
    }
    if (file.size > MAX_FILE_SIZE) {
      return `文件过大，最大支持 ${MAX_FILE_SIZE / (1024 * 1024)}MB`;
    }
    if (file.size === 0) {
      return '文件内容为空';
    }
    return null;
  };

  const handleUpload = useCallback(async (files: FileList) => {
    setError(null);
    setIsUploading(true);

    const newSources: UploadedSource[] = [];
    const errors: string[] = [];

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      setUploadProgress(`正在处理 ${file.name} (${i + 1}/${files.length})...`);

      const validationError = validateFile(file);
      if (validationError) {
        errors.push(`${file.name}: ${validationError}`);
        continue;
      }

      try {
        const result = await studioUploadApi.uploadFile(file);
        newSources.push({
          id: `file-${Date.now()}-${i}`,
          name: result.filename,
          charCount: result.char_count,
          text: result.text,
          type: 'file',
        });
      } catch (err) {
        errors.push(`${file.name}: ${getStudioErrorMessage(err)}`);
      }
    }

    if (newSources.length > 0) {
      onSourcesChange([...sources, ...newSources]);
    }

    if (errors.length > 0) {
      setError(errors.join('\n'));
    }

    setIsUploading(false);
    setUploadProgress(null);
  }, [sources, onSourcesChange]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleUpload(files);
    }
  }, [handleUpload]);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleUpload(files);
    }
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [handleUpload]);

  const handleClick = () => {
    fileInputRef.current?.click();
  };

  const handleRemoveSource = (id: string) => {
    onSourcesChange(sources.filter(s => s.id !== id));
  };

  return (
    <div className={cn('flex flex-col h-full', className)}>
      <input
        ref={fileInputRef}
        type="file"
        accept={ALLOWED_EXTENSIONS.join(',')}
        onChange={handleFileSelect}
        className="hidden"
        multiple
      />

      {/* Source List */}
      {sources.length > 0 && (
        <div className="flex-1 overflow-auto space-y-2 mb-4">
          {sources.map((source) => (
            <div
              key={source.id}
              className="group flex items-center gap-3 p-3 bg-white border border-slate-200 rounded-xl hover:border-slate-300 transition-colors"
            >
              <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center flex-shrink-0">
                {source.type === 'file' ? getFileIcon(source.name) : (
                  <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-slate-700 truncate">{source.name}</p>
                <p className="text-xs text-slate-500">{source.charCount.toLocaleString()} 字符</p>
              </div>
              <button
                onClick={() => handleRemoveSource(source.id)}
                className="p-1.5 opacity-0 group-hover:opacity-100 hover:bg-slate-100 rounded-lg transition-all"
              >
                <svg className="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Upload Zone */}
      <div
        onClick={handleClick}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={cn(
          'relative border-2 border-dashed rounded-xl p-6 transition-all cursor-pointer',
          sources.length > 0 ? 'py-4' : 'py-8',
          isDragging
            ? 'border-primary-500 bg-primary-50'
            : 'border-slate-300 hover:border-slate-400 hover:bg-slate-50',
          isUploading && 'pointer-events-none opacity-60'
        )}
      >
        <div className="flex flex-col items-center gap-2 text-center">
          {isUploading ? (
            <>
              <svg className="w-7 h-7 text-primary-500 animate-spin" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              <p className="text-sm text-slate-600">{uploadProgress || '正在上传...'}</p>
            </>
          ) : (
            <>
              <svg className={cn('w-7 h-7', isDragging ? 'text-primary-500' : 'text-slate-400')} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
              </svg>
              <div>
                <p className="text-sm font-medium text-slate-700">
                  {sources.length > 0 ? '添加更多素材' : '拖拽文件到此处'}
                </p>
                <p className="text-xs text-slate-500 mt-1">
                  支持 PDF、Word、TXT、Markdown、EPUB、HTML
                </p>
                <p className="text-xs text-slate-400 mt-0.5">
                  最大 50MB，可同时上传多个文件
                </p>
              </div>
            </>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-3 flex items-start gap-2 p-3 bg-red-50 border border-red-200 rounded-xl">
          <svg className="w-4 h-4 text-red-500 flex-shrink-0 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm text-red-600 whitespace-pre-wrap">{error}</p>
        </div>
      )}
    </div>
  );
}
