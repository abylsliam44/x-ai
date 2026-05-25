import { useNavigate } from 'react-router-dom'
import { AppShell } from '../components/layout/AppShell'
import { Topbar } from '../components/layout/Topbar'
import { Icon } from '../components/common/Icon'
import { EmptyState } from '../components/common/EmptyState'
import { Spinner } from '../components/common/Spinner'
import { useProjects } from '../hooks/useProjects'
import { useAuth } from '../hooks/useAuth'
import { relativeTime } from '../lib/utils'
import type { ProjectRead } from '../types/models'

const GOAL_LABELS: Record<string, string> = {
  educate:         'Educate',
  provoke:         'Provoke',
  launch:          'Launch',
  summarize:       'Summarize',
  announce:        'Announce',
  build_authority: 'Authority',
}

const STATUS_CONFIG: Record<string, { dot: string; pill: string; label: string }> = {
  draft:       { dot: 'bg-tx4',               pill: 'border-border text-tx4',        label: 'Draft' },
  researching: { dot: 'bg-tx3',               pill: 'border-border text-tx3',        label: 'Researching' },
  generating:  { dot: 'bg-tx2 animate-pulse', pill: 'border-border2 text-tx2',       label: 'Generating' },
  ready:       { dot: 'bg-tx',                pill: 'border-tx/20 text-tx bg-tx/5',  label: 'Ready' },
  published:   { dot: 'bg-tx',                pill: 'border-tx/20 text-tx bg-tx/5',  label: 'Published' },
  failed:      { dot: 'bg-red-500',           pill: 'border-red-900/40 text-red-400 bg-red-900/10', label: 'Failed' },
}

const QUICK_ACTIONS = [
  {
    icon: 'edit',
    label: 'Text Post',
    desc: 'Sharp single post',
    gradient: 'from-white/5 to-transparent',
  },
  {
    icon: 'list',
    label: 'Thread',
    desc: 'Topic → reply chain',
    gradient: 'from-white/5 to-transparent',
  },
  {
    icon: 'image',
    label: 'Image Post',
    desc: 'Visual + caption',
    gradient: 'from-white/5 to-transparent',
  },
  {
    icon: 'mic',
    label: 'Voice Post',
    desc: 'Dictate → draft',
    gradient: 'from-white/5 to-transparent',
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
      className="relative flex-1 px-5 py-4 rounded-xl border border-border bg-surface card-glow slide-up overflow-hidden"
      style={{ animationDelay: `${delay}s` }}
    >
      {/* Top gradient accent */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
      <div className="font-mono text-[9px] uppercase tracking-[0.2em] text-tx4 mb-3">{label}</div>
      <div className="font-semibold text-[30px] tracking-[-0.03em] leading-none num-reveal gradient-text" style={{ animationDelay: `${delay + 0.05}s` }}>
        {value}
      </div>
      {sub && <div className="font-mono text-[11px] text-tx4 mt-2">{sub}</div>}
    </div>
  )
}

function QuickAction({ icon, label, desc, delay }: { icon: string; label: string; desc: string; delay: number }) {
  const navigate = useNavigate()
  return (
    <button
      className="relative flex flex-col gap-3 p-4 rounded-xl border border-border bg-surface card-glow lift-hover text-left slide-up overflow-hidden group"
      style={{ animationDelay: `${delay}s` }}
      onClick={() => navigate('/projects/new')}
    >
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/8 to-transparent" />
      <div className="w-8 h-8 rounded-lg bg-surface2 border border-border flex items-center justify-center group-hover:border-border2 group-hover:bg-surface transition-all">
        <Icon name={icon} size={15} className="text-tx3 group-hover:text-tx transition-colors" />
      </div>
      <div>
        <div className="text-[13px] font-medium text-tx tracking-[-0.005em]">{label}</div>
        <div className="text-[11px] text-tx4 font-mono mt-0.5">{desc}</div>
      </div>
      <div className="absolute bottom-3 right-3 opacity-0 group-hover:opacity-100 transition-opacity">
        <Icon name="arrow-right" size={11} className="text-tx4" />
      </div>
    </button>
  )
}

function ProjectCard({ project }: { project: ProjectRead }) {
  const navigate = useNavigate()
  const cfg = STATUS_CONFIG[project.status] ?? STATUS_CONFIG.draft

  return (
    <div
      className="group flex items-center gap-4 py-4 border-b border-border cursor-pointer hover:bg-surface/60 transition-all duration-150 px-3 -mx-3 rounded-lg"
      onClick={() => navigate(`/projects/${project.id}`)}
    >
      {/* Status dot */}
      <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-surface2 border border-border shrink-0 group-hover:border-border2 transition-colors">
        <div className={`w-2 h-2 rounded-full ${cfg.dot}`} />
      </div>

      {/* Info */}
      <div className="flex-1 min-w-0">
        <div className="text-[14px] font-medium text-tx tracking-[-0.01em] truncate leading-tight mb-1">
          {project.title}
        </div>
        <div className="flex items-center gap-2 flex-wrap">
          {project.goal && (
            <span className="inline-flex items-center h-[18px] px-2 rounded bg-surface2 border border-border font-mono text-[9px] text-tx4 uppercase tracking-[0.1em]">
              {GOAL_LABELS[project.goal] ?? project.goal}
            </span>
          )}
          <span className="text-[12px] text-tx4 font-mono truncate">{project.topic}</span>
        </div>
      </div>

      {/* Right */}
      <div className="flex items-center gap-3 shrink-0">
        <div className={`inline-flex items-center gap-1.5 h-[22px] px-2.5 rounded-full border font-mono text-[9px] uppercase tracking-[0.1em] ${cfg.pill}`}>
          <div className={`w-1 h-1 rounded-full ${cfg.dot}`} />
          {cfg.label}
        </div>
        <div className="text-[11px] font-mono text-tx4 w-16 text-right">
          {relativeTime(project.created_at)}
        </div>
        <div className="opacity-0 group-hover:opacity-100 transition-opacity">
          <Icon name="chevron-right" size={12} className="text-tx4" />
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
  const projects  = data?.items ?? []
  const total     = data?.total ?? 0
  const ready     = projects.filter(p => p.status === 'ready' || p.status === 'published').length
  const active    = projects.filter(p => p.status === 'generating' || p.status === 'researching').length
  const published = projects.filter(p => p.status === 'published').length

  return (
    <AppShell
      topbar={
        <Topbar
          breadcrumbs={[{ label: 'Dashboard' }]}
          actions={
            <button
              className="relative flex items-center gap-2 h-8 px-4 rounded-lg bg-tx text-bg font-semibold text-[13px] hover:bg-tx/90 transition-all btn-glow overflow-hidden"
              onClick={() => navigate('/projects/new')}
            >
              <Icon name="plus" size={13} />
              New Project
            </button>
          }
        />
      }
    >
      <div className="max-w-[1040px] mx-auto px-8 py-8 pb-24">

        {/* Greeting */}
        <div className="mb-7 slide-up">
          <h1 className="text-[32px] font-semibold tracking-[-0.03em] leading-tight gradient-text">
            Good to see you, {firstName}.
          </h1>
          <p className="text-tx4 text-[13px] mt-1.5 font-mono tracking-wide">
            Research · draft · fact-check · publish — humans at every gate.
          </p>
        </div>

        {/* Stats */}
        {!isLoading && total > 0 && (
          <div className="flex gap-3 mb-7">
            <StatCard label="Total" value={total} delay={0.05} />
            <StatCard label="Ready" value={ready} delay={0.1} />
            <StatCard label="Published" value={published} delay={0.15} />
            <StatCard label="Active" value={active} sub={active > 0 ? 'generating now' : 'idle'} delay={0.2} />
          </div>
        )}

        {/* Quick actions */}
        <div className="mb-7">
          <div className="font-mono text-[9px] uppercase tracking-[0.22em] text-tx4 mb-3">Quick start</div>
          <div className="grid grid-cols-4 gap-2">
            {QUICK_ACTIONS.map((a, i) => (
              <QuickAction key={a.label} {...a} delay={0.08 + i * 0.04} />
            ))}
          </div>
        </div>

        {/* Projects */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <span className="text-[13px] font-semibold tracking-tight">Recent Projects</span>
              {total > 0 && (
                <span className="font-mono text-[11px] text-tx4 bg-surface2 border border-border px-1.5 py-0.5 rounded">
                  {total}
                </span>
              )}
            </div>
            {total > 5 && (
              <button
                className="text-[12px] font-mono text-tx4 hover:text-tx2 transition-colors"
                onClick={() => navigate('/projects')}
              >
                View all →
              </button>
            )}
          </div>

          {isLoading ? (
            <div className="flex justify-center py-20"><Spinner size={20} /></div>
          ) : !projects.length ? (
            <div className="relative rounded-xl border border-border bg-surface overflow-hidden">
              <div className="dot-grid absolute inset-0 opacity-50" />
              <div className="relative">
                <EmptyState
                  title="No projects yet."
                  description="Start with a topic, link, voice note, or file. The agents handle research, drafting, and fact-checking."
                  action={
                    <button
                      className="flex items-center gap-2 h-9 px-5 rounded-lg bg-tx text-bg font-semibold text-[13px] hover:bg-tx/90 transition-all"
                      onClick={() => navigate('/projects/new')}
                    >
                      <Icon name="plus" size={13} />
                      New Project
                    </button>
                  }
                />
              </div>
            </div>
          ) : (
            <div className="flex flex-col slide-up" style={{ animationDelay: '0.12s' }}>
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
