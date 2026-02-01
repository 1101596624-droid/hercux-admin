'use client';

/**
 * PreviewPanel - 预览面板
 * 实时展示当前配置的效果
 */

import React from 'react';
import type { ComponentType, NodeConfig } from '@/types/editor';
import { COMPONENT_TYPE_LABELS } from '@/types/editor';
import { SimulatorRenderer } from '@/components/simulators/SimulatorRenderer';
import { getMediaUrl } from '@/lib/utils';

interface PreviewPanelProps {
  type: ComponentType;
  config: NodeConfig;
}

export function PreviewPanel({ type, config }: PreviewPanelProps) {
  return (
    <div className="border border-dark-200 rounded-lg overflow-hidden">
      <div className="px-4 py-2 bg-dark-50 border-b border-dark-200">
        <span className="text-sm font-medium text-dark-700">预览</span>
      </div>
      <div className="p-4 min-h-[200px] bg-white">
        <PreviewContent type={type} config={config} />
      </div>
    </div>
  );
}

function PreviewContent({ type, config }: PreviewPanelProps) {
  switch (type) {
    case 'video':
      return <VideoPreview config={config} />;
    case 'text_content':
      return <TextPreview config={config} />;
    case 'illustrated_content':
      return <IllustratedPreview config={config} />;
    case 'assessment':
    case 'quick_check':
      return <QuizPreview config={config} />;
    case 'simulator':
      return <SimulatorPreview config={config} />;
    default:
      return (
        <div className="flex items-center justify-center h-full text-dark-400">
          <div className="text-center">
            <div className="text-4xl mb-2">
              {type === 'ai_tutor' && '🤖'}
            </div>
            <p>{COMPONENT_TYPE_LABELS[type]} 预览</p>
          </div>
        </div>
      );
  }
}

function VideoPreview({ config }: { config: NodeConfig }) {
  const videoConfig = config.videoConfig;

  if (!videoConfig?.videoUrl) {
    return (
      <div className="flex items-center justify-center h-48 bg-dark-100 rounded-lg">
        <span className="text-dark-400">请输入视频 URL</span>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <div className="aspect-video bg-dark-900 rounded-lg flex items-center justify-center">
        <svg className="w-16 h-16 text-white opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      </div>
      <p className="text-xs text-dark-500 truncate">{videoConfig.videoUrl}</p>
      {videoConfig.duration && (
        <p className="text-xs text-dark-400">
          时长: {Math.floor(videoConfig.duration / 60)}:{(videoConfig.duration % 60).toString().padStart(2, '0')}
        </p>
      )}
    </div>
  );
}

function TextPreview({ config }: { config: NodeConfig }) {
  const textConfig = config.textConfig;

  if (!textConfig?.content) {
    return (
      <div className="flex items-center justify-center h-32 text-dark-400">
        请输入内容
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="prose prose-sm max-w-none">
        {textConfig.format === 'markdown' ? (
          <pre className="whitespace-pre-wrap text-sm text-dark-700 font-sans">
            {textConfig.content}
          </pre>
        ) : textConfig.format === 'html' ? (
          <div dangerouslySetInnerHTML={{ __html: textConfig.content }} />
        ) : (
          <p className="text-dark-700">{textConfig.content}</p>
        )}
      </div>
      {textConfig.keyPoints && textConfig.keyPoints.length > 0 && (
        <div className="pt-4 border-t border-dark-100">
          <p className="text-xs font-medium text-dark-500 mb-2">关键点</p>
          <ul className="space-y-1">
            {textConfig.keyPoints.map((point, index) => (
              <li key={index} className="flex items-start gap-2 text-sm text-dark-600">
                <span className="text-primary-500">•</span>
                {point}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function QuizPreview({ config }: { config: NodeConfig }) {
  const quizConfig = config.quizConfig;

  if (!quizConfig?.questions.length) {
    return (
      <div className="flex items-center justify-center h-32 text-dark-400">
        请添加题目
      </div>
    );
  }

  const firstQuestion = quizConfig.questions[0];

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between text-sm">
        <span className="text-dark-500">共 {quizConfig.questions.length} 题</span>
        <span className="text-dark-500">及格分: {quizConfig.passingScore}%</span>
      </div>
      <div className="p-4 bg-dark-50 rounded-lg">
        <p className="font-medium text-dark-800 mb-3">
          1. {firstQuestion.question || '(未填写题目)'}
        </p>
        <div className="space-y-2">
          {firstQuestion.options.map((option, index) => (
            <div
              key={index}
              className={`flex items-center gap-2 p-2 rounded ${
                index === firstQuestion.correctIndex
                  ? 'bg-green-50 border border-green-200'
                  : 'bg-white border border-dark-200'
              }`}
            >
              <span className="w-6 h-6 flex items-center justify-center rounded-full bg-dark-100 text-xs font-medium">
                {String.fromCharCode(65 + index)}
              </span>
              <span className="text-sm text-dark-700">
                {option || '(未填写选项)'}
              </span>
              {index === firstQuestion.correctIndex && (
                <span className="ml-auto text-xs text-green-600">正确答案</span>
              )}
            </div>
          ))}
        </div>
      </div>
      {quizConfig.questions.length > 1 && (
        <p className="text-xs text-dark-400 text-center">
          还有 {quizConfig.questions.length - 1} 道题目...
        </p>
      )}
    </div>
  );
}

function SimulatorPreview({ config }: { config: NodeConfig }) {
  const simulatorConfig = config.simulatorConfig;

  // 检查是否有任何有效的模拟器配置
  // 放宽条件：只要有 simulatorConfig 对象就尝试渲染
  if (!simulatorConfig) {
    return (
      <div className="flex items-center justify-center h-32 text-dark-400">
        请配置模拟器
      </div>
    );
  }

  return (
    <SimulatorRenderer config={simulatorConfig} compact />
  );
}

function IllustratedPreview({ config }: { config: NodeConfig }) {
  const textConfig = config.textConfig;
  const imageUrl = getMediaUrl(config.illustratedConfig?.imageUrl);

  return (
    <div className="space-y-4">
      {/* 图片预览 */}
      <div className="relative">
        {imageUrl ? (
          <img
            src={imageUrl}
            alt="图文内容"
            className="w-full h-auto object-contain rounded-lg bg-dark-50"
            style={{ minHeight: '200px', maxHeight: '500px' }}
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = 'none';
            }}
          />
        ) : (
          <div className="flex flex-col items-center justify-center h-32 bg-dark-50 rounded-lg border-2 border-dashed border-dark-200">
            <svg className="w-8 h-8 text-dark-400 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <span className="text-sm text-dark-400">暂无图片</span>
          </div>
        )}
      </div>

      {/* 文本内容 */}
      {textConfig?.content ? (
        <div className="prose prose-sm max-w-none">
          <p className="text-dark-700 text-sm">{textConfig.content}</p>
        </div>
      ) : (
        <p className="text-dark-400 text-sm text-center">请输入文本内容</p>
      )}

      {/* 关键点 */}
      {textConfig?.keyPoints && textConfig.keyPoints.length > 0 && (
        <div className="pt-3 border-t border-dark-100">
          <p className="text-xs font-medium text-dark-500 mb-2">关键点</p>
          <ul className="space-y-1">
            {textConfig.keyPoints.map((point, index) => (
              <li key={index} className="flex items-start gap-2 text-sm text-dark-600">
                <span className="text-primary-500">•</span>
                {point}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
