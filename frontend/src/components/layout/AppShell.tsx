import type { ReactNode } from 'react'
import { Sidebar } from './Sidebar'

interface AppShellProps {
  topbar?: ReactNode
  children: ReactNode
}

export function AppShell({ topbar, children }: AppShellProps) {
  return (
    <div className="min-h-screen flex flex-col">
      {topbar}
      <div
        className="flex flex-1"
        style={{ minHeight: topbar ? 'calc(100vh - 64px)' : '100vh' }}
      >
        <div className="w-[240px] shrink-0">
          <Sidebar />
        </div>
        <main className="flex-1 min-w-0">{children}</main>
      </div>
    </div>
  )
}
