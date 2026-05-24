import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { rag } from '../../lib/api'
import { Icon } from '../common/Icon'
import { Spinner } from '../common/Spinner'
import { EmptyState } from '../common/EmptyState'
import { relativeTime } from '../../lib/utils'

const TYPE_TAG: Record<string, string> = {
  url:    'URL',
  file:   'PDF',
  x_post: 'X',
  manual: 'TXT',
}

interface StageSourcesProps {
  projectId: string
}

export function StageSources({ projectId }: StageSourcesProps) {
  const qc = useQueryClient()
  const [showAdd, setShowAdd] = useState(false)
  const [form, setForm] = useState({ title: '', url: '', raw_text: '', source_type: 'url' })

  const { data, isLoading } = useQuery({
    queryKey: ['sources', projectId],
    queryFn: () => rag.listSources(50),
  })

  const { mutateAsync: addSource, isPending } = useMutation({
    mutationFn: () =>
      rag.createSource({
        project_id: projectId,
        ...form,
        trust_level: 0.8,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['sources', projectId] })
      setShowAdd(false)
      setForm({ title: '', url: '', raw_text: '', source_type: 'url' })
    },
  })

  return (
    <div>
      <div className="flex items-baseline justify-between mb-5">
        <div>
          <h2 className="text-[22px] font-semibold tracking-[-0.015em]">Sources</h2>
          {data && (
            <div className="text-[13px] text-tx3 mt-1">
              {data.total} source{data.total !== 1 ? 's' : ''} available for this workspace
            </div>
          )}
        </div>
        <div className="flex gap-2">
          <button
            className="flex items-center gap-2 h-9 px-4 rounded-pill border border-border2 text-sm text-tx hover:bg-surface2 transition-all"
            onClick={() => setShowAdd((v) => !v)}
          >
            <Icon name="plus" size={14} /> Add Source
          </button>
        </div>
      </div>

      {showAdd && (
        <div className="mb-6 p-5 border border-border2 rounded-xl bg-surface2 flex flex-col gap-3">
          <div className="flex gap-3">
            <select
              value={form.source_type}
              onChange={(e) => setForm((f) => ({ ...f, source_type: e.target.value }))}
              className="bg-surface border border-border rounded-lg px-3 py-2 text-sm text-tx"
            >
              <option value="url">URL</option>
              <option value="x_post">X Post</option>
              <option value="manual">Manual Text</option>
            </select>
            <input
              placeholder="Title (optional)"
              value={form.title}
              onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
              className="flex-1 bg-surface border border-border rounded-lg px-3 py-2 text-sm text-tx placeholder:text-tx4 outline-none"
            />
          </div>
          {form.source_type !== 'manual' && (
            <input
              placeholder="URL"
              value={form.url}
              onChange={(e) => setForm((f) => ({ ...f, url: e.target.value }))}
              className="bg-surface border border-border rounded-lg px-3 py-2 text-sm text-tx placeholder:text-tx4 outline-none"
            />
          )}
          {form.source_type === 'manual' && (
            <textarea
              placeholder="Paste source text..."
              value={form.raw_text}
              onChange={(e) => setForm((f) => ({ ...f, raw_text: e.target.value }))}
              rows={3}
              className="bg-surface border border-border rounded-lg px-3 py-2 text-sm text-tx placeholder:text-tx4 outline-none resize-none"
            />
          )}
          <div className="flex gap-2 justify-end">
            <button
              onClick={() => setShowAdd(false)}
              className="h-8 px-4 rounded-pill border border-border2 text-sm text-tx2 hover:bg-surface transition-all"
            >
              Cancel
            </button>
            <button
              onClick={() => addSource()}
              disabled={isPending}
              className="h-8 px-4 rounded-pill bg-tx text-bg font-semibold text-sm flex items-center gap-2 hover:bg-tx/90 transition-all disabled:opacity-50"
            >
              {isPending ? <Spinner size={14} /> : 'Add'}
            </button>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="flex justify-center py-10"><Spinner size={20} /></div>
      ) : !data?.items.length ? (
        <EmptyState
          title="No sources selected."
          description="Add a link, upload a file, or let the Research Agent discover context."
          action={
            <button
              className="flex items-center gap-2 h-9 px-4 rounded-pill border border-border2 text-sm text-tx hover:bg-surface2 transition-all"
              onClick={() => setShowAdd(true)}
            >
              <Icon name="plus" size={14} /> Add Source
            </button>
          }
        />
      ) : (
        <div className="flex flex-col">
          {data.items.map((s) => (
            <div key={s.id} className="grid py-5 border-b border-border gap-[18px] hover:opacity-70 transition-opacity cursor-default"
              style={{ gridTemplateColumns: '44px 1fr auto' }}>
              <div className="w-11 h-11 rounded-lg flex items-center justify-center bg-surface2 border border-border font-mono text-[11px] text-tx2 font-semibold tracking-[0.04em]">
                {TYPE_TAG[s.source_type] ?? 'SRC'}
              </div>
              <div>
                <div className="text-base font-semibold tracking-[-0.005em]">
                  {s.title ?? s.url ?? 'Untitled source'}
                </div>
                {s.raw_text && (
                  <div className="text-sm text-tx2 mt-1.5 line-clamp-2">
                    "{s.raw_text.slice(0, 200)}"
                  </div>
                )}
                <div className="font-mono text-[12px] text-tx3 mt-2 flex items-center gap-2">
                  {s.author && <span>{s.author}</span>}
                  {s.author && s.url && <span className="text-tx4">·</span>}
                  {s.url && <span className="truncate max-w-[200px]">{s.url}</span>}
                  <span className="text-tx4">·</span>
                  <span>{relativeTime(s.created_at)}</span>
                </div>
              </div>
              <div className="text-right min-w-[90px]">
                <div className="text-lg font-mono font-semibold">{s.trust_level.toFixed(2)}</div>
                <div className="font-mono text-[9px] text-tx3 uppercase tracking-[0.2em] mt-0.5">
                  trust
                </div>
                <div className="score-bar w-20 mt-2 ml-auto">
                  <div className="score-bar-fill" style={{ width: `${s.trust_level * 100}%` }} />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
