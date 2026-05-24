# Agentic X Content Platform — архитектура, логика и UI/UX

> Документ написан на русском языке для проектирования и разработки через Claude Code.  
> **Важно:** сама платформа, весь пользовательский интерфейс, названия кнопок, меню, статусы, empty states, сообщения об ошибках и onboarding-тексты должны быть **только на английском языке**.

---

## 1. Суть продукта

Платформа — это AI-native система для создания качественного контента для X/Twitter.

Главная задача — не просто генерировать посты, а помогать пользователю проходить полный цикл:

```text
Idea / Topic / Link / File / Voice Note
        ↓
Research & Source Grounding
        ↓
Insight Extraction
        ↓
Angle / Thesis Generation
        ↓
Draft Generation
        ↓
Fact-checking + Style Review
        ↓
Human Approval
        ↓
Publish / Schedule / Export
```

Система должна помогать создавать **все основные виды контента, которые реально можно довести до публикации в X/Twitter через API или через поддерживаемый media workflow**:

- text posts;
- X threads;
- quote retweet drafts / quote-style responses;
- image posts;
- visual cards;
- carousel-style image sets;
- GIF-ready posts, если используется готовый GIF или сгенерированная анимация;
- video posts;
- narrated video posts: голос + captions + visual background;
- voice-note-to-post: пользователь диктует идею, система превращает ее в текстовый пост или видео;
- research-style breakdowns;
- essays and strategic narratives.

Важно: если X API не поддерживает отдельный формат как самостоятельный тип публикации, система должна преобразовать его в поддерживаемый формат. Например, голосовой контент публикуется не как отдельный audio-only post, а как короткое MP4-видео с озвучкой, субтитрами и визуальным фоном.

Ключевое отличие от обычного AI wrapper: система должна показывать мышление, источники, агентные шаги, критику качества, процесс улучшения текста и полный путь от идеи до публикации в X.

---

## 2. Product principles

### 2.1. Не AI slop

Платформа не должна генерировать generic контент уровня:

```text
AI is transforming the world. Businesses must adapt.
```

Хороший результат должен иметь:

- конкретную мысль;
- сильный тезис;
- контекст;
- авторскую позицию;
- ясный ритм;
- минимум воды;
- проверяемые факты;
- натуральный стиль.

Пример хорошего результата:

```text
The bottleneck in AI coding is no longer code generation.
It is judgment.

The best engineers will not be the fastest typists.
They will be the people who can define the right problem, constrain the agent, review the output, and know when the answer is subtly wrong.
```

### 2.2. Human-in-the-loop by default

По умолчанию система не публикует контент сама.

Базовый безопасный workflow:

```text
Generate → Review → Approve → Publish
```

Autopilot mode можно добавить позже, но он должен быть явно включаемым режимом с лимитами, расписанием, правилами качества и журналом действий.

### 2.3. X/Twitter integration is mandatory

Интеграция с X/Twitter — не optional feature, а обязательная часть платформы.

Минимальный обязательный workflow:

```text
Connect X Account → Generate Draft → Review → Approve → Publish to X
```

Система должна уметь:

- подключать X account через OAuth;
- хранить access/refresh tokens только в зашифрованном виде;
- публиковать text posts;
- публиковать threads через reply chain;
- загружать media assets перед публикацией;
- публиковать посты с изображениями;
- публиковать посты с GIF/animated media, если формат и тариф API позволяют;
- публиковать видео;
- публиковать narrated voice content как MP4-video;
- сохранять publish logs;
- показывать пользователю понятные ошибки API;
- никогда не публиковать без явного approval в базовом режиме.

Autopilot может существовать только как advanced mode. Даже там должны быть лимиты, правила качества, расписание, журнал действий и возможность выключить автопубликацию.

### 2.4. Multimodal generation is mandatory

Платформа должна генерировать не только текст, но и несколько типов publish-ready контента:

```text
Text → X post / thread
Image → generated visual / quote card / diagram / carousel images
Voice → STT input or TTS narration
Video → captioned MP4 / generated video / narrated visual clip
GIF/animation → animated media workflow where supported
```

Основное правило: каждый тип контента должен иметь понятный путь до публикации в X. Не должно быть функции, которая генерирует asset, но не умеет его сохранить, preview, проверить и отправить в publish pipeline.

### 2.5. Источники важнее уверенного тона

Если факт не подтвержден, система не должна писать его как истину.

Каждый draft должен иметь:

- список использованных источников;
- fact-check report;
- confidence level;
- список claims, которые требуют проверки;
- предупреждения по устаревшим или слабым источникам.

### 2.6. Английский интерфейс

Хотя внутренняя документация может быть на русском, продукт должен быть полностью на английском.

Все UI labels должны быть такими:

```text
New Project
Generate Angles
Research Sources
Create Draft
Fact Check
Improve Hook
Approve & Publish
Schedule Post
Agent Traces
Brand Voice
Writing Samples
```

Нельзя использовать в UI:

```text
Новый проект
Сгенерировать
Проверить факты
Опубликовать
```

---

## 3. Рекомендуемый MVP

MVP должен быть сильным, но не слишком широким.

### 3.1. MVP scope

В первую версию включить:

1. User authentication.
2. Brand voice setup.
3. Upload writing samples.
4. Topic/link/file based content project creation.
5. Research Agent.
6. Angle Generator.
7. Text Post Generator.
8. Thread Generator.
9. Quote Retweet Draft Generator.
10. Image Post Generator: quote cards, diagrams, visual frameworks, carousel images.
11. Media Asset Manager: preview, alt text, metadata, status, storage URL.
12. Voice note input через speech-to-text.
13. TTS-to-video renderer: voice + captions + static background or generated visual.
14. Video Post Generator: at least simple captioned MP4 renderer for MVP.
15. Fact-check report.
16. Style review.
17. Agent traces.
18. Mandatory X connection через OAuth.
19. Manual publish to X after approval.
20. Publish text posts, threads, image posts and video posts to X.

### 3.2. Что можно оставить на post-MVP

- полностью автономный autoposting;
- advanced AI video generation beyond simple captioned MP4 renderer;
- advanced analytics по performance постов;
- team collaboration;
- A/B testing hooks;
- multi-account management;
- integration с Substack/LinkedIn;
- browser extension;
- advanced outbound/growth engine.

---

## 4. High-level архитектура

```text
┌──────────────────────────────────────────────┐
│                  Frontend                    │
│          Next.js / React / Tailwind          │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│                 Backend API                  │
│                  FastAPI                     │
│  Auth / Projects / Drafts / Media / Publish  │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│             Agent Orchestrator               │
│          LangGraph or Custom Graph           │
│ Research → Angles → Draft → Review → Final   │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│                  Workers                     │
│ Celery / RQ / Dramatiq / Temporal optional   │
│ Research / Media / TTS / Video / Publishing  │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│                  Storage                     │
│ PostgreSQL / Redis / Object Storage / Vector │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│              External Providers              │
│ LLM / Web Search / X API / Image / STT / TTS │
└──────────────────────────────────────────────┘
```

---

## 5. Рекомендуемый tech stack

### 5.1. Frontend

Рекомендуется:

- Next.js или Vite + React;
- TypeScript;
- Tailwind CSS;
- shadcn/ui;
- Zustand или TanStack Query;
- React Hook Form + Zod;
- Framer Motion для аккуратных transitions;
- Markdown preview для drafts;
- WebSocket/SSE для отображения прогресса агентов.

Для MVP можно взять:

```text
React + Vite + TypeScript + Tailwind + shadcn/ui
```

### 5.2. Backend

Рекомендуется:

- FastAPI;
- SQLAlchemy 2.x;
- Alembic;
- Pydantic v2;
- PostgreSQL;
- Redis;
- Celery/RQ для background jobs;
- S3-compatible storage: Cloudflare R2, AWS S3 или MinIO;
- pgvector или Chroma для writing samples;
- LangGraph для agent workflow.

### 5.3. AI providers

Сделать provider-agnostic слой:

```text
LLMProvider
ImageProvider
SpeechToTextProvider
TextToSpeechProvider
VideoProvider
SearchProvider
PublisherProvider
```

Так можно менять OpenAI/Anthropic/другие сервисы без переписывания бизнес-логики.

### 5.4. X/Twitter integration

Интеграция с X должна быть отдельным обязательным модулем, а не опциональным bonus. Без нее продукт не считается завершенным для assignment.

Нужно поддержать:

- OAuth connection;
- encrypted token storage;
- refresh token flow;
- account connection status;
- upload media;
- create text post;
- create post with media;
- create thread через reply chain;
- schedule через внутренний scheduler;
- publish logs;
- API rate/error handling;
- graceful fallback, если конкретный media endpoint недоступен на тарифе пользователя.

Обязательный UX:

```text
Connect X Account
  ↓
Generate Content
  ↓
Preview exactly as X post
  ↓
Approve & Publish
  ↓
Show published X URL or error details
```

В базовом режиме запрещено публиковать без действия пользователя `Approve & Publish`.

### 5.5. Supported X content/media matrix

Платформа должна генерировать все ключевые виды контента, которые можно довести до X-публикации.

| Content type | Что генерируем | Как публикуем в X | MVP requirement |
|---|---|---|---|
| Text post | один сильный пост | `POST /2/tweets` with `text` | required |
| Thread | серия связанных постов | первый пост, затем replies через `reply.in_reply_to_tweet_id` | required |
| Quote-style response | умный ответ/quote draft к чужому посту | если quote endpoint/plan доступен — quote flow; иначе обычный пост со ссылкой или copy-ready draft | required as draft, publish fallback required |
| Image post | JPG/PNG/WebP visual, quote card, diagram | upload media → get `media_id` → `POST /2/tweets` with media | required |
| Carousel-style images | набор до 4 изображений для одного поста | upload each image → attach multiple `media_ids` | required if images enabled |
| GIF / animated media | GIF или короткая анимация | chunked/recommended media upload where supported | optional for MVP, architecture required |
| Voice note input | пользователь диктует идею | STT → text/thread/video draft | required |
| Voice/narrated content | TTS voiceover + captions + visual | render MP4 → upload video → publish | required |
| Video post | captioned MP4 or generated short video | chunked upload → processing status → publish with `media_id` | required at simple renderer level |
| Subtitles | SRT/VTT for video | attach as subtitle media when supported | post-MVP, architecture required |

Практическая логика по голосу:

```text
Audio-only content is not treated as a primary publishing target.
Voice content must be converted into a supported X media format: MP4 video.
```

То есть пользователь может говорить голосом, система может генерировать голос, но для публикации в X голос должен попадать в video workflow:

```text
Voice script → TTS audio → captions → static/generative visual → MP4 → X video post
```

### 5.6. X API implementation notes

На уровне кода заложить следующие правила:

- `POST /2/tweets` используется для создания поста;
- media сначала загружается отдельно, затем прикрепляется к посту через `media_id`;
- для больших media/video использовать chunked upload workflow;
- для image posts поддерживать JPG/PNG/GIF/WebP там, где это разрешено текущим API;
- не хардкодить один тариф X API: media endpoints и лимиты могут отличаться по планам;
- все ошибки X API сохранять в `publish_logs`;
- UI должен показывать пользователю понятное сообщение: `X API plan does not allow this media action` вместо сырого stack trace.

---

## 6. Backend modules

Рекомендуемая структура backend:

```text
backend/
  app/
    main.py
    core/
      config.py
      security.py
      encryption.py
      logging.py
      exceptions.py
    db/
      session.py
      base.py
      migrations/
    models/
      user.py
      project.py
      draft.py
      media_asset.py
      writing_sample.py
      agent_trace.py
      publish_job.py
      source.py
      brand_voice.py
    schemas/
      auth.py
      project.py
      draft.py
      media.py
      agents.py
      publish.py
    api/
      v1/
        auth.py
        x_auth.py
        projects.py
        drafts.py
        research.py
        media.py
        publish.py
        traces.py
        settings.py
    services/
      auth_service.py
      project_service.py
      draft_service.py
      media_service.py
      publish_service.py
      fact_check_service.py
      style_service.py
    agents/
      graph.py
      state.py
      research_agent.py
      insight_agent.py
      angle_agent.py
      outline_agent.py
      writer_agent.py
      media_director_agent.py
      fact_checker_agent.py
      editor_agent.py
      style_reviewer_agent.py
      publisher_agent.py
    providers/
      llm/
        base.py
        openai_provider.py
        anthropic_provider.py
      search/
        base.py
        web_search_provider.py
        hn_provider.py
        arxiv_provider.py
      media/
        image_provider.py
        stt_provider.py
        tts_provider.py
        video_provider.py
      x/
        x_client.py
        oauth.py
        media_upload.py
        publisher.py
    workers/
      celery_app.py
      research_jobs.py
      media_jobs.py
      publish_jobs.py
    prompts/
      research.md
      angles.md
      writer.md
      editor.md
      fact_checker.md
      style_reviewer.md
    tests/
```

---

## 7. Frontend modules

Рекомендуемая структура frontend:

```text
frontend/
  src/
    app/
      routes/
        login/
        dashboard/
        projects/
        projects/[id]/
        settings/
    components/
      layout/
        AppShell.tsx
        Sidebar.tsx
        Topbar.tsx
      project/
        ProjectCard.tsx
        ProjectWizard.tsx
        SourcePanel.tsx
        AngleSelector.tsx
        DraftComposer.tsx
        FactCheckPanel.tsx
        AgentTraceTimeline.tsx
      media/
        ImagePreview.tsx
        AudioPreview.tsx
        VideoPreview.tsx
      settings/
        BrandVoiceForm.tsx
        WritingSamplesUploader.tsx
        XConnectionCard.tsx
      ui/
    lib/
      api.ts
      queryClient.ts
      auth.ts
      types.ts
    styles/
```

---

## 8. Data model

### 8.1. users

```text
users
- id
- email
- password_hash
- full_name
- created_at
- updated_at
```

### 8.2. connected_accounts

```text
connected_accounts
- id
- user_id
- provider              # x
- provider_user_id
- access_token_encrypted
- refresh_token_encrypted
- scopes
- expires_at
- created_at
- updated_at
```

### 8.3. brand_voices

```text
brand_voices
- id
- user_id
- name
- description
- tone
- audience
- topics
- forbidden_phrases
- preferred_patterns
- example_post_ids
- created_at
- updated_at
```

### 8.4. writing_samples

```text
writing_samples
- id
- user_id
- brand_voice_id
- source_type           # upload, pasted_text, imported_x, article
- title
- text
- embedding_id
- metadata_json
- created_at
```

### 8.5. content_projects

```text
content_projects
- id
- user_id
- brand_voice_id
- title
- topic
- goal                  # educate, provoke, launch, summarize, announce
- target_audience
- status                # draft, researching, generating, ready, published, failed
- created_at
- updated_at
```

### 8.6. sources

```text
sources
- id
- project_id
- source_type           # url, uploaded_file, x_post, arxiv, hn, manual
- title
- url
- author
- published_at
- extracted_text
- summary
- credibility_score
- created_at
```

### 8.7. angles

```text
angles
- id
- project_id
- title
- thesis
- contrarian_point
- evidence_summary
- risk_notes
- score
- created_at
```

### 8.8. drafts

```text
drafts
- id
- project_id
- selected_angle_id
- type                  # text_post, thread, quote_retweet, image_post, voice_video, video
- status                # draft, reviewed, approved, scheduled, published, rejected
- content_json
- final_text
- quality_score
- style_score
- fact_confidence_score
- created_at
- updated_at
```

### 8.9. media_assets

```text
media_assets
- id
- draft_id
- type                  # image, audio, video, subtitles
- file_url
- storage_key
- mime_type
- duration_seconds
- x_media_id
- status
- created_at
```

### 8.10. fact_checks

```text
fact_checks
- id
- draft_id
- claim
- verdict               # supported, weakly_supported, unsupported, needs_source
- explanation
- source_ids
- created_at
```

### 8.11. agent_traces

```text
agent_traces
- id
- project_id
- draft_id
- agent_name
- step_order
- input_json
- output_json
- model_name
- token_usage_json
- latency_ms
- created_at
```

### 8.12. publish_jobs

```text
publish_jobs
- id
- draft_id
- platform              # x
- status                # pending, running, published, failed, canceled
- scheduled_at
- published_at
- platform_post_id
- error_message
- created_at
- updated_at
```

---

## 9. Agent architecture

### 9.1. Главный orchestrator

Orchestrator отвечает за порядок шагов и состояние проекта.

```text
Input
  ↓
Research Agent
  ↓
Insight Agent
  ↓
Angle Agent
  ↓
Format Planner Agent
  ↓
Writer Agent
  ↓
Media Director Agent, if needed
  ↓
Fact Checker Agent
  ↓
Editor Agent
  ↓
Style Reviewer Agent
  ↓
Final Draft
```

### 9.2. Shared agent state

```python
class ContentState:
    project_id: str
    user_id: str
    topic: str
    goal: str
    target_audience: str
    brand_voice: dict
    writing_samples: list[dict]
    sources: list[dict]
    insights: list[dict]
    angles: list[dict]
    selected_angle: dict | None
    format: str | None
    draft: dict | None
    media_plan: dict | None
    fact_check_report: dict | None
    style_report: dict | None
    final_output: dict | None
```

---

## 10. Agents подробно

### 10.1. Research Agent

Задача: собрать релевантный контекст.

Input:

```text
- topic
- user goal
- source links
- uploaded files
- optional X post URL
```

Output:

```json
{
  "sources": [],
  "key_findings": [],
  "useful_examples": [],
  "contradictions": [],
  "weak_sources": [],
  "research_summary": ""
}
```

Правила:

- не делать выводы без источников;
- разделять факт, мнение и интерпретацию;
- сохранять источники в БД;
- помечать устаревшие данные;
- не использовать сомнительные утверждения в финальном тексте без предупреждения.

### 10.2. Insight Agent

Задача: превратить research в сильные идеи.

Output:

```json
{
  "insights": [
    {
      "claim": "",
      "why_it_matters": "",
      "non_obvious_angle": "",
      "evidence": [],
      "risk": ""
    }
  ]
}
```

Критерий качества:

- мысль должна быть неочевидной;
- мысль должна быть объяснимой за 1–2 предложения;
- мысль должна иметь practical implication;
- нельзя писать общие банальности.

### 10.3. Angle Agent

Задача: предложить несколько углов подачи.

Пример output:

```json
{
  "angles": [
    {
      "title": "Judgment is the new bottleneck",
      "thesis": "AI coding agents make implementation cheaper, but make engineering judgment more important.",
      "tone": "sharp analytical",
      "best_format": "thread",
      "score": 9
    }
  ]
}
```

### 10.4. Format Planner Agent

Задача: выбрать формат.

Поддерживаемые форматы:

```text
text_post
thread
quote_retweet
image_post
carousel
voice_video
short_video
essay
```

Правила выбора:

```text
- Если идея короткая и острая → text_post
- Если тема сложная → thread
- Если есть внешний X post → quote_retweet
- Если есть framework/diagram → image_post или carousel
- Если пользователь дал voice note → voice_to_post или voice_video
- Если нужен storytelling или launch → thread или video
```

### 10.5. Writer Agent

Задача: написать первый draft.

Правила:

- писать на английском;
- избегать AI clichés;
- использовать короткие и средние предложения;
- сохранять сильный thesis;
- не добавлять неподтвержденные факты;
- не использовать emojis по умолчанию;
- не использовать hashtags по умолчанию;
- не делать слишком рекламный тон;
- сохранять естественный rhythm.

### 10.6. Media Director Agent

Задача: создать media brief.

Для image post:

```json
{
  "visual_type": "quote_card | diagram | framework | meme | infographic",
  "headline": "",
  "visual_metaphor": "",
  "layout": "",
  "image_prompt": "",
  "alt_text": ""
}
```

Для voice/video:

```json
{
  "script": "",
  "voice_tone": "calm, confident, analytical",
  "captions": [],
  "background_style": "minimal dark gradient",
  "duration_target_seconds": 45
}
```

### 10.7. Fact Checker Agent

Задача: проверить утверждения.

Output:

```json
{
  "claims": [
    {
      "claim": "",
      "verdict": "supported | weakly_supported | unsupported | needs_source",
      "explanation": "",
      "source_ids": []
    }
  ],
  "overall_confidence": 0.0,
  "unsafe_claims": []
}
```

Правила:

- выделять claims из draft;
- проверять claims по источникам;
- не пропускать цифры без источника;
- помечать потенциально устаревшие данные;
- предлагать safer wording.

### 10.8. Editor Agent

Задача: улучшить текст.

Проверяет:

- hook;
- clarity;
- rhythm;
- specificity;
- density;
- unnecessary words;
- repetition;
- weak ending;
- overclaiming.

Output:

```json
{
  "critique": [],
  "revised_draft": "",
  "changes_made": []
}
```

### 10.9. Style Reviewer Agent

Задача: сравнить draft с brand voice пользователя.

Output:

```json
{
  "style_score": 8.4,
  "matches": [],
  "mismatches": [],
  "suggested_adjustments": []
}
```

### 10.10. Publisher Agent

Задача: публиковать только approved drafts.

Правила:

- не публиковать draft без статуса `approved`;
- проверять connected account;
- проверять media readiness;
- логировать request/response;
- сохранять platform_post_id;
- при ошибке не retry бесконечно;
- для video ждать processing status.

---

## 10.5. Multimodal generation requirements

Этот раздел обязателен для Claude Code: все генераторы должны проектироваться как части одного content pipeline, а не как разрозненные кнопки.

### 10.5.1. Единая модель результата

Любой generated output должен сохраняться как `Draft` + optional `MediaAsset`.

```text
ContentProject
  ↓
Draft
  ↓
MediaAsset[]
  ↓
FactCheckReport
  ↓
StyleReview
  ↓
PublishJob
```

Нельзя генерировать media только в памяти браузера. Все assets должны иметь status, preview URL, storage URL и publish readiness.

### 10.5.2. Text generation

Поддержать:

- short post;
- long-form X post;
- thread;
- quote-style response;
- reply draft;
- research breakdown;
- hook variants;
- rewrite variants.

### 10.5.3. Image generation

Поддержать:

- quote card;
- thesis card;
- diagram;
- framework visual;
- checklist visual;
- carousel image set;
- alt text generation.

Для MVP можно сделать два режима:

```text
1. Deterministic renderer: HTML/CSS/SVG/canvas → image
2. AI image provider: prompt → generated image
```

Deterministic renderer важен, потому что для текстовых карточек он дает более контролируемый результат, чем image model.

### 10.5.4. Voice generation and voice input

Есть два разных сценария:

```text
Voice input: user speaks → STT → idea extraction → post/thread/video
Voice output: generated script → TTS → audio asset → MP4 video workflow
```

Голос должен использоваться не только как media, но и как UX acceleration: пользователь может быстро надиктовать сырую мысль, а система делает из нее сильный draft.

### 10.5.5. Video generation

MVP video не должен зависеть от тяжелой AI video generation. Базовый надежный вариант:

```text
script + TTS audio + captions + background visual + subtle animation → MP4
```

Post-MVP можно подключить video generation provider:

```text
topic → concept → storyboard → scene prompts → generated video → captions → final MP4
```

### 10.5.6. Publish readiness checks

Перед публикацией любого draft система должна проверить:

```text
- content is not empty
- media assets are uploaded and processed
- text length is valid for selected format
- thread order is valid
- media type is supported
- X account is connected
- token is valid or refreshed
- draft is approved
- fact-check status is acceptable
- style review passed or user explicitly overrides
```

---

## 11. Workflows по типам контента

### 11.1. Text post

```text
User enters topic
  ↓
Research Agent collects context
  ↓
Angle Agent proposes 5 angles
  ↓
User selects one angle
  ↓
Writer Agent creates post
  ↓
Fact Checker verifies claims
  ↓
Editor improves hook and rhythm
  ↓
User approves
  ↓
Publish or export
```

### 11.2. Thread

```text
Topic
  ↓
Research
  ↓
Thesis
  ↓
Outline
  ↓
Tweet-by-tweet draft
  ↓
Hook optimization
  ↓
Fact-check per tweet
  ↓
Style review
  ↓
Approve
  ↓
Publish as reply chain
```

Thread content JSON:

```json
{
  "type": "thread",
  "posts": [
    {"order": 1, "text": "Hook..."},
    {"order": 2, "text": "Point 1..."},
    {"order": 3, "text": "Point 2..."}
  ]
}
```

### 11.3. Quote retweet draft

```text
User pastes X post URL or text
  ↓
System extracts post context
  ↓
Research Agent checks background if needed
  ↓
Angle Agent generates response strategies
  ↓
Writer creates 3 quote options:
      - agreement with added insight
      - respectful challenge
      - broader synthesis
  ↓
User selects
  ↓
Publish or copy
```

Важно: если API limitations не позволяют сделать настоящую quote публикацию, система должна дать пользователю copy-ready текст или обычный post со ссылкой.

### 11.4. Image post

```text
Selected angle
  ↓
Media Director creates visual brief
  ↓
Image generation or internal quote-card renderer
  ↓
Alt text generation
  ↓
Quality check
  ↓
Upload media
  ↓
Publish post with media
```

Рекомендуемые image formats:

- quote card;
- concept diagram;
- 2x2 matrix;
- before/after workflow;
- checklist;
- simple framework;
- carousel slides.

### 11.5. Voice input to text post

```text
User uploads/records voice note
  ↓
Speech-to-text
  ↓
Idea cleanup
  ↓
Angle extraction
  ↓
Draft generation
  ↓
Review
```

Это очень полезная UX-фича, потому что пользователь может надиктовать сырую мысль, а система превратит ее в сильный draft.

### 11.6. Voice/narrated video post

```text
Draft or thread
  ↓
Script Agent creates 30–60 sec script
  ↓
TTS generates audio
  ↓
Caption generator creates subtitles
  ↓
Video renderer combines:
      - background image
      - captions
      - audio
      - optional waveform
  ↓
MP4 saved to object storage
  ↓
Upload video to X
  ↓
Publish
```

Для MVP лучше делать не сложную AI video generation, а стабильный renderer:

```text
static visual + captions + TTS voice + subtle animation
```

### 11.7. Full video generation

Post-MVP pipeline:

```text
Topic
  ↓
Video Concept
  ↓
Script
  ↓
Storyboard
  ↓
Scene prompts
  ↓
Video generation provider
  ↓
Captions
  ↓
Final render
  ↓
Review
  ↓
Publish
```

---

## 12. X publishing logic — обязательная интеграция

Этот модуль обязателен. Он отвечает за реальные публикации в X после approval пользователя.

Запрещено смешивать генерацию и публикацию в одном сервисе. Генераторы создают drafts/assets, Publisher Service только публикует approved content.

### 12.1. Text post

```text
POST /2/tweets
body:
{
  "text": "..."
}
```

### 12.2. Media post

```text
Upload media
  ↓
Receive media_id
  ↓
POST /2/tweets
body:
{
  "text": "...",
  "media": {
    "media_ids": ["..."]
  }
}
```

### 12.3. Thread

```text
Create first post
  ↓
Get first post id
  ↓
Create second post as reply to previous id
  ↓
Repeat until thread is complete
```

### 12.4. Video upload

Для больших media использовать chunked upload:

```text
INIT → APPEND chunks → FINALIZE → STATUS → POST
```

Publisher должен уметь ждать processing status. Нельзя считать видео опубликованным, пока media processing не завершился успешно.

### 12.5. Voice publishing

Голосовой контент публикуется как video post:

```text
TTS audio
  ↓
Captions
  ↓
Background image / generated visual
  ↓
MP4 render
  ↓
Chunked upload
  ↓
POST /2/tweets with media_id
```

В UI это можно назвать `Voice Post` или `Narrated Post`, но технически это `video` media asset.

### 12.6. Supported media constraints

Заложить в коде конфигурационный слой, а не магические числа:

```text
SUPPORTED_IMAGE_TYPES = [jpg, jpeg, png, gif, webp]
SUPPORTED_VIDEO_TYPES = [mp4, webm, mov/quicktime where available]
MAX_IMAGES_PER_POST = 4
MAX_GIFS_PER_POST = 1
MAX_VIDEOS_PER_POST = 1
```

Эти значения должны быть вынесены в config, потому что X API и тарифные ограничения могут меняться.

### 12.7. Safety rules

Publisher service должен проверять:

```text
- draft.status == approved
- connected account exists
- token is valid or refreshable
- media assets are ready
- fact confidence is acceptable
- user has not exceeded platform limits
- content is not empty
```

---

## 13. UI/UX architecture

## 13.1. Основные страницы

### 1. Landing Page

UI language: English.

Sections:

```text
Hero
Problem
How it works
Examples
Agent workflow
Pricing placeholder
CTA
```

Hero copy example:

```text
Create high-signal content without sounding like AI.
Research, draft, fact-check, and publish sharp posts for X.
```

CTA:

```text
Start Writing
View Demo
```

### 2. Login / Sign Up

Minimal UI:

```text
Continue with Google
Continue with Email
```

### 3. Dashboard

Purpose: показать проекты и быстрые действия.

Blocks:

```text
New Content Project
Recent Drafts
Scheduled Posts
Connected Accounts
Brand Voice Score
```

Primary CTA:

```text
New Project
```

### 4. New Project Wizard

Step 1: Input

```text
What do you want to create?
[ Topic / URL / X Post / File / Voice Note ]
```

Step 2: Goal

```text
What is the goal?
- Educate
- Challenge an assumption
- Explain a trend
- Launch something
- Summarize research
- Build authority
```

Step 3: Format

```text
Recommended formats:
- Sharp Post
- Thread
- Quote Retweet
- Image Post
- Narrated Video
```

Step 4: Brand Voice

```text
Select brand voice
Upload samples
```

### 5. Research Workspace

Цель: показать, что система не просто пишет, а исследует.

Layout:

```text
Left: Source list
Center: Research summary
Right: Key findings / contradictions / weak claims
```

UI labels:

```text
Sources
Key Findings
Contradictions
Weak Evidence
Use in Draft
Exclude
```

### 6. Angle Selection Screen

Показывает 5–7 вариантов тезисов.

Card structure:

```text
Angle title
Thesis
Why it works
Risk
Best format
Score
```

Buttons:

```text
Use This Angle
Generate More
Make It Sharper
Make It More Contrarian
```

### 7. Composer Studio

Главная рабочая зона.

Layout:

```text
Left Sidebar: Project context
Center: Draft editor
Right Sidebar: Assistant panels
```

Right Sidebar panels:

```text
Fact Check
Style Review
Hook Variants
Rewrite Options
Sources
Agent Traces
```

Buttons:

```text
Improve Hook
Make Shorter
Add More Specificity
Make More Opinionated
Remove AI Phrases
Fact Check Again
Approve Draft
```

### 8. Media Studio

Для image/video/audio.

Tabs:

```text
Visual Brief
Image Preview
Voice
Captions
Video Preview
```

Actions:

```text
Regenerate Image
Edit Visual Direction
Generate Alt Text
Generate Captions
Render Video
```

### 9. Review & Publish Screen

Показывает финальную проверку.

Sections:

```text
Final Draft
Media Preview
Fact-check Summary
Style Score
Risk Warnings
Publishing Account
Schedule
```

Buttons:

```text
Approve & Publish
Schedule
Save as Draft
Copy Text
```

### 10. Agent Traces Screen

Цель: deliverable для assignment и прозрачность продукта.

Timeline:

```text
Research Agent
Insight Agent
Angle Agent
Writer Agent
Fact Checker
Editor
Style Reviewer
Publisher
```

Для каждого шага:

```text
Input
Output
Sources
Model
Tokens
Latency
```

### 11. Settings

Sections:

```text
Profile
Brand Voice
Writing Samples
Connected Accounts
API Keys optional
Publishing Rules
Data Export
```

---

## 14. UX principles

### 14.1. Пользователь всегда видит следующий шаг

Плохой UX:

```text
Generate
```

Хороший UX:

```text
Generate 5 Angles
Create First Draft
Run Fact Check
Improve Hook
Approve & Publish
```

### 14.2. AI должен объяснять, что он делает

Во время генерации показывать прогресс:

```text
Researching sources...
Extracting non-obvious insights...
Generating angles...
Writing draft...
Checking factual claims...
Improving rhythm and clarity...
```

### 14.3. Не перегружать пользователя

Не показывать все агентные JSON-данные сразу. По умолчанию показывать human-readable summary, а raw traces — в отдельной вкладке.

### 14.4. Draft-first UX

Любая генерация должна приводить к редактируемому draft, а не к финальному locked output.

### 14.5. Сильная работа с пустыми состояниями

Примеры empty states на английском:

```text
No writing samples yet.
Upload a few examples so the system can learn your voice.
```

```text
No sources selected.
Add a link, upload a file, or let the Research Agent discover context.
```

```text
No drafts yet.
Start with a topic or paste an X post to generate your first angle.
```

---

## 15. Quality evaluation system

Каждый draft должен получать оценки.

### 15.1. Metrics

```text
Insight Density: 0–10
Specificity: 0–10
Clarity: 0–10
Originality: 0–10
Style Match: 0–10
Factual Confidence: 0–10
AI Slop Risk: 0–10
Hook Strength: 0–10
```

### 15.2. AI Slop detector

Фразы, которые нужно снижать или удалять:

```text
- game-changer
- in today's fast-paced world
- unlock the power of
- revolutionizing the way
- it is important to note
- businesses must adapt
- the future is here
- seamless experience
- cutting-edge technology
```

### 15.3. Draft quality gate

Перед публикацией:

```text
- Factual Confidence >= 7
- AI Slop Risk <= 3
- Style Match >= 7
- Draft is not empty
- Media is ready if required
- User approval exists
```

Если gate не пройден:

```text
Show warning → suggest fixes → do not publish automatically
```

---

## 16. Prompting standards

Все prompts хранить в отдельных `.md` файлах.

Пример:

```text
backend/app/prompts/writer.md
backend/app/prompts/fact_checker.md
backend/app/prompts/style_reviewer.md
```

### 16.1. Общий prompt format

```xml
<role>
You are a high-taste editorial AI agent for X/Twitter content.
</role>

<context>
User topic: {{topic}}
Brand voice: {{brand_voice}}
Sources: {{sources}}
Selected angle: {{selected_angle}}
</context>

<task>
Write a draft for the selected format.
</task>

<constraints>
- Write in English.
- Avoid generic AI phrasing.
- Do not invent facts.
- Prefer concrete claims over broad statements.
- Preserve a natural rhythm.
</constraints>

<output_format>
Return valid JSON only.
</output_format>
```

### 16.2. Writer Agent output schema

```json
{
  "draft_type": "text_post",
  "text": "",
  "rationale": "",
  "claims_used": [],
  "style_notes": [],
  "risk_notes": []
}
```

---

## 17. Security and privacy

### 17.1. Tokens

X access tokens and refresh tokens must be encrypted.

Rules:

```text
- Never log raw tokens
- Never return tokens to frontend
- Store encrypted tokens only
- Use separate encryption key from environment
- Rotate tokens if needed
```

### 17.2. User files

Uploaded files may contain private information.

Rules:

```text
- Store files in private bucket
- Generate signed URLs only when needed
- Extract text asynchronously
- Allow user to delete files
- Do not use user samples for other users
```

### 17.3. Publishing safety

```text
- No publishing without approval in default mode
- Store audit logs
- Rate-limit publish actions
- Add confirmation modal before first publish
```

---

## 18. API endpoints

### 18.1. Auth

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/logout
GET  /api/v1/auth/me
```

### 18.2. X OAuth

```text
GET  /api/v1/x/connect
GET  /api/v1/x/callback
POST /api/v1/x/disconnect
GET  /api/v1/x/status
```

### 18.3. Projects

```text
POST /api/v1/projects
GET  /api/v1/projects
GET  /api/v1/projects/{project_id}
PATCH /api/v1/projects/{project_id}
DELETE /api/v1/projects/{project_id}
```

### 18.4. Research and agents

```text
POST /api/v1/projects/{project_id}/research
POST /api/v1/projects/{project_id}/angles
POST /api/v1/projects/{project_id}/drafts/generate
POST /api/v1/drafts/{draft_id}/fact-check
POST /api/v1/drafts/{draft_id}/revise
GET  /api/v1/projects/{project_id}/traces
```

### 18.5. Media

```text
POST /api/v1/media/image
POST /api/v1/media/speech-to-text
POST /api/v1/media/text-to-speech
POST /api/v1/media/video/render
GET  /api/v1/media/jobs/{job_id}
```

### 18.6. Publish

```text
POST /api/v1/drafts/{draft_id}/approve
POST /api/v1/drafts/{draft_id}/publish/x
POST /api/v1/drafts/{draft_id}/schedule/x
GET  /api/v1/publish/jobs/{job_id}
```

---

## 19. Background jobs

### 19.1. Почему нужны workers

Некоторые операции долгие:

- research;
- file parsing;
- image generation;
- TTS;
- video rendering;
- media upload;
- scheduled publishing.

Их нельзя выполнять напрямую внутри HTTP request.

### 19.2. Job flow

```text
Frontend sends request
  ↓
Backend creates job in DB
  ↓
Worker processes job
  ↓
Worker updates status
  ↓
Frontend polls or receives SSE/WebSocket update
```

Job statuses:

```text
pending
running
completed
failed
canceled
```

---

## 20. Claude Code implementation best practices

Этот раздел предназначен для работы через Claude Code.

### 20.1. Общие правила для Claude Code

Claude Code должен работать пошагово, не пытаться построить весь продукт одним запросом.

Правила:

```text
1. Сначала читать CLAUDE.md.
2. Перед изменениями изучать существующую структуру проекта.
3. Делать маленькие атомарные изменения.
4. Не создавать лишние файлы без необходимости.
5. Не менять архитектуру без причины.
6. После каждого этапа запускать тесты/линтеры, если они есть.
7. Не хардкодить секреты.
8. Не писать русский текст в UI.
9. Все UI labels, placeholders, errors, empty states — English only.
10. После значимых изменений обновлять docs и agent traces examples.
```

### 20.2. Рекомендуемый порядок разработки

#### Phase 1 — Project foundation

```text
- Initialize backend FastAPI app
- Initialize frontend React app
- Add Docker Compose
- Add PostgreSQL and Redis
- Add env examples
- Add basic auth
- Add project model
```

#### Phase 2 — Content project workflow

```text
- Create project wizard
- Save topic/goal/format
- Add dashboard
- Add project detail page
```

#### Phase 3 — Agent orchestration

```text
- Add agent state
- Add Research Agent mock
- Add Angle Agent
- Add Writer Agent
- Save agent traces
```

#### Phase 4 — Draft studio

```text
- Add Draft Composer UI
- Add draft generation endpoint
- Add revise actions
- Add hook variants
```

#### Phase 5 — Fact-checking and style review

```text
- Add claim extraction
- Add fact-check report
- Add style score
- Add quality gate
```

#### Phase 6 — Media

```text
- Add image brief generation
- Add quote-card renderer or image provider
- Add voice note STT
- Add TTS
- Add simple captioned video renderer
```

#### Phase 7 — Mandatory X integration

```text
- Add OAuth connect
- Store encrypted tokens
- Add account connection status UI
- Add publish text post
- Add upload image
- Add publish media post
- Add upload video/chunked upload abstraction
- Add publish narrated MP4 voice post
- Add thread publishing
- Add publish logs and error states
```

#### Phase 8 — Polish and deliverables

```text
- Add examples
- Add seed data
- Add screenshots
- Add README
- Add agent traces folder
- Deploy frontend/backend
```

### 20.3. CLAUDE.md template

В корень проекта добавить файл `CLAUDE.md`.

```markdown
# CLAUDE.md

## Project

This is an Agentic X Content Platform. The product helps users research, draft, fact-check, improve, and publish high-signal content for X/Twitter.

## Product language

The app UI must be English only. Never add Russian text to frontend labels, buttons, placeholders, errors, empty states, or onboarding copy.

## Tech stack

Backend: FastAPI, PostgreSQL, Redis, SQLAlchemy, Alembic, Pydantic.  
Frontend: React, TypeScript, Tailwind, shadcn/ui.  
Agents: LangGraph or a custom graph orchestrator.  
Storage: PostgreSQL, object storage, vector DB.

## Core workflow

Idea → Research → Insights → Angles → Draft → Fact-check → Style review → Human approval → Publish/Schedule.

## Development rules

- Make small, focused changes.
- Do not rewrite unrelated code.
- Do not hardcode secrets.
- Do not publish content without explicit user approval.
- Keep provider integrations behind interfaces.
- Store all agent steps in agent_traces.
- Add tests for business logic.
- Keep prompts in markdown files under backend/app/prompts.

## Quality rules

Generated content must avoid generic AI phrasing. It should be specific, opinionated, clear, source-grounded, and natural.

## Before finishing a task

- Run available tests or explain why not possible.
- Check TypeScript/Python errors if applicable.
- Update documentation if architecture changed.
- Provide a short summary of changed files.
```

### 20.4. Пример prompt для Claude Code на старт проекта

```text
Read CLAUDE.md first.
Create the initial monorepo structure for the Agentic X Content Platform.
Use FastAPI for backend and React + TypeScript + Tailwind for frontend.
Do not implement all features yet.
Create only the foundation:
- backend app skeleton
- frontend app skeleton
- Docker Compose with PostgreSQL and Redis
- .env.example files
- README with local setup
- basic health check endpoint
- basic frontend landing page in English

Important:
- UI text must be English only.
- Keep changes small and clean.
- Do not hardcode secrets.
```

### 20.5. Пример prompt для реализации агентного workflow

```text
Read CLAUDE.md and inspect the current backend structure.
Implement the first version of the agent workflow for content generation.
Scope:
- Add ContentState schema
- Add ResearchAgent mock implementation
- Add AngleAgent implementation
- Add WriterAgent implementation
- Add AgentTrace model and persistence
- Add endpoint POST /api/v1/projects/{project_id}/drafts/generate

Do not add media generation yet.
Do not add X publishing yet.
All generated user-facing content should be in English.
Add tests for the workflow service if test setup exists.
```

### 20.6. Пример prompt для UI/UX

```text
Read CLAUDE.md and inspect the frontend structure.
Build the Project Workspace UI in English.
Scope:
- Project detail page
- Angle selection cards
- Draft composer
- Right sidebar with Fact Check, Style Review, Sources, Agent Traces tabs
- Loading states for agent progress

Use Tailwind and shadcn/ui.
Keep the UI clean, minimal, and premium.
Do not use Russian text anywhere in the UI.
```

---

## 21. Repository deliverables

Для сдачи assignment в GitHub должны быть:

```text
README.md
CLAUDE.md
.env.example
docker-compose.yml
backend/
frontend/
agent_traces/
  example_text_post.json
  example_thread.json
  example_quote_retweet.json
  example_fact_check.json
docs/
  architecture.md
  product_spec.md
  ui_ux.md
```

README должен содержать:

```text
- product description
- architecture overview
- tech stack
- local setup
- env variables
- how to run backend
- how to run frontend
- example workflows
- screenshots
- deployment links
```

---

## 22. Example agent trace

```json
{
  "project_id": "demo-ai-agents",
  "input": {
    "topic": "AI coding agents and the future of software engineering",
    "goal": "Build authority",
    "format": "thread"
  },
  "steps": [
    {
      "agent": "ResearchAgent",
      "output": {
        "key_findings": [
          "AI coding tools reduce implementation friction but increase the importance of review and specification."
        ],
        "sources": []
      }
    },
    {
      "agent": "AngleAgent",
      "output": {
        "selected_angle": "The bottleneck moves from coding speed to engineering judgment."
      }
    },
    {
      "agent": "WriterAgent",
      "output": {
        "draft_type": "thread",
        "posts": [
          "AI coding agents do not eliminate engineers. They expose weak engineering judgment faster.",
          "The scarce skill is no longer typing code. It is knowing what should exist, what should not, and what is subtly wrong."
        ]
      }
    },
    {
      "agent": "FactCheckerAgent",
      "output": {
        "overall_confidence": 0.82,
        "unsupported_claims": []
      }
    },
    {
      "agent": "EditorAgent",
      "output": {
        "changes_made": [
          "Reduced generic phrasing",
          "Improved hook",
          "Made final line sharper"
        ]
      }
    }
  ]
}
```

---

## 23. Definition of Done

MVP считается готовым, если пользователь может:

```text
1. Зарегистрироваться.
2. Создать content project.
3. Добавить topic/link/file/voice input.
4. Получить research summary.
5. Получить несколько angles.
6. Выбрать angle.
7. Сгенерировать text post или thread.
8. Получить fact-check report.
9. Улучшить draft через editor actions.
10. Посмотреть agent traces.
11. Сохранить draft.
12. Подключить X аккаунт optional.
13. Опубликовать approved draft optional.
```

---

## 24. Самое важное для оценки задания

Оценивать будут не просто наличие кнопки “Generate”.

Сильные стороны проекта должны быть:

```text
- high-quality writing;
- non-obvious angles;
- visible agent workflow;
- source grounding;
- fact-checking;
- style adaptation;
- thoughtful UI/UX;
- safe publishing;
- clean architecture;
- readable code;
- clear README and traces.
```

Главный message проекта:

```text
This is not a tweet generator.
This is an agentic editorial system for high-signal technical content.
```
