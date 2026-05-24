import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './LandingPage.css'

const MARQUEE_ITEMS = [
  { type: 'label', text: 'Trusted by' },
  { type: 'name',  text: 'Founders' },
  { type: 'name',  text: 'Operators' },
  { type: 'label', text: 'Built for' },
  { type: 'name',  text: 'Technical writers' },
  { type: 'name',  text: 'Indie hackers' },
  { type: 'label', text: 'Powered by' },
  { type: 'name',  text: 'LangGraph' },
  { type: 'name',  text: 'Claude' },
  { type: 'name',  text: 'OpenAI' },
  { type: 'label', text: 'Publishes to' },
  { type: 'name',  text: 'X / Twitter' },
]

export function LandingPage() {
  const navigate = useNavigate()

  useEffect(() => {
    const io = new IntersectionObserver(
      (entries) => entries.forEach(e => { if (e.isIntersecting) e.target.classList.add('in') }),
      { threshold: 0.12 }
    )
    document.querySelectorAll('.lp-reveal').forEach(el => io.observe(el))
    return () => io.disconnect()
  }, [])

  return (
    <div className="landing-page">

      {/* ── NAV ──────────────────────────────────────── */}
      <nav className="lp-nav">
        <a href="#" className="lp-nav-brand">
          <span className="lp-mark">n</span>
          <span>nfactorial<span style={{ color: 'var(--text-3)', fontWeight: 400, marginLeft: 6 }}>— X Content</span></span>
        </a>
        <div className="lp-nav-links">
          <a href="#how">How it works</a>
          <a href="#features">Features</a>
          <a href="#pricing">Pricing</a>
        </div>
        <div className="lp-nav-cta">
          <button className="lp-btn" onClick={() => navigate('/login')}>Sign in</button>
          <button className="lp-btn lp-btn-primary" onClick={() => navigate('/register')}>Start free</button>
        </div>
      </nav>

      {/* ── HERO ─────────────────────────────────────── */}
      <header className="lp-hero">
        <div className="lp-hero-grid">
          <div>
            <span className="lp-badge">
              <span className="lp-dot"></span>
              Now connecting to X
            </span>
            <h1>
              Publish to X<br />
              like an <span className="lp-stroke">operator</span>,<br />
              not a content<span className="lp-glow">&nbsp;mill</span>.
            </h1>
            <p>nfactorial — X Content is an agentic platform that researches, drafts, fact-checks and publishes posts on X — with humans at every gate. Built for founders who'd rather ship than tweet.</p>
            <div className="lp-hero-cta">
              <button className="lp-btn lp-btn-primary lp-btn-lg" onClick={() => navigate('/register')}>
                Start drafting <span className="lp-btn-arrow">→</span>
              </button>
              <button className="lp-btn lp-btn-lg" onClick={() => navigate('/login')}>See a live demo</button>
            </div>
            <div className="lp-hero-meta">
              <div>
                <div style={{ fontSize: 13, textTransform: 'none', letterSpacing: '.02em', color: 'var(--text-2)', fontFamily: 'var(--sans)', lineHeight: 1.5, maxWidth: 560 }}>
                  No content calendar to maintain. No fact-checking spreadsheet. No "voice doc" to enforce by hand. Drop a topic, approve the gates, publish the thread.
                </div>
              </div>
            </div>
          </div>

          {/* Thread mockup */}
          <div className="lp-hero-thread-wrap">
            <div className="lp-ann a1"><span className="lp-check">●</span> Research complete</div>
            <div className="lp-ann a2"><span className="lp-check">✓</span> Fact check passed</div>
            <div className="lp-ann a3"><span className="lp-check">●</span> Brand voice OK</div>

            <div className="lp-hero-thread">
              <div className="lp-ht-bar">
                <div className="lp-lights"><span></span><span></span><span></span></div>
                <span>nfactorial · drafting</span>
                <span className="lp-spacer"></span>
                <span className="lp-live"><span className="lp-led"></span> live</span>
              </div>

              <div className="lp-ht-post">
                <div className="lp-av">N<div className="lp-tl"></div></div>
                <div>
                  <div className="lp-head">
                    <span className="lp-name">nfactorial</span>
                    <span className="lp-handle">@nfactorial_hq</span>
                    <span className="lp-dot">·</span>
                    <span className="lp-time">now</span>
                  </div>
                  <div className="lp-body">{`The cost of building a startup has collapsed.\n\nThe cost of being noticed has not.\n\nDistribution is the only moat that scales.`}</div>
                  <div className="lp-actions">
                    <span>↺ reply</span><span>↻ repost</span><span>♡ like</span><span>↗ share</span>
                  </div>
                </div>
              </div>

              <div className="lp-ht-post">
                <div className="lp-av">N<div className="lp-tl"></div></div>
                <div>
                  <div className="lp-head">
                    <span className="lp-name">nfactorial</span>
                    <span className="lp-handle">@nfactorial_hq</span>
                    <span className="lp-dot">·</span>
                    <span className="lp-time">now</span>
                  </div>
                  <div className="lp-body">{`Software margins are deflating toward zero.\n\nAttention margins are inflating toward infinity.\n\nThe arbitrage is in the middle — and most teams are still optimizing the product, not the channel.`}</div>
                  <div className="lp-actions">
                    <span>↺ reply</span><span>↻ repost</span><span>♡ like</span><span>↗ share</span>
                  </div>
                </div>
              </div>

              <div className="lp-ht-post">
                <div className="lp-av">N</div>
                <div>
                  <div className="lp-head">
                    <span className="lp-name">nfactorial</span>
                    <span className="lp-handle">@nfactorial_hq</span>
                    <span className="lp-dot">·</span>
                    <span className="lp-time">now</span>
                  </div>
                  <div className="lp-body">{`We've been wrong about content velocity.\n\nMore posts ≠ more growth. Calibration beats cadence, every time.`}</div>
                  <div className="lp-actions">
                    <span>↺ reply</span><span>↻ repost</span><span>♡ like</span><span>↗ share</span>
                  </div>
                </div>
              </div>

              <div className="lp-ht-typing-bar">
                <span className="lp-spinner"></span>
                writer-agent · streaming next post…
              </div>
            </div>
          </div>
        </div>

        {/* Marquee */}
        <div className="lp-marq-wrap">
          <div className="lp-marq">
            {[...MARQUEE_ITEMS, ...MARQUEE_ITEMS].map((item, i) => (
              item.type === 'label'
                ? <span key={i} className="lp-label">{item.text}</span>
                : <span key={i} className="lp-marq-name">{item.text}</span>
            ))}
          </div>
        </div>
      </header>

      {/* ── HOW IT WORKS ─────────────────────────────── */}
      <section className="lp-section lp-reveal" id="how">
        <div className="lp-section-eyebrow">How it works</div>
        <h2>Six agents. <span className="lp-stroke">One thread.</span><br />No marketing speak.</h2>
        <p className="lp-sub">Every post moves through the same DAG: research, insight, angle, draft, review, publish. You see every step and approve every gate.</p>

        <div className="lp-pipeline-vis">
          <div className="lp-pipeline-track">
            <div className="lp-pl-spark"></div>

            {[
              { n: '01', name: 'Research', desc: 'Scans the web, your uploads, internal docs.',
                icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/></svg> },
              { n: '02', name: 'Insight', desc: 'Extracts non-obvious, evidence-backed claims.',
                icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M12 3l1.6 4.5L18 9l-4.4 1.6L12 15l-1.6-4.4L6 9l4.4-1.5z"/></svg> },
              { n: '03', name: 'Angle', desc: 'Generates 4 takes; you pick the sharpest.',
                icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><circle cx="6" cy="6" r="2"/><circle cx="18" cy="6" r="2"/><circle cx="12" cy="20" r="2"/><path d="M6 8v3a2 2 0 0 0 2 2h8a2 2 0 0 0 2-2V8M12 13v5"/></svg> },
              { n: '04', name: 'Draft', desc: 'Writes in your voice with citations inline.',
                icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M3 21l4-1 12-12-3-3L4 17z"/></svg> },
              { n: '05', name: 'Review', desc: 'Fact-checks every claim. Flags style breaks.',
                icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><polyline points="4 12 10 18 20 6"/></svg> },
              { n: '06', name: 'Publish', desc: 'Schedules or pushes the reply chain to X.',
                icon: <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8"><path d="M14 4l6 6-9 9-3 3-3-3 3-3 9-9z"/><path d="M14 10l4 4"/></svg> },
            ].map(step => (
              <div key={step.n} className="lp-pl-node">
                <div className="lp-pl-num">{step.n}</div>
                <div className="lp-circle">{step.icon}</div>
                <div className="lp-pl-name">{step.name}</div>
                <div className="lp-pl-desc">{step.desc}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FEATURES BENTO ───────────────────────────── */}
      <section className="lp-section lp-reveal" id="features">
        <div className="lp-section-eyebrow">What's in the box</div>
        <h2>Built for the part of writing<br />that <span className="lp-stroke">isn't</span> writing.</h2>
        <p className="lp-sub">Research, voice modelling, fact-checking, scheduling, and an X reply-chain publisher — all in one workspace.</p>

        <div className="lp-bento">
          {/* Research */}
          <div className="lp-b-card lp-b-1">
            <div className="lp-tag">Research engine</div>
            <h3>Scan the web like a junior analyst with a deadline.</h3>
            <p className="lp-lead">Pulls from your knowledge graph, the open web, your uploaded PDFs, and recent X discourse. Sources are scored and dropped below a credibility threshold.</p>
            <div className="lp-b-sources">
              {[
                { pill: 'PAP', title: 'Research paper',       meta: 'arxiv · peer-reviewed',     cred: 'High' },
                { pill: 'PDF', title: 'Your uploaded document', meta: 'internal · first-party data', cred: 'First-party' },
                { pill: 'X',   title: 'Operator post on X',   meta: 'x.com · verified author',   cred: 'Medium' },
              ].map(src => (
                <div key={src.pill} className="lp-b-src">
                  <div className="lp-tag-pill">{src.pill}</div>
                  <div>
                    <div className="lp-src-title">{src.title}</div>
                    <div className="lp-src-meta">{src.meta}</div>
                  </div>
                  <div style={{ fontSize: 11, letterSpacing: '.16em', textTransform: 'uppercase', color: 'var(--text-3)', fontWeight: 500 }}>{src.cred}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Voice */}
          <div className="lp-b-card lp-b-2">
            <div className="lp-tag">Voice modeling</div>
            <h3>Sounds like you. Not like ChatGPT.</h3>
            <p className="lp-lead">Upload 20 samples. We learn rhythm, cadence, forbidden phrases, and the specific way you start a sentence.</p>
            <div className="lp-voice-wave">
              {Array.from({ length: 15 }).map((_, i) => <i key={i}></i>)}
            </div>
          </div>

          {/* Fact check */}
          <div className="lp-b-card lp-b-3">
            <div className="lp-tag">Fact check</div>
            <h3>Every number has a source. Or it gets flagged.</h3>
            <div className="lp-fc-demo">
              <div className="lp-row"><span className="lp-claim">A cited statistic</span><span className="lp-v lp-v-sup">Supported</span></div>
              <div className="lp-row"><span className="lp-claim">A general assertion</span><span className="lp-v lp-v-weak">Weak</span></div>
              <div className="lp-row"><span className="lp-claim">An unsourced claim</span><span className="lp-v lp-v-need">Needs src</span></div>
            </div>
          </div>

          {/* Schedule */}
          <div className="lp-b-card lp-b-4">
            <div className="lp-tag">Schedule</div>
            <h3>Cadence without the grind.</h3>
            <p className="lp-lead">Sees when your audience is awake. Spaces threads so you don't burn the feed.</p>
            <div className="lp-heatmap">
              {['','l1','','l2','l3','l4','l3','l2','l1','','l1','l2','l3','l2',
                'l1','l2','l3','l4','l4','l3','l2','l3','l4','l3','l2','l1','',''].map((cls, i) => (
                <i key={i} className={cls || undefined}></i>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── WHY SWITCH ───────────────────────────────── */}
      <section className="lp-section lp-reveal">
        <div className="lp-section-eyebrow">Why teams switch</div>
        <h2>The work that matters,<br />without the work that <span className="lp-stroke">doesn't</span>.</h2>
        <p className="lp-sub">Research, drafting, fact-checking and scheduling all happen in one loop — so you can spend your time on the ideas, not the choreography.</p>

        <div className="lp-why-grid">
          {[
            { h: 'Cadence without grind',  d: 'Publish on a real rhythm without writing every post by hand. The agents draft, you approve.' },
            { h: 'Citations or nothing',   d: 'Every claim is either tied to a source or flagged at the gate. Hallucinations don\'t make it to the timeline.' },
            { h: 'Your voice, not theirs', d: 'Trained on your writing samples — cadence, taboo phrases, sentence starters. It sounds like you, not like a model.' },
            { h: 'Humans at every gate',   d: 'Approve sources, angles, the draft, and the publish. Nothing ships without you saying so.' },
          ].map(cell => (
            <div key={cell.h} className="lp-why-cell">
              <div className="lp-why-h">{cell.h}</div>
              <div className="lp-why-d">{cell.d}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── COMPARISON ───────────────────────────────── */}
      <section className="lp-section lp-reveal">
        <div className="lp-section-eyebrow">Before / After</div>
        <h2>Writing one thread<br />used to take <span className="lp-stroke">a Tuesday</span>.</h2>

        <div className="lp-compare">
          <div className="lp-cmp-col before">
            <div className="lp-cmp-label">Before nfactorial</div>
            <h3>The thread-writing Tuesday</h3>
            <ul className="lp-cmp-list">
              {[
                'Open a pile of tabs, lose half of them',
                'Fact-check by squinting at your PDFs',
                'Forget the actual point you wanted to make',
                'Rewrite the opener until it feels okay',
                'Publish late at night, past your audience',
              ].map(item => (
                <li key={item} className="x"><span className="ic">○</span> {item}</li>
              ))}
            </ul>
          </div>
          <div className="lp-cmp-col after">
            <div className="lp-cmp-label">With nfactorial</div>
            <h3>The thread-writing coffee</h3>
            <ul className="lp-cmp-list">
              {[
                'Drop a topic, get scored sources back',
                'Pick from a few angles, see the thesis',
                'Draft streams in your voice, with citations',
                'Every claim verified or flagged',
                'Schedule for when your audience is awake',
              ].map(item => (
                <li key={item} className="v"><span className="ic">●</span> {item}</li>
              ))}
            </ul>
          </div>
        </div>
      </section>

      {/* ── PRICING ──────────────────────────────────── */}
      <section className="lp-section lp-reveal" id="pricing">
        <div className="lp-section-eyebrow">Plans</div>
        <h2>Pick a plan<br />that matches your <span className="lp-stroke">cadence</span>.</h2>
        <p className="lp-sub">Three tiers, from a single founder voice to a content team running many accounts. Pricing on request.</p>

        <div className="lp-pricing">
          {/* Solo */}
          <div className="lp-price-card">
            <div className="lp-tier">Solo</div>
            <div className="lp-price-h">For founders</div>
            <div className="lp-per">testing the voice</div>
            <p className="lp-pitch">One brand voice. Manual publishing. Standard research depth. Enough to find out whether the loop works for you.</p>
            <ul className="lp-pl">
              {['One brand voice','Standard research depth','Manual publishing','Fact-check + style gates'].map(f => (
                <li key={f}><span className="ic">✓</span> {f}</li>
              ))}
            </ul>
            <button className="lp-pbtn" onClick={() => navigate('/register')}>Start free</button>
          </div>

          {/* Operator (featured) */}
          <div className="lp-price-card featured">
            <div className="lp-tier">Operator <span className="lp-badge-hot">Most popular</span></div>
            <div className="lp-price-h">For founders</div>
            <div className="lp-per">shipping content as infrastructure</div>
            <p className="lp-pitch">Multiple voices, deep research, auto-scheduling, full reply-chain publishing, and the agent trace explorer.</p>
            <ul className="lp-pl">
              {['Multiple brand voices','Deep research + uploads','Auto-schedule + reply chain','Agent trace explorer','Priority support'].map(f => (
                <li key={f}><span className="ic">✓</span> {f}</li>
              ))}
            </ul>
            <button className="lp-pbtn" onClick={() => navigate('/register')}>Start trial</button>
          </div>

          {/* Studio */}
          <div className="lp-price-card">
            <div className="lp-tier">Studio</div>
            <div className="lp-price-h">For teams</div>
            <div className="lp-per">running parallel accounts</div>
            <p className="lp-pitch">Multi-account publishing, SSO, audit logs, custom agent steps, and a workspace built for studios and agencies.</p>
            <ul className="lp-pl">
              {['Everything in Operator','Multi-account publishing','SSO + audit logs','Custom agent steps'].map(f => (
                <li key={f}><span className="ic">✓</span> {f}</li>
              ))}
            </ul>
            <button className="lp-pbtn">Talk to us</button>
          </div>
        </div>
      </section>

      {/* ── CTA ──────────────────────────────────────── */}
      <section className="lp-section lp-reveal">
        <div className="lp-cta-shell">
          <h2>Make every post<br />worth <span className="lp-stroke">publishing</span>.</h2>
          <p>Start free. Connect X in a couple of clicks. Draft your first thread in one sitting.</p>
          <div className="lp-cta-btns">
            <button className="lp-btn lp-btn-primary lp-btn-lg" onClick={() => navigate('/register')}>
              Start drafting <span className="lp-btn-arrow">→</span>
            </button>
            <button className="lp-btn lp-btn-lg">Read the docs</button>
          </div>
        </div>
      </section>

      {/* ── FOOTER ───────────────────────────────────── */}
      <footer className="lp-footer">
        <div className="lp-foot-grid">
          <div>
            <div className="lp-nav-brand" style={{ marginBottom: 4 }}>
              <span className="lp-mark">n</span>
              <span>nfactorial <span style={{ color: 'var(--text-3)', fontWeight: 400 }}>— X Content</span></span>
            </div>
            <p className="lp-foot-lead">Agentic content infrastructure for X. Research, draft, fact-check, publish — with humans at every gate.</p>
          </div>
          <div className="lp-foot-col">
            <h5>Product</h5>
            <ul>
              <li onClick={() => document.getElementById('how')?.scrollIntoView({ behavior: 'smooth' })}>How it works</li>
              <li onClick={() => document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' })}>Features</li>
              <li onClick={() => document.getElementById('pricing')?.scrollIntoView({ behavior: 'smooth' })}>Pricing</li>
              <li>Changelog</li>
              <li>Roadmap</li>
            </ul>
          </div>
          <div className="lp-foot-col">
            <h5>Resources</h5>
            <ul>
              <li>Docs</li>
              <li>API reference</li>
              <li>Brand voice guide</li>
              <li>Blog</li>
              <li>Support</li>
            </ul>
          </div>
          <div className="lp-foot-col">
            <h5>Company</h5>
            <ul>
              <li>About</li>
              <li>Careers</li>
              <li>Privacy</li>
              <li>Terms</li>
              <li>X · @nfactorial_hq</li>
            </ul>
          </div>
        </div>
        <div className="lp-foot-base">
          <span>© nfactorial — X Content</span>
          <span>status · operational</span>
        </div>
      </footer>

    </div>
  )
}
