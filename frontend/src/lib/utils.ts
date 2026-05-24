import { formatDistanceToNow, format } from 'date-fns'

export function relativeTime(date: string): string {
  try {
    return formatDistanceToNow(new Date(date), { addSuffix: true })
  } catch {
    return date
  }
}

export function formatDate(date: string): string {
  try {
    return format(new Date(date), 'MMM d, yyyy')
  } catch {
    return date
  }
}

export function formatDateTime(date: string): string {
  try {
    return format(new Date(date), 'MMM d, yyyy · HH:mm')
  } catch {
    return date
  }
}

export function statusColor(status: string): string {
  switch (status) {
    case 'approved':
    case 'published':
    case 'done':
    case 'completed':
      return 'text-white bg-white/10'
    case 'ready_for_review':
    case 'running':
      return 'text-tx2'
    case 'draft':
    case 'pending':
    case 'queued':
      return 'text-tx3'
    case 'failed':
    case 'rejected':
    case 'error':
      return 'text-red-400'
    default:
      return 'text-tx3'
  }
}

export function statusLabel(status: string): string {
  return status
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (c) => c.toUpperCase())
}

export function draftTypeLabel(type: string): string {
  const map: Record<string, string> = {
    text_post: 'Text Post',
    thread: 'Thread',
    quote_post: 'Quote Post',
    image_post: 'Image Post',
    carousel_post: 'Carousel',
    gif_post: 'GIF',
    voice_video_post: 'Voice Video',
    video_post: 'Video',
    research_article: 'Research Article',
  }
  return map[type] ?? type
}

export function clamp(n: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, n))
}

export function cn(...classes: (string | false | null | undefined)[]): string {
  return classes.filter(Boolean).join(' ')
}
