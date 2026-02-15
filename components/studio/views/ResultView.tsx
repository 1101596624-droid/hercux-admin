/**
 * ResultView - 结果视图组件 (两栏布局)
 * 基于 HERCU 课程包标准规范 v2.0
 */

import { Layers, Clock, ChevronRight, Copy, Download, RotateCcw, Check, Edit3, Save, GraduationCap } from 'lucide-react';
import { cn } from '@/lib/utils';
import { StepRenderer } from '@/components/studio/steps/StepRenderer';
import type { CoursePackage, Lesson } from '@/types';
import { DIFFICULTY_LABELS, DIFFICULTY_COLORS, type CourseDifficulty } from '@/types/editor';

interface ResultViewProps {
  generatedPackage: CoursePackage;
  selectedLessonId: string | null;
  setSelectedLessonId: (id: string | null) => void;
  selectedLesson: Lesson | null;
  copiedJson: boolean;
  handleCopyJson: () => void;
  handleExportJson: () => void;
  handleReset: () => void;
  handleEnterEditor: () => void;
  handleSaveToDatabase?: () => void;
  isSaving?: boolean;
}

export function ResultView({
  generatedPackage,
  selectedLessonId,
  setSelectedLessonId,
  selectedLesson,
  copiedJson,
  handleCopyJson,
  handleExportJson,
  handleReset,
  handleEnterEditor,
  handleSaveToDatabase,
  isSaving,
}: ResultViewProps) {
  const itemCount = generatedPackage.lessons.length;

  return (
    <div className="flex-1 flex min-h-0">
      {/* Left: Lesson List */}
      <div className="w-80 bg-white border-r border-slate-200 flex flex-col">
        <div className="p-6 border-b border-slate-200">
          <h2 className="text-lg font-bold text-slate-900">{generatedPackage.meta.title}</h2>
          <p className="text-sm text-slate-500 mt-1">{generatedPackage.meta.description}</p>
          <div className="flex items-center gap-4 mt-3 text-xs text-slate-500">
            <span className="flex items-center gap-1">
              <Layers size={12} />
              {itemCount} 个课时
            </span>
            <span className="flex items-center gap-1">
              <Clock size={12} />
              约 {generatedPackage.meta.estimated_hours} 小时
            </span>
            {generatedPackage.meta.difficulty && (
              <span className={cn(
                'flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium',
                DIFFICULTY_COLORS[generatedPackage.meta.difficulty as CourseDifficulty] || 'bg-slate-100 text-slate-600'
              )}>
                <GraduationCap size={12} />
                {DIFFICULTY_LABELS[generatedPackage.meta.difficulty as CourseDifficulty] || generatedPackage.meta.difficulty}
              </span>
            )}
          </div>
        </div>
        <div className="flex-1 overflow-auto p-4 space-y-2">
          {generatedPackage.lessons.map((lesson, index) => (
            <button
              key={lesson.lesson_id}
              onClick={() => setSelectedLessonId(lesson.lesson_id)}
              className={cn(
                'w-full p-3 rounded-xl text-left transition-all',
                selectedLessonId === lesson.lesson_id
                  ? 'bg-red-50 border-2 border-red-500'
                  : 'bg-slate-50 border-2 border-transparent hover:bg-slate-100'
              )}
            >
              <div className="flex items-start gap-3">
                <div
                  className={cn(
                    'w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0',
                    selectedLessonId === lesson.lesson_id
                      ? 'bg-red-500 text-white'
                      : 'bg-slate-200 text-slate-600'
                  )}
                >
                  {index + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <p
                    className={cn(
                      'text-sm font-medium truncate',
                      selectedLessonId === lesson.lesson_id ? 'text-red-700' : 'text-slate-700'
                    )}
                  >
                    {lesson.title}
                  </p>
                  <p className="text-xs text-slate-500 mt-0.5">
                    {lesson.total_steps || lesson.steps.length} 步骤 · 约 {lesson.estimated_minutes} 分钟
                  </p>
                </div>
                <ChevronRight
                  size={16}
                  className={cn(
                    'flex-shrink-0',
                    selectedLessonId === lesson.lesson_id ? 'text-red-500' : 'text-slate-400'
                  )}
                />
              </div>
            </button>
          ))}
        </div>

        {/* Actions */}
        <div className="p-4 border-t border-slate-200 space-y-2">
          <button
            onClick={handleEnterEditor}
            className="w-full px-4 py-2.5 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center justify-center gap-2 font-medium"
          >
            <Edit3 size={16} />
            进入编辑器
          </button>
          {handleSaveToDatabase && (
            <button
              onClick={handleSaveToDatabase}
              disabled={isSaving}
              className="w-full px-4 py-2.5 text-sm bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors flex items-center justify-center gap-2 font-medium"
            >
              <Save size={16} />
              {isSaving ? '保存中...' : '保存到数据库'}
            </button>
          )}
          <div className="flex gap-2">
            <button
              onClick={handleCopyJson}
              className="flex-1 px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 border border-slate-200 rounded-lg transition-colors flex items-center justify-center gap-1.5"
            >
              {copiedJson ? <Check size={14} className="text-green-600" /> : <Copy size={14} />}
              {copiedJson ? '已复制' : '复制'}
            </button>
            <button
              onClick={handleExportJson}
              className="flex-1 px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 border border-slate-200 rounded-lg transition-colors flex items-center justify-center gap-1.5"
            >
              <Download size={14} />
              导出
            </button>
            <button
              onClick={handleReset}
              className="px-3 py-2 text-sm text-slate-600 hover:bg-slate-100 border border-slate-200 rounded-lg transition-colors flex items-center justify-center"
              title="新建课程"
            >
              <RotateCcw size={14} />
            </button>
          </div>
        </div>
      </div>

      {/* Center: Lesson Content */}
      <div className="flex-1 flex flex-col min-h-0">
        <div className="p-6 border-b border-slate-200 bg-white flex items-center justify-between flex-shrink-0">
          <div>
            <h3 className="text-lg font-bold text-slate-900">
              {selectedLesson?.title || '选择一个课时'}
            </h3>
            {selectedLesson && (
              <p className="text-sm text-slate-500 mt-1">
                学习目标: {selectedLesson.learning_objectives?.join('、') || '无'}
              </p>
            )}
          </div>
        </div>
        <div className="flex-1 overflow-auto p-6 bg-slate-50">
          {selectedLesson ? (
            <div className="space-y-6">
              {/* Lesson Rationale */}
              {selectedLesson.rationale && (
                <div className="bg-gradient-to-r from-red-50 to-orange-50 rounded-2xl p-4 border border-red-100">
                  <p className="text-sm text-red-700">
                    <span className="font-medium">设计理念：</span>{selectedLesson.rationale}
                  </p>
                </div>
              )}

              {/* Steps - Use StepRenderer */}
              {selectedLesson.steps.map((step, stepIndex) => (
                <StepRenderer key={step.step_id} step={step} stepIndex={stepIndex} />
              ))}
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-slate-500">
              请从左侧选择一个课时查看内容
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
