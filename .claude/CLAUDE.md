# Project memory (owner: benkas418)

Loaded in every Claude Code session on this repository. Update it when a decision,
a tool or a lesson must survive the session. Keep it under 150 lines.

## Owner and projects

- The owner writes in French; answer in French. Preferences: direct, verified results,
  honest limits, no automatic agreement.
- **football-intel/**: football prediction platform (Python, FastAPI, PostgreSQL).
  Source of truth: `football-intel/docs/DECISIONS.md` (D1–D56), `docs/RESULTS.md`,
  `docs/DATA_SOURCES.md`. Active model `routed_competition`; it equals the market and
  has no measured edge (CLV −2.5 % at average price, D54).
- **PitUp**: delivery marketplace in Lubumbashi (customers, partner shops, couriers).
  Not in this repository. Use the `prediction-modeling` skill for what to log.
- Work branches: `ccr-4d6bcf99-mmbgxo` and `claude/branche-higgsfield-974raq`; push both.

## Skills in .claude/skills (117) — pick by theme

38 come from master (marketingskills v2: copywriting, ad-creative, social, sms, offers,
referrals, onboarding, analytics, aso…; skill-creator, brainstorming, deep-research…).
Where names overlapped, master's newer version was kept. Main ones added by us:

| Theme | Skills |
|---|---|
| Agents, AI apps, automation | ai-agent-engineering, vercel-ai-sdk, activepieces-automation, agent-designer, agent-workflow-designer, rag-architect, senior-prompt-engineer |
| Claude Code itself | claude-code-workflow, karpathy-guidelines |
| Football data and models | football-data-sources, prediction-modeling, statistical-analyst, senior-data-scientist, experiment-designer, pandas-pro |
| Video (Higgsfield) | seedance-video (our own), html-reel, video-to-superprompt, video-content-strategist, cinematic-scroll-site |
| Marketing, copy, social | copywriting, copy-editing, content-strategy, content-humanizer, social-content, social-media-manager, social-media-analyzer, ad-creative, paid-ads, marketing-psychology, launch-strategy, referral-program, pricing-strategy, marketing-context, marketing-ideas |
| Growth, product (PitUp) | page-cro, signup-flow-cro, onboarding-cro, churn-prevention, ab-test-setup, analytics-tracking, campaign-analytics, local-seo-manager, app-store-optimization, product-discovery, product-analytics, roast |
| Design, UI/UX, 3D | design-taste-frontend, no-ai-design-slop, audit-ai-design-slop, ui-design-system, ux-researcher-designer, landing-page, pricing-page, tailwindcss, gsap, animation-systems, build-awwwards-quality-sites, cinematic-scroll-storytelling, threejs, build-threejs-scroll-worlds, webgl-3d-object, 3d-orbit-inspect-demo, react-3d-web, design-first-ui-prompting |
| Code, data, deploy | python-pro, fastapi-expert, postgres-pro, sql-pro, database-designer, typescript-pro, javascript-pro, react-expert, nextjs-developer, react-native-expert, flutter-expert, api-designer, debugging-wizard, test-master, secure-code-guardian, devops-engineer, docker-development, ci-cd-pipeline-builder, data-quality-auditor |

Handoffs: skill `handoff-notes` writes notes to `.claude/handoffs/` (committed). Read the
newest one when the owner says "reprends où on s'est arrêtés". Project plugins
(`.claude/plugins/*`, incl. session-handoff) do NOT load in fresh cloud sessions.

## Repositories the owner sent (2026-10-29) and their status

| Repository | Status |
|---|---|
| Leonxlnx/taste-skill | Installed as design-taste-frontend |
| OneFootball scraper idea | Integrated in football-intel (D50) |
| openfootball/football.json, eddwebster/football_analytics, hudl/open-data, soccerdata, worldfootballR, understat | Evaluated; knowledge in football-data-sources; xG tested, no gain (D55) |
| tunjayoff/sofascore_scraper | Tool; Sofascore blocks cloud IPs; residential proxy approved (D56), needs `SOFASCORE_CLIENT__PROXY` |
| multica-ai/andrej-karpathy-skills, alirezarezvani, Jeffallan, MengTo skills | 74 MIT skills installed |
| ComposioHQ, Seedance skill repos (no licence) | Replaced by our own seedance-video; 3 Composio skills not kept |
| microsoft/ai-agents-for-beginners, bojieli/ai-agent-book | Distilled into ai-agent-engineering |
| shanraisshan/claude-code-best-practice | Distilled into claude-code-workflow |
| vercel/ai, activepieces, playcanvas/react, 3D portfolio, Astra prompt repos | Distilled into vercel-ai-sdk, activepieces-automation, react-3d-web, cinematic-scroll-site |
| UppuluriKalyani/ML-Nexus | Distilled into prediction-modeling (random splits = main mistake) |
| Alishahryar1/free-claude-code | Tool (proxy to other model providers); reinstall with the setup script |
| David-E-Kay/claude-session-handoff | Vendored in .claude/plugins (works locally only); replaced in cloud by skill handoff-notes |
| ww-w-ai/super-token-saver | Not enabled: injects instructions that force sub-agent delegation and edits ~/.claude/settings.json; its report command can publish a public gist. Install on a local machine only if wanted |
| sajidmahamud835/MarketSync-EA | Rejected: its "AI" returns random stop-loss/take-profit; would place real trades |
| higgsfield-ai/higgsfield, o3de, ai-agent frameworks lists | Not relevant (GPU training framework; game engine — owner may revisit) |
| 3641397194-wq/gpt6-Astra, claude-code-best/claude-code, asgeirtj/system_prompts_leaks | Refused: jailbreak injector with unknown relay; unauthorised reconstruction of proprietary code; leaked confidential prompts |

## Tools outside the repository

The cloud container is reset between sessions. Reinstall the external tools with
`football-intel/scripts/claude-cloud-setup.sh` (or set it as the environment setup script).

## Lessons (do not repeat)

- `pkill -f`/`pgrep -f` with a pattern that also appears in the current command kills
  the current shell (exit 144). Find PIDs in one call, kill them in another.
- uv in the image is old (0.11): install a recent uv with pip in a venv for Python 3.14.
- sofascore_scraper crashes on Python 3.13 (`_ThreadHandle`); use Python 3.14.
- Big GitHub repos (hudl/open-data) stall through the proxy; fetch only needed folders.
- Shot/feature files change column names between seasons: check coverage per period.
- Environment setup script runs before the repo exists: it must be self-contained and end with `exit 0`.
- Never trust a "best price" CLV or a random-split score; compare on recent data.
