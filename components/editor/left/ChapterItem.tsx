'use client';

/**
 * ChapterItem - 章节项组件
 * 支持展开/折叠、选中、拖拽
 */

import React from 'react';
import { cn } from '@/lib/cn';
import type { EditorChapter, EditorSection } from '@/types/editor';
import { COMPONENT_TYPE_LABELS } from '@/types/editor';
import type { ComponentType } from '@/types/editor';

// 可用的小节类型（与 ComponentTypeSelector 保持一致，排除未实装类型）
const AVAILABLE_SECTION_TYPES: { type: ComponentType; label: string }[] = [
  { type: 'text_content', label: '文本内容' },
  { type: 'illustrated_content', label: '图文内容' },
  { type: 'video', label: '视频' },
  { type: 'simulator', label: '交互模拟器' },
  { type: 'ai_tutor', label: 'AI 导师' },
  { type: 'assessment', label: '测验' },
  { type: 'quick_check', label: '快速检测' },
];

interface ChapterItemProps {
  chapter: EditorChapter;
  index: number; // 章节序号 (0-indexed)
  isSelected: boolean;
  selectedSectionId: string | null;
  onSelect: () => void;
  onToggleExpand: () => void;
  onSelectSection: (sectionId: string) => void;
  onAddSection: (type?: ComponentType) => void;
  onDeleteChapter: () => void;
  onRenameChapter: (title: string) => void;
  onDeleteSection: (sectionId: string) => void;
}

const componentTypeIcons: Record<string, React.ReactNode> = {
  video: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  simulator: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  ),
  quiz: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
    </svg>
  ),
  diagram: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
    </svg>
  ),
  text_content: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
    </svg>
  ),
  ai_tutor: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
    </svg>
  ),
  exam: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  model_3d: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5" />
    </svg>
  ),
  reading: (
    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
    </svg>
  ),
};

export function ChapterItem({
  chapter,
  index,
  isSelected,
  selectedSectionId,
  onSelect,
  onToggleExpand,
  onSelectSection,
  onAddSection,
  onDeleteChapter,
  onRenameChapter,
  onDeleteSection,
}: ChapterItemProps) {
  const [isEditing, setIsEditing] = React.useState(false);
  const [editTitle, setEditTitle] = React.useState(chapter.title);
  const [showMenu, setShowMenu] = React.useState(false);
  const [showTypeSelector, setShowTypeSelector] = React.useState(false);
  const displayIndex = index + 1; // 显示序号从1开始

  const handleRename = () => {
    if (editTitle.trim() && editTitle !== chapter.title) {
      onRenameChapter(editTitle.trim());
    }
    setIsEditing(false);
  };

  const handleAddSectionWithType = (type: ComponentType) => {
    onAddSection(type);
    setShowTypeSelector(false);
  };

  return (
    <div className="select-none">
      {/* Chapter Header */}
      <div
        className={cn(
          'flex items-center gap-2 px-3 py-2 cursor-pointer hover:bg-dark-50 group',
          isSelected && !selectedSectionId && 'bg-primary-50 hover:bg-primary-100'
        )}
        onClick={onSelect}
      >
        {/* Expand/Collapse Button */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggleExpand();
          }}
          className="p-0.5 rounded hover:bg-dark-200"
        >
          <svg
            className={cn(
              'w-4 h-4 text-dark-500 transition-transform',
              chapter.expanded && 'rotate-90'
            )}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
          </svg>
        </button>

        {/* 序号圆圈 */}
        <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-500 text-white flex items-center justify-center text-xs font-bold">
          {displayIndex}
        </div>

        {/* Title */}
        {isEditing ? (
          <input
            type="text"
            value={editTitle}
            onChange={(e) => setEditTitle(e.target.value)}
            onBlur={handleRename}
            onKeyDown={(e) => {
              if (e.key === 'Enter') handleRename();
              if (e.key === 'Escape') {
                setEditTitle(chapter.title);
                setIsEditing(false);
              }
            }}
            className="flex-1 px-1 py-0.5 text-sm border border-primary-300 rounded focus:outline-none focus:ring-1 focus:ring-primary-500"
            autoFocus
            onClick={(e) => e.stopPropagation()}
          />
        ) : (
          <span className="flex-1 text-sm font-medium text-dark-800 truncate">
            {chapter.title}
          </span>
        )}

        {/* Section Count */}
        <span className="text-xs text-dark-400">
          {chapter.sections.length}
        </span>

        {/* Menu Button */}
        <div className="relative">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setShowMenu(!showMenu);
            }}
            className="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-dark-200"
          >
            <svg className="w-4 h-4 text-dark-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
            </svg>
          </button>

          {/* Dropdown Menu */}
          {showMenu && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={() => { setShowMenu(false); setShowTypeSelector(false); }}
              />
              <div className="absolute right-0 top-full mt-1 w-36 bg-white rounded-lg shadow-lg border border-dark-200 py-1 z-20">
                <div className="relative">
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      setShowTypeSelector(!showTypeSelector);
                    }}
                    className="w-full px-3 py-1.5 text-left text-sm text-dark-700 hover:bg-dark-50 flex items-center justify-between"
                  >
                    添加小节
                    <svg className="w-3 h-3 text-dark-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </button>
                  {showTypeSelector && (
                    <div className="absolute left-full top-0 ml-1 w-40 bg-white rounded-lg shadow-lg border border-dark-200 py-1 z-30">
                      {AVAILABLE_SECTION_TYPES.map((item) => (
                        <button
                          key={item.type}
                          onClick={(e) => {
                            e.stopPropagation();
                            handleAddSectionWithType(item.type);
                            setShowMenu(false);
                          }}
                          className="w-full px-3 py-1.5 text-left text-sm text-dark-700 hover:bg-dark-50"
                        >
                          {item.label}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setIsEditing(true);
                    setShowMenu(false);
                  }}
                  className="w-full px-3 py-1.5 text-left text-sm text-dark-700 hover:bg-dark-50"
                >
                  重命名
                </button>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    onDeleteChapter();
                    setShowMenu(false);
                  }}
                  className="w-full px-3 py-1.5 text-left text-sm text-red-600 hover:bg-red-50"
                >
                  删除章节
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Sections */}
      {chapter.expanded && chapter.sections.length > 0 && (
        <div className="ml-6 border-l border-dark-100">
          {chapter.sections.map((section) => (
            <SectionItem
              key={section.id}
              section={section}
              isSelected={selectedSectionId === section.id}
              onSelect={() => onSelectSection(section.id)}
              onDelete={() => onDeleteSection(section.id)}
            />
          ))}
        </div>
      )}

      {/* Empty State */}
      {chapter.expanded && chapter.sections.length === 0 && (
        <div className="ml-6 pl-4 py-2 relative">
          <button
            onClick={() => setShowTypeSelector(!showTypeSelector)}
            className="text-sm text-dark-400 hover:text-primary-600"
          >
            + 添加小节
          </button>
          {showTypeSelector && !showMenu && (
            <>
              <div
                className="fixed inset-0 z-10"
                onClick={() => setShowTypeSelector(false)}
              />
              <div className="absolute left-4 top-full mt-1 w-40 bg-white rounded-lg shadow-lg border border-dark-200 py-1 z-20">
                {AVAILABLE_SECTION_TYPES.map((item) => (
                  <button
                    key={item.type}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleAddSectionWithType(item.type);
                    }}
                    className="w-full px-3 py-1.5 text-left text-sm text-dark-700 hover:bg-dark-50"
                  >
                    {item.label}
                  </button>
                ))}
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

interface SectionItemProps {
  section: EditorSection;
  isSelected: boolean;
  onSelect: () => void;
  onDelete: () => void;
}

function SectionItem({ section, isSelected, onSelect, onDelete }: SectionItemProps) {
  const [showMenu, setShowMenu] = React.useState(false);

  return (
    <div
      className={cn(
        'flex items-center gap-2 px-3 py-1.5 cursor-pointer hover:bg-dark-50 group',
        isSelected && 'bg-primary-50 hover:bg-primary-100'
      )}
      onClick={onSelect}
    >
      {/* Component Type Icon */}
      <span className="text-dark-400">
        {componentTypeIcons[section.componentType] || componentTypeIcons.text_content}
      </span>

      {/* Title */}
      <span className="flex-1 text-sm text-dark-700 truncate">
        {section.title}
      </span>

      {/* Type Badge */}
      <span className="text-xs text-dark-400 hidden group-hover:inline">
        {COMPONENT_TYPE_LABELS[section.componentType]}
      </span>

      {/* Menu Button */}
      <div className="relative">
        <button
          onClick={(e) => {
            e.stopPropagation();
            setShowMenu(!showMenu);
          }}
          className="p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-dark-200"
        >
          <svg className="w-3 h-3 text-dark-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
          </svg>
        </button>

        {showMenu && (
          <>
            <div
              className="fixed inset-0 z-10"
              onClick={() => setShowMenu(false)}
            />
            <div className="absolute right-0 top-full mt-1 w-28 bg-white rounded-lg shadow-lg border border-dark-200 py-1 z-20">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete();
                  setShowMenu(false);
                }}
                className="w-full px-3 py-1.5 text-left text-sm text-red-600 hover:bg-red-50"
              >
                删除
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
