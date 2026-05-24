import { useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { AppShell } from '../components/layout/AppShell'
import { Topbar } from '../components/layout/Topbar'
import { Icon } from '../components/common/Icon'
import { Spinner } from '../components/common/Spinner'
import { useCreateProject } from '../hooks/useProjects'
import { ApiError } from '../lib/api'
import type { DraftType } from '../types/models'

const GOALS = [
  { id: 'educate',         label: 'Educate',                  desc: 'Share knowledge and explain a concept' },
  { id: 'provoke',         label: 'Challenge an assumption',   desc: 'Offer a contrarian or surprising take' },
  { id: 'launch',          label: 'Launch something',          desc: 'Announce a product, feature, or idea' },
  { id: 'summarize',       label: 'Summarize research',        desc: 'Distill a paper, report, or set of findings' },
  { id: 'build_authority', label: 'Build authority',           desc: 'Establish expert positioning in your space' },
]

const FORMATS: { id: DraftType; label: string; desc: string; icon: string }[] = [
  { id: 'text_post',        label: 'Text Post',       desc: 'Single sharp post, ≤280 chars',   icon: 'edit' },
  { id: 'thread',           label: 'Thread',          desc: 'Multi-post reply chain',           icon: 'traces' },
  { id: 'quote_post',       label: 'Quote Post',      desc: 'Response to an existing X post',   icon: 'rt' },
  { id: 'image_post',       label: 'Image Post',      desc: 'Post with generated visual card',  icon: 'image' },
  { id: 'carousel_post',    label: 'Carousel',        desc: 'Set of up to 4 images',            icon: 'lib' },
  { id: 'gif_post',         label: 'GIF',             desc: 'Animated media post',              icon: 'spark' },
  { id: 'voice_video_post', label: 'Voice Video',     desc: 'TTS narration → MP4 for X',       icon: 'voice' },
  { id: 'video_post',       label: 'Video',           desc: 'Captioned MP4 video post',         icon: 'video' },
  { id: 'research_article', label: 'Research Article',desc: 'Long-form research breakdown',     icon: 'search' },
]

export function ProjectWizardPage() {
  const navigate = useNavigate()
  const { mutateAsync: createProject, isPending } = useCreateProject()

  const [title, setTitle] = useState('')
  const [topic, setTopic] = useState('')
  const [goal, setGoal] = useState('')
  const [audience, setAudience] = useState('')
  const [format, setFormat] = useState<DraftType>('thread')
  const [error, setError] = useState('')
  const [step, setStep] = useState(1)

  const handleNext = () => {
    if (step === 1 && !title.trim()) { setError('Title is required.'); return }
    if (step === 1 && !topic.trim()) { setError('Topic is required.'); return }
    setError('')
    setStep((s) => s + 1)
  }

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      const project = await createProject({
        title: title.trim(),
        topic: topic.trim(),
        goal: goal || undefined,
        target_audience: audience.trim() || undefined,
      })
      navigate(`/projects/${project.id}`, { state: { preferredFormat: format } })
    } catch (err) {
      if (err instanceof ApiError) setError(err.message)
      else setError('Failed to create project.')
    }
  }

  return (
    <AppShell
      topbar={
        <Topbar
          breadcrumbs={[
            { label: 'Projects', to: '/projects' },
            { label: 'New Project' },
          ]}
        />
      }
    >
      <div className="max-w-[700px] mx-auto px-9 py-12">
        {/* Step indicator */}
        <div className="flex items-center gap-2 mb-8 font-mono text-[11px] text-tx4">
          {['Input', 'Goal', 'Format'].map((s, i) => (
            <span
              key={i}
              className={`flex items-center gap-2 ${i + 1 <= step ? 'text-tx' : 'text-tx4'}`}
            >
              {i > 0 && <span className="text-tx4">→</span>}
              <span className={i + 1 === step ? 'font-semibold' : ''}>{s}</span>
            </span>
          ))}
        </div>

        {error && (
          <div className="mb-6 px-4 py-3 border border-red-900/50 bg-red-900/10 rounded-xl text-red-400 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Step 1: Input */}
          {step === 1 && (
            <div className="flex flex-col gap-6">
              <div>
                <h1 className="text-3xl font-semibold tracking-[-0.02em] mb-2">
                  What do you want to create?
                </h1>
                <p className="text-tx2 text-sm">
                  Give the system a topic and title. Everything else is generated.
                </p>
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-mono text-tx3 uppercase tracking-wider">
                  Project Title
                </label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Why distribution is the new moat"
                  className="w-full bg-surface border border-border rounded-xl px-4 py-3 text-sm text-tx placeholder:text-tx4 outline-none focus:border-border2 transition-colors"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-mono text-tx3 uppercase tracking-wider">
                  Topic / Thesis
                </label>
                <textarea
                  value={topic}
                  onChange={(e) => setTopic(e.target.value)}
                  placeholder="The core idea, argument, or question you want to explore..."
                  rows={4}
                  className="w-full bg-surface border border-border rounded-xl px-4 py-3 text-sm text-tx placeholder:text-tx4 outline-none focus:border-border2 transition-colors resize-none"
                />
              </div>

              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-mono text-tx3 uppercase tracking-wider">
                  Target Audience (optional)
                </label>
                <input
                  type="text"
                  value={audience}
                  onChange={(e) => setAudience(e.target.value)}
                  placeholder="e.g. Founders, operators, technical investors"
                  className="w-full bg-surface border border-border rounded-xl px-4 py-3 text-sm text-tx placeholder:text-tx4 outline-none focus:border-border2 transition-colors"
                />
              </div>

              <button
                type="button"
                onClick={handleNext}
                className="flex items-center gap-2 h-11 px-6 rounded-pill bg-tx text-bg font-semibold text-sm hover:bg-tx/90 transition-all self-start"
              >
                Next <Icon name="arrow-right" size={14} />
              </button>
            </div>
          )}

          {/* Step 2: Goal */}
          {step === 2 && (
            <div className="flex flex-col gap-6">
              <div>
                <h1 className="text-3xl font-semibold tracking-[-0.02em] mb-2">
                  What is the goal?
                </h1>
                <p className="text-tx2 text-sm">
                  This shapes the angle selection and writing style.
                </p>
              </div>

              <div className="flex flex-col border-t border-l border-border">
                {GOALS.map((g) => (
                  <div
                    key={g.id}
                    className={`px-6 py-5 border-b border-r border-border cursor-pointer transition-all ${
                      goal === g.id ? 'bg-tx text-bg' : 'hover:bg-surface2'
                    }`}
                    onClick={() => setGoal(g.id)}
                  >
                    <div className={`font-semibold text-base ${goal === g.id ? 'text-bg' : 'text-tx'}`}>
                      {g.label}
                    </div>
                    <div className={`text-sm mt-1 ${goal === g.id ? 'text-bg/70' : 'text-tx2'}`}>
                      {g.desc}
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="flex items-center gap-2 h-11 px-6 rounded-pill border border-border2 text-tx2 text-sm hover:bg-surface2 transition-all"
                >
                  <Icon name="arrow-left" size={14} /> Back
                </button>
                <button
                  type="button"
                  onClick={() => setStep(3)}
                  className="flex items-center gap-2 h-11 px-6 rounded-pill bg-tx text-bg font-semibold text-sm hover:bg-tx/90 transition-all"
                >
                  Next <Icon name="arrow-right" size={14} />
                </button>
              </div>
            </div>
          )}

          {/* Step 3: Format */}
          {step === 3 && (
            <div className="flex flex-col gap-6">
              <div>
                <h1 className="text-3xl font-semibold tracking-[-0.02em] mb-2">
                  Preferred format
                </h1>
                <p className="text-tx2 text-sm">
                  The AI will confirm the best format after research. This is your starting preference.
                </p>
              </div>

              <div className="grid grid-cols-2 gap-0 border-t border-l border-border">
                {FORMATS.map((f) => (
                  <div
                    key={f.id}
                    className={`px-5 py-4 border-b border-r border-border cursor-pointer transition-all flex items-start gap-3 ${
                      format === f.id ? 'bg-tx text-bg' : 'hover:bg-surface2'
                    }`}
                    onClick={() => setFormat(f.id)}
                  >
                    <Icon
                      name={f.icon}
                      size={16}
                      stroke={format === f.id ? '#000' : 'currentColor'}
                      className="mt-0.5 shrink-0"
                    />
                    <div>
                      <div className={`font-semibold text-sm ${format === f.id ? 'text-bg' : 'text-tx'}`}>
                        {f.label}
                      </div>
                      <div className={`text-xs mt-0.5 ${format === f.id ? 'text-bg/70' : 'text-tx3'}`}>
                        {f.desc}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex items-center gap-3">
                <button
                  type="button"
                  onClick={() => setStep(2)}
                  className="flex items-center gap-2 h-11 px-6 rounded-pill border border-border2 text-tx2 text-sm hover:bg-surface2 transition-all"
                >
                  <Icon name="arrow-left" size={14} /> Back
                </button>
                <button
                  type="submit"
                  disabled={isPending}
                  className="flex items-center gap-2 h-11 px-6 rounded-pill bg-tx text-bg font-semibold text-sm hover:bg-tx/90 transition-all disabled:opacity-50"
                >
                  {isPending ? <Spinner size={16} /> : (
                    <>
                      Create Project <Icon name="rocket" size={14} />
                    </>
                  )}
                </button>
              </div>
            </div>
          )}
        </form>
      </div>
    </AppShell>
  )
}
