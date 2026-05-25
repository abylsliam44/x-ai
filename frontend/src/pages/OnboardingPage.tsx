import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import { rag, ApiError } from '../lib/api'
import { useXConnect, useXStatus } from '../hooks/useXConnection'
import { Spinner } from '../components/common/Spinner'
import { Icon } from '../components/common/Icon'
import { markOnboardingDone } from '../lib/onboarding'

const STEPS = [
  { id: 'voice',   label: 'Your Voice' },
  { id: 'samples', label: 'Writing Samples' },
  { id: 'connect', label: 'Connect X' },
]

export function OnboardingPage() {
  const [step, setStep] = useState(0)
  const navigate = useNavigate()

  const finish = () => {
    markOnboardingDone()
    navigate('/dashboard', { replace: true })
  }

  return (
    <div className="min-h-screen bg-bg flex flex-col relative">
      {/* Dot grid */}
      <div className="dot-grid absolute inset-0 pointer-events-none opacity-40" />

      {/* Header */}
      <div className="relative flex items-center justify-between px-8 h-14 border-b border-border" style={{ background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(20px)' }}>
        <div className="flex items-center gap-2.5">
          <div className="brand-glow w-[22px] h-[22px] rounded-[5px] bg-tx flex items-center justify-center font-bold text-[12px] text-bg">
            n
          </div>
          <div className="flex flex-col leading-none">
            <span className="font-semibold text-[13px] tracking-[-0.02em]">nfactorial</span>
            <span className="font-mono text-[9px] text-tx4 tracking-[0.1em] uppercase">X Content</span>
          </div>
        </div>
        <button
          onClick={finish}
          className="font-mono text-[11px] text-tx4 hover:text-tx2 transition-colors px-3 py-1.5 rounded-lg hover:bg-surface2"
        >
          Skip setup →
        </button>
      </div>

      {/* Progress bar */}
      <div className="relative h-[2px] bg-border">
        <div
          className="absolute left-0 top-0 h-full bg-tx transition-all duration-500 ease-out"
          style={{ width: `${((step + 1) / STEPS.length) * 100}%` }}
        />
      </div>

      {/* Step indicators */}
      <div className="relative flex items-center justify-center gap-8 pt-8 pb-2">
        {STEPS.map((s, i) => (
          <div key={s.id} className="flex items-center gap-2">
            <div className={`w-[22px] h-[22px] rounded-full flex items-center justify-center text-[11px] font-semibold transition-all duration-300 ${
              i < step
                ? 'bg-tx text-bg agent-check'
                : i === step
                ? 'bg-tx text-bg ring-4 ring-tx/10'
                : 'bg-surface2 border border-border text-tx4'
            }`}>
              {i < step ? <Icon name="check" size={11} /> : i + 1}
            </div>
            <span className={`text-[12px] font-medium transition-colors ${
              i === step ? 'text-tx' : i < step ? 'text-tx3' : 'text-tx4'
            }`}>
              {s.label}
            </span>
          </div>
        ))}
      </div>

      {/* Content */}
      <div className="relative flex-1 flex items-start justify-center pt-10 px-4">
        <div className="w-full max-w-[520px] slide-up">
          {step === 0 && <StepVoice onNext={() => setStep(1)} />}
          {step === 1 && <StepSamples onNext={() => setStep(2)} onBack={() => setStep(0)} />}
          {step === 2 && <StepConnect onFinish={finish} onBack={() => setStep(1)} />}
        </div>
      </div>
    </div>
  )
}

// ── Step 1: Brand Voice ───────────────────────────────────────────────

function StepVoice({ onNext }: { onNext: () => void }) {
  const [tone, setTone] = useState('')
  const [audience, setAudience] = useState('')
  const [forbidden, setForbidden] = useState('')

  const handleNext = () => {
    if (tone || audience || forbidden) {
      localStorage.setItem('brand_voice_draft', JSON.stringify({ tone, audience, forbidden }))
    }
    onNext()
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-[32px] font-semibold tracking-[-0.025em] mb-2">Define your voice</h1>
        <p className="text-tx2 text-sm leading-relaxed">
          This guides the style reviewer and editor agents. You can update it anytime in Settings.
        </p>
      </div>

      <div className="flex flex-col gap-5">
        <Field
          label="Tone"
          placeholder="e.g. Analytical, contrarian, low-jargon"
          desc="The overall feel and register of your writing"
          value={tone}
          onChange={setTone}
        />
        <Field
          label="Target Audience"
          placeholder="e.g. Founders, operators, technical investors"
          desc="Who you are typically writing for"
          value={audience}
          onChange={setAudience}
        />
        <Field
          label="Forbidden Phrases"
          placeholder="e.g. leverage, synergy, game-changer"
          desc="Words and phrases to always avoid"
          value={forbidden}
          onChange={setForbidden}
        />
      </div>

      <div className="mt-8 flex items-center justify-between">
        <p className="text-[11px] font-mono text-tx4">You can update this anytime in Settings.</p>
        <button
          onClick={handleNext}
          className="flex items-center gap-2 h-9 px-5 rounded-lg bg-tx text-bg font-semibold text-[13px] hover:bg-tx/90 transition-all"
        >
          Continue <Icon name="arrow-right" size={13} />
        </button>
      </div>
    </div>
  )
}

// ── Step 2: Writing Samples ───────────────────────────────────────────

function StepSamples({ onNext, onBack }: { onNext: () => void; onBack: () => void }) {
  const [text, setText] = useState('')
  const [title, setTitle] = useState('')
  const [added, setAdded] = useState(0)
  const [error, setError] = useState('')

  const { mutateAsync: addSample, isPending } = useMutation({
    mutationFn: () => rag.createWritingSample(title || 'Sample ' + (added + 1), text),
    onSuccess: () => {
      setAdded((n) => n + 1)
      setText('')
      setTitle('')
      setError('')
    },
    onError: (err) => {
      setError(err instanceof ApiError ? err.message : 'Failed to save sample.')
    },
  })

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-[32px] font-semibold tracking-[-0.025em] mb-2">Add writing samples</h1>
        <p className="text-tx2 text-sm leading-relaxed">
          Paste examples of your best writing so the system can match your style.
          Even one sample makes a difference.
        </p>
      </div>

      {added > 0 && (
        <div className="mb-4 px-4 py-3 border border-tx/20 bg-tx/5 rounded-xl flex items-center gap-2 text-sm text-tx">
          <Icon name="check" size={14} />
          {added} sample{added !== 1 ? 's' : ''} added
        </div>
      )}

      {error && (
        <div className="mb-4 px-4 py-3 border border-red-900/50 bg-red-900/10 rounded-xl text-red-400 text-xs">
          {error}
        </div>
      )}

      <div className="flex flex-col gap-3 p-5 border border-border rounded-xl bg-surface2">
        <input
          placeholder="Title (optional)"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          className="w-full bg-surface border border-border rounded-lg px-3 py-2.5 text-sm text-tx placeholder:text-tx4 outline-none focus:border-border2 transition-colors"
        />
        <textarea
          placeholder="Paste a thread, post, or essay that represents your voice..."
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={6}
          className="w-full bg-surface border border-border rounded-lg px-3 py-2.5 text-sm text-tx placeholder:text-tx4 outline-none focus:border-border2 transition-colors resize-none"
        />
        <div className="flex justify-end">
          <button
            onClick={() => addSample()}
            disabled={isPending || !text.trim()}
            className="flex items-center gap-2 h-9 px-4 rounded-pill border border-border2 text-sm text-tx hover:bg-surface transition-all disabled:opacity-40"
          >
            {isPending ? <Spinner size={13} /> : <Icon name="plus" size={13} />}
            Add Sample
          </button>
        </div>
      </div>

      <div className="mt-8 flex items-center justify-between">
        <button
          onClick={onBack}
          className="flex items-center gap-2 h-9 px-4 rounded-lg border border-border text-[13px] text-tx3 hover:bg-surface2 hover:text-tx transition-all"
        >
          <Icon name="arrow-left" size={13} /> Back
        </button>
        <button
          onClick={onNext}
          className="flex items-center gap-2 h-9 px-5 rounded-lg bg-tx text-bg font-semibold text-[13px] hover:bg-tx/90 transition-all"
        >
          {added > 0 ? 'Continue' : 'Skip for now'} <Icon name="arrow-right" size={13} />
        </button>
      </div>
    </div>
  )
}

// ── Step 3: Connect X ─────────────────────────────────────────────────

function StepConnect({ onFinish, onBack }: { onFinish: () => void; onBack: () => void }) {
  const { data: xStatus, isLoading } = useXStatus()
  const { mutateAsync: connect, isPending: isConnecting } = useXConnect()

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-[32px] font-semibold tracking-[-0.025em] mb-2">Connect X account</h1>
        <p className="text-tx2 text-sm leading-relaxed">
          Required to publish directly from the platform. Tokens are stored encrypted
          and never exposed to the frontend.
        </p>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-10"><Spinner size={20} /></div>
      ) : xStatus?.connected ? (
        <div className="p-5 border border-tx/20 bg-tx/5 rounded-xl flex items-center gap-4">
          <div className="w-10 h-10 rounded-full bg-surface2 border border-border flex items-center justify-center">
            <Icon name="twitter" size={18} />
          </div>
          <div>
            <div className="font-semibold text-sm">@{xStatus.username}</div>
            <div className="text-xs text-tx3 font-mono mt-0.5">Connected · ready to publish</div>
          </div>
          <div className="ml-auto">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-pill bg-tx/10 text-tx border border-tx/20 text-xs font-mono uppercase tracking-wider">
              <div className="w-1.5 h-1.5 rounded-full bg-tx" />
              Connected
            </div>
          </div>
        </div>
      ) : (
        <div className="p-5 border border-border rounded-xl flex items-center gap-4">
          <div className="w-10 h-10 rounded-full bg-surface2 border border-border flex items-center justify-center">
            <Icon name="twitter" size={18} />
          </div>
          <div>
            <div className="font-semibold text-sm">X / Twitter</div>
            <div className="text-xs text-tx3 mt-0.5">Not connected</div>
          </div>
          <div className="ml-auto">
            <button
              onClick={() => connect()}
              disabled={isConnecting}
              className="flex items-center gap-2 h-9 px-4 rounded-pill bg-tx text-bg font-semibold text-sm hover:bg-tx/90 transition-all disabled:opacity-50"
            >
              {isConnecting ? <Spinner size={13} /> : <Icon name="twitter" size={13} />}
              Connect
            </button>
          </div>
        </div>
      )}

      <div className="mt-4 px-4 py-3 border border-border rounded-xl bg-surface2 text-xs text-tx3 flex gap-3">
        <Icon name="info" size={13} className="shrink-0 mt-0.5" />
        <span>You can connect or disconnect your X account anytime from Settings.</span>
      </div>

      <div className="mt-8 flex items-center justify-between">
        <button
          onClick={onBack}
          className="flex items-center gap-2 h-9 px-4 rounded-lg border border-border text-[13px] text-tx3 hover:bg-surface2 hover:text-tx transition-all"
        >
          <Icon name="arrow-left" size={13} /> Back
        </button>
        <button
          onClick={onFinish}
          className="flex items-center gap-2 h-9 px-5 rounded-lg bg-tx text-bg font-semibold text-[13px] hover:bg-tx/90 transition-all"
        >
          {xStatus?.connected ? 'Go to Dashboard' : 'Skip for now'} <Icon name="arrow-right" size={13} />
        </button>
      </div>
    </div>
  )
}

// ── Shared ────────────────────────────────────────────────────────────

function Field({
  label, placeholder, desc, value, onChange,
}: {
  label: string
  placeholder: string
  desc: string
  value: string
  onChange: (v: string) => void
}) {
  return (
    <div className="flex flex-col gap-1.5">
      <label className="text-xs font-mono text-tx3 uppercase tracking-wider">{label}</label>
      <input
        placeholder={placeholder}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full bg-surface border border-border rounded-xl px-4 py-3 text-sm text-tx placeholder:text-tx4 outline-none focus:border-border2 transition-colors"
      />
      <div className="text-xs text-tx4">{desc}</div>
    </div>
  )
}
