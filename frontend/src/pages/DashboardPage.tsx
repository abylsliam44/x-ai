import { useNavigate } from 'react-router-dom'
import { AppShell } from '../components/layout/AppShell'
import { Topbar } from '../components/layout/Topbar'
import { Icon } from '../components/common/Icon'
import { EmptyState } from '../components/common/EmptyState'
import { Spinner } from '../components/common/Spinner'
import { useProjects } from '../hooks/useProjects'
import { useAuth } from '../hooks/useAuth'
import { relativeTime, statusLabel, draftTypeLabel } from '../lib/utils'

const GOAL_LABELS: Record<string, string> = {
  educate: 'Educate',
  provoke: 'Provoke',
  launch: 'Launch',
  summarize: 'Summarize',
  announce: 'Announce',
  build_authority: 'Build Authority',
}

const STATUS_DOT: Record<string, string> = {
  draft:              'bg-tx4',
  researching:        'bg-tx3',
  generating:         'bg-tx2 animate-pulse',
  ready:              'bg-tx',
  published:          'bg-tx',
  failed:             'bg-red-500',
}

export function DashboardPage() {
  const { user } = useAuth()
  const { data, isLoading } = useProjects()
  const navigate = useNavigate()

  const firstName = user?.full_name?.split(' ')[0] ?? 'there'

  return (
    <AppShell
      topbar={
        <Topbar
          breadcrumbs={[{ label: 'Dashboard' }]}
          actions={
            <button
              className="flex items-center gap-2 h-9 px-4 rounded-pill bg-tx text-bg font-semibold text-sm hover:bg-tx/90 transition-all"
              onClick={() => navigate('/projects/new')}
            >
              <Icon name="plus" size={14} />
              New Project
            </button>
          }
        />
      }
    >
      <div className="max-w-[1100px] mx-auto px-9 py-9 pb-24">
        {/* Greeting */}
        <div className="mb-10">
          <h1 className="text-[40px] font-semibold tracking-[-0.025em] leading-tight">
            Good to see you, {firstName}.
          </h1>
          <p className="text-tx2 text-base mt-3">
            Research, draft, fact-check, and publish to X — with humans at every gate.
          </p>
        </div>

        {/* Projects */}
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-lg font-semibold tracking-tight">Projects</h2>
          {data && data.total > 0 && (
            <span className="font-mono text-[11px] text-tx4">{data.total} total</span>
          )}
        </div>

        {isLoading ? (
          <div className="flex justify-center py-20">
            <Spinner size={24} />
          </div>
        ) : !data?.items.length ? (
          <EmptyState
            title="No projects yet."
            description="Start with a topic, link, or voice note. The system handles the rest."
            action={
              <button
                className="flex items-center gap-2 h-9 px-4 rounded-pill bg-tx text-bg font-semibold text-sm hover:bg-tx/90 transition-all"
                onClick={() => navigate('/projects/new')}
              >
                <Icon name="plus" size={14} />
                New Project
              </button>
            }
          />
        ) : (
          <div className="flex flex-col">
            {data.items.map((project) => (
              <div
                key={project.id}
                className="flex items-start gap-5 py-5 border-b border-border cursor-pointer hover:opacity-70 transition-opacity"
                onClick={() => navigate(`/projects/${project.id}`)}
              >
                {/* Status dot */}
                <div className="flex items-center justify-center w-11 h-11 rounded-lg bg-surface2 border border-border shrink-0 mt-0.5">
                  <div
                    className={`w-2 h-2 rounded-full ${STATUS_DOT[project.status] ?? 'bg-tx4'}`}
                  />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="text-base font-semibold text-tx tracking-[-0.005em] truncate">
                    {project.title}
                  </div>
                  <div className="text-sm text-tx2 mt-1.5 line-clamp-2">
                    {project.topic}
                  </div>
                  <div className="flex items-center gap-4 mt-3 font-mono text-[12px] text-tx3">
                    {project.goal && (
                      <span>{GOAL_LABELS[project.goal] ?? project.goal}</span>
                    )}
                    {project.target_audience && (
                      <>
                        <span className="text-tx4">·</span>
                        <span>{project.target_audience}</span>
                      </>
                    )}
                  </div>
                </div>

                <div className="text-right shrink-0 min-w-[100px]">
                  <div className="inline-flex items-center gap-1.5 text-[11px] font-mono uppercase tracking-[0.12em] text-tx3 px-3 py-1 border border-border rounded-pill">
                    {statusLabel(project.status)}
                  </div>
                  <div className="text-[12px] font-mono text-tx4 mt-2">
                    {relativeTime(project.created_at)}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AppShell>
  )
}
