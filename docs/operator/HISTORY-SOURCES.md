# History-source hunt — Task H

**Observed:** 2026-10-02 UTC
**Mode:** documentation/specification only. No production code, fetcher, warehouse
migration, or crawl was shipped. All page checks below used the sandbox
web-fetch relay; raw `curl` was not used. A site that exposes an old score or a
vendor's green/red result is not trusted settlement evidence until it is joined
to our warehouse score facts and market semantics.

## Decision rules

- **Vote archive:** retain the original dated fixture, publication/date context,
  market, selection, and raw page/file provenance. Re-settle from our warehouse
  scores; never import the vendor's win/loss grade as truth.
- **Price archive:** retain bookmaker, opening/closing label, odds, fixture, date,
  source URL, retrieval timestamp, checksum, and raw-file provenance. Opening
  and closing are separate observations; do not call a pre-closing snapshot a
  precise kickoff price.
- Locale mirrors from one operator are one publisher. They cannot become extra
  consensus votes. Bookmaker odds may be price evidence without being an
  independent prediction voice.
- History can backfill research, CLV, and corroboration audits, but it does not
  alter PR #20 gates, the pick path, consensus weights, the #18 lane,
  `scripts/auto_tickets.py`, or production enablement.
- Every future crawl must fetch `robots.txt` first, use an honest UA, one
  in-flight request, a bounded interval, and stop on 403, 429, or a challenge.
  No solver, paid proxy, browser bypass, CAPTCHA workaround, or synthetic row.
  The plans below are not authorization to start crawling.

## Priority 0 — already-trusted sources

The existing adapters establish what the current source family can do. This is
an archive-plan assessment, not a request to replay history yet.

| site / class | URL template + observed date range | parseability receipt | settlement path | independence / echo notes | verdict and archive-crawl plan |
|---|---|---|---|---|---|
| [aFootballReport](https://afootballreport.com) — vote/market archive candidate | Current pages: `/predictions/1X2-football-tips`, `/predictions/over-1.5-goals`, `/predictions/over-2.5-goals`, `/predictions/both-teams-to-score`; no dated path in the adapter or sampled page. Current relay sample showed daily rows dated `10/02`, 1X2 percentages/tipsters, and over/BTTS logic. | HTML tables are machine-readable enough for the existing regex adapter; rows contain both teams, tip, percentages and sometimes affiliate-book odds. The page says predictions update twice daily. | Use warehouse scores; head-to-head pages are form/context, not an immutable tip archive. | Streak/affiliate content can echo market consensus; no independent vote credit without overlap testing. | **Forward-only until a dated archive is proven.** After operator approval, test sitemap and any previous-entry links one at a time; do not treat head-to-head history as past predictions. |
| [BetClan](https://www.betclan.com) — vote archive candidate | Existing adapter permits only `/todays-football-predictions/` and `/tomorrow-football-predictions/`. Relay sample showed `2026-10-02`, fixture links under `/predictionsdetails/football/<id>/...`, and a current listing. No past-date URL was established. | Listing is parseable; detail pages expose winner and vote/probability bars. | Warehouse scores; detail-page “H2H” is not settlement. | Vote bars may be crowd/market echo; same-publisher pages are one voice. | **Forward-only; archive unverified.** Spec a robots-first probe of sitemap/detail IDs and any explicit date navigation, capped at one sample per candidate URL; no date-loop yet. |
| [PredictZ](https://www.predictz.com) — vote archive | `/predictions/YYYYMMDD/`; the existing adapter records `MIN_DATE = 2026-01-01`. Relay fetched [`/predictions/20260101/`](https://www.predictz.com/predictions/20260101/) and showed dated match-winner tips, 1X2 odds, predicted score text, and links for BTTS/O-U/correct-score variants. | Server-rendered repeated match blocks; current parser already extracts fixture, categorical pick, predicted score, odds and league. | Warehouse scores; do not use the site's `/results/` page as the only settlement fact. | Categorical tip plus odds can mirror other public models; keep at zero additional weight until overlap/independence review. | **Mineable-backfill candidate, bounded to the verified 2026-01-01 floor initially.** Plan a descending date crawl only after confirming the actual oldest served date, with one raw HTML snapshot and checksum per day. |
| [WinDrawWin](https://www.windrawwin.com) — vote archive | Existing future template `/predictions/future/YYYYMMDD/`; relay fetched [`/predictions/history/20250729/`](https://www.windrawwin.com/predictions/history/20250729/) and showed historical navigation, result, stake, prediction, exact-score suggestion and success marker. Search evidence also exposes `/predictions/yesterday/`. | Repeated markdown tables expose home/away, final score, prediction, suggested score and vendor grade. Existing adapter parses future pages; history parser is not yet implemented. | Warehouse scores; vendor green tick/red cross is audit metadata only. | Editorial tip tables and “stake” labels are one publisher; likely echo with bookmaker consensus. | **Mineable-backfill candidate.** First spec a history parser for `/predictions/history/YYYYMMDD/` and market subpaths; compare vendor grade to independent re-settlement before any research score is accepted. |
| [FreeSuperTips](https://www.freesupertips.com) — vote archive candidate | Current `/predictions/` sample exposes future match-preview links, not a dated results table. Robots explicitly disallows `/ppc-free-bet-archive/` and several date/query patterns including `date=2018`. | Current preview cards are parseable only after following individual match pages; no approved historical table was observed. | Warehouse scores if a frozen tip capture exists; current preview/result text is not enough. | Editorial publisher, no extra vote until dated immutable capture. | **Forward-only / historical reject for now.** Do not bypass robots' archive restrictions. Keep only capture-forward data already in the ledger. |
| [ZuluBet](https://www.zulubet.com) — vote/price archive | Existing template `https://www.zulubet.com/tips-DD-MM-YYYY.html`; relay fetched [`tips-20-12-2024.html`](https://www.zulubet.com/tips-20-12-2024.html), showing rows with date, home, away, 1X2 percentages, tip, odds and FT score. Existing adapter's floor is `2023-12-25`; search receipts also found 2025/2026 dated pages. | Large server-rendered table; existing regex parser handles teams, probabilities, tip, odds and score. | Use warehouse scores for historical grading despite the source score column. | Existing source is already part of the ledger; backfill must dedupe exact fixture keys and must not turn old rows into extra votes. | **Mineable-backfill candidate, subject to robots/terms clarification.** Relay `robots.txt` returned 404, so absence is not permission. Request an operator policy decision, then crawl only an allowlisted date range with immutable raw files. |
| [Statarea](https://old.statarea.com) — vote archive | `/predictions/YYYY-MM-DD`; relay fetched [`/predictions/2017-01-01`](https://old.statarea.com/predictions/2017-01-01), which rendered a dated prediction table and current date-navigation links. Existing adapter documentation says the archive reaches 2015–2017; the sampled page proves at least 2017. | Wide machine-readable table: fixture sides, FT/HT result, 1X2, HT 1X2, O/U 1.5/2.5/3.5 and handicap percentages. Robots says `User-agent: * Allow: /`. | Warehouse score facts; source result cells are useful corroboration, not the sole settle. | Existing trusted source; historical rows must be deduped against existing Statarea ledgers and never add consensus weight retroactively. | **Mineable-backfill candidate.** Establish an oldest-date boundary with sparse probes, then crawl date-by-date at low rate and preserve the source timezone (`America/Chicago` observed on page). |
| [BettingClosed](https://www.bettingclosed.com) — vote/price archive | `/predictions/date-matches/YYYY-MM-DD[/bet-type/{1x2,under-over,gol-nogol,correct-scores}]`; existing adapter documents a 2012 floor. Relay fetched [`.../2012-01-01/under-over`](https://www.bettingclosed.com/predictions/date-matches/2012-01-01/under-over); page rendered the table schema and calendar but no rows, and displayed an off-by-one title (`January 01, 2011`). | Existing regex parser expects repeated match rows containing teams, FT result, pick, pick odds, bookmaker and full odds tooltip. Sample proves the table contract but not populated 2012 coverage. | Vendor result is on-page; production grading must still join warehouse score and flag source/date mismatch. | Source is already in the warehouse family; same-publisher history is not a new vote. | **Mineable candidate pending boundary correction.** First resolve the URL/title year discrepancy with one or two non-production probes; then crawl market paths and merge by fixture, retaining book-labelled odds separately. |

### Priority 0 common crawl proposal

1. Read and record `robots.txt` and terms for the exact host. If unavailable,
   stop for operator review rather than assuming allow.
2. Maintain an allowlisted date range and URL generator per source. Use one
   worker, a source-specific interval, conditional requests where supported,
   and an immutable raw response under gitignored history storage.
3. Parse into a source-specific raw table with `source_url`, `retrieved_at`,
   `sha256`, parser version, and raw source date. Normalize fixture identity
   only after raw capture; never overwrite a prior snapshot.
4. Join scores through the existing warehouse/backfill. Keep `vendor_result`,
   `vendor_grade`, and `independent_result` separate. Count missing and
   conflicting joins before any mining experiment.
5. Write a report first. No source enters consensus, pricing gates, or tickets
   from this task.

## Priority 1 — four verified archive doors

All four were re-checked through the sandbox web-fetch relay on 2026-10-02.
Robots receipts are recorded here; no bulk download was performed.

| site / class | URL template + date range | parseability receipt (fetched sample) | settlement path | independence + echo notes | verdict |
|---|---|---|---|---|---|
| [Football-Data.co.uk](https://football-data.co.uk) — **price archive, Class-B gold** | Country/league pages such as [`data.php`](https://football-data.co.uk/data.php), `englandm.php`, then per-season CSVs conventionally under `/mmz{season}/{league}.csv` (example proposal: `/mmz4281/2526/E0.csv`). The data page says **32 seasons results / 27 seasons betting odds / 27 seasons match stats**, and was updated `02/10/26`; it also says league odds include pre-close and closing fields, with Pinnacle closing odds back to 2012/13. | `robots.txt` explicitly `User-agent: * Disallow:` while blocking named AI-training/aggressive bots. `data.php` says CSV/Excel is free and computer-ready; [`notes.txt`](https://football-data.co.uk/notes.txt) documents `Date`, `HomeTeam`, `AwayTeam`, results, `B365H/D/A`, `PSH/D/A`, `BFH/D/A`, `WHH/D/A`, `B365CH/CD/CA`, `PSCH/D/A`, and `BbMx*`. The relay returned HTTP 500 for direct CSV parsing, so the exact CSV body still needs a controlled downloader receipt; this is not treated as a successful download. | Results in the same file are useful as a cross-check, but final settlement remains our warehouse score. Price history does not need vendor tip settlement. | Price archive is not a prediction vote. Bookmaker/market labels are legitimate price evidence; bookmaker clones and same-publisher data must not be counted as independent voices. | **Mineable price-history candidate; highest priority.** Start with one league/season sample after operator approval, checksum raw CSV, record schema/header changes, and add only a proposed warehouse table first. Complements live sources; does not replace them. |
| [AllFootballPredictions](https://www.allfootballpredictions.com) — vote archive with odds | Stable category archives: [`/archive/`](https://www.allfootballpredictions.com/archive/), `/archive/1x2-archive/`, `/archive/btts-archive/`, `/archive/over-under-bet-archive/`, etc. The archive page claims monthly/yearly history; fetched 1X2 page contained September, August, July and June 2026 sections, with date, home, result, away, prediction, odd and vendor bet result. | `robots.txt`: `User-agent: *`, disallows only `/wp-admin/` and permits public archive pages; sitemap index present. Markdown tables are directly parseable, including 1X2 and BTTS examples. | Independent settlement against warehouse scores and market rules. Preserve `vendor_result` and `vendor_bet_result`; vendor self-grade is explicitly non-authoritative. | One publisher and many paid products; high selection/market echo risk. Compare claimed-vs-independent accuracy and inspect selective archive omissions. | **Mineable vote-backfill candidate, subject to trust gate.** Crawl one category/month first; flag material vendor-vs-independent divergence, missing losers, duplicate fixtures, HT/FT and combo semantics. |
| [FootballPredictions.net](https://footballpredictions.net) — vote archive/results | Stable rolling pages [`/football-results-yesterday`](https://footballpredictions.net/football-results-yesterday), `/football-results-2-days-ago`, and `/football-results-3-days-ago`; exact historical date parameter was not established. EN/DE/ES/FR/PT sitemap families are listed in robots. | Robots blocks only useful-links/API paths in the public family. Fetched yesterday page rendered dated fixture blocks with both teams, kickoff, FT score, tip/selection and preview links. The German path guessed as `/de/football-results-yesterday` returned “Page not found”, so localized slug templates must be discovered from each sitemap, not inferred. | Our warehouse score; page score is a source observation. Rolling pages require daily capture if history is to be preserved. | EN/DE/ES/FR/PT are one publisher; dedupe by fixture and publisher, never five votes. Public tip/model may mirror common odds. | **Mineable only as a capture-forward/rolling-backfill candidate.** Download daily rolling pages before they roll off; use sitemap-discovered locale slugs and one canonical publisher row. Arbitrary deep backfill is unproven. |
| [BetIdeas](https://betideas.com) — vote archive/results | [`/prediction-results/`](https://betideas.com/prediction-results/) is the stable results page. Robots allows `*` and lists base, `/es/`, `/de/`, `/it/`, `/fr/` sitemap indexes. A dated URL template was not exposed in the fetched page. | Fetched page updated **2 October 2026**, exposes filters and counts (`All Tips 31`, BTTS 15, Team To Win 16), but said “No Tips Available Right Now”; its explanatory text claims an extensive historical archive and per-result analysis. The Spanish guessed `/es/prediction-results/` returned 404. Thus a parseability receipt for populated result rows is still missing. | Re-settle from warehouse; vendor green/red result is not evidence. | Five locale editions are one publisher; filters/AI/editorial outputs can echo bookmaker consensus. | **Forward-only / archive candidate pending populated-row receipt.** Find the actual result API/HTML link from the sitemap or page controls without touching `/api` unless robots explicitly permits it; otherwise do not backfill from search snippets. |

### Football-Data proposed warehouse schema (diff-ready, not applied)

The first price-history implementation should keep raw provenance separate from
normalized odds. The DDL is a proposal for operator review, not a migration:

```sql
-- Proposed DuckDB/warehouse table; do not apply in Task H.
CREATE TABLE fd_odds (
    download_id VARCHAR NOT NULL,
    source VARCHAR NOT NULL DEFAULT 'football-data.co.uk',
    country VARCHAR,
    league VARCHAR NOT NULL,
    season VARCHAR NOT NULL,
    match_date DATE NOT NULL,
    kickoff VARCHAR,
    home VARCHAR NOT NULL,
    away VARCHAR NOT NULL,
    fthg INTEGER,
    ftag INTEGER,
    ftr VARCHAR,
    -- pre-closing/opening-side snapshot as labelled by Football-Data
    b365_h DOUBLE, b365_d DOUBLE, b365_a DOUBLE,
    ps_h DOUBLE, ps_d DOUBLE, ps_a DOUBLE,
    bf_h DOUBLE, bf_d DOUBLE, bf_a DOUBLE,
    wh_h DOUBLE, wh_d DOUBLE, wh_a DOUBLE,
    -- closing columns (the source uses the C suffix)
    b365c_h DOUBLE, b365c_d DOUBLE, b365c_a DOUBLE,
    psc_h DOUBLE, psc_d DOUBLE, psc_a DOUBLE,
    bfc_h DOUBLE, bfc_d DOUBLE, bfc_a DOUBLE,
    whc_h DOUBLE, whc_d DOUBLE, whc_a DOUBLE,
    -- market aggregates and other retained source columns
    bbmx_h DOUBLE, bbmx_d DOUBLE, bbmx_a DOUBLE,
    bbav_h DOUBLE, bbav_d DOUBLE, bbav_a DOUBLE,
    raw_row_number INTEGER,
    raw_file_sha256 VARCHAR,
    source_url VARCHAR NOT NULL,
    retrieved_at TIMESTAMPTZ NOT NULL,
    parser_version VARCHAR NOT NULL
);

CREATE TABLE fd_downloads (
    download_id VARCHAR PRIMARY KEY,
    source_url VARCHAR NOT NULL,
    country VARCHAR,
    league VARCHAR,
    season VARCHAR,
    retrieved_at TIMESTAMPTZ NOT NULL,
    http_status INTEGER,
    content_sha256 VARCHAR NOT NULL,
    byte_count BIGINT,
    row_count INTEGER,
    header_sha256 VARCHAR,
    parser_version VARCHAR NOT NULL,
    raw_path VARCHAR NOT NULL,
    notes VARCHAR
);
```

Implementation notes: preserve the original header names in a sidecar/header
record because bookmaker columns change by season; parse `Date` as `dd/mm/yy`
with an explicit season context; reject odds `<= 1.0` as missing/junk; retain
nulls rather than forward-fill. `B365H/D/A` and equivalents are not asserted to
be exact market-open timestamps. `C` columns are closing observations. The
Football-Data page warns that Pinnacle's public API has been unreliable since
23/07/2025; that warning must become provenance, not silently cleaned data.

## Priority 2 — dated-archive pattern hunt

These are leads only. The same robots-first and maximum-three-samples rule
applies. No one below is promoted by this document.

| site / class | URL-template evidence and receipt | parseability / settlement | verdict |
|---|---|---|---|
| [Adibet.co](https://www.adibet.co) — vote/archive lead | Robots says `User-agent: * Allow: /`. Fetched homepage exposes `cat_25`, `cat_20.html`, `cat_45/`, and a `paged_2.html` previous-entry link; search evidence showed dated fixed-match/monthly archive rows. | Current page is sparse and heavily vendor/fixed-match oriented; no stable canonical date table was proven in the fetched page. Re-settle independently if ever sampled. | **Hold/reject pending transparent archive receipt.** Vendor self-grading and fixed-match claims are a high-risk echo/trust class. |
| [Sokapedia SoloPredict](https://sokapedia.com/predictions/solopredict) — vote/price lead | Robots allows the public path and exposes sitemaps. Fetched page links `/today-football-predictions`, `/tomorrow-football-predictions`, `/yesterday-football-predictions`, and current fixture URLs; rows show date/time, teams, probabilities, prediction, average/1X2 odds. | Machine-readable repeated fixture links; no settled “yesterday” page was fetched in this pass, so warehouse settlement and historical retention are unproven. Treat as Sokapedia publisher, not automatically the Solopredict brand. | **Mineable candidate after one dated-yesterday sample and publisher identity check.** Potentially useful for both vote shadow and named price fields, but no extra vote by default. |
| [VIP Predictions](https://www.vippredictions.com) — vote/price lead | Robots exposes content-signal terms but no ordinary `User-agent: *` allow/disallow section; operator must review the signal policy. Fetched homepage uses `?date=YYYY-MM-DD` navigation and contains dated tables with teams, 1X2 odds and predicted scores. | HTML table is parseable and wide-league; current page did not prove past settlement or immutable publication. | **Hold for robots/content-signal review and one past-date sample.** Do not treat the predicted score as a result or add its locales/tipsters as independent votes. |
| Footystreet — unverified lead | Sandbox robots fetch failed; no exact canonical domain/template or page receipt was established. | No parseability or settlement evidence. | **Reject/UNVERIFIED; do not fetch again until an exact URL and robots receipt are supplied.** |
| Winspear — unverified lead | Sandbox robots fetch failed; no exact canonical domain/template or page receipt was established. | No parseability or settlement evidence. | **Reject/UNVERIFIED; do not fetch again until an exact URL and robots receipt are supplied.** |
| Generic `/archive`, sitemap-dated pages | Use only after a source-specific robots receipt. Candidate patterns include `/archive/`, `/archive/YYYY/MM/`, `/predictions/history/YYYYMMDD/`, `?date=YYYY-MM-DD`, `/yesterday`, and sitemap URLs. | A page must expose both fixture sides, selection/market, original date, and a score path from our warehouse. Search snippets are not receipts. | **Pattern only, not a source.** Add a row only after a fetched sample proves URL reproducibility and settlement semantics. |

## H2 — non-English expansion (2026-10-02 UTC)

This section records the sandbox re-verification of the Turkish, Russian,
Portuguese, Italian, Japanese, Greek, and Chinese leads. It remains
specification-only: no archive crawl or downloader was started. `robots.txt`
was fetched before each sample where the host responded; the pass used at most
1–3 sample pages per site. A fetch failure is a negative receipt, not an
authorization to retry with another transport.

| site / class | URL/date evidence | parseability receipt | warehouse-score settlement | independence / echo notes | verdict |
|---|---|---|---|---|---|
| [Sahadan](https://www.sahadan.com) / `arsiv-origin.sahadan.com` (TR) — **price archive target** | `www.sahadan.com/robots.txt` allows `*` and disallows `/api/`, `/_nuxt/`; named AI-training bots are blocked. The archive host's robots fetch failed in the relay, so archive-host permission is **unverified**. Requested [`arsiv-origin.sahadan.com/Iddaa/program.aspx`](http://arsiv-origin.sahadan.com/Iddaa/program.aspx) was not reachable. | Public [`www.sahadan.com/iddaa-programi`](https://www.sahadan.com/iddaa-programi) rendered a dated `02.10.2026` program with navigation back to `16.09.2026`, deep leagues, 1/X/2, double chance and O/U-style fields. It did not prove the archive-host `05.12.2024` URL or a working date parameter. | Odds are raw price evidence, not a vote. Join results to warehouse scores; preserve Turkish market labels and bookmaker/time semantics. | A price archive is not an independent prediction voice. Treat the current page as a shape receipt only until dated odds are verified. | **Top conditional Class-B price candidate, not archive-verified.** Operator gate: obtain archive-host robots receipt, then one dated `05.12.2024` or equivalent sample; stop on 403/challenge. |
| [Legalbet.ru](https://legalbet.ru) — **named-expert vote archive** | `legalbet.ru/robots.txt` permits public tips/archive but restricts several expert/stat/query patterns for generic agents; use exact allowed URLs only. [`/tips/archive/`](https://legalbet.ru/tips/archive/) is linked from `/tips/` and was fetched. | Archive rows rendered named expert links such as [`/expert/ilinov/`](https://legalbet.ru/expert/ilinov/), dated tips, selections, bookmaker labels/odds, `Завершен` status and displayed W/L/ROI (for example `57/7/39`, `ROI 16.0%`). The expert index also describes per-expert statistics. | Re-settle with warehouse scores and retain author identity, timestamp, market and book. Displayed expert ROI/W/L is vendor metadata, not settlement. | Experts are multiple donors within one publisher; never count Legalbet as several publisher votes. Editorial/bookmaker content is a likely echo class. | **Strongest mineable vote-bank candidate.** Sample more public archive rows only after operator approval; preserve immutable dated tip and expert-page links, with a minimum settled sample per expert. |
| [Academia das Apostas Brasil](https://www.academiadasapostasbrasil.com) / [PT](https://www.academiadasapostas.com) — **community/editorial vote lead** | Both robots files allow public pages but specify `Crawl-delay: 200`; `Baiduspider`/`PetalBot` are blocked. Both expose sitemaps. `/tips/` was fetched on both domains. | BR rendered current match previews and links to `/stats/match/.../preview`; PT rendered current analyses and a `38 em aberto` count. The fetched pages did **not** expose the claimed `+10 mercados / 24 votos` community percentage grid or a dated archive. | Warehouse settlement required; editorial prose and displayed community percentages are untrusted until recomputed against warehouse scores. | Treat BR/PT as one publisher until proven otherwise: same Academia branding, CDN, and near-identical structure. Explicitly dedupe the domains. | **Conditional deep-LatAm vote candidate.** Sample one linked match preview and any `/tips/listing`/archive URL discovered from sitemap, respecting the 200-second delay; do not accept the unverified vote grid. |
| [vprognoze.ru](https://vprognoze.ru) / [vprognoze.kz](https://vprognoze.kz) — **community vote/track-record lead** | Both robots permit public forecast pages but disallow user/stat endpoints, rating/query forms, and several archive/search parameters. Do not infer permission for blocked `?do=stat*`, user, or rating URLs. Both home pages were fetched. | Both rendered dated fixture slugs such as `/topforecast/<id>-<teams>-2026-10-02.html`, multiple forecasts per match, 1X2 odds, named users, bankroll and ROI snippets. The rating archive itself was not fetched because the robots rules target those paths; archive depth is therefore unproven. | Re-settle every pick from warehouse scores; user ROI/bank is vendor metadata until independently recomputed. | `.ru` and `.kz` are presumptively one publisher/mirror and must be deduped. User-level forecasts are not independent from the site-level donor until identity and overlap checks pass. | **Secondary donor candidate, not archive-mineable yet.** Use public dated match pages only; request an operator decision before any rating/stat path, with minimum settled rows per tipster. |
| [Football LAB](https://www.football-lab.jp) (JP) — **data/history lead, not prediction archive** | `www.football-lab.jp/robots.txt` is `User-agent: * Disallow:` (open). Homepage was the one public sample. | Homepage rendered J1/J2/J3 team datasets and dated analysis columns, but no dated tips, bookmaker odds, or prediction archive. | Useful team-performance data is not a vote or price archive; no settlement role is proven. | A data portal is not an independent tipster. Do not turn team statistics into a synthetic vote. | **Reject for H2 history mining; retain only as a possible feature/data source.** |
| [Superscommesse.it](https://www.superscommesse.it) (IT) — **editorial vote archive lead** | `superscommesse.it/robots.txt` permits public content and exposes `sitemap-pronostici.xml`, `sitemap-risultati.xml`, and `pronostici_oggi.xml`; operational/admin paths are restricted. [`/pronostici/`](https://www.superscommesse.it/pronostici/) was fetched. | Current page rendered named authors, fixtures, dates/times and league labels for `02–03.10.2026`. No historical archive page was sampled, but the result/tip sitemap split gives a concrete discovery path. | Re-settle from warehouse scores; verify bookmaker/odds fields on one match page before using them. | Same-publisher named authors are not independent publishers; current editorial tips may echo bookmaker consensus. | **Mineable editorial candidate pending history sample.** Probe sitemap result/pronostic URLs and one older dated article; preserve author and publication time. |
| [FootyStats Greece](https://footystats.org/greece/football-league/predictions) — **community vote/price lead** | `footystats.org/robots.txt` allows public prediction pages but disallows APIs, `/u/*` user pages and query-date patterns; selected agents have crawl delays. The public Greece prediction page was fetched. | Page is a completed `2020/21` Greece Football League season with `180/180` matches, links back to `2013/14`, and repeated predictions containing market, odds, date, user coins and H2H links. User-profile links are robots-blocked; original publication timestamps are not shown. | Re-settle from warehouse scores; coin counts/user names are community metadata, not truth. | Community users are one site-level donor pool; do not count H2H or the site's own stats as independent sources. | **Mineable Greek historical candidate, bounded to public league pages.** Do not follow `/u/*` or API paths; test one season/league join before broader mining. |
| [ProTipster Greece](https://www.protipster.com/betting-tips/football/greece) — **tipster vote lead** | `www.protipster.com/robots.txt` permits public pages and only disallows `/affiliate/`; locale sitemaps are listed. The Greece page was fetched. | Page rendered named tipsters, market labels, odds, fixture links and dates, but also showed `0 Tips found` in the country section. No historical results page was established. | Warehouse settlement required; tipster pick, odds, and any on-page result are source observations until recomputed. | Tipsters are community authors within one publisher, not independent publishers. | **Forward-only/lead.** Find a public past-date or tipster-history URL before archive work; do not infer depth from current prediction blocks. |
| [500.com](https://www.500.com) / [`trade.500.com/jczq`](https://trade.500.com/jczq/) (CN) — **price-history target** | `500.com/robots.txt` allows much public content but disallows important odds/history subpaths, including `/pages/info/odds/europe.php*`; exact `odds.500.com` verification returned a security-verification page. Public trade URL exposes `date=YYYY-MM-DD` links and history-date navigation. | [`trade.500.com/jczq`](https://trade.500.com/jczq/) rendered “赛果回查” dates, match IDs, teams, results/odds columns, and bookmaker/market table headings; the live relay sample had zero matches after cutoff. No blocked odds-centre path was bypassed. | Price history feeds corroboration/CLV research only; preserve Chinese market labels and bookmaker columns, and use warehouse scores for results. | Price evidence is not a prediction vote. Do not treat bookmaker columns or 500.com's own result labels as independent donors. | **High-signal conditional Class-B price candidate.** First operator-approved probe is one public `trade` date page, not the blocked odds centre; hold rather than bypass if a history path is disallowed. |
| [okooo.com](https://okooo.com) — **Chinese price/archive lead** | `okooo.com/robots.txt` explicitly disallows `/History/`, `/match/`, `/League/`, `/DataProvider/`, and related data paths; sitemap is present. | No public history sample was fetched in this pass. `/History/` is explicitly disallowed, so the apparent archive class has no compliant dated-page receipt. | No settlement/parseability receipt; do not use search snippets as warehouse evidence. | No independence claim can be made; blocked history is a hold, not a missing-data invitation. | **Reject/hold unless a permitted dated odds path is identified.** |
| 310win — **Chinese price lead** | `310win.com/robots.txt` fetch failed in the relay; no permission receipt. | No compliant page or date parameter was verified; search results were generic live-score snippets, not an archive receipt. | No settlement or parseability evidence. | No independence evidence. | **UNVERIFIED/reject; do not retry through another transport.** |
| Soccer-King.ai — **Japanese prediction lead** | `soccer-king.ai/robots.txt` fetch failed in the relay; no permission receipt. | No dated archive or parseable prediction/odds page was verified. Football LAB is the verified Japanese data site, but it is not a prediction/odds archive. | No settlement evidence. | No independence evidence. | **UNVERIFIED/reject.** |

### Chinese and Turkish archive constraint

The Chinese candidates are promising because public pages expose date/history
selectors, but robots explicitly blocks important `History`, odds, or API paths
on some hosts and `odds.500.com` returned a security-verification page. The
Turkish Sahadan primary site is reachable and its current program proves the
odds-grid shape, but the requested archive host was not reachable from the
sandbox. These are **conditional archive candidates**, not verified download
sources. No challenge bypass or alternate scraping route is authorized.

## English-site hunting directive

**English-site hunting is closed unless a new class surfaces.** The next hunt
should remain in non-English price-history, named-expert vote archives, and
community-track-record sources, with the same robots-first and independent
settlement standard.

## Ordered work after operator review

1. **Football-Data price history:** approve the host/terms, fetch one CSV

   through the cooperative downloader, save a checksum/provenance row, parse the
   header, and compare opening/closing fields to the notes. Then expand by
   league×season; never put raw files in Git.
2. **Existing sources:** start with PredictZ, WinDrawWin, Statarea, ZuluBet
   (only after robots policy), and BettingClosed boundary correction. Generate
   independent re-settlement coverage and vendor-grade divergence reports.
3. **AllFootballPredictions:** one category/month sample, then claimed-vs-
   independent grade audit. Reject or quarantine material selective-history or
   market-semantics divergence.
4. **Rolling publishers:** FootballPredictions.net and BetIdeas need daily
   capture if their “yesterday” pages are the only stable archive. Do not infer
   arbitrary historical URL forms from locale mirrors.
5. Only after reports are reviewed may any history be used for research mining or
   price corroboration backfill. This Task H document makes no production
   change and assigns no new consensus weight.
