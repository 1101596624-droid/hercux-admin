/**
 * TextContentStep - 文本内容步骤组件
 */

import { CheckCircle2 } from 'lucide-react';

interface ContentObject {
  body?: string;
  text?: string;
  key_points?: string[];
}

interface TextContentStepProps {
  content: ContentObject | string;
}

export function TextContentStep({ content }: TextContentStepProps) {
  // 解析 content - 可能是字符串形式的对象
  let parsedContent: ContentObject;

  if (typeof content === 'string') {
    // 尝试解析字符串形式的对象
    try {
      // 处理 Python 风格的字符串（单引号）
      const jsonStr = content.replace(/'/g, '"');
      parsedContent = JSON.parse(jsonStr);
    } catch {
      // 如果解析失败，当作纯文本处理
      parsedContent = { body: content };
    }
  } else {
    parsedContent = content;
  }

  const bodyText = parsedContent.body || parsedContent.text || '';
  const keyPoints = parsedContent.key_points || [];

  if (!bodyText && keyPoints.length === 0) {
    return (
      <div className="text-slate-400 text-center py-4">
        内容加载中...
      </div>
    );
  }

  return (
    <div>
      {bodyText && (
        <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">
          {bodyText}
        </p>
      )}
      {keyPoints.length > 0 && (
        <div className="mt-4 space-y-2">
          <p className="text-sm font-medium text-slate-600">关键要点:</p>
          <ul className="space-y-1">
            {keyPoints.map((point: string, i: number) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-600">
                <CheckCircle2 size={14} className="text-green-500 mt-0.5 flex-shrink-0" />
                <span>{point}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
