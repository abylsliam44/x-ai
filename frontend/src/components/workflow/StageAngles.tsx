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

const SCORE_COLORS = [
  { min: 8, label: 'Strong',   cls: 'text-tx bg-tx/10 border-tx/30' },
  { min: 6, label: 'Good',     cls: 'text-tx2 bg-surface2 border-border2' },
  { min: 0, label: 'Moderate', cls: 'text-tx3 bg-surface border-border' },
]

function scoreConfig(score?: number | null) {
  if (score == null) return null
  return SCORE_COLORS.find(c => score >= c.min) ?? SCORE_COLORS[2]
}

const GENERATE_STEPS = [
  'Scanning sources…',
  'Extracting insights…',
  'Finding angles…',
  'Ranking by impact…',
]

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
              ? `${angles.length} strategic framings · select one to drive the draft`
              : 'Generate angles to see non-obvious takes on your topic'}
          </div>
        </div>
        <button
          className="flex items-center gap-2 h-9 px-4 rounded-pill border border-border2 text-sm text-tx hover:bg-surface2 transition-all disabled:opacity-50 shrink-0"
          onClick={() => onGenerate(5, context)}
          disabled={isGenerating}
        >
          {isGenerating ? <Spinner size={14} /> : <Icon name="spark" size={14} />}
          {angles.length > 0 ? 'Regenerate' : 'Generate Angles'}
        </button>
      </div>

      {/* Context input when empty */}
      {angles.length === 0 && !isGenerating && (
        <div className="mb-6 slide-up">
          <input
            value={context}
            onChange={(e) => setContext(e.target.value)}
            placeholder="Optional: additional context or constraints (e.g. 'focus on technical audience')"
            className="w-full bg-surface border border-border rounded-xl px-4 py-3 text-sm text-tx placeholder:text-tx4 outline-none focus:border-border2 transition-colors"
          />
          <p className="text-xs text-tx4 font-mono mt-2">
            The system will analyze your sources and generate 5 strategic framings with theses and evidence.
          </p>
        </div>
      )}

      {/* Generating state */}
      {isGenerating && angles.length === 0 && (
        <div className="py-12 slide-up">
          <div className="max-w-sm mx-auto">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-5 h-5 rounded-full border-2 border-border2 border-t-tx animate-spin shrink-0" />
              <span className="font-mono text-[11px] text-tx2 tracking-[0.15em] uppercase">
                Generating angles…
              </span>
            </div>
            <div className="flex flex-col gap-2">
              {GENERATE_STEPS.map((step, i) => (
                <div
                  key={step}
                  className="flex items-center gap-3"
                  style={{ animationDelay: `${i * 0.4}s`, animation: 'slideInLeft 0.4s cubic-bezier(.2,.9,.3,1) both' }}
                >
                  <div className="w-1.5 h-1.5 rounded-full bg-border2 shrink-0" />
                  <span className="text-sm text-tx4">{step}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Angle cards */}
      {angles.length > 0 && (
        <div className="grid gap-3" style={{ gridTemplateColumns: 'repeat(2, 1fr)' }}>
          {angles.map((a, idx) => {
            const isSel = selectedAngle?.title === a.title
            const sc    = scoreConfig(a.score)

            return (
              <div
                key={idx}
                className={`relative p-6 min-h-[200px] flex flex-col cursor-pointer rounded-2xl border transition-all duration-200 slide-up ${
                  isSel
                    ? 'bg-tx text-bg border-tx shadow-[0_0_0_1px_rgba(255,255,255,0.3)]'
                    : 'bg-surface border-border hover:border-border2 hover:bg-surface2'
                }`}
                style={{ animationDelay: `${idx * 0.06}s` }}
                onClick={() => onSelect(a)}
              >
                {/* Top row: score + index */}
                <div className="flex items-center justify-between mb-3">
                  <span className={`font-mono text-[10px] uppercase tracking-[0.2em] ${isSel ? 'text-bg/60' : 'text-tx4'}`}>
                    {String(idx + 1).padStart(2, '0')}
                  </span>
                  <div className="flex items-center gap-2">
                    {sc && a.score != null && (
                      <span className={`inline-flex items-center gap-1 h-5 px-2 rounded-full text-[10px] font-mono font-semibold border ${isSel ? 'bg-bg/20 text-bg border-bg/30' : sc.cls}`}>
                        {a.score.toFixed(1)} · {sc.label}
                      </span>
                    )}
                    {a.best_format && (
                      <span className={`inline-flex items-center h-5 px-2 rounded-full text-[10px] font-mono border ${isSel ? 'bg-bg/20 text-bg/70 border-bg/30' : 'text-tx3 border-border bg-surface2'}`}>
                        {a.best_format.replace(/_/g, ' ')}
                      </span>
                    )}
                  </div>
                </div>

                {/* Title */}
                <div className={`text-[18px] font-semibold leading-[1.25] tracking-[-0.01em] mb-2 ${isSel ? 'text-bg' : 'text-tx'}`}>
                  {a.title}
                </div>

                {/* Thesis */}
                <div className={`text-sm leading-[1.55] flex-1 ${isSel ? 'text-bg/70' : 'text-tx2'}`}>
                  {a.thesis}
                </div>

                {/* Hook */}
                {a.hook && (
                  <div className={`mt-3 text-xs italic leading-relaxed ${isSel ? 'text-bg/55' : 'text-tx3'}`}>
                    "{a.hook}"
                  </div>
                )}

                {/* Selected indicator */}
                {isSel && (
                  <div className="mt-4 flex items-center gap-2 font-mono text-[11px] font-semibold text-bg/80 agent-step-enter">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                      <polyline points="4 12 10 18 20 6"/>
                    </svg>
                    Selected — will drive the draft
                  </div>
                )}
              </div>
            )
          })}
        </div>
      )}

      {/* After selection CTA */}
      {selectedAngle && (
        <div className="mt-5 px-4 py-3 rounded-xl border border-border bg-surface flex items-center gap-3 slide-up">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-tx2 shrink-0">
            <polyline points="4 12 10 18 20 6"/>
          </svg>
          <div className="flex-1 min-w-0">
            <span className="text-sm text-tx2">Angle selected: </span>
            <span className="text-sm font-medium text-tx truncate">{selectedAngle.title}</span>
          </div>
          <span className="text-xs text-tx3 font-mono shrink-0">→ go to Draft tab</span>
        </div>
      )}
    </div>
  )
}
