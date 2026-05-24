import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { media } from '../lib/api'

export function useMediaAssets(draftId: string | undefined) {
  return useQuery({
    queryKey: ['media', draftId],
    queryFn: () => media.list(draftId!),
    enabled: !!draftId,
  })
}

export function useGenerateImage(draftId: string | undefined) {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: (payload: {
      prompt: string
      style?: string
      aspect_ratio?: string
    }) =>
      media.generateImage({
        draft_id: draftId,
        ...payload,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['media', draftId] })
    },
  })
}
