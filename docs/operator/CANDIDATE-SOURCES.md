# Candidate source scouting — PR #21 / Task B

**Status:** triage only; no adapter or fetcher is proposed here. **Observed 2026-10-02 UTC.**
Pages and `robots.txt` were retrieved as single cooperative HTML samples with the
Arena page fetcher. No solver, proxy, browser challenge bypass, CAPTCHA
workaround, login, or paid access was used. A successful sample is not a
production approval.

**Sandbox receipt for the new seed pass (2026-10-02 UTC):** direct `curl` from
this checkout was attempted against every supplied seed page and its relevant
`robots.txt`. Every attempt returned `HTTP 000` with
`OpenSSL SSL_ERROR_SYSCALL` (zero bytes). Therefore the seed rows below are
**UNVERIFIED from the sandbox**, even where the separate page fetcher returned
content. They must not be promoted or fetched by a production adapter until a
cooperative sandbox fetch succeeds.

## Decision rules

- A source that cannot be fetched reliably is **not a production source**.
- Challenge-walled JS, login-gated, or otherwise non-reproducible sources are
  **training-only at most**. No paid access is to be purchased.
- A vote source needs a stable fixture/date/market/prediction and a settlement
  trail. A price source needs an explicit bookmaker identity, selection, odds,
  capture time, and a cooperative page/API path. An odds-looking number without
  a book name is not a price donor.
- Any eventual vote donor must first run as a committed shadow for at least 30
  days and pass the existing independence yardstick: correlation `< 0.95`, pick
  agreement `< 95%`, and not dead weight on triple-covered fixtures. This is
  especially important because the current fb-zb overlap is **0.535 correlation
  / 60.6% pick agreement** (the existing `docs/operator/SOURCE-TRIAGE.md`
  receipt). Prefer a source that adds a genuinely different voice, not another
  odds-copying echo chamber.
- No row from this document enters the pick path. `scripts/auto_tickets.py`
  remains the sole owner of staking/tickets.

## Triage table

`robots` is assessed for the sampled URL, not as a blanket permission for every
future URL. `HTML` means the sample rendered useful server-side text; it does
not mean that high-rate crawling is acceptable.

| candidate / URL (sample) | language | reachable / robots cooperative? | fetchability class | observed data type | settlement path in sample | cooperative-fit verdict |
|---|---|---|---|---|---|---|
| [Betimate FR](https://betimate.com/fr/football-predictions/france/france-ligue-1) | French | Yes, HTML returned; `/robots.txt` has `User-agent: * Allow: /` for this path | cooperative HTML | 1X2 probability/pick, O/U 2.5, BTTS, predicted score; league links also expose today/tomorrow/yesterday views | Past/yesterday and live-score navigation is present; verify that the prediction and final result remain joinable before capture | **vote-source candidate**, shadow first; same operator has many locale mirrors, so de-duplicate by publisher before independence testing |
| [Legalbet ES](https://legalbet.es/pronosticos-deportivos/el-deporte-futbol/la-liga/) | Spanish | Yes, HTML returned; `robots` does not disallow the sampled league page (it does restrict account/admin/expert subpaths) | cooperative HTML | Expert 1X2, O/U, BTTS and team-total tips; bookmaker label and decimal quote; expert record/ROI | Sample links finalized fixtures to match pages and exposes expert history/results | **vote-source candidate**; bookmaker-labelled quotes are a possible price cross-check only, not a live price feed |
| [webPronostici](https://www.webpronostici.com/pronostici/italia/italia-serie-a/) | Italian | Yes, HTML returned; `robots` allows the public target and only blocks admin/system paths | cooperative HTML | Public table schema for 1X2, mixed, O/U, BTTS/no-BTTS and correct-score; `Book`, `Quota`, `Esito` columns; sample day had no active Serie A fixtures | `Esito` is explicitly in the table and league standings/results are public; historical coverage needs a second sample | **vote-source candidate**, especially for Italian coverage; price candidate only when the book name and capture date are retained |
| [SportyTrader BR](https://www.sportytrader.com/pt-br/palpites/futebol/brasil/brasileirao-serie-a-343/) | Brazilian Portuguese | Yes, HTML returned; `/pt-br/palpites` is not disallowed; `robots` blocks `/book`, `/async`, `/widgets` and account surfaces | cooperative HTML, with member prompts | Model 1X2 probability; match tips; separate bookmaker-labelled 1X2 odds links; live-results link | Public page links to live results and dated fixtures, but the sampled model rows were behind a `CRIAR CONTA` prompt and one displayed `Odd 0` | **price-source candidate** for explicitly named bookmaker rows after a freshness/zero-value audit; model vote data is shadow-only until the account prompt is proven irrelevant |
| [FootyStats TR](https://footystats.org/tr/predictions) | Turkish | Yes, HTML returned; `/tr/predictions` is allowed; robots asks for crawl delays for some agents and blocks API/user/premium-adjacent paths | cooperative HTML, dynamic extras but useful server-side rows | Community/team tips: 1X2, O/U 1.5/2.5/3.5, BTTS, corners, first-half and correct score; displayed odds but no reliable bookmaker identity in the sample | “Bahis takibi”/member pages imply tracked results; the public sample did not provide a complete immutable settlement row | **vote-source candidate** for a bounded shadow; **not** a price source without a named book and timestamp; do not buy Premium |
| [Scores24 CN](https://scores24.live/cn/soccer/m-03-10-2026-china-u23-uzbekistan-u23-prediction) | Simplified Chinese | Yes, HTML returned; robots permits current-year match pages for `*` and explicitly disallows feed/API paths | cooperative HTML | Editorial/model 1X2-ish tips, O/U, team totals, BTTS/trends, correct-score probabilities; named Bovada odds appear | Same page exposes H2H, recent results and match overview; settlement is available as a result page, but editorial tip/result linkage should be tested | **price-source candidate** only for named bookmaker rows, with a strict echo-chamber check; prediction text is a **vote-source shadow candidate**, never two votes by default |
| [SoccerVital Czechia](https://www.soccervital.com/table-czechia-first-league-soccer-results-and-prediction.html) | English page, Czech league | Yes, HTML returned; robots only disallows `/thisgo/`; sampled public league page is allowed | cooperative HTML | 1X2 odds, 1X2/1X/X2 tips, O/U direction, predicted score and confidence; broad Czech lower-league coverage | Strongest settlement surface in sample: public “Past Predictions” table links dated match pages with final scores and confidence | **vote-source candidate** for Czech coverage; odds have no bookmaker identity in sample, so not a price source |
| [Wettbasis Bundesliga](https://www.wettbasis.com/sportwetten-tipps/tipps-category/bundesliga-tipps) | German | Yes, HTML returned; robots does not disallow the sampled `/sportwetten-tipps/` path | cooperative HTML | German editorial/AI tips, 1X2, O/U, BTTS, handicap and bookmaker-labelled links; dated fixture cards | Archive is article-oriented; sample exposes fixture date and recent pages but no durable structured result field for every tip | **vote-source candidate** only as a low-volume shadow; no paid bookmaker navigation and no price ingestion from redirect links |
| [OneFootball DE Wetten](https://onefootball.com/de/wetten/tipps/deutschland-vs-serbien-01-10-2026) | German | Yes, HTML returned; robots only disallows admin/magazine/network, not the public betting article | cooperative HTML | Single-match editorial tip (handicap), bookmaker link, H2H, last-five results and article date | H2H/form results are present, but the article does not expose an immutable settled-tip field | **regime-labelled training-only** unless the operator can prove an append-only tip/settlement archive; not a production donor |
| [Football4Cast Japan](https://sports4cast.com/4casts/football4cast/japanese-football-predictions/) | English page, Japanese J1 coverage | Yes, HTML returned; robots allows `*` but explicitly disallows GPTBot/ClaudeBot/CCBot/Bytespider/etc. | cooperative HTML for a normal browser/operator, but **robots AI-training opt-out** | Predicted score/probability/verdict and a “Results & Predictions” section; no stable Japanese-language structured feed in sample | Public results table exists, but model-to-result linkage is not yet an auditable row contract | **reject for production** under the cooperative-only standing decision; do not crawl as a model-training donor while the robots opt-out applies |

## New seed pass — sandbox verification is mandatory

The following rows are the requested German/Spanish seeds. The **web-fetched
observations** are useful scouting evidence only; the sandbox column is the
decision gate. `UNVERIFIED` means no production use, no fetcher, and no vote or
price weight.

| candidate / URL actually checked | language | reachable from sandbox? | robots.txt cooperative? | fetchability class | observed data type | settlement path | verdict |
|---|---|---|---|---|---|---|---|
| [Bundesligatrend sample](https://www.bundesligatrend.de/mainz-gegen-gladbach-tipp-prognose-bundesliga-quoten-25-10-2024.html) | German | **UNVERIFIED** — sandbox `curl`: HTTP 000 / TLS `SSL_ERROR_SYSCALL` | Web-fetched robots allows the sample path; sandbox robots **UNVERIFIED** | Web fetcher showed cooperative HTML; sandbox class **UNVERIFIED** | 1X2 and O/U tip, predicted score, named NEO.bet/Bet365/Betano/Oddset quotes with quote timestamp | Article has fixture date and form, but the sample does not contain an immutable final settlement row; would need an append-only article/result join | **UNVERIFIED**; do not promote. If sandbox access is later proven, vote shadow first; named quotes are historical price cross-checks only |
| `https://wettforum.de` (supplied seed) | German | **UNVERIFIED** — sandbox HTTP 000 / TLS error | **UNVERIFIED** | **UNVERIFIED**; no verified page | No sandbox observation. A related page linked by Wettbasis is [Wettforum on sportwettenvergleich.net](https://www.sportwettenvergleich.net/wettforum/), which is a public community forum | Forum posts are mutable/user-attributed and do not provide a stable tip/result ledger in the checked sample | **UNVERIFIED / training-only at most**; noisy community posts are not a production vote or price donor |
| [Wettpoint Bundesliga tips](https://fussball.wettpoint.com/en/betting-tips/1-bundesliga_germany.html) | German/English UI | **UNVERIFIED** — sandbox HTTP 000 / TLS error; page fetcher redirected to a sparse Wettpoint home page | **UNVERIFIED** — robots request did not yield a usable robots document | **UNVERIFIED**; search evidence shows public HTML, but the exact path was not reproducibly fetched here | Search evidence shows 1X2 and O/U tips, historical results, H2H/statistics; no reliable named-book field in the checked evidence | Historical “Result” lines appear beside prior tips in search output, but the exact page contract and immutable joins were not verified | **UNVERIFIED**; do not promote until the exact archive path is sandbox-fetchable and settlement rows are proven |
| [FutbolPronosticos](https://www.futbolpronosticos.com/predicciones-de-futbol) | Spanish | **UNVERIFIED** — sandbox HTTP 000 / TLS error | Web-fetched robots exposes content-signal text but sandbox robots **UNVERIFIED**; no production AI-training permission inferred | Web fetcher showed cooperative server-side HTML; sandbox class **UNVERIFIED** | Daily 1X2, O/U, BTTS, double chance, exact score, percentages and some decimal odds; sample included an affiliate-linked 22Bet quote | Per-match “Pronostico” pages and today/tomorrow/result routes exist; an immutable append-only settled-tip field was not shown | **UNVERIFIED**; vote-source candidate only after sandbox and settlement audit; price-source candidate only when bookmaker identity, selection and timestamp are retained |
| [PronosticosFutbol.ai](https://pronosticosfutbol.ai/pronosticos-futbol-manana) | Spanish | **UNVERIFIED** — sandbox HTTP 000 / TLS error | Web-fetched robots: `User-agent: * Allow: /`, `Disallow: /api/`; sandbox robots **UNVERIFIED** | Web fetcher showed cooperative server-side HTML; sandbox class **UNVERIFIED** | 1X2, O/U, BTTS, double chance, Asian handicap, half-time and exact score with percentages; some pages show decimal odds | Dated match pages include finished/upcoming states and community agreement, but append-only settlement semantics need a historical sample | **UNVERIFIED**; vote-source candidate for bounded shadow only after sandbox verification; not a price donor without a named bookmaker per row |
| [SportyTrader ES sample](https://sportytrader.es/pronosticos/grecia-holanda-375935) | Spanish | **UNVERIFIED** — sandbox HTTP 000 / TLS error | Web-fetched robots allows public prediction paths but disallows `/book/`, `/async/`, `/widgets/`, member/account and redirect surfaces; sandbox robots **UNVERIFIED** | Web fetcher showed cooperative HTML with affiliate/member prompts; sandbox class **UNVERIFIED** | Model 1X2/O/U/BTTS probabilities plus named bookmaker odds (Bet365, Sportium, Luckia, 1xBet, William Hill, Interwetten, etc.), live-results and recent-results links | Public page contains match date, publication/modified time, result links and recent results; preserve the page snapshot because model text can be edited | **UNVERIFIED**; **price-source candidate** only after sandbox/freshness audit. Treat ES/FR/DE/IT/PT-BR locales as one SportyTrader publisher, never five votes |
| SportyTrader locale set — [ES sample](https://sportytrader.es/pronosticos/grecia-holanda-375935), existing [PT-BR sample](https://www.sportytrader.com/pt-br/palpites/futebol/brasil/brasileirao-serie-a-343/) | Spanish, Portuguese; FR/DE/IT not checked in this pass | ES/PT-BR sandbox HTTP 000; FR/DE/IT **UNVERIFIED** and not fetched from sandbox | ES robots reviewed by web fetcher; other locale robots **UNVERIFIED** | **UNVERIFIED** by sandbox; do not assume one locale's policy applies to another | Same publisher family: model probabilities, bookmaker-labelled odds, dated fixtures and result links; PT-BR sample also showed account/member prompts and an `Odd 0` hazard | Match pages and live-result links exist, but retain bookmaker, capture timestamp and locale; discard zero/missing odds | **UNVERIFIED / one publisher only**; price-source candidate after exact-locale checks, never independent vote expansion |

### Seed-pass independence and access decisions

- `futbolpronosticos.com`, `pronosticosfutbol.ai`, and SportyTrader are not
  independent merely because they are Spanish or show different markets. They
  need overlap testing against the existing fb-zb board before any shadow vote.
- SportyTrader locale pages are one publisher. The ES/PT-BR evidence does not
  authorize FR/DE/IT; each exact locale needs its own sandbox page and robots
  receipt.
- `wettforum.de` was not silently converted into a different domain. The
  related `sportwettenvergleich.net/wettforum/` forum was recorded as a lead,
  not as verification of the supplied seed.
- A web-search/page-fetch hit is not a sandbox receipt. All HTTP 000 seed rows
  remain unverified and are deliberately excluded from production.

## Triage notes

### Best first shadows

1. **SoccerVital** — the cleanest public Czech-language-market coverage and
   explicit past-prediction/result table. Its odds are not book-labelled, so it
   is a vote donor, not a price donor.
2. **Legalbet ES** — public expert history plus Spanish 1X2/OU/BTTS coverage.
   The expert pages and fixture pages must be captured together so a later
   correction cannot rewrite a prior tip.
3. **webPronostici IT** — the schema is unusually close to the required
   settlement shape (`Prono`, `Quota`, `Book`, `Esito`), but the sample had no
   active Serie A rows; recheck on a match day before spending integration
   effort.
4. **FootyStats TR** — useful Turkish-market breadth, but community/member
   attribution and the lack of bookmaker identity make it a lower-confidence
   vote shadow, not a price source.

### Price-only candidates (do not turn into votes automatically)

- **SportyTrader BR** and **Scores24 CN** expose named bookmaker odds in the
  sample. Their prediction/model surfaces should not be counted as independent
  votes merely because the page also prints a probability. Capture only rows
  with book, selection, decimal odds, fixture, and timestamp; discard
  `Odd 0`/missing values and retain the source page for audit.
- A bookmaker link or affiliate redirect is not itself a cooperative odds API.
  No login, paid plan, or redirect scraping is approved.

### Shared-publisher and echo-chamber risks

Betimate's locale pages and some model/affiliate pages may be one upstream
publisher rendered in different languages. Treat locale variants as **one
source**, not multiple votes. Scores24, SportyTrader, and FootyStats also mix
model/community text with market odds; measure overlap against forebet,
zulubet, and statarea on shared fixtures before any vote weight is considered.
The goal is donor diversity, not simply a larger roster. The existing
fb-zb `0.535 / 60.6%` result is the independence receipt to beat, not a gate to
weaken.

### Fetchability and settlement caveats

- No challenge-walled source was promoted. If a future sample returns a JS
  challenge, a login wall, or inconsistent HTML, label it
  `training-only`/`reject` and stop; do not add a browser, proxy, solver or
  CAPTCHA path.
- A page showing historical scores is not automatically a settlement contract.
  The operator review must require stable fixture identity, timezone/date,
  market semantics, publication timestamp, and a non-mutating settled result.
- The next implementation step, if approved, is a 30-day **shadow capture**
  with no change to `SOURCES_*`, no pick-path dependency, and no ticket/staking
  effect. This document intentionally contains no fetcher code.

## Operator review checklist

- [ ] Select at most two first shadow candidates, preferably from different
      publishers/languages.
- [ ] Confirm robots scope and contact/terms for the exact proposed URL before
      recurring capture.
- [ ] Define an append-only capture schema and settlement join receipt.
- [ ] Run the existing source-independence audit after the shadow window.
- [ ] Explicitly approve whether each candidate is a vote donor or a
      bookmaker-labelled price donor; never infer both roles.
- [ ] Keep Forebet historical-only post-2026-06-12 and leave
      `EDGE_FACTORY_FOREBET_BROWSER=off` unchanged.
