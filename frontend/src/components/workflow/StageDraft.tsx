import { useState, useEffect, useRef } from 'react'
import { Icon } from '../common/Icon'
import { Spinner } from '../common/Spinner'
import { FactCheckPanel } from '../drafts/FactCheckPanel'
import { StylePanel } from '../drafts/StylePanel'
import { AgentTracesPanel } from '../drafts/AgentTracesPanel'
import { XPreview } from '../drafts/XPreview'
import { assetUrl, ApiError } from '../../lib/api'
import { useGenerateImage, useMediaAssets } from '../../hooks/useMedia'
import type { AngleOption, DraftRead, DraftType, MediaRead } from '../../types/models'
import { draftTypeLabel } from '../../lib/utils'

type RightTab = 'fact-check' | 'style' | 'traces' | 'preview' | 'media'

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
              {(['preview', 'media', 'fact-check', 'style', 'traces'] as RightTab[]).map((tab) => (
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
            {rightTab === 'media' && (
              <MediaPanel draft={draft} selectedAngle={selectedAngle} />
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

function MediaPanel({
  draft,
  selectedAngle,
}: {
  draft: DraftRead
  selectedAngle: AngleOption | null
}) {
  const defaultPrompt = selectedAngle?.hook || draft.title || draft.text?.slice(0, 120) || 'Editorial concept image'
  const [prompt, setPrompt] = useState(defaultPrompt)
  const [style, setStyle] = useState('minimal editorial, premium SaaS visual, high contrast')
  const [aspectRatio, setAspectRatio] = useState('1:1')
  const [error, setError] = useState('')
  const { data: assets = [], isLoading } = useMediaAssets(draft.id)
  const { mutateAsync: generateImage, isPending } = useGenerateImage(draft.id)
  const imageAssets = assets.filter((asset) => asset.type === 'image' || asset.type === 'carousel_image')

  const handleGenerate = async () => {
    setError('')
    try {
      await generateImage({
        prompt,
        style: style || undefined,
        aspect_ratio: aspectRatio,
      })
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Image generation failed.')
    }
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="font-semibold text-base">Media</h3>
          <div className="text-[12px] text-tx3 mt-1">
            {imageAssets.length} asset{imageAssets.length !== 1 ? 's' : ''}
          </div>
        </div>
        {isLoading && <Spinner size={16} />}
      </div>

      <div className="flex flex-col gap-3 mb-5">
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={3}
          className="w-full bg-surface border border-border rounded-xl px-3 py-2 text-sm text-tx placeholder:text-tx4 outline-none focus:border-border2 transition-colors resize-none"
          placeholder="Image prompt"
        />
        <input
          value={style}
          onChange={(e) => setStyle(e.target.value)}
          className="w-full bg-surface border border-border rounded-xl px-3 py-2 text-sm text-tx placeholder:text-tx4 outline-none focus:border-border2 transition-colors"
          placeholder="Style"
        />
        <div className="flex gap-2">
          {['1:1', '4:5', '16:9', '9:16'].map((ratio) => (
            <button
              key={ratio}
              onClick={() => setAspectRatio(ratio)}
              className={`h-8 px-3 rounded-pill text-xs font-mono border transition-all ${
                aspectRatio === ratio
                  ? 'bg-tx text-bg border-tx'
                  : 'border-border2 text-tx2 hover:bg-surface2'
              }`}
            >
              {ratio}
            </button>
          ))}
        </div>
        <button
          className="flex items-center justify-center gap-2 h-10 rounded-pill bg-tx text-bg font-semibold text-sm hover:bg-tx/90 transition-all disabled:opacity-50"
          onClick={handleGenerate}
          disabled={isPending || !prompt.trim()}
        >
          {isPending ? <Spinner size={14} /> : <Icon name="image" size={14} />}
          {isPending ? 'Generating…' : 'Generate Image'}
        </button>
        {error && (
          <div className="px-3 py-2 border border-red-900/50 bg-red-900/10 rounded-lg text-red-400 text-xs">
            {error}
          </div>
        )}
      </div>

      {imageAssets.length > 0 ? (
        <div className="grid grid-cols-2 gap-3">
          {imageAssets.map((asset) => (
            <MediaThumb key={asset.id} asset={asset} />
          ))}
        </div>
      ) : (
        <div className="py-8 text-center border border-border rounded-xl text-tx3 text-sm">
          No media yet.
        </div>
      )}
    </div>
  )
}

function MediaThumb({ asset }: { asset: MediaRead }) {
  const src = assetUrl(asset.file_url)
  return (
    <a
      href={src || undefined}
      target="_blank"
      rel="noopener noreferrer"
      className="block border border-border rounded-xl overflow-hidden bg-surface2 hover:border-border2 transition-colors"
    >
      {src ? (
        <img src={src} alt="" className="w-full aspect-square object-cover bg-bg" />
      ) : (
        <div className="w-full aspect-square flex items-center justify-center text-tx3">
          <Icon name="image" size={22} />
        </div>
      )}
      <div className="px-3 py-2 text-[11px] font-mono text-tx3 truncate">
        {String(asset.meta?.aspect_ratio ?? asset.type)} · {asset.status}
      </div>
    </a>
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

const AGENT_PIPELINE = [
  {
    name: 'Research Agent',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>
      </svg>
    ),
    desc: 'Scanning web sources and uploaded documents…',
  },
  {
    name: 'Retrieval Agent',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
    ),
    desc: 'Ranking and filtering context by relevance…',
  },
  {
    name: 'Insight Agent',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5z"/>
      </svg>
    ),
    desc: 'Extracting non-obvious, evidence-backed claims…',
  },
  {
    name: 'Angle Agent',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="6" cy="6" r="2"/><circle cx="18" cy="6" r="2"/><circle cx="12" cy="20" r="2"/>
        <path d="M6 8v3a2 2 0 002 2h8a2 2 0 002-2V8M12 13v5"/>
      </svg>
    ),
    desc: 'Generating strategic framings of the topic…',
  },
  {
    name: 'Outline Agent',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>
      </svg>
    ),
    desc: 'Structuring the argument and post flow…',
  },
  {
    name: 'Draft Writer',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M3 21l4-1 12-12-3-3L4 17z"/>
      </svg>
    ),
    desc: 'Writing in your brand voice with citations…',
  },
  {
    name: 'Fact Checker',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <polyline points="4 12 10 18 20 6"/>
      </svg>
    ),
    desc: 'Verifying each claim against research sources…',
  },
  {
    name: 'Style Reviewer',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="12" cy="12" r="10"/><path d="M12 8v4l2 2"/>
      </svg>
    ),
    desc: 'Checking tone, cadence, and voice alignment…',
  },
  {
    name: 'Editor',
    icon: (
      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M17 3a2.83 2.83 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/>
      </svg>
    ),
    desc: 'Sharpening hook, rhythm, and removing AI phrasing…',
  },
]

// Approximate seconds each agent takes; used to pace the simulation
const AGENT_DURATIONS = [6, 3, 4, 4, 3, 8, 5, 4, 3]

function AgentProgressDisplay() {
  const [activeIdx, setActiveIdx] = useState(0)
  const [doneMask, setDoneMask] = useState<boolean[]>(Array(AGENT_PIPELINE.length).fill(false))
  const [elapsed, setElapsed] = useState<number[]>(Array(AGENT_PIPELINE.length).fill(0))
  const startRef  = useRef<number[]>(Array(AGENT_PIPELINE.length).fill(0))
  const timerIds  = useRef<ReturnType<typeof setTimeout>[]>([])

  useEffect(() => {
    let current = 0
    let isMounted = true

    function advance() {
      if (!isMounted || current >= AGENT_PIPELINE.length) return
      startRef.current[current] = Date.now()

      // Tick elapsed time every 200 ms
      const tickId = setInterval(() => {
        if (!isMounted) { clearInterval(tickId); return }
        const idx = current
        setElapsed(prev => {
          const next = [...prev]
          next[idx] = (Date.now() - startRef.current[idx]) / 1000
          return next
        })
      }, 200) as unknown as ReturnType<typeof setTimeout>
      timerIds.current.push(tickId)

      const stepMs = AGENT_DURATIONS[current] * 1000
      const doneId = setTimeout(() => {
        clearInterval(tickId as unknown as ReturnType<typeof setInterval>)
        if (!isMounted) return
        const finishedIdx = current
        setDoneMask(prev => { const n = [...prev]; n[finishedIdx] = true; return n })
        current += 1
        if (current < AGENT_PIPELINE.length) setActiveIdx(current)
        advance()
      }, stepMs)
      timerIds.current.push(doneId)
    }

    advance()

    return () => {
      isMounted = false
      timerIds.current.forEach(id => {
        clearTimeout(id)
        clearInterval(id as unknown as ReturnType<typeof setInterval>)
      })
      timerIds.current = []
    }
  }, [])

  return (
    <div className="my-6 rounded-2xl border border-border bg-surface overflow-hidden slide-up">
      {/* Header */}
      <div className="flex items-center justify-between px-5 py-4 border-b border-border bg-surface2">
        <div className="flex items-center gap-3">
          <div className="relative w-4 h-4">
            <div className="w-4 h-4 rounded-full border-2 border-border2 border-t-tx animate-spin" />
          </div>
          <span className="font-mono text-[11px] text-tx2 tracking-[0.18em] uppercase">
            Agent Pipeline · Running
          </span>
        </div>
        <span className="font-mono text-[11px] text-tx4">
          {activeIdx + 1} / {AGENT_PIPELINE.length}
        </span>
      </div>

      {/* Steps */}
      <div className="relative px-5 py-4">
        {/* Vertical connector */}
        <div
          className="absolute left-[31px] top-4 bottom-4 w-px bg-border"
          style={{ top: 28, bottom: 28 }}
        />
        {/* Progress fill */}
        <div
          className="absolute left-[31px] w-px bg-tx transition-all duration-700"
          style={{
            top: 28,
            height: `${(activeIdx / Math.max(1, AGENT_PIPELINE.length - 1)) * (100 - 6)}%`,
          }}
        />

        <div className="flex flex-col gap-0">
          {AGENT_PIPELINE.map((agent, i) => {
            const isDone   = doneMask[i]
            const isActive = i === activeIdx && !isDone
            const isPend   = i > activeIdx

            return (
              <div
                key={agent.name}
                className="relative flex items-start gap-4 py-[11px]"
                style={{
                  animationDelay: `${i * 0.05}s`,
                }}
              >
                {/* Icon circle */}
                <div
                  className={`relative z-10 w-7 h-7 rounded-full flex items-center justify-center shrink-0 border transition-all duration-300 ${
                    isDone
                      ? 'bg-tx border-tx text-bg'
                      : isActive
                      ? 'bg-surface2 border-tx text-tx agent-active-ring'
                      : 'bg-surface border-border text-tx4'
                  }`}
                >
                  {isDone ? (
                    <svg className="agent-check" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                      <polyline points="4 12 10 18 20 6"/>
                    </svg>
                  ) : (
                    <span className={isActive ? 'text-tx' : ''}>{agent.icon}</span>
                  )}
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0 pt-[3px]">
                  <div className={`text-sm font-medium leading-snug transition-colors ${
                    isDone ? 'text-tx2' : isActive ? 'text-tx' : 'text-tx4'
                  }`}>
                    {agent.name}
                  </div>
                  {isActive && (
                    <div className="text-xs text-tx3 font-mono mt-0.5 agent-step-enter">
                      {agent.desc}
                    </div>
                  )}
                </div>

                {/* Right: status / timing */}
                <div className="shrink-0 text-right pt-[3px]">
                  {isDone && (
                    <span className="font-mono text-[11px] text-tx3 agent-step-enter">
                      {elapsed[i] > 0 ? `${elapsed[i].toFixed(1)}s` : '—'}
                    </span>
                  )}
                  {isActive && (
                    <span className="inline-flex items-center gap-1.5 font-mono text-[10px] text-tx2 agent-step-enter">
                      <span className="pulse-dot w-[5px] h-[5px]" />
                      running
                    </span>
                  )}
                  {isPend && (
                    <span className="font-mono text-[10px] text-tx4">queued</span>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
