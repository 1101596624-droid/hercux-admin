/**
 * AiTutorStep - AI 导师步骤组件
 */

interface AiTutorStepProps {
  ai_spec: {
    opening_message: string;
    conversation_goals?: Array<{
      goal: string;
    }>;
  };
}

export function AiTutorStep({ ai_spec }: AiTutorStepProps) {
  return (
    <div className="space-y-3">
      <div className="bg-green-50 rounded-xl p-4">
        <p className="text-sm text-green-800 italic">
          "{ai_spec.opening_message}"
        </p>
      </div>
      {ai_spec.conversation_goals && (
        <div className="space-y-2">
          <p className="text-sm font-medium text-slate-600">对话目标:</p>
          {ai_spec.conversation_goals.map((goal, i) => (
            <div key={i} className="text-xs bg-slate-50 rounded p-2">
              <span className="text-green-600 font-medium">{goal.goal}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
