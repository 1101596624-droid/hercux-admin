/**
 * PracticeStep - 练习步骤组件
 */

interface PracticeStepProps {
  content: {
    instructions?: string;
    tasks?: string[];
    text?: string;
    markdown?: string;
    html?: string;
  };
}

export function PracticeStep({ content }: PracticeStepProps) {
  return (
    <div className="space-y-3">
      {typeof content === 'object' && 'instructions' in content && content.instructions && (
        <p className="text-slate-700">{content.instructions}</p>
      )}
      {typeof content === 'object' && 'text' in content && content.text && (
        <p className="text-slate-700">{content.text}</p>
      )}
      {typeof content === 'object' && 'markdown' in content && content.markdown && (
        <p className="text-slate-700">{content.markdown}</p>
      )}
      {typeof content === 'object' && 'tasks' in content && content.tasks && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-slate-600">练习任务:</p>
          <ul className="space-y-1">
            {content.tasks.map((task: string, i: number) => (
              <li key={i} className="flex items-start gap-2 text-sm text-slate-600">
                <svg className="w-3.5 h-3.5 text-rose-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
                <span>{task}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
