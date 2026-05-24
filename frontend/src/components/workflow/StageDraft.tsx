import { useState } from 'react'
import { Icon } from '../common/Icon'
import { Spinner } from '../common/Spinner'
import { FactCheckPanel } from '../drafts/FactCheckPanel'
import { StylePanel } from '../drafts/StylePanel'
import { AgentTracesPanel } from '../drafts/AgentTracesPanel'
import { XPreview } from '../drafts/XPreview'
import type { AngleOption, DraftRead, DraftType } from '../../types/models'
import { draftTypeLabel } from '../../lib/utils'

type RightTab = 'fact-check' | 'style' | 'traces' | 'preview'

const DRAFT_TYPES: DraftType[] = [
  'text_post', 'thread', 'quote_post', 'image_post',
  'carousel_post', 'voice_video_post', 'video_post', 'research_article',
]

interface StageDraftProps {
  projectId: string
  draft: DraftRead | null
  selectedAngle: AngleOption | null
  onGenerate: (type: DraftType, angle: AngleOption | null, instructions?: string) => Promise<void>
  onRevise: (instructions: string) => Promise<void>
  onApprove: () => Promise<void>
  isGenerating: boolean
  isRevising: boolean
  isApproving: boolean
}

export function StageDraft({
  projectId,
  draft,
  selectedAngle,
  onGenerate,
  onRevise,
  onApprove,
  isGenerating,
  isRevising,
  isApproving,
}: StageDraftProps) {
  const [draftType, setDraftType] = useState<DraftType>('thread')
  const [customInstructions, setCustomInstructions] = useState('')
  const [rightTab, setRightTab] = useState<RightTab>('preview')

  const posts: string[] = (() => {
    if (!draft) return []
    if (draft.thread_items && draft.thread_items.length > 0) {
      return draft.thread_items.map((item) => {
        const ti = item as Record<string, unknown>
        return (ti.text as string) || ''
      })
    }
    if (draft.text) return [draft.text]
    return []
  })()

  return (
    <div>
      <div className="flex items-baseline justify-between mb-5">
        <div>
          <h2 className="text-[22px] font-semibold tracking-[-0.015em]">Draft</h2>
          <div className="text-[13px] text-tx3 mt-1">
            {draft
              ? `${draftTypeLabel(draft.type)} · status: ${draft.status}`
              : 'Generate a draft from the selected angle'}
          </div>
        </div>
        <div className="flex gap-2">
          {draft && draft.status !== 'approved' && (
            <button
              className="flex items-center gap-2 h-9 px-4 rounded-pill border border-border2 text-sm text-tx hover:bg-surface2 transition-all disabled:opacity-50"
              onClick={onApprove}
              disabled={isApproving}
            >
              {isApproving ? <Spinner size={14} /> : <Icon name="check" size={14} />}
              Approve
            </button>
          )}
          {draft?.status === 'approved' && (
            <div className="flex items-center gap-2 h-9 px-4 rounded-pill bg-tx/10 border border-tx/20 text-sm text-tx font-semibold">
              <Icon name="check" size={14} /> Approved
            </div>
          )}
        </div>
      </div>

      {!draft && (
        <div className="mb-6 flex flex-col gap-4">
          {!selectedAngle && (
            <div className="px-4 py-3 border border-border rounded-xl text-tx3 text-sm">
              Select an angle first to generate a targeted draft.
            </div>
          )}
          <div className="flex flex-wrap gap-2">
            {DRAFT_TYPES.map((t) => (
              <button
                key={t}
                onClick={() => setDraftType(t)}
                className={`h-8 px-3 rounded-pill text-xs font-mono border transition-all ${
                  draftType === t
                    ? 'bg-tx text-bg border-tx'
                    : 'border-border2 text-tx2 hover:bg-surface2'
                }`}
              >
                {draftTypeLabel(t)}
              </button>
            ))}
          </div>
          <textarea
            value={customInstructions}
            onChange={(e) => setCustomInstructions(e.target.value)}
            placeholder="Optional additional instructions for the writer agent..."
            rows={2}
            className="w-full bg-surface border border-border rounded-xl px-4 py-3 text-sm text-tx placeholder:text-tx4 outline-none focus:border-border2 transition-colors resize-none"
          />
          <button
            className="flex items-center gap-2 h-10 px-5 rounded-pill bg-tx text-bg font-semibold text-sm hover:bg-tx/90 transition-all disabled:opacity-50 self-start"
            onClick={() => onGenerate(draftType, selectedAngle, customInstructions || undefined)}
            disabled={isGenerating}
          >
            {isGenerating ? <Spinner size={14} /> : <Icon name="edit" size={14} />}
            {isGenerating ? 'Generating Draft…' : 'Create First Draft'}
          </button>
        </div>
      )}

      {isGenerating && !draft && (
        <AgentProgressDisplay />
      )}

      {draft && (
        <div className="grid gap-10" style={{ gridTemplateColumns: '1fr 440px' }}>
          {/* Left: Draft composer */}
          <div>
            <div className="flex items-center gap-2 mb-4 font-mono text-[11px] uppercase tracking-[0.18em] text-tx3">
              <div className="pulse-dot" />
              Composer · {draftTypeLabel(draft.type)}
            </div>

            {posts.length > 0 ? (
              <div className="flex flex-col">
                {posts.map((text, i) => (
                  <PostItem
                    key={i}
                    index={i}
                    text={text}
                    total={posts.length}
                    isThread={draft.type === 'thread'}
                  />
                ))}
              </div>
            ) : (
              <div className="py-10 text-center text-tx3 text-sm">
                Draft content will appear here.
              </div>
            )}

            {/* Revise actions */}
            <div className="mt-6 flex flex-wrap gap-2">
              {[
                'Make sharper',
                'Make more concise',
                'Make more contrarian',
                'Make more analytical',
                'Remove AI phrasing',
                'Improve hook',
              ].map((action) => (
                <button
                  key={action}
                  className="h-8 px-3 rounded-pill text-xs border border-border2 text-tx2 hover:bg-surface2 hover:text-tx transition-all disabled:opacity-50"
                  onClick={() => onRevise(action)}
                  disabled={isRevising}
                >
                  {isRevising ? <Spinner size={12} /> : action}
                </button>
              ))}
            </div>
          </div>

          {/* Right: Panel tabs */}
          <div>
            <div className="flex border-b border-border mb-4">
              {(['preview', 'fact-check', 'style', 'traces'] as RightTab[]).map((tab) => (
                <button
                  key={tab}
                  onClick={() => setRightTab(tab)}
                  className={`relative py-3 mr-5 text-xs font-mono uppercase tracking-[0.12em] transition-colors ${
                    rightTab === tab ? 'text-tx' : 'text-tx3 hover:text-tx2'
                  }`}
                >
                  {tab === 'fact-check' ? 'Fact Check' :
                   tab.charAt(0).toUpperCase() + tab.slice(1)}
                  {rightTab === tab && (
                    <span className="absolute left-0 right-0 bottom-[-1px] h-[1px] bg-tx" />
                  )}
                </button>
              ))}
            </div>

            {rightTab === 'preview' && (
              <XPreview posts={posts} draftType={draft.type} />
            )}
            {rightTab === 'fact-check' && (
              <FactCheckPanel draftId={draft.id} />
            )}
            {rightTab === 'style' && (
              <StylePanel draftId={draft.id} onRevise={onRevise} isRevising={isRevising} />
            )}
            {rightTab === 'traces' && (
              <AgentTracesPanel projectId={projectId} draftId={draft.id} />
            )}
          </div>
        </div>
      )}
    </div>
  )
}

function PostItem({ index, text, total, isThread }: { index: number; text: string; total: number; isThread: boolean }) {
  const len = text.length
  return (
    <div className="relative pl-12 pb-5 pt-[18px] border-b border-border last:border-0">
      <div className="absolute left-0 top-[18px] w-8 h-8 flex items-center justify-center font-mono text-xs border border-border2 rounded-full text-tx2">
        {index + 1}
      </div>
      <div className="text-base leading-[1.55] whitespace-pre-wrap">{text}</div>
      <div className="flex items-center gap-4 mt-3 font-mono text-[11px] text-tx3 uppercase tracking-[0.08em]">
        <span className={len > 280 ? 'text-tx' : ''}>{len}/280</span>
        {isThread && index > 0 && <span>↳ replies to {index}</span>}
      </div>
    </div>
  )
}

function AgentProgressDisplay() {
  const AGENTS = [
    'Research Agent',
    'Retrieval Agent',
    'Insight Agent',
    'Angle Agent',
    'Outline Agent',
    'Draft Writer',
    'Fact Checker',
    'Style Reviewer',
    'Editor',
  ]
  return (
    <div className="py-8 flex flex-col items-center gap-6">
      <Spinner size={24} />
      <div className="flex flex-col gap-2 w-full max-w-xs">
        {AGENTS.map((agent, i) => (
          <div key={agent} className="flex items-center gap-3 text-sm">
            <div className={`w-2 h-2 rounded-full shrink-0 ${i === 0 ? 'bg-tx animate-pulse' : 'bg-border2'}`} />
            <span className={i === 0 ? 'text-tx' : 'text-tx4'}>{agent}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
