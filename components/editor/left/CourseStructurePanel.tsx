'use client';

/**
 * CourseStructurePanel - 左侧面板容器
 * 包含章节树和操作按钮
 */

import React from 'react';
import { useEditorStore } from '@/stores/editor/useEditorStore';
import { ChapterTree } from './ChapterTree';
import { Button } from '@/components/ui/Button';

export function CourseStructurePanel() {
  const { addChapter, chapters } = useEditorStore();

  return (
    <div className="h-full flex flex-col">
      {/* Actions */}
      <div className="flex-shrink-0 p-3 border-b border-dark-100">
        <Button
          variant="outline"
          size="sm"
          fullWidth
          onClick={() => addChapter()}
          icon={
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
          }
        >
          添加章节
        </Button>
      </div>

      {/* Chapter Tree */}
      <div className="flex-1 overflow-auto">
        <ChapterTree />
      </div>

      {/* Stats */}
      <div className="flex-shrink-0 p-3 border-t border-dark-100 bg-dark-50">
        <div className="flex justify-between text-xs text-dark-500">
          <span>共 {chapters.length} 章</span>
          <span>
            {chapters.reduce((sum, ch) => sum + ch.sections.length, 0)} 小节
          </span>
        </div>
      </div>
    </div>
  );
}
