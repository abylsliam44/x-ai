export type StageId = 'sources' | 'insights' | 'angles' | 'draft' | 'review' | 'publish'

const STAGES: { id: StageId; num: string; label: string }[] = [
  { id: 'sources',  num: '01', label: 'Sources' },
  { id: 'insights', num: '02', label: 'Insights' },
  { id: 'angles',   num: '03', label: 'Angles' },
  { id: 'draft',    num: '04', label: 'Draft' },
  { id: 'review',   num: '05', label: 'Review' },
  { id: 'publish',  num: '06', label: 'Publish' },
]

interface StageNavProps {
  active: StageId
  onPick: (id: StageId) => void
  completed?: Set<StageId>
}

export function StageNav({ active, onPick, completed }: StageNavProps) {
  const activeIdx = STAGES.findIndex((s) => s.id === active)

  return (
    <nav className="flex border-b border-border mb-7">
      {STAGES.map((s, i) => {
        const isDone = completed?.has(s.id) || i < activeIdx
        const isActive = s.id === active

        return (
          <button
            key={s.id}
            className={`relative flex items-center gap-[10px] py-[14px] mr-8 text-sm font-medium transition-colors ${
              isActive ? 'text-tx stage-tab-active' : isDone ? 'text-tx2' : 'text-tx3 hover:text-tx2'
            }`}
            onClick={() => onPick(s.id)}
          >
            <span
              className={`font-mono text-[11px] ${
                isActive ? 'text-tx' : isDone ? 'text-tx2' : 'text-tx4'
              }`}
            >
              {isDone && !isActive ? '✓' : s.num}
            </span>
            <span>{s.label}</span>
            {isActive && (
              <span className="absolute left-0 right-0 bottom-[-1px] h-[1px] bg-tx" />
            )}
          </button>
        )
      })}
    </nav>
  )
}
