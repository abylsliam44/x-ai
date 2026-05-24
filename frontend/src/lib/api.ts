import type {
  AgentTraceRead,
  AngleOption,
  DraftRead,
  DraftType,
  FactCheckResponse,
  GenerateAnglesResponse,
  HealthResponse,
  MediaRead,
  Page,
  ProjectCreate,
  ProjectRead,
  PublishJobRead,
  SourceRead,
  TokenResponse,
  User,
  WritingSampleRead,
  XConnectResponse,
  XStatusResponse,
} from '../types/models'

const rawBase = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/+$/, '')
const BASE = rawBase.endsWith('/api') ? rawBase.slice(0, -4) : rawBase
const API = `${BASE}/api/v1`

export function assetUrl(url: string | null | undefined): string {
  if (!url) return ''
  if (/^https?:\/\//i.test(url)) return url
  if (url.startsWith('/static/') && BASE) return `${BASE}${url}`
  return url
}

function getToken(): string | null {
  return localStorage.getItem('token')
}

class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function request<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> | undefined),
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  let res: Response
  try {
    res = await fetch(`${API}${path}`, { ...options, headers })
  } catch {
    throw new ApiError(0, 'network_error', 'Backend is offline or unreachable')
  }

  if (res.status === 204) return undefined as T

  let body: unknown
  try {
    body = await res.json()
  } catch {
    body = {}
  }

  if (!res.ok) {
    const err = body as { error?: { code?: string; message?: string } | string }
    const errObj = typeof err.error === 'object' ? err.error : null
    const code = errObj?.code ?? 'api_error'
    const message = errObj?.message ?? (typeof err.error === 'string' ? err.error : `HTTP ${res.status}`)
    if (res.status === 401) {
      localStorage.removeItem('token')
    }
    throw new ApiError(res.status, code, message)
  }

  return body as T
}

// ── Auth ──────────────────────────────────────────────────────────────

export const auth = {
  register: (email: string, password: string, full_name: string) =>
    request<TokenResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name }),
    }),

  login: (email: string, password: string) =>
    request<TokenResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  me: () => request<User>('/users/me'),
}

// ── Health ────────────────────────────────────────────────────────────

export const health = {
  get: () => request<HealthResponse>('/health'),
}

// ── Media ─────────────────────────────────────────────────────────────

export const media = {
  list: (draftId?: string, limit = 50) => {
    const params = new URLSearchParams({ limit: String(limit) })
    if (draftId) params.set('draft_id', draftId)
    return request<MediaRead[]>(`/media?${params.toString()}`)
  },

  generateImage: (data: {
    draft_id?: string
    prompt: string
    style?: string
    aspect_ratio?: string
  }) =>
    request<MediaRead>('/media/generate-image', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
}

// ── Projects ──────────────────────────────────────────────────────────

export const projects = {
  list: (limit = 20, offset = 0) =>
    request<Page<ProjectRead>>(`/projects?limit=${limit}&offset=${offset}`),

  get: (id: string) => request<ProjectRead>(`/projects/${id}`),

  create: (data: ProjectCreate) =>
    request<ProjectRead>('/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  update: (id: string, data: Partial<ProjectCreate & { status: string }>) =>
    request<ProjectRead>(`/projects/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  generateAngles: (
    id: string,
    count = 5,
    additional_context?: string,
  ) =>
    request<GenerateAnglesResponse>(`/projects/${id}/generate-angles`, {
      method: 'POST',
      body: JSON.stringify({ count, additional_context }),
    }),

  generateDraft: (
    id: string,
    type: DraftType,
    angle?: AngleOption,
    additional_instructions?: string,
    include_media = false,
    media_preferences?: Record<string, unknown>,
  ) =>
    request<DraftRead>(`/projects/${id}/generate-draft`, {
      method: 'POST',
      body: JSON.stringify({
        type,
        angle,
        additional_instructions,
        include_media,
        media_preferences,
      }),
    }),

  traces: (id: string, limit = 50) =>
    request<Page<AgentTraceRead>>(`/projects/${id}/traces?limit=${limit}`),
}

// ── Drafts ────────────────────────────────────────────────────────────

export const drafts = {
  get: (id: string) => request<DraftRead>(`/drafts/${id}`),

  revise: (id: string, instructions: string, keep_structure = true) =>
    request<DraftRead>(`/drafts/${id}/revise`, {
      method: 'POST',
      body: JSON.stringify({ instructions, keep_structure }),
    }),

  factCheck: (id: string) =>
    request<FactCheckResponse>(`/drafts/${id}/fact-check`, { method: 'POST' }),

  approve: (id: string, note?: string) =>
    request<DraftRead>(`/drafts/${id}/approve`, {
      method: 'POST',
      body: JSON.stringify({ note }),
    }),

  publish: (id: string, scheduled_at?: string) =>
    request<PublishJobRead>(`/drafts/${id}/publish`, {
      method: 'POST',
      body: JSON.stringify({ scheduled_at }),
    }),

  schedulePublish: (id: string, scheduled_at: string) =>
    request<PublishJobRead>(`/drafts/${id}/schedule-publish`, {
      method: 'POST',
      body: JSON.stringify({ scheduled_at }),
    }),
}

// ── RAG ───────────────────────────────────────────────────────────────

export const rag = {
  listWritingSamples: (limit = 20) =>
    request<Page<WritingSampleRead>>(`/rag/writing-samples?limit=${limit}`),

  createWritingSample: (title: string, text: string, source_type = 'paste') =>
    request<WritingSampleRead>('/rag/writing-samples', {
      method: 'POST',
      body: JSON.stringify({ title, text, source_type }),
    }),

  listSources: (limit = 20) =>
    request<Page<SourceRead>>(`/rag/sources?limit=${limit}`),

  createSource: (data: {
    project_id?: string
    source_type?: string
    title?: string
    url?: string
    author?: string
    raw_text?: string
    trust_level?: number
  }) =>
    request<SourceRead>('/rag/sources', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
}

// ── X / Twitter ───────────────────────────────────────────────────────

export const xapi = {
  status: () => request<XStatusResponse>('/x/status'),

  connect: () => request<XConnectResponse>('/x/connect'),

  disconnect: () =>
    request<void>('/x/disconnect', { method: 'DELETE' }),
}

// ── Traces ────────────────────────────────────────────────────────────

export const traces = {
  forDraft: (draftId: string, limit = 50) =>
    request<Page<AgentTraceRead>>(`/traces/draft/${draftId}?limit=${limit}`),

  forProject: (projectId: string, limit = 50) =>
    projects.traces(projectId, limit),
}

// ── Publish Jobs ──────────────────────────────────────────────────────

export const publishJobs = {
  list: () => request<Page<PublishJobRead>>('/publish/jobs'),
  get: (id: string) => request<PublishJobRead>(`/publish/jobs/${id}`),
}

export { ApiError }
