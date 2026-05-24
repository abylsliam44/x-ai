import { useState } from 'react'
import { Icon } from '../common/Icon'
import { Spinner } from '../common/Spinner'
import type { AngleOption } from '../../types/models'

interface StageAnglesProps {
  projectId: string
  angles: AngleOption[]
  selectedAngle: AngleOption | null
  onSelect: (angle: AngleOption) => void
  onGenerate: (count?: number, context?: string) => Promise<void>
  isGenerating: boolean
}

export function StageAngles({
  angles,
  selectedAngle,
  onSelect,
  onGenerate,
  isGenerating,
}: StageAnglesProps) {
  const [context, setContext] = useState('')

  return (
    <div>
      <div className="flex items-baseline justify-between mb-5">
        <div>
          <h2 className="text-[22px] font-semibold tracking-[-0.015em]">Angles</h2>
          <div className="text-[13px] text-tx3 mt-1">
            {angles.length > 0
              ? `${angles.length} angles generated · select one to drive the draft`
              : 'Generate angles to see strategic framings of your topic'}
          </div>
        </div>
        <div className="flex gap-2">
          <button
            className="flex items-center gap-2 h-9 px-4 rounded-pill border border-border2 text-sm text-tx hover:bg-surface2 transition-all disabled:opacity-50"
            onClick={() => onGenerate(5, context)}
            disabled={isGenerating}
          >
            {isGenerating ? <Spinner size={14} /> : <Icon name="spark" size={14} />}
            {angles.length > 0 ? 'Regenerate' : 'Generate Angles'}
          </button>
        </div>
      </div>

      {/* Optional context input */}
      {angles.length === 0 && (
        <div className="mb-6">
          <input
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="Optional: additional context or constraints..."
            className="w-full bg-surface border border-border rounded-xl px-4 py-3 text-sm text-tx placeholder:text-tx4 outline-none focus:border-border2 transition-colors"
          />
        </div>
      )}

      {isGenerating && angles.length === 0 && (
        <div className="py-16 text-center">
          <div className="flex flex-col items-center gap-4">
            <Spinner size={24} />
            <div className="font-mono text-xs text-tx3 tracking-[0.15em] uppercase">
              Generating angles…
            </div>
          </div>
        </div>
      )}

      {angles.length > 0 && (
        <div
          className="grid border-t border-l border-border"
          style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}
        >
          {angles.map((a, idx) => {
            const isSel = selectedAngle?.title === a.title
            return (
              <div
                key={idx}
                className={`relative p-[26px] min-h-[200px] flex flex-col cursor-pointer border-b border-r border-border transition-all ${
                  isSel
                    ? 'bg-tx text-bg'
                    : 'hover:bg-surface2'
                }`}
                onClick={() => onSelect(a)}
              >
                <div className="flex items-start gap-4 mb-3">
                  <div className={`flex-1 text-[19px] font-semibold leading-[1.25] tracking-[-0.01em] ${isSel ? 'text-bg' : 'text-tx'}`}>
                    {a.title}
                  </div>
                </div>
                <div className={`text-sm leading-[1.55] flex-1 ${isSel ? 'text-bg/70' : 'text-tx2'}`}>
                  {a.thesis}
                </div>
                {a.hook && (
                  <div className={`text-xs mt-3 italic ${isSel ? 'text-bg/60' : 'text-tx3'}`}>
                    Hook: "{a.hook}"
                  </div>
                )}
                <div className={`flex items-center gap-4 mt-4 font-mono text-[11px] uppercase tracking-[0.12em] ${isSel ? 'text-bg/60' : 'text-tx3'}`}>
                  {isSel && (
                    <span className={`flex items-center gap-1.5 font-semibold ml-auto ${isSel ? 'text-bg' : 'text-tx'}`}>
                      <Icon name="check" size={13} stroke={isSel ? '#000' : 'currentColor'} />
                      Selected
                    </span>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
