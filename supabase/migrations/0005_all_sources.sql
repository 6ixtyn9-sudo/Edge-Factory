-- ============================================================
-- 0005_all_sources.sql — register remaining 6 adapters (12 total)
-- ============================================================
insert into sources (key, kind, base_url) values
('predictz', 'predictions', 'https://www.predictz.com'),
('windrawwin', 'predictions', 'https://www.windrawwin.com'),
('betclan', 'predictions', 'https://www.betclan.com'),
('freesupertips', 'predictions', 'https://www.freesupertips.com'),
('bettingclosed', 'predictions', 'https://www.bettingclosed.com'),
('bzzoiro', 'predictions', 'https://sports.bzzoiro.com')
on conflict (key) do nothing;

-- bzzoiro is a real ML model API (CatBoost, xG)
-- Auth: Authorization: Token <key>
-- Endpoint: /api/v2/predictions/
-- Provides: p1/px/p2, xg_home/xg_away, p_o15/p_o25/p_o35, p_gg, pred_score, confidence, model_version
-- Capture-forward: snapshot ALL upcoming daily; settle later via /api/v2/events/
