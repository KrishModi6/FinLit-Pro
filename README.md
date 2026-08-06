# 📈 Stock Guide

A free, structured stock market course for students, built as an IB CAS project and live at
**[finlitpro.org](https://www.finlitpro.org/)**.

> "I made this course to help my fellow classmates and other students across the world learn about stocks."
>
> "This website I created has the potential to help you learn what I've learned in my time and more."

Modelled on the open, module-based structure of [USACO Guide](https://usaco.guide/): three difficulty
tracks, open navigation, a quiz at the bottom of every lesson, and progress that follows you around.

![React](https://img.shields.io/badge/React-18-61dafb.svg)
![Vite](https://img.shields.io/badge/Vite-5-646cff.svg)
![Tailwind](https://img.shields.io/badge/Tailwind-3-38bdf8.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## The course

| Track | Title | Covers |
| --- | --- | --- |
| **Beginner** | How Stocks Actually Work | What a share is, exchanges, why prices move, brokerages, quotes, indices, market cycles, dividends, and a full walkthrough of buying a first share |
| **Intermediate** | Stable vs Unstable Stocks | Blue chips and dividend aristocrats, beta, fundamental analysis, technical analysis, ETFs and diversification, why you keep a stable core, and a GameStop-vs-boring case study |
| **Hard** | Risky Bets: When to Take Them, When to Walk Away | High-risk instruments, options mechanics, position sizing, when a bet is defensible, GameStop and Enron post-mortems, investor psychology, and one options trade run to both endings |

Nothing is gated. The recommended order is conveyed by numbering, not by locking doors.

## The Simulator

A separate section at `/simulator`, deliberately outside the course: no progress tracking, its own
sub-nav. Six tools, each carried over from the previous Streamlit version of the app and rebuilt to run
entirely in the browser.

| Tool | What it does |
| --- | --- |
| Market Explorer | Real price history for any ticker, with moving averages, RSI, volatility and max drawdown |
| AI Predictor | Monte Carlo projection built from a stock's own historical drift and volatility |
| AI Advisor | Chat grounded in the course; explains mechanics and refuses personalised advice |
| Growth Calculator | Compound projection with monthly contributions, plus what a fee costs over decades |
| Portfolio Builder | Weights, weighted beta, sector concentration and over-exposure warnings |
| Stock Analyzer | A transparent six-criteria stability read from numbers off a quote page |
| Compare | Two companies side by side with a plain-English read of each gap |
| Options Payoff | Break-even, maximum loss and the payoff ladder next to just buying shares |
| Scenario Projector | 2,000-run Monte Carlo showing the spread of outcomes, not one tidy number |

The last six work entirely on numbers **you type in**: no network, nothing that can break. The first
three need the two serverless functions below.

## Serverless functions

Two endpoints in `api/`, run by Vercel. `npm run dev` serves them too, via a small middleware plugin
in `vite.config.js`, so the market tools work locally without deploying.

| Endpoint | Key required | What it does |
| --- | --- | --- |
| `GET /api/quote?symbol=AAPL&range=1y` | No | Proxies Yahoo Finance chart data. Exists because Yahoo sends no CORS headers, so the browser cannot call it directly. Validates the ticker against a strict pattern before building the outbound URL, and edge-caches for 5 minutes. |
| `POST /api/advisor` | **Yes** | Streams a Claude reply. Uses `claude-opus-5` via the official `@anthropic-ai/sdk`, with a system prompt grounded in the course that refuses personalised investment advice. |

### Enabling the AI Advisor

Set `ANTHROPIC_API_KEY` in **Vercel → Settings → Environment Variables**. Do not put it in the repo.
For local development, put it in `.env.local` (gitignored).

Without the key the endpoint returns a clear `503` and the UI shows that message, so the rest of the
site is unaffected.

The risk-tolerance questionnaire that used to be a standalone tool now lives in the course as the
Beginner lesson [Know Your Risk Profile](src/content/beginner/KnowYourRiskProfile.jsx), because the score
means nothing without the lesson explaining tolerance versus capacity around it.

## Tech stack

- **React 18** + **React Router 6**: SPA, no backend
- **Vite 5**: dev server and build
- **Tailwind CSS 3**: styling, with a `.lesson` typography layer so lesson content is written as plain
  semantic HTML
- **LocalStorage**: all progress, quiz scores, saved exercise answers and the theme preference

There is no server, no database, no account, and no analytics beyond Vercel's page-view counter. Progress
never leaves the reader's browser.

## Running it

```bash
npm install
npm run dev
```

Then open the URL Vite prints (default `http://localhost:5173`).

Or open it in a **GitHub Codespace**: `.devcontainer/devcontainer.json` installs dependencies and
starts the dev server on port 5173 automatically. It also prompts for an optional
`ANTHROPIC_API_KEY` Codespace secret, which only the AI Advisor needs.

```bash
npm run build     # regenerates the sitemap, then builds to dist/
npm run preview   # serve the production build locally
```

## Project structure

```
index.html                     Vite entry + all SEO metadata + pre-paint theme script
vercel.json                    Vite build config + SPA rewrites
tailwind.config.js             Design tokens (ink scale, track colours)
scripts/
  generate-sitemap.mjs         Builds public/sitemap.xml from the curriculum
public/                        Static assets copied verbatim (robots, sitemap, og-image)
src/
  main.jsx                     Root render, providers, router
  App.jsx                      Route table
  index.css                    Tailwind layers + `.lesson` typography
  context/
    ProgressContext.jsx        Completion, quiz scores, per-track stats (LocalStorage)
    ThemeContext.jsx           Light/dark, persisted
  data/
    curriculum.js              Single source of truth: tracks, modules, order, colours
    glossary.js                Every key term, powers /glossary and inline hover popovers
  components/
    layout/
      SiteLayout.jsx           Navbar + footer (home, dashboard, glossary, 404)
      CourseLayout.jsx         Navbar + sidebar + footer (tracks and lessons)
      Navbar.jsx  Sidebar.jsx  Footer.jsx  ScrollToTop.jsx
    ui/
      Quiz.jsx                 End-of-lesson quiz with instant feedback
      Callout.jsx              did-you-know / real-talk / warning / example / note
      KeyTerm.jsx              Inline definition card
      Term.jsx                 Hover-to-define inline glossary term
      TryIt.jsx                Hands-on exercise with an auto-saving answer box
      ProgressBar.jsx          Bar + ring variants
      Icons.jsx                Inline SVG icon set
  pages/
    Home.jsx  Dashboard.jsx  TrackPage.jsx  ModulePage.jsx  Glossary.jsx  NotFound.jsx
  content/
    index.js                   Module id → lazily-imported lesson component
    beginner/  intermediate/  hard/    One .jsx file per lesson
```

### Adding a lesson

1. Add an entry to the relevant track's `modules` array in `src/data/curriculum.js`.
2. Create `src/content/<track>/<Component>.jsx`.
3. Register it in `src/content/index.js` under the module id (`<track>/<slug>`).

A lesson component receives one prop, `moduleId`, and forwards it to `<Quiz>` and `<TryIt>` so their
saved state is scoped correctly. It ends with `<Quiz moduleId={moduleId} questions={QUESTIONS} />`.

## Deployment

Vercel builds from this repo and serves `dist/`. The SPA rewrite in `vercel.json` sends every
non-file path to `index.html` so deep links like `/hard/options-basics` work on a hard refresh.

The rewrite source is `/((?!api/).*)` rather than `/(.*)`: the negative lookahead keeps `/api/*`
on the serverless functions instead of handing them `index.html`.

> `vercel.json` is validated against a strict schema **before** the build starts, and unknown keys
> are rejected. A stray `"comment"` field inside a rewrite object fails the deployment with no
> build logs at all, which looks like an outage rather than a config error. Keep it to the
> documented keys; JSON comments are not allowed either.

## ⚠️ Disclaimer

This site is **educational material, not financial advice**. Nothing in it is a recommendation to buy or
sell any security. Company and ticker names appear only as real-world illustrations of concepts.
Investing involves risk, including the permanent loss of capital. Do your own research and consult a
licensed financial professional before investing.

## The previous version

finlitpro.org used to serve a Streamlit app, also called FinLit Pro, with a different set of
features: an AI Predictor built on Monte Carlo simulation, a GPT-backed AI Advisor, live technical
analysis charts, and a portfolio tracker.

That app is not gone. It has been archived, intact and still runnable, in a separate private
repository: **[KrishModi6/finlit-pro-legacy](https://github.com/KrishModi6/finlit-pro-legacy)**.
The Playwright keep-alive that stops Streamlit Community Cloud hibernating it moved there too, so
`finlitpro.streamlit.app` keeps running independently of this site.

Nothing Python remains in this repository.

## 🎓 IB CAS

- **Creativity**: designing and building the platform
- **Activity**: ongoing research into markets and writing the curriculum
- **Service**: free, open financial education for other students

## License

MIT.
