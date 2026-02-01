'use client';

/**
 * ChapterTree - 章节树组件
 * 展示课程的章节和小节结构
 */

import React from 'react';
import { useEditorStore } from '@/stores/editor/useEditorStore';
import { ChapterItem } from './ChapterItem';

export function ChapterTree() {
  const {
    chapters,
    selectedChapterId,
    selectedSectionId,
    selectChapter,
    selectSection,
    toggleChapterExpanded,
    addSection,
    deleteChapter,
    updateChapter,
    deleteSection,
  } = useEditorStore();

  if (chapters.length === 0) {
    return (
      <div className="p-4 text-center text-dark-400 text-sm">
        暂无章节，点击上方按钮添加
      </div>
    );
  }

  return (
    <div className="py-2">
      {chapters.map((chapter, index) => (
        <ChapterItem
          key={chapter.id}
          chapter={chapter}
          index={index}
          isSelected={selectedChapterId === chapter.id}
          selectedSectionId={selectedSectionId}
          onSelect={() => selectChapter(chapter.id)}
          onToggleExpand={() => toggleChapterExpanded(chapter.id)}
          onSelectSection={(sectionId) => selectSection(sectionId)}
          onAddSection={() => addSection(chapter.id)}
          onDeleteChapter={() => deleteChapter(chapter.id)}
          onRenameChapter={(title) => updateChapter(chapter.id, { title })}
          onDeleteSection={(sectionId) => deleteSection(sectionId)}
        />
      ))}
    </div>
  );
}
