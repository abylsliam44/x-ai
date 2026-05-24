import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { drafts, traces } from '../lib/api'

export function useDraft(id: string | undefined) {
  return useQuery({
    queryKey: ['draft', id],
    queryFn: () => drafts.get(id!),
    enabled: !!id,
  })
}

export function useReviseDraft(draftId: string | undefined) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (instructions: string) =>
      drafts.revise(draftId!, instructions),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['draft', draftId] })
    },
  })
}

export function useFactCheck(draftId: string | undefined) {
  return useMutation({
    mutationFn: () => drafts.factCheck(draftId!),
  })
}

export function useApproveDraft(draftId: string | undefined) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (note?: string) => drafts.approve(draftId!, note),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['draft', draftId] })
    },
  })
}

export function usePublishDraft(draftId: string | undefined) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (scheduled_at?: string) =>
      drafts.publish(draftId!, scheduled_at),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['draft', draftId] })
    },
  })
}

export function useDraftTraces(draftId: string | undefined) {
  return useQuery({
    queryKey: ['draft-traces', draftId],
    queryFn: () => traces.forDraft(draftId!),
    enabled: !!draftId,
  })
}
