/**
 * AssessmentStep - 测评步骤组件
 */

import { cn } from '@/lib/utils';

interface AssessmentStepProps {
  assessment_spec: {
    type: string;
    pass_required?: boolean;
    questions?: Array<{
      question: string;
      options?: string[];
      correct?: string | number;
      explanation?: string;
    }>;
  };
}

export function AssessmentStep({ assessment_spec }: AssessmentStepProps) {
  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 text-xs text-slate-500">
        <span className="px-2 py-0.5 bg-amber-100 text-amber-700 rounded">
          {assessment_spec.type}
        </span>
        {assessment_spec.pass_required && (
          <span className="px-2 py-0.5 bg-red-100 text-red-700 rounded">
            必须通过
          </span>
        )}
      </div>
      {assessment_spec.questions?.map((q, i) => (
        <div key={i} className="p-4 bg-slate-50 rounded-xl">
          <p className="text-sm font-medium text-slate-700">
            {i + 1}. {q.question}
          </p>
          {q.options && (
            <div className="mt-2 space-y-1">
              {q.options.map((opt, j) => (
                <p
                  key={j}
                  className={cn(
                    'text-xs px-2 py-1 rounded',
                    opt === q.correct || (typeof q.correct === 'number' && j === q.correct)
                      ? 'bg-green-100 text-green-700'
                      : 'text-slate-500'
                  )}
                >
                  {opt}
                </p>
              ))}
            </div>
          )}
          {q.explanation && (
            <p className="text-xs text-slate-500 mt-2 italic">
              解释: {q.explanation}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}
