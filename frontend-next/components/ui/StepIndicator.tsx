'use client';
interface StepIndicatorProps {
  steps: string[];
  current: number;
}
export default function StepIndicator({ steps, current }: StepIndicatorProps) {
  return (
    <div className="flex items-center gap-0 mb-6">
      {steps.map((s, i) => {
        const done = i + 1 < current;
        const active = i + 1 === current;
        return (
          <div key={s} className="flex items-center flex-1">
            <div className="flex items-center gap-2">
              <div
                className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0"
                style={{
                  background: active ? '#2563EB' : done ? '#059669' : '#E5E7EB',
                  color: active || done ? 'white' : '#9CA3AF',
                }}
              >
                {done ? '✓' : i + 1}
              </div>
              <span
                className="text-xs font-medium whitespace-nowrap"
                style={{ color: active ? '#2563EB' : done ? '#059669' : '#9CA3AF' }}
              >
                {s}
              </span>
            </div>
            {i < steps.length - 1 && (
              <div className="flex-1 h-px mx-2" style={{ background: done ? '#059669' : '#E5E7EB' }} />
            )}
          </div>
        );
      })}
    </div>
  );
}