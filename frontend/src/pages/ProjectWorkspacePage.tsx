import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { AppShell } from '../components/layout/AppShell'
import { Topbar } from '../components/layout/Topbar'
import { Icon } from '../components/common/Icon'
import { Spinner } from '../components/common/Spinner'
import { StageNav, type StageId } from '../components/workflow/StageNav'
import { StageSources } from '../components/workflow/StageSources'
import { StageAngles } from '../components/workflow/StageAngles'
import { StageDraft } from '../components/workflow/StageDraft'
import { StageReview } from '../components/workflow/StageReview'
import { StagePublish } from '../components/workflow/StagePublish'
import { useProject, useGenerateAngles, useGenerateDraft } from '../hooks/useProjects'
import { useReviseDraft, useApproveDraft } from '../hooks/useDrafts'
import { ApiError } from '../lib/api'
import type { AngleOption, DraftRead, DraftType } from '../types/models'

export function ProjectWorkspacePage() {
  const { id } = useParams<{ id: string }>()

  const [stage, setStage] = useState<StageId>('sources')
  const [angles, setAngles] = useState<AngleOption[]>([])
  const [selectedAngle, setSelectedAngle] = useState<AngleOption | null>(null)
  const [draft, setDraft] = useState<DraftRead | null>(null)
  const [error, setError] = useState('')
  const [completedStages, setCompletedStages] = useState<Set<StageId>>(new Set())

  const { data: project, isLoading } = useProject(id)
  const { mutateAsync: generateAngles, isPending: isGeneratingAngles } = useGenerateAngles(id)
  const { mutateAsync: generateDraft, isPending: isGeneratingDraft } = useGenerateDraft(id)
  const { mutateAsync: reviseDraft, isPending: isRevising } = useReviseDraft(draft?.id)
  const { mutateAsync: approveDraft, isPending: isApproving } = useApproveDraft(draft?.id)

  const markComplete = (s: StageId) =>
    setCompletedStages((prev) => new Set([...prev, s]))

  const handleGenerateAngles = async (count?: number, context?: string) => {
    setError('')
    try {
      const res = await generateAngles({ count, context })
      setAngles(res.angles)
      markComplete('sources')
      setStage('angles')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to generate angles.')
    }
  }

  const handleGenerateDraft = async (type: DraftType, angle: AngleOption | null, instructions?: string) => {
    setError('')
    try {
      const res = await generateDraft({ type, angle: angle ?? undefined, instructions: instructions ?? undefined })
      setDraft(res)
      markComplete('angles')
      setStage('draft')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to generate draft.')
    }
  }

  const handleRevise = async (instructions: string) => {
    setError('')
    try {
      const res = await reviseDraft(instructions)
      setDraft(res)
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to revise draft.')
    }
  }

  const handleApprove = async () => {
    setError('')
    try {
      const res = await approveDraft(undefined)
      setDraft(res)
      markComplete('review')
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Failed to approve draft.')
    }
  }

  if (isLoading) {
    return (
      <AppShell topbar={<Topbar breadcrumbs={[{ label: 'Projects', to: '/projects' }, { label: 'Loading…' }]} />}>
        <div className="flex justify-center pt-20"><Spinner size={24} /></div>
      </AppShell>
    )
  }

  if (!project) {
    return (
      <AppShell topbar={<Topbar breadcrumbs={[{ label: 'Projects', to: '/projects' }, { label: 'Not Found' }]} />}>
        <div className="flex justify-center pt-20 text-tx3">Project not found.</div>
      </AppShell>
    )
  }

  return (
    <AppShell
      topbar={
        <Topbar
          breadcrumbs={[
            { label: 'Projects', to: '/projects' },
            { label: project.title },
          ]}
          chip={draft ? 'Draft in progress' : 'Research'}
          actions={
            <div className="flex items-center gap-2">
              {angles.length === 0 && (
                <button
                  className="flex items-center gap-2 h-9 px-4 rounded-pill border border-border2 text-sm text-tx hover:bg-surface2 transition-all disabled:opacity-50"
                  onClick={() => handleGenerateAngles(5)}
                  disabled={isGeneratingAngles}
                >
                  {isGeneratingAngles ? <Spinner size={14} /> : <Icon name="spark" size={14} />}
                  Generate Angles
                </button>
              )}
              {draft && draft.status !== 'approved' && (
                <button
                  className="flex items-center gap-2 h-9 px-4 rounded-pill border border-border2 text-sm text-tx hover:bg-surface2 transition-all disabled:opacity-50"
                  onClick={handleApprove}
                  disabled={isApproving}
                >
                  {isApproving ? <Spinner size={14} /> : <Icon name="check" size={14} />}
                  Approve
                </button>
              )}
              {draft?.status === 'approved' && (
                <button
                  className="flex items-center gap-2 h-9 px-4 rounded-pill bg-tx text-bg font-semibold text-sm hover:bg-tx/90 transition-all"
                  onClick={() => setStage('publish')}
                >
                  <Icon name="rocket" size={14} /> Publish
                </button>
              )}
            </div>
          }
        />
      }
    >
      <div className="max-w-[1100px] mx-auto px-9 py-9 pb-24">
        {/* Project header */}
        <div className="mb-9">
          <div className="flex items-center gap-3 mb-3 font-mono text-[11px] uppercase tracking-[0.22em] text-tx3">
            <span className="pulse-dot" />
            <span>
              {draft ? `${draft.type.replace(/_/g, ' ')} · ${draft.status}` : 'Research in progress'}
            </span>
          </div>
          <h1 className="text-[40px] font-semibold tracking-[-0.025em] leading-[1.1] max-w-[880px]">
            {project.title}
          </h1>
          <p className="text-tx2 text-base mt-4 max-w-[720px] leading-relaxed">
            {project.topic}
          </p>
          {project.goal && (
            <div className="mt-3 font-mono text-[12px] text-tx3">
              Goal: {project.goal.replace(/_/g, ' ')}
              {project.target_audience && ` · ${project.target_audience}`}
            </div>
          )}
        </div>

        {/* Error banner */}
        {error && (
          <div className="mb-6 px-4 py-3 border border-red-900/50 bg-red-900/10 rounded-xl text-red-400 text-sm flex items-center gap-2">
            <Icon name="warning" size={14} />
            {error}
            <button className="ml-auto text-red-400/70 hover:text-red-400" onClick={() => setError('')}>
              <Icon name="x" size={14} />
            </button>
          </div>
        )}

        {/* Stage nav */}
        <StageNav active={stage} onPick={setStage} completed={completedStages} />

        {/* Stage content */}
        {stage === 'sources' && (
          <div>
            <StageSources projectId={project.id} />
            <div className="mt-8 pt-6 border-t border-border">
              <button
                className="flex items-center gap-2 h-10 px-5 rounded-pill bg-tx text-bg font-semibold text-sm hover:bg-tx/90 transition-all disabled:opacity-50"
                onClick={() => handleGenerateAngles(5)}
                disabled={isGeneratingAngles}
              >
                {isGeneratingAngles ? <Spinner size={14} /> : <Icon name="spark" size={14} />}
                {isGeneratingAngles ? 'Generating Angles…' : 'Generate Angles →'}
              </button>
            </div>
          </div>
        )}

        {stage === 'insights' && (
          <div className="py-10 text-center text-tx3 text-sm">
            <div className="font-mono text-[11px] uppercase tracking-wider mb-3">Insights</div>
            <p className="text-tx2">
              Generate angles to extract non-obvious insights from your research sources.
            </p>
            <button
              className="mt-6 flex items-center gap-2 h-10 px-5 rounded-pill bg-tx text-bg font-semibold text-sm hover:bg-tx/90 transition-all disabled:opacity-50 mx-auto"
              onClick={() => handleGenerateAngles(5)}
              disabled={isGeneratingAngles}
            >
              {isGeneratingAngles ? <Spinner size={14} /> : <Icon name="spark" size={14} />}
              Generate Angles to Extract Insights
            </button>
          </div>
        )}

        {stage === 'angles' && (
          <StageAngles
            projectId={project.id}
            angles={angles}
            selectedAngle={selectedAngle}
            onSelect={(a) => {
              setSelectedAngle(a)
            }}
            onGenerate={handleGenerateAngles}
            isGenerating={isGeneratingAngles}
          />
        )}

        {stage === 'draft' && (
          <StageDraft
            projectId={project.id}
            draft={draft}
            selectedAngle={selectedAngle}
            onGenerate={handleGenerateDraft}
            onRevise={handleRevise}
            onApprove={handleApprove}
            isGenerating={isGeneratingDraft}
            isRevising={isRevising}
            isApproving={isApproving}
          />
        )}

        {stage === 'review' && (
          <StageReview
            draft={draft}
            onApprove={handleApprove}
            isApproving={isApproving}
          />
        )}

        {stage === 'publish' && (
          <StagePublish draft={draft} />
        )}
      </div>
    </AppShell>
  )
}
