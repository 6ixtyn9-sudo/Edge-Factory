-- ============================================================
-- 0004_new_sources.sql — register the 5 new adapters
-- ============================================================
insert into sources (key, kind, base_url) values
  ('zulubet',         'predictions', 'https://www.zulubet.com'),
  ('statarea',        'predictions', 'https://old.statarea.com'),
  ('scoutingstats',   'predictions', 'https://scoutingstats.ai'),
  ('vitibet',         'predictions', 'https://www.vitibet.com'),
  ('afootballreport', 'predictions', 'https://afootballreport.com')
on conflict (key) do nothing;
