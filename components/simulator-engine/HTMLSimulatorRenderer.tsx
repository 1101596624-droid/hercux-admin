import React, { useEffect, useRef, useState } from 'react';

interface HTMLSimulatorRendererProps {
  htmlContent: string;
  width?: number;
  height?: number;
  onReady?: () => void;
  onError?: (error: Error) => void;
  className?: string;
  showBorder?: boolean;
}

const HTMLSimulatorRenderer: React.FC<HTMLSimulatorRendererProps> = ({
  htmlContent,
  width,
  height,
  onReady,
  onError,
  className = '',
  showBorder = false
}) => {
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    const iframe = iframeRef.current;
    if (!iframe) return;

    // 监听iframe加载完成
    const handleLoad = () => {
      setIsReady(true);
      onReady?.();
    };

    // 监听iframe错误
    const handleError = (event: ErrorEvent) => {
      console.error('HTMLSimulator Error:', event.error);
      onError?.(event.error);
    };

    iframe.addEventListener('load', handleLoad);
    window.addEventListener('error', handleError);

    return () => {
      iframe.removeEventListener('load', handleLoad);
      window.removeEventListener('error', handleError);
    };
  }, [onReady, onError]);

  // 安全策略配置
  const sandbox = [
    'allow-scripts',           // 允许JavaScript
    'allow-same-origin',       // 允许同源访问（用于postMessage）
    // 'allow-forms',          // 如果需要表单
    // 'allow-modals',         // 如果需要alert/confirm
  ].join(' ');

  return (
    <div
      className={`html-simulator-wrapper ${className}`}
      style={{
        width: width || '100%',
        height: height || '100%',
        border: showBorder ? '2px solid #334155' : 'none',
        borderRadius: '8px',
        overflow: 'hidden',
        position: 'relative'
      }}
    >
      <iframe
        ref={iframeRef}
        srcDoc={htmlContent}
        sandbox={sandbox}
        style={{
          width: '100%',
          height: '100%',
          border: 'none',
          display: 'block'
        }}
        title="HTML Simulator"
      />

      {!isReady && (
        <div
          style={{
            position: 'absolute',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            color: '#94A3B8',
            fontSize: '14px'
          }}
        >
          加载中...
        </div>
      )}
    </div>
  );
};

export default HTMLSimulatorRenderer;