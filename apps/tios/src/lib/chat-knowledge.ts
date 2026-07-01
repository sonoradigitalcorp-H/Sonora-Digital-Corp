/**
 * SIGNAL Chat Agent — Knowledge Base
 * Context-aware responses for every module/page.
 * From first-time user onboarding to senior-level strategic queries.
 */

export interface ChatContext {
  page: string;
  userLevel?: 'new' | 'regular' | 'senior';
}

export interface KnowledgeEntry {
  keywords: string[];
  response: string;
  followUps?: string[];
}

// ─── Page-specific knowledge ─────────────────────────────────────────

const PAGE_KNOWLEDGE: Record<string, { overview: string; faq: KnowledgeEntry[] }> = {
  '/dashboard': {
    overview:
      'Welcome to **Mission Control** — your intelligence nerve center. Here you\'ll find real-time KPIs, top artist rankings, growth trends, active alerts, and market pulse data. Everything you need to understand your operation at a glance.',
    faq: [
      {
        keywords: ['kpi', 'metric', 'number', 'stat', 'what mean', 'card'],
        response:
          'The KPIs at the top show: **Artists Tracked** (total artists under intelligence), **Avg Discovery Score** (mean AI evaluation score), **Active Pipeline** (artists in negotiation), **Alerts Active** (critical notifications), **Prospect Radar** (new high-potential discoveries), and **Signing Readiness** (artists ready to sign). Each card has a trend indicator showing change from last period.',
        followUps: ['How are discovery scores calculated?', 'What triggers an alert?', 'How often do KPIs update?'],
      },
      {
        keywords: ['live', 'real-time', 'refresh', 'update', 'frequency'],
        response:
          'SIGNAL operates in **near real-time**. The KPI data refreshes every 30 seconds by default. The "Live" badge indicates you\'re viewing live intelligence. You can manually refresh any section by navigating away and back.',
        followUps: ['Can I change the refresh rate?', 'What\'s the data source?'],
      },
      {
        keywords: ['top artist', 'ranking', 'score', 'discovery score', 'ranked'],
        response:
          'The **Top Artists by Discovery Score** panel shows the highest-ranked artists in your intelligence pool. Scores are AI-computed based on: streaming growth, social momentum, genre trends, market fit, and 23 other proprietary signals. Artists with scores above 80 are considered "signing-ready."',
        followUps: ['What factors affect the score?', 'How often are scores recalculated?'],
      },
      {
        keywords: ['alert', 'notification', 'bell', 'unread', 'active alert'],
        response:
          'The **Active Alerts** panel surfaces critical intelligence requiring your attention. Alerts can be: critical (immediate action), warning (monitoring needed), info (intelligence update), or success (positive milestone). Click "View All Alerts" for the full feed.',
        followUps: ['Can I configure which alerts I receive?', 'How do I mark alerts as read?'],
      },
      {
        keywords: ['market pulse', 'market', 'indicator', 'genre', 'trend'],
        response:
          '**Market Pulse** provides key market indicators — genre trends, competitive landscape, and market health scores. This data is aggregated from streaming platforms, social media, and industry reports.',
        followUps: ['What sources does Market Pulse use?', 'Can I filter by region?'],
      },
      {
        keywords: ['discovery feed', 'feed', 'live feed', 'stream'],
        response:
          'The **Live Discovery Feed** is a real-time stream of intelligence events: breakout artists, new discoveries, milestone achievements, market shifts, and signing opportunities. Each event is timestamped and actionable.',
        followUps: ['Can I filter the feed?', 'How do I act on a discovery?'],
      },
    ],
  },

  '/command-center': {
    overview:
      '**Command Center** is where you orchestrate all SIGNAL agents and operations. Think of it as the bridge of your intelligence starship — deploy agents, monitor missions, and coordinate strategic actions.',
    faq: [
      {
        keywords: ['agent', 'mission', 'deploy', 'orchestrate', 'command'],
        response:
          'From Command Center you can deploy AI agents on specific missions: artist discovery sweeps, market analysis deep-dives, contract intelligence gathering, and competitive monitoring. Each mission shows its status, progress, and findings.',
        followUps: ['How do I create a new mission?', 'What agents are available?'],
      },
      {
        keywords: ['status', 'running', 'completed', 'failed', 'progress'],
        response:
          'Missions display one of these statuses: **Idle** (awaiting deployment), **Running** (actively gathering intelligence), **Review** (findings ready for human review), **Completed** (mission finished), or **Failed** (encountered an error).',
        followUps: ['What happens when a mission fails?', 'Can I retry a mission?'],
      },
      {
        keywords: ['automation', 'auto', 'schedule', 'recurring'],
        response:
          'You can schedule recurring missions — daily market scans, weekly artist sweeps, or monthly competitive analyses. Configure frequency, scope, and notification preferences in the mission settings.',
        followUps: ['How do I set up a recurring mission?', 'Can I get email reports?'],
      },
    ],
  },

  '/workflows': {
    overview:
      '**Workflows** automate multi-step intelligence processes. Chain together agent actions, approvals, and notifications into repeatable pipelines. Save hours of manual work.',
    faq: [
      {
        keywords: ['create', 'new', 'build', 'design', 'add'],
        response:
          'To create a workflow, click "New Workflow" and define triggers, steps, and actions. You can chain: data collection → AI analysis → human approval → notification. Each step can be conditional based on previous results.',
        followUps: ['What triggers are available?', 'Can I add human approval steps?'],
      },
      {
        keywords: ['template', 'example', 'pre-built', 'starter'],
        response:
          'SIGNAL includes starter templates: *Artist Onboarding*, *Weekly Market Briefing*, *Alert Escalation*, *Contract Review Pipeline*. Use these as-is or customize them for your needs.',
        followUps: ['How do I import a template?', 'Can I share workflows with my team?'],
      },
      {
        keywords: ['error', 'fail', 'broken', 'debug', 'log'],
        response:
          'If a workflow fails, check the **Execution Log** for each step. Common issues: API rate limits, missing data sources, or approval timeouts. You can retry from the failed step without restarting the entire workflow.',
        followUps: ['How do I view execution logs?', 'Can I set up error notifications?'],
      },
    ],
  },

  '/agents': {
    overview:
      '**Agent Performance** gives you visibility into every AI agent operating in your SIGNAL instance. Monitor their activity, accuracy, and efficiency.',
    faq: [
      {
        keywords: ['agent', 'what', 'type', 'kind', 'role'],
        response:
          'SIGNAL operates **8 specialized agents**: GBrain (orchestrator), Engram (memory), OpenClaw (gateway), Hermes (general assistant), Analyst (data), Writer (content), Legal (compliance), and YAMI (mental health). Each has specific tools and boundaries.',
        followUps: ['What does each agent do?', 'Can I customize agent behavior?'],
      },
      {
        keywords: ['metric', 'performance', 'accuracy', 'speed', 'uptime'],
        response:
          'Key metrics include: **Tasks Completed**, **Success Rate**, **Avg Response Time**, **Memory Usage**, and **Tool Calls**. Agents with success rates below 90% may need retraining or scope adjustment.',
        followUps: ['How do I retrain an agent?', 'What is normal response time?'],
      },
      {
        keywords: ['tool', 'capability', 'skill', 'integration'],
        response:
          'Each agent has specific tools. For example, Analyst can run statistical models and generate charts; Writer can draft documents in English and Spanish; Legal can review contracts for compliance risks.',
        followUps: ['Can I add new tools to an agent?', 'How do skills work?'],
      },
    ],
  },

  '/artists': {
    overview:
      '**Artist Radar** is your complete artist intelligence database. Every artist SIGNAL tracks — with full dossiers, scores, growth trajectories, and contact information.',
    faq: [
      {
        keywords: ['add', 'track', 'new artist', 'monitor', 'discover'],
        response:
          'To add an artist, use the **Discovery Engine** to find emerging talent, or manually add via "Track New Artist." SIGNAL will automatically begin collecting intelligence: streaming data, social metrics, genre analysis, and market positioning.',
        followUps: ['How long does it take to build a dossier?', 'Can I import artists from a CSV?'],
      },
      {
        keywords: ['score', 'rating', 'assessment', 'grade'],
        response:
          'The **Discovery Score** (0–100) is SIGNAL\'s proprietary AI evaluation. It factors: streaming growth (30%), social momentum (20%), genre health (15%), market demand (15%), live performance (10%), and industry buzz (10%). Scores above 75 are "high potential."',
        followUps: ['How is streaming growth calculated?', 'What is a good score for signing?'],
      },
      {
        keywords: ['contact', 'email', 'manager', 'phone', 'reach'],
        response:
          'When contact information is available, it appears in the artist dossier under "Contact." SIGNAL gathers this from public sources, industry databases, and direct submissions. All contact data is labeled with its source and confidence level.',
        followUps: ['How do I update contact info?', 'Is contact data verified?'],
      },
      {
        keywords: ['filter', 'sort', 'search', 'find', 'genre', 'city', 'country'],
        response:
          'Use the filters bar to narrow by: genre, country, city, score range, growth trend, status, and more. You can also sort by score, growth rate, followers, or recently updated. The search bar supports natural language queries.',
        followUps: ['Can I save filtered views?', 'How do I export the list?'],
      },
    ],
  },

  '/discovery': {
    overview:
      '**Discovery Engine** surfaces emerging talent before they break. SIGNAL continuously scans streaming platforms, social media, and industry signals to find the next big artists.',
    faq: [
      {
        keywords: ['how', 'work', 'algorithm', 'find', 'detect'],
        response:
          'SIGNAL\'s Discovery Engine monitors 50,000+ emerging artists across Spotify, Apple Music, YouTube, TikTok, Instagram, and SoundCloud. It detects breakout patterns: viral growth, playlist additions, collaborator rises, and genre micro-trends — often weeks before traditional A&R.',
        followUps: ['How early can SIGNAL detect a breakout?', 'What platforms are monitored?'],
      },
      {
        keywords: ['recommend', 'suggest', 'match', 'similar'],
        response:
          'The engine can generate **similar artist recommendations** based on any artist you select. It analyzes sonic profiles, audience overlap, genre adjacency, and market positioning to find comparable emerging talent.',
        followUps: ['Can I discover artists similar to my current roster?', 'How accurate are recommendations?'],
      },
      {
        keywords: ['save', 'bookmark', 'watchlist', 'favorite', 'shortlist'],
        response:
          'Click the bookmark icon on any artist to add them to your **Watchlist**. Artists on your watchlist get enhanced monitoring — more frequent data refreshes and priority alerting.',
        followUps: ['Can I share my watchlist with my team?', 'What\'s the watchlist limit?'],
      },
    ],
  },

  '/analytics': {
    overview:
      '**Analytics** provides deep data exploration tools. Build custom charts, run statistical analyses, and export intelligence reports.',
    faq: [
      {
        keywords: ['chart', 'graph', 'visualize', 'plot', 'report'],
        response:
          'You can create custom visualizations: trend lines, bar charts, heat maps, scatter plots, and geographic distributions. Select metrics, time ranges, and filters to build your view. All charts can be exported as PNG or embedded in reports.',
        followUps: ['How do I create a custom chart?', 'What metrics can I chart?'],
      },
      {
        keywords: ['export', 'download', 'csv', 'pdf', 'data'],
        response:
          'Export options include: **CSV** (raw data), **PDF** (formatted report), **PNG** (chart image), and **JSON** (API-ready). For scheduled exports, set up a workflow with the Export action.',
        followUps: ['Can I schedule automatic exports?', 'What data is included in CSV export?'],
      },
      {
        keywords: ['compare', 'benchmark', 'vs', 'versus', 'competitor'],
        response:
          'The comparison tool lets you benchmark artists, genres, or markets side-by-side. Select up to 5 entities and choose metrics — SIGNAL generates a comparative analysis with visual overlays.',
        followUps: ['Can I compare against industry benchmarks?', 'How do I save comparisons?'],
      },
    ],
  },

  '/alerts': {
    overview:
      '**Alerts** is your intelligence notification center. Configure what SIGNAL watches for and how you get notified.',
    faq: [
      {
        keywords: ['create', 'configure', 'set up', 'new alert', 'custom'],
        response:
          'To create a custom alert: click "New Alert Rule," choose a trigger (score threshold, growth spike, genre trend, etc.), set conditions, and select notification channels (in-app, email, Slack). Alerts can monitor individual artists, entire genres, or global trends.',
        followUps: ['What triggers are available?', 'Can I set alert priorities?'],
      },
      {
        keywords: ['email', 'slack', 'webhook', 'notification', 'channel'],
        response:
          'Alert channels available: **In-App** (notification bell), **Email** (daily digest or instant), **Slack/Discord** (via webhook), and **SMS** (for critical alerts only). Configure channels in Settings > Notifications.',
        followUps: ['How do I connect Slack?', 'Can I get a daily alert summary?'],
      },
      {
        keywords: ['mute', 'silence', 'pause', 'disable', 'snooze'],
        response:
          'You can snooze alerts for 1h, 4h, 24h, or indefinitely. Muted alerts are still logged but won\'t notify you. Use this during focused work periods or non-business hours.',
        followUps: ['Can I set quiet hours?', 'How do I view muted alerts?'],
      },
    ],
  },

  '/reports': {
    overview:
      '**Reports** is your executive briefing center. Generate, schedule, and share intelligence reports with stakeholders.',
    faq: [
      {
        keywords: ['generate', 'create', 'new report', 'build'],
        response:
          'To generate a report: select a template (Weekly Briefing, Artist Deep Dive, Market Analysis, Competitive Landscape), choose the data scope, and click Generate. SIGNAL\'s Writer agent drafts the report with charts, analysis, and executive summary.',
        followUps: ['What templates are available?', 'Can I customize report templates?'],
      },
      {
        keywords: ['schedule', 'auto', 'recurring', 'weekly', 'monthly'],
        response:
          'You can schedule reports to be generated automatically: daily, weekly, or monthly. Scheduled reports can be emailed directly to stakeholders or saved to your report library.',
        followUps: ['Can I add recipients to scheduled reports?', 'What format are scheduled reports?'],
      },
      {
        keywords: ['pdf', 'download', 'share', 'export', 'email'],
        response:
          'Reports can be exported as **PDF** (print-ready), **Markdown** (editable), or **HTML** (interactive web view). You can share via email, get a shareable link, or add to a shared workspace.',
        followUps: ['Can I brand reports with my logo?', 'Are reports bilingual?'],
      },
    ],
  },

  '/contracts': {
    overview:
      '**Contracts** manages your contract intelligence lifecycle — from drafting to signature to compliance monitoring.',
    faq: [
      {
        keywords: ['create', 'draft', 'new contract', 'template'],
        response:
          'Use the "New Contract" button to start drafting. Choose a template type (Artist Agreement, Licensing Deal, Management Contract) and SIGNAL\'s Legal agent will generate a compliant draft with key clauses pre-populated based on industry standards.',
        followUps: ['What templates are available?', 'Can I upload my own templates?'],
      },
      {
        keywords: ['review', 'clause', 'risk', 'compliance', 'legal'],
        response:
          'The **Legal Harness** agent reviews contracts for: compliance risks, unfavorable clauses, missing terms, and regulatory issues. It compares against your predefined policies and flags anything that requires human attention.',
        followUps: ['How long does a review take?', 'What does the agent check for?'],
      },
      {
        keywords: ['sign', 'e-sign', 'digital signature', 'approve'],
        response:
          'Contracts move through stages: Draft → Legal Review → Artist Review → Signing → Active. Digital signatures are supported through integrated e-signature providers. Each stage requires human approval — agents cannot sign contracts.',
        followUps: ['What e-signature providers are supported?', 'How do I send for signature?'],
      },
      {
        keywords: ['track', 'status', 'pipeline', 'negotiation'],
        response:
          'The Signing Pipeline shows every contract\'s current stage, time in stage, and any blockers. You can filter by stage, priority, or responsible party. Contracts approaching deadlines are highlighted.',
        followUps: ['Can I set contract deadlines?', 'How do I reassign a contract?'],
      },
    ],
  },

  '/signings': {
    overview:
      '**Signing Pipeline** tracks every artist deal from first offer to signed contract. Full visibility into your deal flow.',
    faq: [
      {
        keywords: ['stage', 'step', 'progress', 'where', 'status'],
        response:
          'Pipeline stages: **Discovery** → **Initial Contact** → **Meeting** → **Offer** → **Negotiation** → **Legal Review** → **Signing** → **Announced**. Each stage shows time elapsed and any blockers.',
        followUps: ['How do I move a deal to the next stage?', 'What happens when a deal is stuck?'],
      },
      {
        keywords: ['offer', 'value', 'amount', 'budget', 'deal'],
        response:
          'Offer details — advance, royalty split, term length, territory — are visible in each deal card. SIGNAL can suggest competitive offer ranges based on artist score, market comps, and your budget parameters.',
        followUps: ['How does SIGNAL suggest offer values?', 'Can I compare offers?'],
      },
      {
        keywords: ['priority', 'hot', 'urgent', 'focus'],
        response:
          'Deals can be tagged as "Hot" (competitive pressure), "Priority" (strategic importance), or "Urgent" (time-sensitive deadline). Priority deals rise to the top of your pipeline and trigger enhanced monitoring.',
        followUps: ['Can I set automated priority rules?', 'What makes a deal hot?'],
      },
    ],
  },

  '/war-rooms': {
    overview:
      '**War Rooms** are high-stakes strategic spaces for competitive negotiations, crisis management, and critical decisions. Real-time collaboration with your full intelligence stack.',
    faq: [
      {
        keywords: ['create', 'new', 'open', 'launch'],
        response:
          'To open a War Room: click "New War Room," name your operation, select the target artist or situation, and invite team members. The War Room automatically pulls all relevant intelligence — dossier, alerts, market data, deal status.',
        followUps: ['Who can I invite to a War Room?', 'Can I have multiple War Rooms?'],
      },
      {
        keywords: ['collaborate', 'team', 'chat', 'comment', 'note'],
        response:
          'War Rooms include: a team chat, shared annotations on artist data, decision log, and action items. All team members see updates in real time. Every action is logged for post-operation review.',
        followUps: ['Can I add external users?', 'Are War Rooms recorded?'],
      },
      {
        keywords: ['timer', 'countdown', 'deadline', 'urgency'],
        response:
          'Critical operations can have a countdown timer — for competitive signing deadlines, offer expirations, or event-driven opportunities. The timer is visible to all team members and triggers escalation alerts.',
        followUps: ['Can I extend a timer?', 'What happens when time runs out?'],
      },
    ],
  },

  '/market': {
    overview:
      '**Market Intelligence** gives you the macro view — genre trends, regional heat maps, competitive landscape, and industry forecasts.',
    faq: [
      {
        keywords: ['genre', 'trend', 'popular', 'rising', 'declining'],
        response:
          'The genre trends view shows which genres are gaining/losing market share, with projections for next quarter. SIGNAL tracks 23 genres across 50+ markets. Drill into any genre to see top artists, key markets, and demographic breakdowns.',
        followUps: ['What are the top 5 rising genres?', 'Can I see genre trends by region?'],
      },
      {
        keywords: ['region', 'country', 'city', 'geography', 'map'],
        response:
          'The geographic heat map shows talent density, market activity, and growth regions. Zoom from global view down to city-level intelligence. Color intensity represents SIGNAL\'s composite "Opportunity Index."',
        followUps: ['What is the Opportunity Index?', 'Which cities have the most emerging talent?'],
      },
      {
        keywords: ['competitor', 'label', 'rival', 'other', 'industry'],
        response:
          'The competitive landscape section tracks other labels\' signing activity, A&R moves, and market positioning. See who\'s signing whom, for how much, and in which genres. This data is aggregated from public announcements and industry sources.',
        followUps: ['How current is competitor data?', 'Can I get alerts on competitor moves?'],
      },
    ],
  },

  '/playlists': {
    overview:
      '**Playlist Monitor** tracks your artists\' performance on every major playlist platform — Spotify, Apple Music, YouTube Music, and more.',
    faq: [
      {
        keywords: ['track', 'monitor', 'playlist', 'spotify', 'apple'],
        response:
          'SIGNAL monitors playlist additions, drops, and position changes for all your tracked artists. See which playlists drive the most streams, which curators are most influential, and how playlist activity correlates with overall growth.',
        followUps: ['How many playlists are tracked?', 'Can I track playlists by genre?'],
      },
      {
        keywords: ['curator', 'editorial', 'algorithmic', 'user', 'type'],
        response:
          'Playlists are categorized: **Editorial** (platform-curated, highest impact), **Algorithmic** (personalized, high volume), **User/Indie** (community-curated, niche), and **Brand** (corporate, emerging). Each category has different growth implications.',
        followUps: ['Which playlist type drives the most growth?', 'How do I pitch to editorial curators?'],
      },
      {
        keywords: ['alert', 'added', 'dropped', 'movement', 'change'],
        response:
          'You\'ll receive alerts when: an artist is added to an editorial playlist, dropped from a key playlist, or moves significantly in position. Configure threshold-based alerts for playlist changes.',
        followUps: ['Can I get alerts for specific playlists?', 'How do I view playlist history?'],
      },
    ],
  },

  '/finance': {
    overview:
      '**Financial View** provides budget intelligence, deal economics, and financial forecasting for your A&R operations.',
    faq: [
      {
        keywords: ['budget', 'spend', 'cost', 'expense', 'allocated'],
        response:
          'The budget overview shows: allocated vs. spent across deal types, artist categories, and time periods. Track advance payments, royalty projections, and recoupment status. All figures are in your configured currency.',
        followUps: ['Can I set budget limits?', 'How do I forecast future spend?'],
      },
      {
        keywords: ['roi', 'return', 'value', 'projection', 'forecast'],
        response:
          'SIGNAL computes projected ROI for each signed artist based on: advance amount, streaming projections, touring potential, brand partnership estimates, and historical comparables. ROI is shown as a multiple and as an annual percentage.',
        followUps: ['How accurate are ROI projections?', 'What data drives projections?'],
      },
      {
        keywords: ['report', 'export', 'statement', 'summary'],
        response:
          'Financial reports can be generated: Deal Summary, Budget vs. Actual, ROI Analysis, and Cash Flow Projection. Export as PDF (board-ready) or CSV (for your finance team).',
        followUps: ['Can I schedule financial reports?', 'Who can access financial data?'],
      },
    ],
  },

  '/settings': {
    overview:
      '**Settings** is where you configure SIGNAL to work your way — team management, integrations, notification preferences, and system configuration.',
    faq: [
      {
        keywords: ['team', 'user', 'invite', 'member', 'role', 'permission'],
        response:
          'Go to **Team** to invite members, assign roles (Admin, Analyst, Viewer, Finance), and manage permissions. Each role has predefined access levels. You can also create custom roles with specific module permissions.',
        followUps: ['What are the default roles?', 'Can I restrict access to specific modules?'],
      },
      {
        keywords: ['integration', 'connect', 'api', 'slack', 'spotify', 'webhook'],
        response:
          'SIGNAL integrates with: Spotify for Artists, Apple Music for Artists, YouTube Analytics, Slack/Discord, Google Drive, DocuSign, and more. Visit the **Integrations** tab to connect services. Each integration has its own configuration page.',
        followUps: ['How do I connect Spotify?', 'Can I build custom integrations?'],
      },
      {
        keywords: ['billing', 'plan', 'upgrade', 'subscription', 'license'],
        response:
          'Your current plan and usage stats are shown here. Upgrade to access more artist slots, team members, or advanced features. Enterprise plans include dedicated support, custom integrations, and SLA guarantees.',
        followUps: ['What\'s included in my current plan?', 'How do I upgrade?'],
      },
      {
        keywords: ['security', 'password', 'two-factor', '2fa', 'sso'],
        response:
          'Security settings include: password policy, two-factor authentication (2FA), SAML/SSO for enterprise, session management, and API key management. Enable 2FA for all team members handling sensitive deal data.',
        followUps: ['How do I enable SSO?', 'Can I rotate API keys?'],
      },
    ],
  },
};

// ─── General knowledge (cross-page) ──────────────────────────────────

const GENERAL_FAQ: KnowledgeEntry[] = [
  {
    keywords: ['hello', 'hi', 'hey', 'hola', 'start', 'begin', 'help', 'what can you do', 'empezar', 'ayuda', 'comenzar'],
    response:
      '👋 Hi! I\'m **SIGNAL Assist**, your AI intelligence guide. I can help you:\n\n• **Navigate** any module — explain what\'s on the page\n• **Interpret data** — scores, KPIs, trends\n• **Answer questions** — about artists, deals, alerts\n• **Guide workflows** — creating missions, reports, contracts\n\nJust tell me what you\'re working on or ask me anything. I adapt to your experience level — from first steps to advanced strategy.',
    followUps: ['How do I get started?', 'What can SIGNAL do?', 'Explain the dashboard'],
  },
  {
    keywords: ['tutorial', 'onboarding', 'guide', 'walkthrough', 'getting started', 'tutorial', 'guía', 'primeros pasos', 'introducción'],
    response:
      '**Getting Started with SIGNAL**\n\n1️⃣ **Mission Control** — Start here for your daily overview\n2️⃣ **Artist Radar** — Browse your artist intelligence\n3️⃣ **Discovery Engine** — Find emerging talent\n4️⃣ **Command Center** — Deploy your first agent mission\n5️⃣ **Reports** — Generate your first briefing\n\nPro tip: Use the **search bar** (top of screen) to instantly jump to any module or artist. What would you like to explore first?',
    followUps: ['Explain the sidebar navigation', 'What should I do first?', 'How do I track an artist?'],
  },
  {
    keywords: ['bilingual', 'español', 'spanish', 'english', 'language', 'translate'],
    response:
      'SIGNAL is fully bilingual in **English** and **Spanish**. All reports, alerts, and agent communications can be generated in either language. The platform UI is currently in English, but agent outputs respect your language preference.\n\n_SIGNAL es completamente bilingüe en inglés y español. Todos los informes, alertas y comunicaciones de agentes se pueden generar en cualquiera de los dos idiomas._',
    followUps: ['How do I change my language preference?', 'Can agents respond in Spanish?'],
  },
  {
    keywords: ['data', 'source', 'api', 'integration', 'where', 'streaming', 'platform'],
    response:
      'SIGNAL aggregates intelligence from: **Spotify**, **Apple Music**, **YouTube/TikTok**, **SoundCloud**, **Instagram**, **Shazam**, and **industry databases**. Data is collected via official APIs and public sources. Each data point is labeled with its source and freshness timestamp.',
    followUps: ['How fresh is the data?', 'Can I add my own data sources?'],
  },
  {
    keywords: ['privacy', 'security', 'data protection', 'gdpr', 'confidential'],
    response:
      'SIGNAL is built with enterprise-grade security: **end-to-end encryption**, **SOC 2 compliance**, **GDPR-ready**, and **role-based access control**. Your deal data, artist intelligence, and strategic information are never shared outside your organization. Full security documentation is available in Settings.',
    followUps: ['Is my data used to train AI models?', 'Can I get a security audit report?'],
  },
  {
    keywords: ['shortcut', 'keyboard', 'hotkey', 'efficiency', 'power user', 'tips'],
    response:
      '**Power User Shortcuts:**\n\n• `Cmd/Ctrl + K` — Open command palette\n• `Cmd/Ctrl + ,` — Settings\n• `Cmd/Ctrl + B` — Toggle sidebar\n• `?` — Show all shortcuts\n• `Cmd/Ctrl + Shift + F` — Global search\n\nPro tip: You can type `/` anywhere to quickly search and navigate.',
    followUps: ['Can I customize shortcuts?', 'What is the command palette?'],
  },
  {
    keywords: ['mobile', 'phone', 'tablet', 'app', 'remote'],
    response:
      'SIGNAL is fully responsive and works on **tablets** and **large phones** in landscape mode. A dedicated mobile app is on the roadmap. For now, the web interface adapts to your screen size with a collapsible sidebar and touch-friendly controls.',
    followUps: ['Is there an iOS app?', 'Can I get push notifications on mobile?'],
  },
  {
    keywords: ['support', 'contact', 'help', 'ticket', 'email', 'phone'],
    response:
      'Need help beyond what I can provide?\n\n• **Documentation** — Full docs in Settings\n• **Email** — support@signal.agent\n• **Enterprise Support** — Available 24/7 for Enterprise plans\n• **Community** — Join the SIGNAL user community\n\nYour Account Manager is also available for personalized assistance.',
    followUps: ['How do I reach my Account Manager?', 'What are Enterprise support hours?'],
  },
];

// ─── Main query engine ───────────────────────────────────────────────

export function generateResponse(
  userMessage: string,
  page: string
): { response: string; suggestions: string[] } {
  const msg = userMessage.toLowerCase().trim();

  // 1. Try page-specific FAQ first
  const pageKnowledge = PAGE_KNOWLEDGE[page];
  if (pageKnowledge) {
    // Check overview requests
    if (
      msg.includes('what') && (msg.includes('this') || msg.includes('here') || msg.includes('page') || msg.includes('module')) ||
      msg.includes('explain') || msg.includes('overview') || msg.includes('tell me about')
    ) {
      const suggestions = pageKnowledge.faq.slice(0, 3).flatMap(f => f.followUps ?? []);
      return {
        response: pageKnowledge.overview,
        suggestions: suggestions.slice(0, 3),
      };
    }

    // Match against page FAQ keywords
    for (const entry of pageKnowledge.faq) {
      if (entry.keywords.some(k => msg.includes(k))) {
        return {
          response: entry.response,
          suggestions: entry.followUps?.slice(0, 3) ?? [],
        };
      }
    }
  }

  // 2. Try general FAQ
  for (const entry of GENERAL_FAQ) {
    if (entry.keywords.some(k => msg.includes(k))) {
      return {
        response: entry.response,
        suggestions: entry.followUps?.slice(0, 3) ?? [],
      };
    }
  }

  // 3. Fallback — contextual intelligent response
  const pageName = page.split('/').filter(Boolean).pop() || 'dashboard';
  const fallbacks: Record<string, string> = {
    dashboard: 'Mission Control',
    'command-center': 'Command Center',
    workflows: 'Workflows',
    agents: 'Agent Performance',
    artists: 'Artist Radar',
    discovery: 'Discovery Engine',
    analytics: 'Analytics',
    alerts: 'Alerts',
    reports: 'Reports',
    contracts: 'Contracts',
    signings: 'Signing Pipeline',
    'war-rooms': 'War Rooms',
    market: 'Market Intelligence',
    playlists: 'Playlist Monitor',
    finance: 'Financial View',
    settings: 'Settings',
  };
  const label = fallbacks[pageName] || 'this page';

  return {
    response: `I understand you're asking about something on **${label}** that I don't have a specific answer for yet. Here's what I can tell you:\n\nThis module is designed to help you with ${pageName === 'dashboard' ? 'executive oversight and real-time intelligence monitoring' : 'your specific intelligence tasks in this area'}.\n\nTry asking me something more specific, or I can help you with:\n• Understanding the data on this page\n• Navigating to another module\n• General questions about SIGNAL's capabilities`,
    suggestions: [
      'What can I do here?',
      'Show me around',
      'How do I get started?',
    ],
  };
}
