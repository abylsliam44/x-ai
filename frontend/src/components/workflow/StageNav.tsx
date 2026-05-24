export type StageId = 'sources' | 'insights' | 'angles' | 'draft' | 'review' | 'publish'

const STAGES: {
  id: StageId
  num: string
  label: string
  icon: React.ReactNode
  desc: string
}[] = [
  {
    id: 'sources', num: '01', label: 'Sources', desc: 'Add context',
    icon: (
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>
      </svg>
    ),
  },
  {
    id: 'insights', num: '02', label: 'Insights', desc: 'Key findings',
    icon: (
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5z"/>
      </svg>
    ),
  },
  {
    id: 'angles', num: '03', label: 'Angles', desc: 'Pick your thesis',
    icon: (
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <circle cx="6" cy="6" r="2"/><circle cx="18" cy="6" r="2"/><circle cx="12" cy="20" r="2"/>
        <path d="M6 8v3a2 2 0 002 2h8a2 2 0 002-2V8M12 13v5"/>
      </svg>
    ),
  },
  {
    id: 'draft', num: '04', label: 'Draft', desc: 'Write & revise',
    icon: (
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <path d="M3 21l4-1 12-12-3-3L4 17z"/>
      </svg>
    ),
  },
  {
    id: 'review', num: '05', label: 'Review', desc: 'Fact-check & approve',
    icon: (
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <polyline points="4 12 10 18 20 6"/>
      </svg>
    ),
  },
  {
    id: 'publish', num: '06', label: 'Publish', desc: 'Send to X',
    icon: (
      <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
        <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/>
      </svg>
    ),
  },
]

import type React from 'react'

interface StageNavProps {
  active: StageId
  onPick: (id: StageId) => void
  completed?: Set<StageId>
}

export function StageNav({ active, onPick, completed }: StageNavProps) {
  const activeIdx = STAGES.findIndex((s) => s.id === active)
  const progressPct = (activeIdx / (STAGES.length - 1)) * 100

  return (
    <div className="mb-8">
      {/* Progress bar */}
      <div className="h-px bg-border mb-1 relative overflow-hidden rounded-full">
        <div
          className="absolute left-0 top-0 h-full bg-tx transition-all duration-500"
          style={{ width: `${progressPct}%` }}
        />
      </div>

      <nav className="flex gap-1">
        {STAGES.map((s, i) => {
          const isDone   = (completed?.has(s.id) || i < activeIdx)
          const isActive = s.id === active

          return (
            <button
              key={s.id}
              className={`group relative flex items-center gap-2 px-3 py-2.5 rounded-xl text-xs font-medium transition-all duration-200 flex-1 justify-center ${
                isActive
                  ? 'bg-surface2 text-tx border border-border2'
                  : isDone
                  ? 'text-tx2 hover:bg-surface hover:text-tx'
                  : 'text-tx4 hover:bg-surface hover:text-tx3'
              }`}
              onClick={() => onPick(s.id)}
              title={s.desc}
            >
              <span className={`transition-colors ${
                isActive ? 'text-tx' : isDone ? 'text-tx2' : 'text-tx4'
              }`}>
                {isDone && !isActive ? (
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="3">
                    <polyline points="4 12 10 18 20 6"/>
                  </svg>
                ) : s.icon}
              </span>
              <span className="hidden sm:inline">{s.label}</span>
              <span className="sm:hidden font-mono text-[10px]">{s.num}</span>
            </button>
          )
        })}
      </nav>
    </div>
  )
}
