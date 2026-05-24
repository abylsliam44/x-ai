import { useState } from 'react'
import { Icon } from '../common/Icon'
import { Spinner } from '../common/Spinner'
import { useFactCheck } from '../../hooks/useDrafts'
import type { FactCheckResponse } from '../../types/models'

const VERDICT_CONFIG = {
  supported:        { label: 'Supported',    className: 'bg-tx text-bg' },
  weakly_supported: { label: 'Weak',         className: 'bg-surface2 text-tx border border-border2' },
  contradicted:     { label: 'Contradicted', className: 'bg-red-900/30 text-red-400 border border-red-900/50' },
  unverifiable:     { label: 'Unverifiable', className: 'bg-transparent text-tx border border-border2' },
} as const

interface FactCheckPanelProps {
  draftId: string
}

export function FactCheckPanel({ draftId }: FactCheckPanelProps) {
  const [report, setReport] = useState<FactCheckResponse | null>(null)
  const { mutateAsync: runFactCheck, isPending } = useFactCheck(draftId)

  const handleRun = async () => {
    const result = await runFactCheck()
    setReport(result)
  }

  const circ = 2 * Math.PI * 64
  const score = report?.overall_score ?? 0
  const dash = circ * score

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-semibold">Fact Check</span>
        <button
          onClick={handleRun}
          disabled={isPending}
          className="flex items-center gap-1.5 h-8 px-3 rounded-pill border border-border2 text-xs text-tx2 hover:bg-surface2 transition-all disabled:opacity-50"
        >
          {isPending ? <Spinner size={12} /> : <Icon name="refresh" size={12} />}
          {report ? 'Re-check' : 'Run Fact Check'}
        </button>
      </div>

      {!report && !isPending && (
        <div className="py-10 text-center text-tx3 text-sm">
          Run fact check to verify claims in this draft.
        </div>
      )}

      {isPending && (
        <div className="py-8 flex flex-col items-center gap-3">
          <Spinner size={20} />
          <div className="font-mono text-xs text-tx3 tracking-wider">Checking claims…</div>
        </div>
      )}

      {report && (
        <div>
          {/* Score ring */}
          <div className="flex flex-col items-center mb-6 py-4 border border-border rounded-xl">
            <div className="font-mono text-[10px] text-tx3 uppercase tracking-[0.22em] mb-4">
              Overall Confidence
            </div>
            <svg width="120" height="120" viewBox="0 0 160 160">
              <circle cx="80" cy="80" r="64" fill="none" stroke="var(--border)" strokeWidth="6" />
              <circle
                cx="80" cy="80" r="64" fill="none" stroke="#fff" strokeWidth="6"
                strokeDasharray={`${dash} ${circ - dash}`}
                strokeLinecap="round"
                transform="rotate(-90 80 80)"
                style={{ transition: 'stroke-dasharray .6s ease' }}
              />
              <text x="80" y="84" textAnchor="middle" fill="currentColor"
                style={{ fontFamily: 'var(--mono)', fontSize: 30, fontWeight: 600 }}>
                {Math.round(score * 100)}
              </text>
              <text x="80" y="106" textAnchor="middle" fill="var(--text-3)"
                style={{ fontFamily: 'var(--mono)', fontSize: 10, letterSpacing: '0.18em' }}>
                %
              </text>
            </svg>

            <div className="flex gap-6 mt-4 pt-4 border-t border-border w-full px-4">
              {[
                { k: 'supported', label: 'Supported' },
                { k: 'weakly_supported', label: 'Weak' },
                { k: 'contradicted', label: 'Bad' },
              ].map(({ k, label }) => (
                <div key={k} className="text-center flex-1">
                  <div className="font-mono text-lg font-semibold">
                    {report.items.filter((i) => i.verdict === k).length}
                  </div>
                  <div className="font-mono text-[9px] uppercase tracking-[0.18em] text-tx3 mt-1">
                    {label}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Claims */}
          <div className="flex flex-col">
            {report.items.map((item, i) => {
              const cfg = VERDICT_CONFIG[item.verdict as keyof typeof VERDICT_CONFIG] ?? VERDICT_CONFIG.unverifiable
              return (
                <div key={i} className="py-4 border-b border-border last:border-0 grid gap-4"
                  style={{ gridTemplateColumns: '1fr auto' }}>
                  <div>
                    <div className="text-sm font-medium leading-snug">{item.claim}</div>
                    {item.suggested_fix && (
                      <div className="text-xs text-tx3 mt-1.5 font-mono">
                        → {item.suggested_fix}
                      </div>
                    )}
                    <div className="text-xs font-mono text-tx4 mt-1">
                      confidence: {(item.confidence * 100).toFixed(0)}%
                    </div>
                  </div>
                  <div className={`inline-flex items-center font-mono text-[10.5px] font-semibold uppercase tracking-[0.12em] px-3 py-1.5 rounded-pill whitespace-nowrap h-fit ${cfg.className}`}>
                    {cfg.label}
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
