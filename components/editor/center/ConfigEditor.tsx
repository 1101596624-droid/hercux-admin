'use client';

/**
 * ConfigEditor - 配置编辑器
 * 根据组件类型显示不同的配置表单
 */

import React, { useState, useRef, useCallback } from 'react';
import type { ComponentType, NodeConfig, VideoConfig, QuizConfig, TextConfig, QuizQuestion, IllustratedConfig } from '@/types/editor';
import { Input } from '@/components/ui/Input';
import { SimulatorConfigEditor } from './SimulatorConfigEditor';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
const BACKEND_ORIGIN = process.env.NEXT_PUBLIC_STUDIO_API_URL || 'http://localhost:8000';

/** 将后端返回的相对路径解析为完整 URL */
function resolveMediaUrl(url: string): string {
  if (!url || url.startsWith('http://') || url.startsWith('https://') || url.startsWith('blob:')) return url;
  return `${BACKEND_ORIGIN}${url}`;
}

/** Helper: upload file via multipart/form-data */
async function uploadFile(
  endpoint: string,
  file: File,
  extraFields?: Record<string, string>,
  onProgress?: (pct: number) => void,
): Promise<any> {
  const token = typeof window !== 'undefined' ? localStorage.getItem('auth_token') : null;
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', `${API_BASE_URL}${endpoint}`);
    if (token) xhr.setRequestHeader('Authorization', `Bearer ${token}`);
    xhr.upload.onprogress = (e) => {
      if (e.lengthComputable && onProgress) onProgress(Math.round((e.loaded / e.total) * 100));
    };
    xhr.onload = () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText));
      } else {
        try { reject(new Error(JSON.parse(xhr.responseText).detail || `上传失败 (${xhr.status})`)); }
        catch { reject(new Error(`上传失败 (${xhr.status})`)); }
      }
    };
    xhr.onerror = () => reject(new Error('网络错误'));
    const fd = new FormData();
    fd.append('file', file);
    if (extraFields) Object.entries(extraFields).forEach(([k, v]) => fd.append(k, v));
    xhr.send(fd);
  });
}

interface ConfigEditorProps {
  type: ComponentType;
  config: NodeConfig;
  onChange: (config: Partial<NodeConfig>) => void;
}

export function ConfigEditor({ type, config, onChange }: ConfigEditorProps) {
  switch (type) {
    case 'video':
      return (
        <VideoConfigEditor
          config={config.videoConfig}
          onChange={(videoConfig) => onChange({ videoConfig })}
        />
      );
    case 'text_content':
      return (
        <TextConfigEditor
          config={config.textConfig}
          onChange={(textConfig) => onChange({ textConfig })}
        />
      );
    case 'assessment':
    case 'quick_check':
      return (
        <QuizConfigEditor
          config={config.quizConfig}
          onChange={(quizConfig) => onChange({ quizConfig })}
        />
      );
    case 'simulator':
      return (
        <SimulatorConfigEditor
          config={config.simulatorConfig}
          onChange={(simulatorConfig) => onChange({ simulatorConfig })}
        />
      );
    case 'illustrated_content':
      return (
        <IllustratedConfigEditor
          textConfig={config.textConfig}
          illustratedConfig={config.illustratedConfig}
          onChange={(updates) => onChange(updates)}
        />
      );
    default:
      return (
        <div className="text-dark-500 text-sm">
          该组件类型暂不支持编辑
        </div>
      );
  }
}

// Video Config Editor
interface VideoConfigEditorProps {
  config?: VideoConfig;
  onChange: (config: VideoConfig) => void;
}

function VideoConfigEditor({ config, onChange }: VideoConfigEditorProps) {
  const currentConfig: VideoConfig = config || { videoUrl: '' };
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [showUrlInput, setShowUrlInput] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = useCallback(async (file: File) => {
    const validTypes = ['video/mp4', 'video/webm', 'video/quicktime', 'video/x-msvideo', 'video/x-matroska', 'video/x-flv', 'video/x-ms-wmv', 'video/x-m4v'];
    if (!file.type.startsWith('video/')) {
      setError('请选择视频文件');
      return;
    }
    if (file.size > 100 * 1024 * 1024) {
      setError('视频文件不能超过 100MB');
      return;
    }
    setUploading(true);
    setProgress(0);
    setError(null);
    try {
      const result = await uploadFile('/upload/video', file, undefined, setProgress);
      onChange({ ...currentConfig, videoUrl: result.file_url });
    } catch (e: any) {
      setError(e.message || '上传失败');
    } finally {
      setUploading(false);
    }
  }, [currentConfig, onChange]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  }, [handleUpload]);

  const handleDelete = () => {
    onChange({ ...currentConfig, videoUrl: '' });
  };

  return (
    <div className="space-y-4">
      {/* Upload area or video preview */}
      {currentConfig.videoUrl ? (
        <div className="space-y-2">
          <label className="block text-sm font-medium text-dark-700">视频预览</label>
          <video
            src={resolveMediaUrl(currentConfig.videoUrl)}
            controls
            className="w-full rounded-lg border border-dark-200"
          />
          <div className="flex gap-2">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="text-sm text-primary-600 hover:text-primary-700"
            >
              重新上传
            </button>
            <button onClick={handleDelete} className="text-sm text-red-500 hover:text-red-600">
              删除视频
            </button>
          </div>
        </div>
      ) : (
        <div>
          <label className="block text-sm font-medium text-dark-700 mb-1.5">上传视频</label>
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => !uploading && fileInputRef.current?.click()}
            className="border-2 border-dashed border-dark-300 rounded-lg p-8 text-center cursor-pointer hover:border-primary-400 hover:bg-primary-50/30 transition-colors"
          >
            {uploading ? (
              <div className="space-y-2">
                <p className="text-sm text-dark-500">上传中... {progress}%</p>
                <div className="w-full bg-dark-200 rounded-full h-2">
                  <div className="bg-primary-500 h-2 rounded-full transition-all" style={{ width: `${progress}%` }} />
                </div>
              </div>
            ) : (
              <>
                <svg className="w-10 h-10 mx-auto text-dark-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <p className="text-sm text-dark-500">拖拽视频到此处，或点击选择文件</p>
                <p className="text-xs text-dark-400 mt-1">支持 mp4, webm, mov 等格式，最大 100MB</p>
              </>
            )}
          </div>
        </div>
      )}

      <input
        ref={fileInputRef}
        type="file"
        accept="video/*"
        className="hidden"
        onChange={(e) => { const f = e.target.files?.[0]; if (f) handleUpload(f); e.target.value = ''; }}
      />

      {error && <p className="text-sm text-red-500">{error}</p>}

      {/* Collapsible URL input */}
      <div>
        <button
          onClick={() => setShowUrlInput(!showUrlInput)}
          className="text-xs text-dark-400 hover:text-dark-600 flex items-center gap-1"
        >
          <svg className={`w-3 h-3 transition-transform ${showUrlInput ? 'rotate-90' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
          手动输入 URL
        </button>
        {showUrlInput && (
          <div className="mt-2">
            <Input
              label="视频 URL"
              placeholder="https://example.com/video.mp4"
              value={currentConfig.videoUrl}
              onChange={(e) => onChange({ ...currentConfig, videoUrl: e.target.value })}
            />
          </div>
        )}
      </div>

      <Input
        label="字幕 URL（可选）"
        placeholder="https://example.com/subtitle.vtt"
        value={currentConfig.subtitleUrl || ''}
        onChange={(e) => onChange({ ...currentConfig, subtitleUrl: e.target.value })}
      />
      <Input
        label="视频时长（秒）"
        type="number"
        placeholder="300"
        value={currentConfig.duration || ''}
        onChange={(e) => onChange({ ...currentConfig, duration: parseInt(e.target.value) || undefined })}
      />
      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="autoPlay"
          checked={currentConfig.autoPlay || false}
          onChange={(e) => onChange({ ...currentConfig, autoPlay: e.target.checked })}
          className="rounded border-dark-300 text-primary-600 focus:ring-primary-500"
        />
        <label htmlFor="autoPlay" className="text-sm text-dark-700">
          自动播放
        </label>
      </div>
    </div>
  );
}

// Text Config Editor
interface TextConfigEditorProps {
  config?: TextConfig;
  onChange: (config: TextConfig) => void;
}

function TextConfigEditor({ config, onChange }: TextConfigEditorProps) {
  const currentConfig: TextConfig = config || { content: '', format: 'markdown' };

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-dark-700 mb-1.5">
          内容格式
        </label>
        <select
          value={currentConfig.format}
          onChange={(e) => onChange({ ...currentConfig, format: e.target.value as TextConfig['format'] })}
          className="w-full rounded-lg border border-dark-200 px-3 py-2 text-dark-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
          <option value="markdown">Markdown</option>
          <option value="html">HTML</option>
          <option value="plain">纯文本</option>
        </select>
      </div>
      <div>
        <label className="block text-sm font-medium text-dark-700 mb-1.5">
          内容
        </label>
        <textarea
          value={currentConfig.content}
          onChange={(e) => onChange({ ...currentConfig, content: e.target.value })}
          placeholder="输入内容..."
          rows={10}
          className="w-full rounded-lg border border-dark-200 px-3 py-2 text-dark-900 focus:outline-none focus:ring-2 focus:ring-primary-500 font-mono text-sm"
        />
      </div>
      <div>
        <label className="block text-sm font-medium text-dark-700 mb-1.5">
          关键点（每行一个）
        </label>
        <textarea
          value={(currentConfig.keyPoints || []).join('\n')}
          onChange={(e) => onChange({
            ...currentConfig,
            keyPoints: e.target.value.split('\n').filter(Boolean),
          })}
          placeholder="关键点1&#10;关键点2&#10;关键点3"
          rows={4}
          className="w-full rounded-lg border border-dark-200 px-3 py-2 text-dark-900 focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
        />
      </div>
    </div>
  );
}

// Quiz Config Editor
interface QuizConfigEditorProps {
  config?: QuizConfig;
  onChange: (config: QuizConfig) => void;
}

function QuizConfigEditor({ config, onChange }: QuizConfigEditorProps) {
  const currentConfig: QuizConfig = config || { questions: [], passingScore: 60 };

  const addQuestion = () => {
    const newQuestion: QuizQuestion = {
      id: `q-${Date.now()}`,
      question: '',
      options: ['', '', '', ''],
      correctIndex: 0,
    };
    onChange({
      ...currentConfig,
      questions: [...currentConfig.questions, newQuestion],
    });
  };

  const updateQuestion = (index: number, updates: Partial<QuizQuestion>) => {
    const newQuestions = [...currentConfig.questions];
    newQuestions[index] = { ...newQuestions[index], ...updates };
    onChange({ ...currentConfig, questions: newQuestions });
  };

  const deleteQuestion = (index: number) => {
    onChange({
      ...currentConfig,
      questions: currentConfig.questions.filter((_, i) => i !== index),
    });
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-4">
        <Input
          label="及格分数"
          type="number"
          min={0}
          max={100}
          value={currentConfig.passingScore}
          onChange={(e) => onChange({ ...currentConfig, passingScore: parseInt(e.target.value) || 60 })}
          className="w-32"
        />
        <div className="flex items-center gap-2 mt-6">
          <input
            type="checkbox"
            id="showExplanation"
            checked={currentConfig.showExplanation || false}
            onChange={(e) => onChange({ ...currentConfig, showExplanation: e.target.checked })}
            className="rounded border-dark-300 text-primary-600 focus:ring-primary-500"
          />
          <label htmlFor="showExplanation" className="text-sm text-dark-700">
            显示解析
          </label>
        </div>
      </div>

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <label className="text-sm font-medium text-dark-700">
            题目列表 ({currentConfig.questions.length})
          </label>
          <button
            onClick={addQuestion}
            className="text-sm text-primary-600 hover:text-primary-700"
          >
            + 添加题目
          </button>
        </div>

        {currentConfig.questions.map((question, index) => (
          <div key={question.id} className="p-4 border border-dark-200 rounded-lg space-y-3">
            <div className="flex items-start justify-between">
              <span className="text-sm font-medium text-dark-500">题目 {index + 1}</span>
              <button
                onClick={() => deleteQuestion(index)}
                className="text-red-500 hover:text-red-600 text-sm"
              >
                删除
              </button>
            </div>
            <Input
              placeholder="输入题目..."
              value={question.question}
              onChange={(e) => updateQuestion(index, { question: e.target.value })}
            />
            <div className="space-y-2">
              {question.options.map((option, optIndex) => (
                <div key={optIndex} className="flex items-center gap-2">
                  <input
                    type="radio"
                    name={`correct-${question.id}`}
                    checked={question.correctIndex === optIndex}
                    onChange={() => updateQuestion(index, { correctIndex: optIndex })}
                    className="text-primary-600 focus:ring-primary-500"
                  />
                  <input
                    type="text"
                    placeholder={`选项 ${String.fromCharCode(65 + optIndex)}`}
                    value={option}
                    onChange={(e) => {
                      const newOptions = [...question.options];
                      newOptions[optIndex] = e.target.value;
                      updateQuestion(index, { options: newOptions });
                    }}
                    className="flex-1 rounded border border-dark-200 px-2 py-1 text-sm focus:outline-none focus:ring-1 focus:ring-primary-500"
                  />
                </div>
              ))}
            </div>
            <Input
              placeholder="解析（可选）"
              value={question.explanation || ''}
              onChange={(e) => updateQuestion(index, { explanation: e.target.value })}
            />
          </div>
        ))}

        {currentConfig.questions.length === 0 && (
          <div className="text-center py-8 text-dark-400 text-sm">
            暂无题目，点击上方按钮添加
          </div>
        )}
      </div>
    </div>
  );
}

// Illustrated Content Config Editor
interface IllustratedConfigEditorProps {
  textConfig?: TextConfig;
  illustratedConfig?: IllustratedConfig;
  onChange: (updates: Partial<NodeConfig>) => void;
}

function IllustratedConfigEditor({ textConfig, illustratedConfig, onChange }: IllustratedConfigEditorProps) {
  const currentTextConfig: TextConfig = textConfig || { content: '', format: 'markdown' };
  const currentIllustratedConfig: IllustratedConfig = illustratedConfig || {};
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showUrlInput, setShowUrlInput] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = useCallback(async (file: File) => {
    if (!file.type.startsWith('image/')) {
      setError('请选择图片文件');
      return;
    }
    setUploading(true);
    setError(null);
    try {
      const result = await uploadFile('/upload/image', file, { category: 'images' });
      onChange({
        illustratedConfig: { ...currentIllustratedConfig, imageUrl: result.file_url }
      });
    } catch (e: any) {
      setError(e.message || '上传失败');
    } finally {
      setUploading(false);
    }
  }, [currentIllustratedConfig, onChange]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) handleUpload(file);
  }, [handleUpload]);

  const handleDeleteImage = () => {
    onChange({
      illustratedConfig: { ...currentIllustratedConfig, imageUrl: '' }
    });
  };

  return (
    <div className="space-y-6">
      {/* 图片配置 */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium text-dark-700 border-b border-dark-200 pb-2">图片配置</h4>

        {/* Upload area or image preview */}
        {currentIllustratedConfig.imageUrl ? (
          <div className="space-y-2">
            <img
              src={resolveMediaUrl(currentIllustratedConfig.imageUrl)}
              alt={currentIllustratedConfig.imageAlt || ''}
              className="max-w-full h-auto rounded-lg border border-dark-200 object-contain"
            />
            <div className="flex gap-2">
              <button
                onClick={() => fileInputRef.current?.click()}
                className="text-sm text-primary-600 hover:text-primary-700"
              >
                重新上传
              </button>
              <button onClick={handleDeleteImage} className="text-sm text-red-500 hover:text-red-600">
                删除图片
              </button>
            </div>
          </div>
        ) : (
          <div
            onDragOver={(e) => e.preventDefault()}
            onDrop={handleDrop}
            onClick={() => !uploading && fileInputRef.current?.click()}
            className="border-2 border-dashed border-dark-300 rounded-lg p-8 text-center cursor-pointer hover:border-primary-400 hover:bg-primary-50/30 transition-colors"
          >
            {uploading ? (
              <p className="text-sm text-dark-500">上传中...</p>
            ) : (
              <>
                <svg className="w-10 h-10 mx-auto text-dark-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <p className="text-sm text-dark-500">拖拽图片到此处，或点击选择文件</p>
                <p className="text-xs text-dark-400 mt-1">支持 jpg, png, gif, webp 格式</p>
              </>
            )}
          </div>
        )}

        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={(e) => { const f = e.target.files?.[0]; if (f) handleUpload(f); e.target.value = ''; }}
        />

        {error && <p className="text-sm text-red-500">{error}</p>}

        {/* Collapsible URL input */}
        <div>
          <button
            onClick={() => setShowUrlInput(!showUrlInput)}
            className="text-xs text-dark-400 hover:text-dark-600 flex items-center gap-1"
          >
            <svg className={`w-3 h-3 transition-transform ${showUrlInput ? 'rotate-90' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
            </svg>
            手动输入 URL
          </button>
          {showUrlInput && (
            <div className="mt-2">
              <Input
                label="图片 URL"
                placeholder="https://example.com/image.jpg"
                value={currentIllustratedConfig.imageUrl || ''}
                onChange={(e) => onChange({
                  illustratedConfig: { ...currentIllustratedConfig, imageUrl: e.target.value }
                })}
              />
            </div>
          )}
        </div>

        <Input
          label="图片描述（Alt）"
          placeholder="图片的描述文字"
          value={currentIllustratedConfig.imageAlt || ''}
          onChange={(e) => onChange({
            illustratedConfig: { ...currentIllustratedConfig, imageAlt: e.target.value }
          })}
        />
        <Input
          label="图片标题"
          placeholder="图片下方显示的标题"
          value={currentIllustratedConfig.imageCaption || ''}
          onChange={(e) => onChange({
            illustratedConfig: { ...currentIllustratedConfig, imageCaption: e.target.value }
          })}
        />
        <div>
          <label className="block text-sm font-medium text-dark-700 mb-1.5">
            布局方式
          </label>
          <select
            value={currentIllustratedConfig.layout || 'text_left_image_right'}
            onChange={(e) => onChange({
              illustratedConfig: { ...currentIllustratedConfig, layout: e.target.value as IllustratedConfig['layout'] }
            })}
            className="w-full rounded-lg border border-dark-200 px-3 py-2 text-dark-900 focus:outline-none focus:ring-2 focus:ring-primary-500"
          >
            <option value="text_left_image_right">文字左 图片右</option>
            <option value="image_left_text_right">图片左 文字右</option>
            <option value="text_top_image_bottom">文字上 图片下</option>
          </select>
        </div>
      </div>

      {/* 文本配置 */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium text-dark-700 border-b border-dark-200 pb-2">文本内容</h4>
        <div>
          <label className="block text-sm font-medium text-dark-700 mb-1.5">
            内容
          </label>
          <textarea
            value={currentTextConfig.content}
            onChange={(e) => onChange({
              textConfig: { ...currentTextConfig, content: e.target.value }
            })}
            placeholder="输入文本内容..."
            rows={8}
            className="w-full rounded-lg border border-dark-200 px-3 py-2 text-dark-900 focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-dark-700 mb-1.5">
            关键点（每行一个）
          </label>
          <textarea
            value={(currentTextConfig.keyPoints || []).join('\n')}
            onChange={(e) => onChange({
              textConfig: {
                ...currentTextConfig,
                keyPoints: e.target.value.split('\n').filter(Boolean),
              }
            })}
            placeholder="关键点1&#10;关键点2&#10;关键点3"
            rows={4}
            className="w-full rounded-lg border border-dark-200 px-3 py-2 text-dark-900 focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
          />
        </div>
      </div>
    </div>
  );
}

