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
        className="grid items-center h-16 border-b border-border"
        style={{
          gridTemplateColumns: '240px 1fr auto',
          background: 'rgba(0,0,0,.85)',
          backdropFilter: 'blur(20px)',
        }}
      >
        {/* Brand */}
        <Link
          to="/dashboard"
          className="flex items-center gap-[10px] px-[22px] h-full border-r border-border hover:opacity-80 transition-opacity"
        >
          <div className="w-[26px] h-[26px] bg-tx text-bg rounded-md flex items-center justify-center font-bold text-sm">
            n
          </div>
          <span className="font-semibold text-[15px] tracking-[-0.01em]">nfactorial</span>
        </Link>

        {/* Breadcrumb */}
        <div className="flex items-center gap-[14px] px-[22px] text-tx2 text-[13px]">
          {breadcrumbs?.map((crumb, i) => (
            <span key={i} className="flex items-center gap-[14px]">
              {i > 0 && <span className="text-tx4">/</span>}
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
            <span className="inline-flex items-center gap-2 h-[30px] px-3 border border-border rounded-pill text-xs text-tx2">
              <span className="w-1.5 h-1.5 rounded-full bg-tx" />
              {chip}
            </span>
          )}
        </div>

        {/* Actions */}
        {actions && (
          <div className="flex items-center gap-2 pr-[22px]">{actions}</div>
        )}
      </div>
    </div>
  )
}
