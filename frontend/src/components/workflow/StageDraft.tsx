import { useState } from 'react'
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
