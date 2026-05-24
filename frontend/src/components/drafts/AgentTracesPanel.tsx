import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { traces as tracesApi } from '../../lib/api'
import { Spinner } from '../common/Spinner'
import { relativeTime } from '../../lib/utils'

// Per-agent visual config
const AGENT_CONFIG: Record<string, { color: string; bg: string; icon: React.ReactNode }> = {
  research:  {
    color: '#6e6e6e', bg: 'rgba(110,110,110,0.12)',
    icon: <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg>,
  },
  retrieval: {
    color: '#6e6e6e', bg: 'rgba(110,110,110,0.12)',
    icon: <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 01-2 2H7l-4 4V5a2 2 0 012-2h14a2 2 0 012 2z"/></svg>,
  },
  insight:   {
    color: '#a8a8a8', bg: 'rgba(168,168,168,0.1)',
    icon: <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5z"/></svg>,
  },
  angle:     {
    color: '#a8a8a8', bg: 'rgba(168,168,168,0.1)',
    icon: <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="6" cy="6" r="2"/><circle cx="18" cy="6" r="2"/><circle cx="12" cy="20" r="2"/><path d="M6 8v3a2 2 0 002 2h8a2 2 0 002-2V8M12 13v5"/></svg>,
  },
  writer:    {
    color: '#fff', bg: 'rgba(255,255,255,0.08)',
    icon: <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 21l4-1 12-12-3-3L4 17z"/></svg>,
  },
  draft:     {
    color: '#fff', bg: 'rgba(255,255,255,0.08)',
    icon: <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M3 21l4-1 12-12-3-3L4 17z"/></svg>,
  },
  fact:      {
    color: '#6ee7b7', bg: 'rgba(110,231,183,0.08)',
    icon: <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="4 12 10 18 20 6"/></svg>,
  },
  style:     {
    color: '#93c5fd', bg: 'rgba(147,197,253,0.08)',
    icon: <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M12 8v4l2 2"/></svg>,
  },
  editor:    {
    color: '#fbbf24', bg: 'rgba(251,191,36,0.08)',
    icon: <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M17 3a2.83 2.83 0 114 4L7.5 20.5 2 22l1.5-5.5L17 3z"/></svg>,
  },
  publisher: {
    color: '#a78bfa', bg: 'rgba(167,139,250,0.08)',
    icon: <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>,
  },
}

function getAgentConfig(agentName: string) {
  const key = agentName.toLowerCase().split(/[\s_]/)[0]
  return AGENT_CONFIG[key] ?? {
    color: '#6e6e6e',
    bg: 'rgba(110,110,110,0.1)',
    icon: <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="4"/></svg>,
  }
}

const STATUS_CONFIG: Record<string, { dot: string; label: string }> = {
  success:   { dot: 'bg-tx',       label: 'Done' },
  completed: { dot: 'bg-tx',       label: 'Done' },
  error:     { dot: 'bg-red-400',  label: 'Error' },
  running:   { dot: 'bg-tx2 animate-pulse', label: 'Running' },
  pending:   { dot: 'bg-border2',  label: 'Pending' },
}

import type React from 'react'

interface AgentTracesPanelProps {
  projectId?: string
  draftId?: string
}

export function AgentTracesPanel({ projectId, draftId }: AgentTracesPanelProps) {
  const [expanded, setExpanded] = useState<string | null>(null)

  const { data, isLoading, refetch, isFetching } = useQuery({
    queryKey: draftId ? ['draft-traces', draftId] : ['project-traces', projectId],
    queryFn: () =>
      draftId
        ? tracesApi.forDraft(draftId)
        : tracesApi.forProject(projectId!),
    enabled: !!(draftId || projectId),
    refetchInterval: 5000,
  })

  const items = data?.items ?? []
  const totalTokens = items.reduce(
    (s, t) => s + (t.tokens_input ?? 0) + (t.tokens_output ?? 0), 0
  )
  const totalMs = items.reduce((s, t) => s + (t.latency_ms ?? 0), 0)

  return (
    <div>
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div>
          <span className="text-sm font-semibold">Agent Traces</span>
          {items.length > 0 && (
            <div className="flex items-center gap-3 mt-1 font-mono text-[10px] text-tx4">
              <span>{items.length} steps</span>
              {totalTokens > 0 && <span>{totalTokens.toLocaleString()} tokens</span>}
              {totalMs > 0 && <span>{(totalMs / 1000).toFixed(1)}s total</span>}
            </div>
          )}
        </div>
        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="flex items-center gap-1.5 h-7 px-2.5 rounded-lg text-tx4 hover:text-tx2 hover:bg-surface2 transition-all disabled:opacity-40"
          title="Refresh traces"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"
            className={isFetching ? 'animate-spin' : ''}>
            <path d="M23 4v6h-6"/><path d="M1 20v-6h6"/>
            <path d="M3.51 9a9 9 0 0114.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0020.49 15"/>
          </svg>
        </button>
      </div>

      {isLoading && (
        <div className="flex justify-center py-10"><Spinner size={18} /></div>
      )}

      {!isLoading && items.length === 0 && (
        <div className="py-10 text-center border border-border rounded-xl">
          <div className="font-mono text-[11px] text-tx4 uppercase tracking-[0.2em] mb-2">No traces yet</div>
          <p className="text-xs text-tx4 max-w-[200px] mx-auto leading-relaxed">
            Start generating content to see the full agent pipeline in action.
          </p>
        </div>
      )}

      {/* Timeline */}
      {items.length > 0 && (
        <div className="relative">
          {/* Vertical connector */}
          <div className="absolute left-[13px] top-4 bottom-2 w-px bg-border z-0" />

          <div className="flex flex-col">
            {items.map((trace, idx) => {
              const isOpen  = expanded === trace.id
              const cfg     = getAgentConfig(trace.agent_name)
              const statCfg = STATUS_CONFIG[trace.status] ?? STATUS_CONFIG.pending
              const tokens  = (trace.tokens_input ?? 0) + (trace.tokens_output ?? 0)

              return (
                <div key={trace.id} className="relative" style={{ animationDelay: `${idx * 0.04}s` }}>
                  <button
                    className={`w-full flex items-start gap-3 py-2.5 text-left transition-all pl-0 ${
                      isOpen ? 'pb-1' : ''
                    }`}
                    onClick={() => setExpanded(isOpen ? null : trace.id)}
                  >
                    {/* Dot */}
                    <div
                      className="relative z-10 flex items-center justify-center w-[27px] h-[27px] rounded-full shrink-0 mt-[1px]"
                      style={{ background: cfg.bg, border: `1px solid ${cfg.color}33` }}
                    >
                      <span style={{ color: cfg.color }}>{cfg.icon}</span>
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-medium text-tx truncate">{trace.agent_name}</span>
                        <span className={`inline-block w-1.5 h-1.5 rounded-full shrink-0 ${statCfg.dot}`} />
                      </div>
                      {trace.step_name && (
                        <div className="font-mono text-[10px] text-tx4 truncate mt-0.5">{trace.step_name}</div>
                      )}
                    </div>

                    {/* Right metrics */}
                    <div className="text-right shrink-0 flex flex-col items-end gap-0.5">
                      {trace.latency_ms != null && (
                        <span className="font-mono text-[10px] text-tx3">{trace.latency_ms}ms</span>
                      )}
                      {tokens > 0 && (
                        <span className="font-mono text-[10px] text-tx4">{tokens.toLocaleString()}t</span>
                      )}
                      <svg
                        width="10" height="10" viewBox="0 0 24 24" fill="none"
                        stroke="currentColor" strokeWidth="2" className="text-tx4"
                        style={{ transform: isOpen ? 'rotate(90deg)' : 'none', transition: 'transform 0.2s' }}
                      >
                        <polyline points="9 18 15 12 9 6"/>
                      </svg>
                    </div>
                  </button>

                  {/* Expanded detail */}
                  {isOpen && (
                    <div className="ml-[39px] mb-2 px-3 py-3 rounded-xl bg-surface border border-border text-xs font-mono slide-up">
                      {/* Meta row */}
                      <div className="flex flex-wrap gap-x-4 gap-y-1 text-tx3 mb-3 pb-2 border-b border-border">
                        {trace.model && (
                          <span className="flex items-center gap-1">
                            <span className="text-tx4">model</span> {trace.model}
                          </span>
                        )}
                        {trace.latency_ms != null && (
                          <span className="flex items-center gap-1">
                            <span className="text-tx4">time</span> {trace.latency_ms}ms
                          </span>
                        )}
                        {tokens > 0 && (
                          <span className="flex items-center gap-1">
                            <span className="text-tx4">tokens</span>
                            {trace.tokens_input ?? 0}in · {trace.tokens_output ?? 0}out
                          </span>
                        )}
                        <span className="flex items-center gap-1 text-tx4">
                          {relativeTime(trace.created_at)}
                        </span>
                      </div>

                      {trace.status === 'error' && trace.error_message && (
                        <div className="mb-2 px-2 py-1.5 rounded bg-red-900/20 text-red-400 text-[10px]">
                          {trace.error_message}
                        </div>
                      )}

                      {trace.input && (
                        <div className="mb-2">
                          <div className="text-tx4 uppercase tracking-wider text-[9px] mb-1">Input</div>
                          <pre className="text-[10px] text-tx3 overflow-auto max-h-28 bg-surface2 p-2 rounded-lg leading-relaxed">
                            {JSON.stringify(trace.input, null, 2)}
                          </pre>
                        </div>
                      )}

                      {trace.output && (
                        <div>
                          <div className="text-tx4 uppercase tracking-wider text-[9px] mb-1">Output</div>
                          <pre className="text-[10px] text-tx3 overflow-auto max-h-28 bg-surface2 p-2 rounded-lg leading-relaxed">
                            {JSON.stringify(trace.output, null, 2)}
                          </pre>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
