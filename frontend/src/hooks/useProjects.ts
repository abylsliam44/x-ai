import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { projects } from '../lib/api'
import type { AngleOption, DraftType, ProjectCreate } from '../types/models'

export function useProjects() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: () => projects.list(50),
  })
}

export function useProject(id: string | undefined) {
  return useQuery({
    queryKey: ['project', id],
    queryFn: () => projects.get(id!),
    enabled: !!id,
  })
}

export function useCreateProject() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (data: ProjectCreate) => projects.create(data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['projects'] })
    },
  })
}

export function useGenerateAngles(projectId: string | undefined) {
  return useMutation({
    mutationFn: ({
      count,
      context,
    }: {
      count?: number
      context?: string
    }) => projects.generateAngles(projectId!, count, context),
  })
}

export function useGenerateDraft(projectId: string | undefined) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: ({
      type,
      angle,
      instructions,
    }: {
      type: DraftType
      angle?: AngleOption
      instructions?: string
    }) =>
      projects.generateDraft(projectId!, type, angle, instructions),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['project', projectId] })
    },
  })
}

export function useProjectTraces(projectId: string | undefined) {
  return useQuery({
    queryKey: ['project-traces', projectId],
    queryFn: () => projects.traces(projectId!),
    enabled: !!projectId,
    refetchInterval: 5000,
  })
}
