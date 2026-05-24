import { useNavigate } from 'react-router-dom'
import { AppShell } from '../components/layout/AppShell'
import { Topbar } from '../components/layout/Topbar'
import { Icon } from '../components/common/Icon'
import { EmptyState } from '../components/common/EmptyState'
import { Spinner } from '../components/common/Spinner'
import { useProjects } from '../hooks/useProjects'
import { useAuth } from '../hooks/useAuth'
import { relativeTime, statusLabel, draftTypeLabel } from '../lib/utils'
import type { ProjectRead } from '../types/models'

const GOAL_LABELS: Record<string, string> = {
  educate:         'Educate',
  provoke:         'Provoke',
  launch:          'Launch',
  summarize:       'Summarize',
  announce:        'Announce',
  build_authority: 'Build Authority',
}

const STATUS_CONFIG: Record<string, { dot: string; pill: string; label: string }> = {
  draft:       { dot: 'bg-tx4',                   pill: 'border-border text-tx4',  label: 'Draft' },
  researching: { dot: 'bg-tx3',                   pill: 'border-border text-tx3',  label: 'Researching' },
  generating:  { dot: 'bg-tx2 animate-pulse',     pill: 'border-border2 text-tx2', label: 'Generating' },
  ready:       { dot: 'bg-tx',                    pill: 'border-tx/30 text-tx',    label: 'Ready' },
  published:   { dot: 'bg-tx',                    pill: 'border-tx/30 text-tx',    label: 'Published' },
  failed:      { dot: 'bg-red-500',               pill: 'border-red-900/50 text-red-400', label: 'Failed' },
}

const QUICK_ACTIONS = [
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M3 21l4-1 12-12-3-3L4 17z"/>
      </svg>
    ),
    title: 'New Post',
    desc: 'Draft a sharp text post or thread',
    to: '/projects/new',
  },
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M9 21V9"/>
      </svg>
    ),
    title: 'Image Post',
    desc: 'Generate a visual with caption',
    to: '/projects/new',
  },
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M12 20h9M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z"/>
      </svg>
    ),
    title: 'Thread',
    desc: 'Turn a topic into a reply chain',
    to: '/projects/new',
  },
  {
    icon: (
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8">
        <path d="M12 1a3 3 0 00-3 3v8a3 3 0 006 0V4a3 3 0 00-3-3z"/>
        <path d="M19 10v2a7 7 0 01-14 0v-2M12 19v4M8 23h8"/>
      </svg>
    ),
    title: 'Voice Post',
    desc: 'Dictate an idea → draft',
    to: '/projects/new',
  },
]

function StatCard({
  label, value, sub, delay = 0,
}: {
  label: string
  value: string | number
  sub?: string
  delay?: number
}) {
  return (
    <div
      className="flex-1 px-5 py-4 rounded-2xl border border-border bg-surface hover:border-border2 transition-colors slide-up"
      style={{ animationDelay: `${delay}s` }}
    >
      <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-tx4 mb-2">{label}</div>
      <div className="font-semibold text-[28px] tracking-[-0.02em] leading-none stat-count" style={{ animationDelay: `${delay + 0.05}s` }}>
        {value}
      </div>
      {sub && <div className="font-mono text-[11px] text-tx4 mt-1.5">{sub}</div>}
    </div>
  )
}

function ProjectCard({ project }: { project: ProjectRead }) {
  const navigate = useNavigate()
  const cfg = STATUS_CONFIG[project.status] ?? STATUS_CONFIG.draft

  return (
    <div
      className="group flex items-start gap-4 py-5 border-b border-border cursor-pointer hover:bg-surface/50 transition-all duration-150 px-1 -mx-1 rounded-xl"
      onClick={() => navigate(`/projects/${project.id}`)}
    >
      {/* Status indicator */}
      <div className="flex items-center justify-center w-10 h-10 rounded-xl bg-surface2 border border-border shrink-0 mt-0.5 group-hover:border-border2 transition-colors">
        <div className={`w-2 h-2 rounded-full ${cfg.dot}`} />
      </div>

      {/* Main info */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start gap-2 mb-1">
          <span className="text-[15px] font-semibold text-tx tracking-[-0.005em] truncate leading-tight">
            {project.title}
          </span>
        </div>
        <p className="text-sm text-tx3 line-clamp-1 leading-relaxed mb-2">
          {project.topic}
        </p>
        <div className="flex items-center gap-3 flex-wrap">
          {project.goal && (
            <span className="inline-flex items-center h-5 px-2 rounded-full bg-surface2 border border-border font-mono text-[10px] text-tx3 uppercase tracking-[0.12em]">
              {GOAL_LABELS[project.goal] ?? project.goal}
            </span>
          )}
          {project.target_audience && (
            <span className="font-mono text-[11px] text-tx4">{project.target_audience}</span>
          )}
        </div>
      </div>

      {/* Right side */}
      <div className="text-right shrink-0 min-w-[110px]">
        <div className={`inline-flex items-center gap-1.5 h-6 px-3 rounded-full border font-mono text-[10px] uppercase tracking-[0.1em] mb-2 ${cfg.pill}`}>
          <div className={`w-1.5 h-1.5 rounded-full ${cfg.dot}`} />
          {cfg.label}
        </div>
        <div className="text-[11px] font-mono text-tx4">
          {relativeTime(project.created_at)}
        </div>
        {/* Hover arrow */}
        <div className="mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-tx3 ml-auto">
            <polyline points="9 18 15 12 9 6"/>
          </svg>
        </div>
      </div>
    </div>
  )
}

export function DashboardPage() {
  const { user } = useAuth()
  const { data, isLoading } = useProjects()
  const navigate = useNavigate()

  const firstName = user?.full_name?.split(' ')[0] ?? 'there'

  const projects = data?.items ?? []
  const total    = data?.total ?? 0
  const ready    = projects.filter(p => p.status === 'ready' || p.status === 'published').length
  const active   = projects.filter(p => p.status === 'generating' || p.status === 'researching').length
  const published = projects.filter(p => p.status === 'published').length

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
        <div className="mb-8 slide-up">
          <h1 className="text-[36px] font-semibold tracking-[-0.025em] leading-tight">
            Good to see you, {firstName}.
          </h1>
          <p className="text-tx3 text-sm mt-2 font-mono">
            Research · draft · fact-check · publish — humans at every gate.
          </p>
        </div>

        {/* Stats row */}
        {!isLoading && total > 0 && (
          <div className="flex gap-3 mb-8">
            <StatCard label="Total projects" value={total} delay={0.05} />
            <StatCard label="Ready to publish" value={ready} delay={0.1} />
            <StatCard label="Published" value={published} delay={0.15} />
            <StatCard label="Active" value={active} sub={active > 0 ? 'generating now' : 'none running'} delay={0.2} />
          </div>
        )}

        {/* Quick actions */}
        <div className="mb-8 slide-up" style={{ animationDelay: '0.1s' }}>
          <div className="font-mono text-[10px] uppercase tracking-[0.2em] text-tx4 mb-3">Quick start</div>
          <div className="grid gap-2" style={{ gridTemplateColumns: 'repeat(4, 1fr)' }}>
            {QUICK_ACTIONS.map((a, i) => (
              <button
                key={a.title}
                className="flex flex-col gap-2 p-4 rounded-xl border border-border bg-surface hover:border-border2 hover:bg-surface2 transition-all text-left slide-up"
                style={{ animationDelay: `${0.1 + i * 0.05}s` }}
                onClick={() => navigate(a.to)}
              >
                <div className="text-tx2">{a.icon}</div>
                <div>
                  <div className="text-sm font-medium text-tx">{a.title}</div>
                  <div className="text-xs text-tx4 font-mono mt-0.5">{a.desc}</div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Projects list */}
        <div>
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-base font-semibold tracking-tight">
              Projects
              {total > 0 && (
                <span className="ml-2 font-mono text-[11px] text-tx4 font-normal">{total}</span>
              )}
            </h2>
          </div>

          {isLoading ? (
            <div className="flex justify-center py-20"><Spinner size={24} /></div>
          ) : !projects.length ? (
            <EmptyState
              title="No projects yet."
              description="Start with a topic, link, voice note, or uploaded document. The agents handle the research, drafting, and fact-checking."
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
            <div className="flex flex-col slide-up" style={{ animationDelay: '0.15s' }}>
              {projects.map(project => (
                <ProjectCard key={project.id} project={project} />
              ))}
            </div>
          )}
        </div>
      </div>
    </AppShell>
  )
}
