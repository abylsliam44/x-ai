// API response types matching backend schemas

export interface User {
  id: string
  email: string
  full_name: string | null
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface TokenResponse {
  access_token: string
  expires_in: number
}

export interface HealthResponse {
  status: string
  version: string
  mock_mode: boolean
}

export interface Page<T> {
  items: T[]
  total: number
  limit: number
  offset: number
}

export interface ProjectRead {
  id: string
  user_id: string
  title: string
  topic: string
  goal: string | null
  target_audience: string | null
  status: string
  created_at: string
  updated_at: string
}

export interface ProjectCreate {
  title: string
  topic: string
  goal?: string
  target_audience?: string
}

export type DraftType =
  | 'text_post'
  | 'thread'
  | 'quote_post'
  | 'image_post'
  | 'carousel_post'
  | 'gif_post'
  | 'voice_video_post'
  | 'video_post'
  | 'research_article'

export type DraftStatus =
  | 'draft'
  | 'ready_for_review'
  | 'approved'
  | 'scheduled'
  | 'published'
  | 'rejected'

export interface DraftRead {
  id: string
  project_id: string
  user_id: string
  type: DraftType
  title: string | null
  text: string | null
  thread_items: Record<string, unknown>[] | null
  status: DraftStatus
  quality_score: number | null
  style_score: number | null
  fact_check_score: number | null
  scheduled_at: string | null
  published_at: string | null
  x_post_id: string | null
  created_at: string
  updated_at: string
}

export interface AngleOption {
  title: string
  thesis: string
  hook: string
  rationale: string
}

export interface GenerateAnglesResponse {
  angles: AngleOption[]
}

export interface AgentTraceRead {
  id: string
  project_id: string | null
  draft_id: string | null
  agent_name: string
  step_name: string | null
  input: Record<string, unknown> | null
  output: Record<string, unknown> | null
  model: string | null
  tokens_input: number | null
  tokens_output: number | null
  latency_ms: number | null
  status: string
  error_message: string | null
  created_at: string
}

export interface FactCheckReportItem {
  claim: string
  verdict: 'supported' | 'weakly_supported' | 'contradicted' | 'unverifiable'
  confidence: number
  evidence: Record<string, unknown>[] | null
  suggested_fix: string | null
}

export interface FactCheckResponse {
  draft_id: string
  overall_score: number
  items: FactCheckReportItem[]
}

export interface WritingSampleRead {
  id: string
  user_id: string
  title: string | null
  source_type: string
  text: string
  meta: Record<string, unknown> | null
  created_at: string
}

export interface SourceRead {
  id: string
  project_id: string | null
  source_type: string
  title: string | null
  url: string | null
  author: string | null
  raw_text: string | null
  trust_level: number
  meta: Record<string, unknown> | null
  created_at: string
}

export interface XStatusResponse {
  connected: boolean
  account_id: string | null
  username: string | null
  x_user_id: string | null
  connected_at: string | null
  scopes: string[]
}

export interface XConnectResponse {
  authorization_url: string
  state: string
  mock: boolean
}

export interface PublishJobRead {
  id: string
  draft_id: string
  user_id: string
  platform: string
  status: string
  scheduled_at: string | null
  attempts: number
  error_message: string | null
  result: Record<string, unknown> | null
  created_at: string
  updated_at: string
}
