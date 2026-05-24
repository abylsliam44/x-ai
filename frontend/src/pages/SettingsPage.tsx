import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { AppShell } from '../components/layout/AppShell'
import { Topbar } from '../components/layout/Topbar'
import { Icon } from '../components/common/Icon'
import { Spinner } from '../components/common/Spinner'
import { EmptyState } from '../components/common/EmptyState'
import { useXStatus, useXConnect, useXDisconnect } from '../hooks/useXConnection'
import { rag, ApiError } from '../lib/api'
import { relativeTime } from '../lib/utils'

type SettingsTab = 'x-connection' | 'writing-samples' | 'brand-voice'

export function SettingsPage() {
  const { tab } = useParams<{ tab?: string }>()
  const navigate = useNavigate()
  const activeTab: SettingsTab = (tab as SettingsTab) ?? 'x-connection'

  const setTab = (t: SettingsTab) => navigate(`/settings/${t}`)

  return (
    <AppShell
      topbar={
        <Topbar
          breadcrumbs={[{ label: 'Settings' }]}
        />
      }
    >
      <div className="max-w-[900px] mx-auto px-9 py-9 pb-24">
        <h1 className="text-[36px] font-semibold tracking-[-0.025em] mb-8">Settings</h1>

        {/* Tab bar */}
        <div className="flex border-b border-border mb-8">
          {(
            [
              { id: 'x-connection',    label: 'X Connection',    icon: 'twitter' },
              { id: 'writing-samples', label: 'Writing Samples', icon: 'lib' },
              { id: 'brand-voice',     label: 'Brand Voice',     icon: 'spark' },
            ] as { id: SettingsTab; label: string; icon: string }[]
          ).map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`relative flex items-center gap-2 py-3.5 mr-7 text-sm font-medium transition-colors ${
                activeTab === t.id ? 'text-tx' : 'text-tx3 hover:text-tx2'
              }`}
            >
              <Icon name={t.icon} size={15} />
              {t.label}
              {activeTab === t.id && (
                <span className="absolute left-0 right-0 bottom-[-1px] h-[1px] bg-tx" />
              )}
            </button>
          ))}
        </div>

        {activeTab === 'x-connection' && <XConnectionTab />}
        {activeTab === 'writing-samples' && <WritingSamplesTab />}
        {activeTab === 'brand-voice' && <BrandVoiceTab />}
      </div>
    </AppShell>
  )
}

function XConnectionTab() {
  const { data: xStatus, isLoading } = useXStatus()
  const { mutateAsync: connect, isPending: isConnecting } = useXConnect()
  const { mutateAsync: disconnect, isPending: isDisconnecting } = useXDisconnect()

  if (isLoading) {
    return <div className="flex justify-center py-10"><Spinner size={20} /></div>
  }

  return (
    <div className="max-w-lg">
      <h2 className="text-lg font-semibold mb-1">X / Twitter Connection</h2>
      <p className="text-tx2 text-sm mb-6">
        Connect your X account to publish content directly from the platform.
        Tokens are stored encrypted and never exposed to the frontend.
      </p>

      <div className="border border-border rounded-xl p-5">
        <div className="flex items-center gap-4 mb-5">
          <div className="w-12 h-12 rounded-full bg-surface2 border border-border flex items-center justify-center">
            <Icon name="twitter" size={20} />
          </div>
          <div>
            <div className="font-semibold text-sm">
              {xStatus?.connected ? `@${xStatus.username}` : 'Not connected'}
            </div>
            <div className={`text-xs mt-0.5 font-mono ${xStatus?.connected ? 'text-tx2' : 'text-tx3'}`}>
              {xStatus?.connected
                ? `X User ID: ${xStatus.x_user_id}`
                : 'Connect your X account to enable publishing'}
            </div>
          </div>
          <div className="ml-auto">
            <div className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-pill text-xs font-mono uppercase tracking-wider ${
              xStatus?.connected ? 'bg-tx/10 text-tx border border-tx/20' : 'bg-border text-tx3'
            }`}>
              <div className={`w-1.5 h-1.5 rounded-full ${xStatus?.connected ? 'bg-tx' : 'bg-tx3'}`} />
              {xStatus?.connected ? 'Connected' : 'Disconnected'}
            </div>
          </div>
        </div>

        {xStatus?.scopes && xStatus.scopes.length > 0 && (
          <div className="mb-5 px-4 py-3 border border-border rounded-lg bg-surface2">
            <div className="text-xs font-mono text-tx3 mb-1 uppercase tracking-wider">Scopes</div>
            <div className="flex flex-wrap gap-2">
              {xStatus.scopes.map((scope) => (
                <span key={scope} className="text-xs font-mono bg-border px-2 py-0.5 rounded text-tx2">
                  {scope}
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="flex gap-3">
          {!xStatus?.connected ? (
            <button
              className="flex items-center gap-2 h-10 px-5 rounded-pill bg-tx text-bg font-semibold text-sm hover:bg-tx/90 transition-all disabled:opacity-50"
              onClick={() => connect()}
              disabled={isConnecting}
            >
              {isConnecting ? <Spinner size={14} /> : <Icon name="twitter" size={14} />}
              Connect X Account
            </button>
          ) : (
            <>
              <button
                className="flex items-center gap-2 h-10 px-5 rounded-pill border border-border2 text-sm text-tx2 hover:bg-surface2 transition-all disabled:opacity-50"
                onClick={() => connect()}
                disabled={isConnecting}
              >
                {isConnecting ? <Spinner size={14} /> : <Icon name="refresh" size={14} />}
                Reconnect
              </button>
              <button
                className="flex items-center gap-2 h-10 px-5 rounded-pill border border-red-900/50 text-sm text-red-400 hover:bg-red-900/10 transition-all disabled:opacity-50"
                onClick={() => disconnect()}
                disabled={isDisconnecting}
              >
                {isDisconnecting ? <Spinner size={14} /> : <Icon name="x" size={14} />}
                Disconnect
              </button>
            </>
          )}
        </div>
      </div>

      <div className="mt-6 px-4 py-4 border border-border rounded-xl bg-surface2 text-xs text-tx3 flex gap-3">
        <Icon name="info" size={14} className="shrink-0 mt-0.5" />
        <div>
          OAuth tokens are encrypted at rest. The frontend never receives raw tokens.
          Voice content is published as MP4 video with captions and audio.
        </div>
      </div>
    </div>
  )
}

function WritingSamplesTab() {
  const qc = useQueryClient()
  const [showAdd, setShowAdd] = useState(false)
  const [title, setTitle] = useState('')
  const [text, setText] = useState('')
  const [error, setError] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['writing-samples'],
    queryFn: () => rag.listWritingSamples(50),
  })

  const { mutateAsync: addSample, isPending } = useMutation({
    mutationFn: () => rag.createWritingSample(title || undefined!, text),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['writing-samples'] })
      setShowAdd(false)
      setTitle('')
      setText('')
      setError('')
    },
    onError: (err) => {
      setError(err instanceof ApiError ? err.message : 'Failed to add sample.')
    },
  })

  return (
    <div className="max-w-2xl">
      <div className="flex items-baseline justify-between mb-5">
        <div>
          <h2 className="text-lg font-semibold mb-1">Writing Samples</h2>
          <p className="text-tx2 text-sm">
            Add examples of your writing so the system can match your voice.
          </p>
        </div>
        <button
          className="flex items-center gap-2 h-9 px-4 rounded-pill border border-border2 text-sm text-tx hover:bg-surface2 transition-all"
          onClick={() => setShowAdd((v) => !v)}
        >
          <Icon name="plus" size={14} /> Add Sample
        </button>
      </div>

      {showAdd && (
        <div className="mb-6 p-5 border border-border2 rounded-xl bg-surface2 flex flex-col gap-3">
          {error && (
            <div className="px-3 py-2 border border-red-900/50 bg-red-900/10 rounded-lg text-red-400 text-xs">
              {error}
            </div>
          )}
          <input
            placeholder="Title (optional)"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm text-tx placeholder:text-tx4 outline-none"
          />
          <textarea
            placeholder="Paste a sample of your writing here. This could be a thread, a post, or an essay..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={6}
            className="w-full bg-surface border border-border rounded-lg px-3 py-2 text-sm text-tx placeholder:text-tx4 outline-none resize-none"
          />
          <div className="flex gap-2 justify-end">
            <button
              onClick={() => { setShowAdd(false); setError('') }}
              className="h-8 px-4 rounded-pill border border-border2 text-sm text-tx2 hover:bg-surface transition-all"
            >
              Cancel
            </button>
            <button
              onClick={() => addSample()}
              disabled={isPending || !text.trim()}
              className="h-8 px-4 rounded-pill bg-tx text-bg font-semibold text-sm flex items-center gap-2 hover:bg-tx/90 transition-all disabled:opacity-50"
            >
              {isPending ? <Spinner size={14} /> : 'Add Sample'}
            </button>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="flex justify-center py-10"><Spinner size={20} /></div>
      ) : !data?.items.length ? (
        <EmptyState
          title="No writing samples yet."
          description="Upload a few examples so the system can learn your voice."
          action={
            <button
              className="flex items-center gap-2 h-9 px-4 rounded-pill border border-border2 text-sm text-tx hover:bg-surface2 transition-all"
              onClick={() => setShowAdd(true)}
            >
              <Icon name="plus" size={14} /> Add Sample
            </button>
          }
        />
      ) : (
        <div className="flex flex-col">
          {data.items.map((sample) => (
            <div key={sample.id} className="py-5 border-b border-border">
              <div className="font-semibold text-sm mb-1">
                {sample.title ?? 'Untitled sample'}
              </div>
              <div className="text-sm text-tx2 line-clamp-3 leading-relaxed">
                {sample.text}
              </div>
              <div className="font-mono text-[11px] text-tx4 mt-2 flex items-center gap-3">
                <span>{sample.source_type}</span>
                <span>·</span>
                <span>{relativeTime(sample.created_at)}</span>
                <span>·</span>
                <span>{sample.text.length} chars</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function BrandVoiceTab() {
  return (
    <div className="max-w-lg">
      <h2 className="text-lg font-semibold mb-1">Brand Voice</h2>
      <p className="text-tx2 text-sm mb-6">
        Configure your writing persona. This guides the style reviewer and editor agents.
      </p>

      <div className="flex flex-col gap-4">
        {[
          { label: 'Voice Name', placeholder: 'e.g. Sharp Operator', desc: 'How you refer to this writing style internally' },
          { label: 'Tone', placeholder: 'e.g. Analytical, contrarian, low-jargon', desc: 'The overall feel and register of your writing' },
          { label: 'Target Audience', placeholder: 'e.g. Founders, operators, technical investors', desc: 'Who you are typically writing for' },
          { label: 'Forbidden Phrases', placeholder: 'e.g. leverage, synergy, game-changer', desc: 'Words and phrases to always avoid' },
        ].map((field) => (
          <div key={field.label} className="flex flex-col gap-1.5">
            <label className="text-xs font-mono text-tx3 uppercase tracking-wider">
              {field.label}
            </label>
            <input
              placeholder={field.placeholder}
              className="w-full bg-surface border border-border rounded-xl px-4 py-3 text-sm text-tx placeholder:text-tx4 outline-none focus:border-border2 transition-colors"
            />
            <div className="text-xs text-tx4">{field.desc}</div>
          </div>
        ))}

        <div className="mt-2">
          <button className="flex items-center gap-2 h-10 px-5 rounded-pill bg-tx text-bg font-semibold text-sm hover:bg-tx/90 transition-all opacity-50 cursor-not-allowed">
            Save Brand Voice
          </button>
          <p className="text-xs text-tx4 mt-2">Brand voice API integration coming soon.</p>
        </div>
      </div>
    </div>
  )
}
