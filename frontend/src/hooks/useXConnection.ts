import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { xapi } from '../lib/api'

export function useXStatus() {
  return useQuery({
    queryKey: ['x-status'],
    queryFn: () => xapi.status(),
    staleTime: 30_000,
    retry: false,
  })
}

export function useXConnect() {
  return useMutation({
    mutationFn: () => xapi.connect(),
    onSuccess: (data) => {
      window.open(data.authorization_url, '_blank', 'width=600,height=700')
    },
  })
}

export function useXDisconnect() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => xapi.disconnect(),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['x-status'] })
    },
  })
}
