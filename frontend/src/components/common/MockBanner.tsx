import { useQuery } from '@tanstack/react-query'
import { health } from '../../lib/api'
import { Icon } from './Icon'

export function MockBanner() {
  const { data } = useQuery({
    queryKey: ['health'],
    queryFn: () => health.get(),
    staleTime: 60_000,
    retry: false,
  })

  if (!data?.mock_mode) return null

  return (
    <div className="flex items-center gap-2 px-4 py-2 bg-surface2 border-b border-border text-tx3 text-xs font-mono">
      <Icon name="info" size={12} />
      Mock Mode Active — external AI, media, and X APIs are simulated.
    </div>
  )
}
