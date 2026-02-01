'use client';

/**
 * NodeConfigPanel - 中间面板容器
 * 节点配置编辑
 */

import React from 'react';
import { useEditorStore, getSelectedSection } from '@/stores/editor/useEditorStore';
import { ComponentTypeSelector } from './ComponentTypeSelector';
import { ConfigEditor } from './ConfigEditor';
import { PreviewPanel } from './PreviewPanel';
import { Input } from '@/components/ui/Input';
import type { ComponentType } from '@/types/editor';

export function NodeConfigPanel() {
  const store = useEditorStore();
  const selectedSection = getSelectedSection(store);

  if (!selectedSection) {
    return (
      <div className="h-full flex items-center justify-center">
        <div className="text-center text-dark-400">
          <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p className="text-lg font-medium mb-1">选择一个小节</p>
          <p className="text-sm">在左侧选择小节以编辑其配置</p>
        </div>
      </div>
    );
  }

  const handleTypeChange = (type: ComponentType) => {
    store.updateSection(selectedSection.id, {
      componentType: type,
      config: { ...selectedSection.config, type },
    });
  };

  const handleTitleChange = (title: string) => {
    store.updateSection(selectedSection.id, { title });
  };

  const handleConfigChange = (configUpdates: Partial<typeof selectedSection.config>) => {
    store.updateSectionConfig(selectedSection.id, configUpdates);
  };

  return (
    <div className="space-y-6">
      {/* Section Title */}
      <div className="bg-white rounded-lg p-4 shadow-sm">
        <Input
          label="小节标题"
          value={selectedSection.title}
          onChange={(e) => handleTitleChange(e.target.value)}
          placeholder="输入小节标题..."
        />
      </div>

      {/* Component Type Selector */}
      <div className="bg-white rounded-lg p-4 shadow-sm">
        <ComponentTypeSelector
          value={selectedSection.componentType}
          onChange={handleTypeChange}
        />
      </div>

      {/* Config Editor */}
      <div className="bg-white rounded-lg p-4 shadow-sm">
        <h3 className="text-sm font-medium text-dark-700 mb-4">配置</h3>
        <ConfigEditor
          type={selectedSection.componentType}
          config={selectedSection.config}
          onChange={handleConfigChange}
        />
      </div>

      {/* Preview */}
      <PreviewPanel
        type={selectedSection.componentType}
        config={selectedSection.config}
      />
    </div>
  );
}
