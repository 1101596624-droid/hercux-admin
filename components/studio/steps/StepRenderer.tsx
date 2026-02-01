/**
 * StepRenderer - 步骤渲染器
 * 基于 HERCU 课程包标准规范 v2.0
 * 支持重新生成和额外提示词
 */

'use client';

import { useState } from 'react';
import { FileText, Image, Video, MessageCircle, CheckCircle2, HelpCircle, Dumbbell, RefreshCw, Sparkles, ChevronDown, ChevronUp, Zap } from 'lucide-react';
import { cn } from '@/lib/utils';
import { TextContentStep } from './TextContentStep';
import { IllustratedContentStep } from './IllustratedContentStep';
import { VideoStep } from './VideoStep';
import { AiTutorStep } from './AiTutorStep';
import { AssessmentStep } from './AssessmentStep';
import { PracticeStep } from './PracticeStep';
import { SimulatorStep } from './SimulatorStep';
import type { LessonStep, StepType } from '@/types';

interface StepRendererProps {
  step: LessonStep;
  stepIndex: number;
  /** 是否显示重新生成按钮 */
  showRegenerate?: boolean;
  /** 重新生成回调 */
  onRegenerate?: (stepIndex: number, additionalPrompt?: string) => void;
  /** 是否正在重新生成 */
  isRegenerating?: boolean;
}

// Step 类型对应的样式配置
const STEP_TYPE_STYLES: Record<StepType, { bgColor: string; iconColor: string; Icon: typeof FileText }> = {
  text_content: { bgColor: 'bg-blue-100', iconColor: 'text-blue-600', Icon: FileText },
  illustrated_content: { bgColor: 'bg-indigo-100', iconColor: 'text-indigo-600', Icon: Image },
  video: { bgColor: 'bg-purple-100', iconColor: 'text-purple-600', Icon: Video },
  simulator: { bgColor: 'bg-cyan-100', iconColor: 'text-cyan-600', Icon: Zap },
  ai_tutor: { bgColor: 'bg-green-100', iconColor: 'text-green-600', Icon: MessageCircle },
  assessment: { bgColor: 'bg-amber-100', iconColor: 'text-amber-600', Icon: CheckCircle2 },
  quick_check: { bgColor: 'bg-orange-100', iconColor: 'text-orange-600', Icon: HelpCircle },
  practice: { bgColor: 'bg-rose-100', iconColor: 'text-rose-600', Icon: Dumbbell },
};

export function StepRenderer({ step, stepIndex, showRegenerate = false, onRegenerate, isRegenerating = false }: StepRendererProps) {
  const style = STEP_TYPE_STYLES[step.type];
  const IconComponent = style?.Icon || FileText;

  // 额外提示词输入状态
  const [showPromptInput, setShowPromptInput] = useState(false);
  const [additionalPrompt, setAdditionalPrompt] = useState('');

  const handleRegenerate = () => {
    if (onRegenerate) {
      onRegenerate(stepIndex, additionalPrompt || undefined);
      setAdditionalPrompt('');
      setShowPromptInput(false);
    }
  };

  return (
    <div key={step.step_id} className="bg-white rounded-2xl p-6 shadow-sm border border-slate-200">
      {/* Step Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <div className={cn(
            'w-8 h-8 rounded-lg flex items-center justify-center',
            style?.bgColor || 'bg-slate-100'
          )}>
            <IconComponent size={18} className={style?.iconColor || 'text-slate-600'} />
          </div>
          <div>
            <h4 className="font-bold text-slate-900">{step.title}</h4>
            <span className="text-xs text-slate-500">步骤 {stepIndex + 1}</span>
          </div>
        </div>

        {/* 重新生成按钮 */}
        {showRegenerate && onRegenerate && (
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowPromptInput(!showPromptInput)}
              className="flex items-center gap-1 px-2 py-1 text-xs text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded transition-colors"
            >
              <Sparkles size={14} />
              提示词
              {showPromptInput ? <ChevronUp size={12} /> : <ChevronDown size={12} />}
            </button>
            <button
              onClick={handleRegenerate}
              disabled={isRegenerating}
              className={cn(
                'flex items-center gap-1 px-3 py-1.5 text-xs font-medium rounded-lg transition-colors',
                isRegenerating
                  ? 'bg-slate-100 text-slate-400 cursor-not-allowed'
                  : 'bg-red-50 text-red-600 hover:bg-red-100'
              )}
            >
              <RefreshCw size={14} className={isRegenerating ? 'animate-spin' : ''} />
              {isRegenerating ? '生成中...' : '重新生成'}
            </button>
          </div>
        )}
      </div>

      {/* 额外提示词输入框 */}
      {showRegenerate && showPromptInput && (
        <div className="mb-4 p-3 bg-slate-50 rounded-lg border border-slate-200">
          <label className="block text-xs font-medium text-slate-600 mb-2">
            额外 AI 提示词（可选）
          </label>
          <textarea
            value={additionalPrompt}
            onChange={(e) => setAdditionalPrompt(e.target.value)}
            placeholder="输入额外的指导，例如：更详细地解释原理、增加实例、使用更简单的语言..."
            className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent resize-none"
            rows={2}
          />
        </div>
      )}

      {/* Step Content by Type */}
      {step.type === 'text_content' && 'content' in step && step.content && (
        <TextContentStep content={step.content} />
      )}

      {step.type === 'illustrated_content' && 'content' in step && (
        <IllustratedContentStep
          content={step.content || {}}
          diagram_spec={'diagram_spec' in step ? (step as any).diagram_spec : undefined}
        />
      )}

      {step.type === 'video' && 'video_spec' in step && step.video_spec && (
        <VideoStep video_spec={step.video_spec} />
      )}

      {step.type === 'ai_tutor' && 'ai_spec' in step && step.ai_spec && (
        <AiTutorStep ai_spec={step.ai_spec} />
      )}

      {(step.type === 'assessment' || step.type === 'quick_check') && 'assessment_spec' in step && step.assessment_spec && (
        <AssessmentStep assessment_spec={step.assessment_spec as any} />
      )}

      {step.type === 'practice' && 'content' in step && step.content && (
        <PracticeStep content={step.content as any} />
      )}

      {step.type === 'simulator' && 'simulator_spec' in step && step.simulator_spec && (
        <SimulatorStep simulator_spec={step.simulator_spec} />
      )}
    </div>
  );
}
