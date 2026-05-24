import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { traces as tracesApi } from '../../lib/api'
import { Spinner } from '../common/Spinner'
import { Icon } from '../common/Icon'
import { relativeTime } from '../../lib/utils'

const STATUS_DOT: Record<string, string> = {
  success:    'bg-tx',
  completed:  'bg-tx',
  error:      'bg-red-400',
  running:    'bg-tx2 animate-pulse',
  pending:    'bg-border2',
}

interface AgentTracesPanelProps {
  projectId?: string
  draftId?: string
}

export function AgentTracesPanel({ projectId, draftId }: AgentTracesPanelProps) {
  const [expanded, setExpanded] = useState<string | null>(null)

  const { data, isLoading, refetch } = useQuery({
    queryKey: draftId ? ['draft-traces', draftId] : ['project-traces', projectId],
    queryFn: () =>
      draftId
        ? tracesApi.forDraft(draftId)
        : tracesApi.forProject(projectId!),
    enabled: !!(draftId || projectId),
    refetchInterval: 5000,
  })

  const items = data?.items ?? []

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm font-semibold">Agent Traces</span>
        <button
          onClick={() => refetch()}
          className="h-7 px-2 rounded text-tx4 hover:text-tx transition-colors"
        >
          <Icon name="refresh" size={14} />
        </button>
      </div>

      {isLoading && (
        <div className="flex justify-center py-8"><Spinner size={18} /></div>
      )}

      {!isLoading && items.length === 0 && (
        <div className="py-8 text-center text-tx3 text-sm">
          No traces yet. Start generating content to see agent activity.
        </div>
      )}

      <div className="flex flex-col gap-0">
        {items.map((trace) => {
          const isOpen = expanded === trace.id
          return (
            <div key={trace.id} className="border-b border-border last:border-0">
              <button
                className="w-full flex items-center gap-3 py-3 text-left hover:bg-surface2 transition-colors px-1 rounded"
                onClick={() => setExpanded(isOpen ? null : trace.id)}
              >
                <div className={`w-2 h-2 rounded-full shrink-0 ${STATUS_DOT[trace.status] ?? 'bg-border2'}`} />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">{trace.agent_name}</div>
                  {trace.step_name && (
                    <div className="text-xs text-tx3 font-mono truncate">{trace.step_name}</div>
                  )}
                </div>
                <div className="text-right shrink-0">
                  {trace.latency_ms != null && (
                    <div className="font-mono text-[11px] text-tx3">
                      {trace.latency_ms}ms
                    </div>
                  )}
                  {trace.tokens_input != null && (
                    <div className="font-mono text-[10px] text-tx4">
                      {(trace.tokens_input + (trace.tokens_output ?? 0)).toLocaleString()} tok
                    </div>
                  )}
                </div>
                <Icon
                  name={isOpen ? 'chevron-down' : 'chevron-right'}
                  size={14}
                  className="text-tx4 shrink-0"
                />
              </button>

              {isOpen && (
                <div className="px-2 pb-3 text-xs font-mono flex flex-col gap-3">
                  <div className="flex items-center gap-4 text-tx3">
                    {trace.model && <span>model: {trace.model}</span>}
                    <span>{relativeTime(trace.created_at)}</span>
                    {trace.status === 'error' && trace.error_message && (
                      <span className="text-red-400">{trace.error_message}</span>
                    )}
                  </div>
                  {trace.input && (
                    <div>
                      <div className="text-tx4 uppercase tracking-wider mb-1">Input</div>
                      <pre className="text-tx3 overflow-auto max-h-32 text-[11px] bg-surface2 p-2 rounded">
                        {JSON.stringify(trace.input, null, 2)}
                      </pre>
                    </div>
                  )}
                  {trace.output && (
                    <div>
                      <div className="text-tx4 uppercase tracking-wider mb-1">Output</div>
                      <pre className="text-tx3 overflow-auto max-h-32 text-[11px] bg-surface2 p-2 rounded">
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
  )
}
