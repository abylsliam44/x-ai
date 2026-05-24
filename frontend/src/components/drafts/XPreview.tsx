import { Icon } from '../common/Icon'
import type { DraftType } from '../../types/models'

interface XPreviewProps {
  posts: string[]
  draftType: DraftType
  username?: string
  displayName?: string
}

export function XPreview({
  posts,
  draftType,
  username = '@you',
  displayName = 'You',
}: XPreviewProps) {
  const isThread = draftType === 'thread'
  const visible = posts.slice(0, 3)
  const remaining = posts.length - visible.length

  if (posts.length === 0) {
    return (
      <div className="border border-border rounded-2xl p-6 text-center text-tx3 text-sm">
        Preview will appear as you generate content.
      </div>
    )
  }

  return (
    <div className="sticky top-[88px]">
      <h4 className="font-mono text-[11px] uppercase tracking-[0.18em] text-tx3 mb-3">
        Preview
      </h4>
      <div className="border border-border rounded-2xl overflow-hidden">
        {visible.map((text, i) => (
          <div
            key={i}
            className="p-[18px] border-b border-border last:border-b-0 grid gap-3"
            style={{ gridTemplateColumns: '44px 1fr' }}
          >
            {/* Avatar */}
            <div className="relative">
              <div
                className="w-11 h-11 rounded-full flex items-center justify-center font-bold text-base text-bg shrink-0"
                style={{ background: 'linear-gradient(135deg, #fff, #888)' }}
              >
                {displayName[0]}
              </div>
              {isThread && i < visible.length - 1 && (
                <div className="thread-line" />
              )}
            </div>

            {/* Content */}
            <div>
              <div className="flex items-center gap-1.5 text-sm">
                <span className="font-bold">{displayName}</span>
                <span className="text-tx3">{username}</span>
                <span className="text-tx3">·</span>
                <span className="text-tx3">now</span>
              </div>
              <div className="text-[15px] leading-[1.5] mt-0.5 whitespace-pre-wrap">
                {text}
              </div>
              <div className="flex gap-10 mt-3 text-tx3">
                <span className="flex items-center gap-1.5 text-[13px] hover:text-tx cursor-pointer">
                  <Icon name="reply" size={15} /> 0
                </span>
                <span className="flex items-center gap-1.5 text-[13px] hover:text-tx cursor-pointer">
                  <Icon name="rt" size={15} /> 0
                </span>
                <span className="flex items-center gap-1.5 text-[13px] hover:text-tx cursor-pointer">
                  <Icon name="heart" size={15} /> 0
                </span>
                <span className="flex items-center gap-1.5 text-[13px] hover:text-tx cursor-pointer">
                  <Icon name="share" size={15} />
                </span>
              </div>
            </div>
          </div>
        ))}

        {remaining > 0 && (
          <div className="px-5 py-3.5 text-center text-tx3 text-sm border-t border-border">
            + {remaining} more {isThread ? 'posts' : 'items'} in this {draftType === 'thread' ? 'thread' : 'draft'}
          </div>
        )}
      </div>
    </div>
  )
}
