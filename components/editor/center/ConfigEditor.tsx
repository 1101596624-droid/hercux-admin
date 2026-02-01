'use client';

/**
 * ConfigEditor - 配置编辑器
 * 根据组件类型显示不同的配置表单
 */

import React from 'react';
import type { ComponentType, NodeConfig, VideoConfig, QuizConfig, TextConfig, QuizQuestion, IllustratedConfig } from '@/types/editor';
import { Input } from '@/components/ui/Input';
import { SimulatorConfigEditor } from './SimulatorConfigEditor';

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
    case 'ai_tutor':
      return <AITutorConfigEditor />;
    default:
      return (
        <div className="text-dark-500 text-sm">
          请选择组件类型
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

  return (
    <div className="space-y-4">
      <Input
        label="视频 URL"
        placeholder="https://example.com/video.mp4"
        value={currentConfig.videoUrl}
        onChange={(e) => onChange({ ...currentConfig, videoUrl: e.target.value })}
      />
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

  return (
    <div className="space-y-6">
      {/* 图片配置 */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium text-dark-700 border-b border-dark-200 pb-2">图片配置</h4>
        <Input
          label="图片 URL"
          placeholder="https://example.com/image.jpg"
          value={currentIllustratedConfig.imageUrl || ''}
          onChange={(e) => onChange({
            illustratedConfig: { ...currentIllustratedConfig, imageUrl: e.target.value }
          })}
        />
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

// Placeholder editors for other types
function DiagramConfigEditor() {
  return (
    <div className="p-4 bg-dark-50 rounded-lg text-center text-dark-500">
      <p className="mb-2">图表配置</p>
      <p className="text-sm">图表编辑器开发中...</p>
    </div>
  );
}

function AITutorConfigEditor() {
  return (
    <div className="p-4 bg-dark-50 rounded-lg text-center text-dark-500">
      <p className="mb-2">AI 导师配置</p>
      <p className="text-sm">请在右侧面板配置 AI 引导</p>
    </div>
  );
}
