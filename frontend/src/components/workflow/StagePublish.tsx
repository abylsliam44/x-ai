import { useState } from 'react'
import { Icon } from '../common/Icon'
import { Spinner } from '../common/Spinner'
import { XPreview } from '../drafts/XPreview'
import { useXStatus, useXConnect } from '../../hooks/useXConnection'
import { usePublishDraft } from '../../hooks/useDrafts'
import { useMediaAssets } from '../../hooks/useMedia'
import type { DraftRead, PublishJobRead } from '../../types/models'
import { draftTypeLabel } from '../../lib/utils'

interface StagePublishProps {
  draft: DraftRead | null
}

export function StagePublish({ draft }: StagePublishProps) {
  const { data: xStatus } = useXStatus()
  const { mutateAsync: connect, isPending: isConnecting } = useXConnect()
  const { mutateAsync: publishDraft, isPending: isPublishing } = usePublishDraft(draft?.id)
  const { data: mediaAssets = [] } = useMediaAssets(draft?.id)
  const [publishResult, setPublishResult] = useState<PublishJobRead | null>(null)
  const [publishError, setPublishError] = useState('')
  const [showPublishModal, setShowPublishModal] = useState(false)

  if (!draft) {
    return (
      <div className="py-16 text-center text-tx3 text-sm">
        Generate and approve a draft before publishing.
      </div>
    )
  }

  const posts: string[] = (() => {
    if (draft.thread_items?.length) {
      return draft.thread_items.map((i) => String((i as Record<string, unknown>).text ?? ''))
    }
    return draft.text ? [draft.text] : []
  })()

  const imageAssets = mediaAssets.filter((asset) => asset.type === 'image' || asset.type === 'carousel_image')
  const requiresImage = draft.type === 'image_post' || draft.type === 'carousel_post'
  const canPublish = draft.status === 'approved' && xStatus?.connected && (!requiresImage || imageAssets.length > 0)

  const handlePublish = async () => {
    setPublishError('')
    try {
      const job = await publishDraft(undefined)
      setPublishResult(job)
      setShowPublishModal(false)
    } catch (err) {
      setPublishError(err instanceof Error ? err.message : 'Publish failed.')
    }
  }

  return (
    <div>
      <div className="flex items-baseline justify-between mb-5">
        <div>
          <h2 className="text-[22px] font-semibold tracking-[-0.015em]">Publish</h2>
          <div className="text-[13px] text-tx3 mt-1">
            Final preview · approve to push to X
          </div>
        </div>
      </div>

      {publishResult && (
        <div className="mb-6 px-4 py-4 border border-border2 rounded-xl bg-surface2">
          <div className="font-mono text-[10px] text-tx3 uppercase tracking-wider mb-1">
            {publishResult.status === 'published' || publishResult.status === 'succeeded' ? 'Published' : 'Job Queued'}
          </div>
          {!!publishResult.result?.tweet_url && (
            <a
              href={String(publishResult.result.tweet_url)}
              target="_blank"
              rel="noopener noreferrer"
              className="font-mono text-sm text-tx hover:underline"
            >
              {String(publishResult.result.tweet_url)}
            </a>
          )}
          <div className="text-xs text-tx3 mt-1">
            Status: {publishResult.status}
          </div>
        </div>
      )}

      <div className="grid gap-10" style={{ gridTemplateColumns: '1fr 340px' }}>
        <XPreview posts={posts} draftType={draft.type} />

        {/* Publish panel */}
        <div>
          <div className="border border-border rounded-xl p-5 sticky top-[88px]">
            <h3 className="font-semibold text-base mb-1">Ready to publish</h3>
            <div className="text-[13px] text-tx3 mb-5">
              {draftTypeLabel(draft.type)} · {posts.length} post{posts.length !== 1 ? 's' : ''}
            </div>

            {/* Pre-publish checks */}
            <div className="flex flex-col border-t border-border">
              {[
                {
                  ok: xStatus?.connected ?? false,
                  label: 'X account connected',
                  val: xStatus?.username ?? 'Not connected',
                },
                {
                  ok: draft.status === 'approved',
                  label: 'Draft approved',
                  val: draft.status,
                },
                {
                  ok: posts.length > 0,
                  label: 'Content ready',
                  val: `${posts.length} post${posts.length !== 1 ? 's' : ''}`,
                },
                ...(requiresImage ? [{
                  ok: imageAssets.length > 0,
                  label: 'Image ready',
                  val: `${imageAssets.length} image${imageAssets.length !== 1 ? 's' : ''}`,
                }] : []),
              ].map((c, i) => (
                <div
                  key={i}
                  className="grid items-center py-3 border-b border-border last:border-0 text-sm gap-3"
                  style={{ gridTemplateColumns: '20px 1fr auto' }}
                >
                  <span className={c.ok ? 'text-tx' : 'text-tx3 opacity-60'}>
                    {c.ok ? '✓' : '○'}
                  </span>
                  <span>{c.label}</span>
                  <span className="font-mono text-[11px] text-tx3 whitespace-nowrap">{c.val}</span>
                </div>
              ))}
            </div>

            {/* X connection */}
            {!xStatus?.connected && (
              <div className="mt-4 mb-2">
                <button
                  className="w-full flex items-center justify-center gap-2 h-10 rounded-pill border border-border2 text-sm text-tx2 hover:bg-surface2 transition-all disabled:opacity-50"
                  onClick={() => connect()}
                  disabled={isConnecting}
                >
                  {isConnecting ? <Spinner size={14} /> : <Icon name="twitter" size={14} />}
                  Connect X Account
                </button>
              </div>
            )}

            {publishError && (
              <div className="mt-3 px-3 py-2 border border-red-900/50 bg-red-900/10 rounded-lg text-red-400 text-xs">
                {publishError}
              </div>
            )}

            {draft.status !== 'approved' && (
              <div className="mt-4 px-3 py-2 border border-border rounded-lg text-tx3 text-xs">
                Draft must be approved before publishing. Go to the Draft or Review stage.
              </div>
            )}

            <button
              className="mt-4 w-full h-13 py-3.5 rounded-pill bg-tx text-bg font-semibold text-sm disabled:opacity-40 hover:bg-tx/90 transition-all flex items-center justify-center gap-2"
              disabled={!canPublish || isPublishing}
              onClick={() => setShowPublishModal(true)}
            >
              {isPublishing ? <Spinner size={16} /> : <Icon name="rocket" size={16} />}
              {isPublishing ? 'Publishing…' : 'Publish to X'}
            </button>
          </div>
        </div>
      </div>

      {/* Confirmation modal */}
      {showPublishModal && (
        <div className="modal-backdrop" onClick={() => setShowPublishModal(false)}>
          <div
            className="modal-panel w-[480px] max-w-[calc(100vw-40px)] bg-surface border border-border2 rounded-2xl p-7"
            onClick={(e) => e.stopPropagation()}
          >
            <h3 className="text-lg font-semibold mb-1">Publish to X</h3>
            <p className="text-sm text-tx2 mb-5">
              {posts.length} post{posts.length !== 1 ? 's' : ''} · {xStatus?.username}
            </p>
            <div className="px-4 py-3 border border-border2 rounded-xl text-sm text-tx2 mb-5">
              This will publish the approved draft to X. This action cannot be undone.
            </div>
            <div className="flex justify-end gap-3">
              <button
                className="h-9 px-5 rounded-pill border border-border2 text-sm text-tx2 hover:bg-surface2 transition-all"
                onClick={() => setShowPublishModal(false)}
              >
                Cancel
              </button>
              <button
                className="h-9 px-5 rounded-pill bg-tx text-bg font-semibold text-sm hover:bg-tx/90 transition-all flex items-center gap-2 disabled:opacity-50"
                onClick={handlePublish}
                disabled={isPublishing}
              >
                {isPublishing ? <Spinner size={14} /> : <Icon name="rocket" size={14} />}
                Publish now
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
