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
  const qc = useQueryClient()
  return useMutation({
    mutationFn: () => xapi.connect(),
    onSuccess: (data) => {
      const popup = window.open(data.authorization_url, '_blank', 'width=600,height=700')
      // Poll until the popup closes or the account becomes connected
      const poll = setInterval(async () => {
        try {
          const status = await xapi.status()
          if (status.connected) {
            clearInterval(poll)
            popup?.close()
            qc.invalidateQueries({ queryKey: ['x-status'] })
          }
        } catch {
          // ignore poll errors
        }
        if (popup?.closed) {
          clearInterval(poll)
          qc.invalidateQueries({ queryKey: ['x-status'] })
        }
      }, 1500)
      // Stop polling after 2 minutes regardless
      setTimeout(() => clearInterval(poll), 120_000)
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
