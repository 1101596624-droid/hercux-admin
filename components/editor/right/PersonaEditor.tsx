'use client';

/**
 * PersonaEditor - AI 人设编辑器
 * 编辑 AI 导师的人设和行为指南
 */

import React from 'react';
import { useEditorStore } from '@/stores/editor/useEditorStore';

const personaTemplates = [
  {
    name: '友好导师',
    persona: `你是一位友好、耐心的学习导师。你的目标是帮助学生理解复杂的概念，并鼓励他们提问。

特点：
- 使用简单易懂的语言解释概念
- 经常使用类比和实例
- 对学生的进步给予积极反馈
- 当学生遇到困难时提供提示而非直接答案`,
  },
  {
    name: '严谨教授',
    persona: `你是一位严谨、专业的教授。你注重知识的准确性和深度理解。

特点：
- 使用专业术语，但会解释其含义
- 强调概念之间的联系
- 鼓励批判性思维
- 提供深入的解释和背景知识`,
  },
  {
    name: '实践教练',
    persona: `你是一位注重实践的技术教练。你相信"做中学"的理念。

特点：
- 引导学生动手实践
- 提供具体的代码示例和练习
- 分析常见错误和最佳实践
- 鼓励学生尝试和实验`,
  },
];

export function PersonaEditor() {
  const { aiGuidance, updatePersona } = useEditorStore();

  const applyTemplate = (template: typeof personaTemplates[0]) => {
    updatePersona(template.persona);
  };

  return (
    <div className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-dark-700 mb-2">
          AI 人设模板
        </label>
        <div className="flex flex-wrap gap-2">
          {personaTemplates.map((template) => (
            <button
              key={template.name}
              onClick={() => applyTemplate(template)}
              className="px-3 py-1 text-xs rounded-full border border-dark-200 hover:border-primary-300 hover:bg-primary-50 transition-colors"
            >
              {template.name}
            </button>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-dark-700 mb-2">
          人设描述
        </label>
        <textarea
          value={aiGuidance.persona}
          onChange={(e) => updatePersona(e.target.value)}
          placeholder="描述 AI 导师的性格、教学风格和行为准则..."
          rows={12}
          className="w-full rounded-lg border border-dark-200 px-3 py-2 text-dark-900 focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm leading-relaxed"
        />
        <p className="mt-1.5 text-xs text-dark-500">
          {aiGuidance.persona.length} 字符
        </p>
      </div>

      <div className="p-3 rounded-lg bg-blue-50 border border-blue-100">
        <h4 className="text-xs font-medium text-blue-800 mb-1">提示</h4>
        <p className="text-xs text-blue-700">
          好的人设描述应包含：AI 的角色定位、教学风格、回答方式、以及与学生互动的准则。
          清晰的人设有助于 AI 提供一致且高质量的教学体验。
        </p>
      </div>
    </div>
  );
}
