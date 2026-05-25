import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'
import { MockBanner } from '../common/MockBanner'

interface TopbarProps {
  breadcrumbs?: { label: string; to?: string }[]
  chip?: string
  actions?: ReactNode
}

export function Topbar({ breadcrumbs, chip, actions }: TopbarProps) {
  return (
    <div className="sticky top-0 z-20 flex flex-col">
      <MockBanner />
      <div
        className="grid items-center h-14 border-b border-border"
        style={{
          gridTemplateColumns: '240px 1fr auto',
          background: 'rgba(0,0,0,0.88)',
          backdropFilter: 'blur(24px)',
          WebkitBackdropFilter: 'blur(24px)',
        }}
      >
        {/* Brand */}
        <Link
          to="/dashboard"
          className="flex items-center gap-[10px] px-5 h-full border-r border-border hover:bg-surface/40 transition-colors"
        >
          <div className="brand-glow w-[24px] h-[24px] bg-tx text-bg rounded-[6px] flex items-center justify-center font-bold text-[13px] shrink-0">
            n
          </div>
          <div className="flex flex-col leading-none">
            <span className="font-semibold text-[13px] tracking-[-0.02em] text-tx">nfactorial</span>
            <span className="font-mono text-[9px] text-tx4 tracking-[0.1em] uppercase mt-0.5">X Content</span>
          </div>
        </Link>

        {/* Breadcrumb */}
        <div className="flex items-center gap-2 px-5 text-tx3 text-[13px]">
          {breadcrumbs?.map((crumb, i) => (
            <span key={i} className="flex items-center gap-2">
              {i > 0 && <span className="text-tx4 text-[11px]">/</span>}
              {crumb.to ? (
                <Link to={crumb.to} className="hover:text-tx transition-colors">
                  {crumb.label}
                </Link>
              ) : (
                <span className="text-tx font-medium">{crumb.label}</span>
              )}
            </span>
          ))}
          {chip && (
            <span className="inline-flex items-center gap-1.5 h-[26px] px-3 border border-border rounded-pill text-[11px] font-mono text-tx3 ml-1">
              <span className="w-1.5 h-1.5 rounded-full bg-tx animate-pulse" />
              {chip}
            </span>
          )}
        </div>

        {/* Actions */}
        {actions && (
          <div className="flex items-center gap-2 pr-5">{actions}</div>
        )}
      </div>
    </div>
  )
}
