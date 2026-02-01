/**
 * IllustratedContentStep - 图文内容步骤组件
 * 显示文本内容和图片/图表
 */

import { useState } from 'react';
import { CheckCircle2, ImageIcon, AlertCircle } from 'lucide-react';
import { getMediaUrl } from '@/lib/utils';

interface DiagramSpec {
  type?: string;
  description?: string;
  image_url?: string;
  image_generated?: boolean;
  annotations?: Array<{ position: string; text: string }>;
}

interface ContentObject {
  body?: string;
  text?: string;
  key_points?: string[];
}

interface IllustratedContentStepProps {
  content: ContentObject | string;
  diagram_spec?: DiagramSpec;
}

export function IllustratedContentStep({ content, diagram_spec }: IllustratedContentStepProps) {
  const [imageError, setImageError] = useState(false);
  const [imageLoading, setImageLoading] = useState(true);

  // 解析 content
  let parsedContent: ContentObject;
  if (typeof content === 'string') {
    try {
      const jsonStr = content.replace(/'/g, '"');
      parsedContent = JSON.parse(jsonStr);
    } catch {
      parsedContent = { body: content };
    }
  } else {
    parsedContent = content;
  }

  const bodyText = parsedContent.body || parsedContent.text || '';
  const keyPoints = parsedContent.key_points || [];
  const imageUrl = getMediaUrl(diagram_spec?.image_url);
  const hasImage = imageUrl && !imageError;

  return (
    <div className="space-y-4">
      {/* 图片区域 */}
      {diagram_spec && (
        <div className="relative">
          {imageUrl && !imageError ? (
            <div className="relative rounded-lg overflow-hidden bg-slate-100">
              {imageLoading && (
                <div className="absolute inset-0 flex items-center justify-center bg-slate-100">
                  <div className="animate-pulse flex flex-col items-center gap-2">
                    <ImageIcon size={32} className="text-slate-400" />
                    <span className="text-sm text-slate-500">加载图片中...</span>
                  </div>
                </div>
              )}
              <img
                src={imageUrl}
                alt={diagram_spec.description || '图表'}
                className={`w-full h-auto object-contain ${imageLoading ? 'opacity-0' : 'opacity-100'}`}
                style={{ minHeight: '300px', maxHeight: '600px' }}
                onLoad={() => setImageLoading(false)}
                onError={() => {
                  setImageError(true);
                  setImageLoading(false);
                }}
              />
            </div>
          ) : (
            <div className="flex flex-col items-center justify-center py-8 bg-slate-50 rounded-lg border-2 border-dashed border-slate-200">
              {imageError ? (
                <>
                  <AlertCircle size={32} className="text-amber-500 mb-2" />
                  <span className="text-sm text-slate-500">图片加载失败</span>
                </>
              ) : diagram_spec.image_generated === false ? (
                <>
                  <ImageIcon size={32} className="text-slate-400 mb-2" />
                  <span className="text-sm text-slate-500">图片生成中...</span>
                </>
              ) : (
                <>
                  <ImageIcon size={32} className="text-slate-400 mb-2" />
                  <span className="text-sm text-slate-500">
                    {diagram_spec.description || '待生成图表'}
                  </span>
                </>
              )}
            </div>
          )}

          {/* 图表描述 */}
          {diagram_spec.description && hasImage && (
            <p className="mt-2 text-xs text-slate-500 text-center italic">
              {diagram_spec.description}
            </p>
          )}
        </div>
      )}

      {/* 文本内容 */}
      {bodyText && (
        <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">
          {bodyText}
        </p>
      )}

      {/* 关键要点 */}
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
