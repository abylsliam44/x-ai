import { Icon } from '../common/Icon'
import { Spinner } from '../common/Spinner'
import { useFactCheck } from '../../hooks/useDrafts'
import type { DraftRead } from '../../types/models'

interface StageReviewProps {
  draft: DraftRead | null
  onApprove: () => Promise<void>
  isApproving: boolean
}

export function StageReview({ draft, onApprove, isApproving }: StageReviewProps) {
  const { mutateAsync: runFactCheck, isPending: isChecking, data: factCheckData } = useFactCheck(draft?.id)

  if (!draft) {
    return (
      <div className="py-16 text-center text-tx3 text-sm">
        Generate a draft first before reviewing.
      </div>
    )
  }

  const checks = [
    { ok: draft.status !== 'draft', label: 'Draft status', val: draft.status },
    { ok: !!draft.text || (draft.thread_items?.length ?? 0) > 0, label: 'Content ready', val: draft.type },
    {
      ok: factCheckData ? factCheckData.overall_score >= 0.6 : true,
      label: 'Fact confidence',
      val: factCheckData ? `${Math.round(factCheckData.overall_score * 100)}%` : 'Not checked',
    },
    { ok: draft.style_score == null || draft.style_score >= 0.6, label: 'Style score', val: draft.style_score ? draft.style_score.toFixed(2) : 'N/A' },
    { ok: draft.status === 'approved', label: 'Approval status', val: draft.status === 'approved' ? 'Approved' : 'Pending' },
  ]

  return (
    <div>
      <div className="flex items-baseline justify-between mb-5">
        <div>
          <h2 className="text-[22px] font-semibold tracking-[-0.015em]">Review</h2>
          <div className="text-[13px] text-tx3 mt-1">
            Final review before approval and publish
          </div>
        </div>
        <div className="flex gap-2">
          <button
            className="flex items-center gap-2 h-9 px-4 rounded-pill border border-border2 text-sm text-tx2 hover:bg-surface2 transition-all disabled:opacity-50"
            onClick={() => runFactCheck()}
            disabled={isChecking}
          >
            {isChecking ? <Spinner size={14} /> : <Icon name="check" size={14} />}
            Run Fact Check
          </button>
          {draft.status !== 'approved' && (
            <button
              className="flex items-center gap-2 h-9 px-4 rounded-pill bg-tx text-bg font-semibold text-sm hover:bg-tx/90 transition-all disabled:opacity-50"
              onClick={onApprove}
              disabled={isApproving}
            >
              {isApproving ? <Spinner size={14} /> : <Icon name="check" size={14} />}
              Approve Draft
            </button>
          )}
          {draft.status === 'approved' && (
            <div className="flex items-center gap-2 h-9 px-4 rounded-pill bg-tx/10 border border-tx/20 text-sm text-tx font-semibold">
              <Icon name="check" size={14} /> Approved
            </div>
          )}
        </div>
      </div>

      <div className="grid gap-8" style={{ gridTemplateColumns: '1fr 300px' }}>
        {/* Draft content preview */}
        <div>
          <div className="font-mono text-[11px] uppercase tracking-[0.18em] text-tx3 mb-4">
            Draft Content
          </div>
          <div className="border border-border rounded-xl overflow-hidden">
            {draft.text && (
              <div className="p-5 text-sm leading-relaxed whitespace-pre-wrap">{draft.text}</div>
            )}
            {draft.thread_items && draft.thread_items.length > 0 && (
              <div className="flex flex-col">
                {draft.thread_items.map((item, i) => {
                  const ti = item as Record<string, unknown>
                  return (
                    <div key={i} className="px-5 py-4 border-b border-border last:border-0">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="font-mono text-[11px] text-tx4">{i + 1}</span>
                        {i > 0 && <span className="text-xs text-tx4">↳ reply</span>}
                      </div>
                      <div className="text-sm leading-relaxed whitespace-pre-wrap">
                        {String(ti.text ?? '')}
                      </div>
                    </div>
                  )
                })}
              </div>
            )}
          </div>

          {/* Fact check results */}
          {factCheckData && (
            <div className="mt-5">
              <div className="font-mono text-[11px] uppercase tracking-[0.18em] text-tx3 mb-3">
                Fact Check · {Math.round(factCheckData.overall_score * 100)}% confidence
              </div>
              <div className="flex flex-col">
                {factCheckData.items.map((item, i) => (
                  <div key={i} className="flex items-start gap-3 py-3 border-b border-border last:border-0">
                    <div className="flex-1 text-sm">{item.claim}</div>
                    <span className={`font-mono text-[10px] uppercase px-2 py-1 rounded-pill font-semibold shrink-0 ${
                      item.verdict === 'supported'
                        ? 'bg-tx text-bg'
                        : item.verdict === 'contradicted'
                        ? 'bg-red-900/30 text-red-400 border border-red-900/50'
                        : 'bg-surface2 text-tx2 border border-border2'
                    }`}>
                      {item.verdict.replace(/_/g, ' ')}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Checklist */}
        <div>
          <div className="border border-border rounded-xl p-5 sticky top-[88px]">
            <h3 className="font-semibold text-base mb-1">Ready to publish?</h3>
            <div className="text-[13px] text-tx3 mb-4">{draft.type.replace(/_/g, ' ')}</div>

            <div className="flex flex-col">
              {checks.map((c, i) => (
                <div
                  key={i}
                  className="grid items-center py-3 border-b border-border last:border-0 text-sm gap-3"
                  style={{ gridTemplateColumns: '20px 1fr auto' }}
                >
                  <span className={c.ok ? 'text-tx' : 'text-tx3 opacity-60'}>
                    {c.ok ? '✓' : '○'}
                  </span>
                  <span className={c.ok ? '' : 'text-tx2'}>{c.label}</span>
                  <span className="font-mono text-[11px] text-tx3 whitespace-nowrap">{c.val}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
