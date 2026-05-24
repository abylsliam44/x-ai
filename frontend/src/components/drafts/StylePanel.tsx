import { Spinner } from '../common/Spinner'

const REVISE_ACTIONS = [
  { label: 'Make sharper',           instruction: 'Make this draft sharper and more opinionated' },
  { label: 'More concise',           instruction: 'Make this draft more concise, remove filler' },
  { label: 'More contrarian',        instruction: 'Make the angle more contrarian and provocative' },
  { label: 'More analytical',        instruction: 'Add more analytical depth and specificity' },
  { label: 'Remove AI phrasing',     instruction: 'Remove all generic AI clichés and filler phrases' },
  { label: 'Strengthen hook',        instruction: 'Rewrite the opening hook to be much stronger' },
  { label: 'Add concrete examples',  instruction: 'Add one or two concrete specific examples' },
  { label: 'Fix ending',             instruction: 'Rewrite the ending to be more memorable and actionable' },
]

interface StylePanelProps {
  draftId: string
  onRevise: (instructions: string) => Promise<void>
  isRevising: boolean
}

export function StylePanel({ onRevise, isRevising }: StylePanelProps) {
  return (
    <div>
      <div className="mb-4">
        <span className="text-sm font-semibold">Style & Quality</span>
        <p className="text-xs text-tx3 mt-1">
          One-click revisions using the Editor Agent.
        </p>
      </div>

      <div className="flex flex-col gap-2">
        {REVISE_ACTIONS.map((action) => (
          <button
            key={action.label}
            className="flex items-center justify-between h-10 px-4 rounded-xl border border-border text-sm text-tx2 hover:bg-surface2 hover:text-tx transition-all text-left disabled:opacity-40"
            onClick={() => onRevise(action.instruction)}
            disabled={isRevising}
          >
            <span>{action.label}</span>
            {isRevising && (
              <Spinner size={12} />
            )}
          </button>
        ))}
      </div>

      <div className="mt-5 px-4 py-3 border border-border rounded-xl bg-surface2">
        <div className="font-mono text-[10px] uppercase tracking-[0.18em] text-tx3 mb-2">
          AI Slop Detector
        </div>
        <div className="text-xs text-tx2">
          Phrases to avoid: game-changer, seamless, revolutionary, cutting-edge,
          in today's fast-paced world, unlock the power of, game-changing technology.
        </div>
      </div>
    </div>
  )
}
