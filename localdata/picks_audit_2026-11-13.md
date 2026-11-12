# Edge Factory — Recent picks audit (2026-10-15 to 2026-11-13)

## Overall

- archived pick rows: 1146
- archived pick dates: 30
- immutable morning-baseline rows: 1075
- late-slate additions (regular-ledger rows not in the morning baseline): 71, of which on days whose regular ledger was rewritten: 48
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 28
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 1078
- eligible prior picks: 1100
- pending/unmatched result picks: 12
- rescheduled result picks (settled ±3d): 3
- voided postponed/cancelled/abandoned events: 9
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 1
- ambiguous result picks: 1
- wins: 683
- hit rate: +63.4% (wins/settled: 683/1078)
- priced picks: 896
- ROI: -0.8% (P&L / 896 priced picks)

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-11-13
- same-day rows excluded: 15

## Rule performance — since activation vs last 30 days

Primary view: recorded post-activation PICK ROWS, including vetoed/watchlist rows; not placed bets or acca returns. No retrospective rule replay. Missing activation dates remain unavailable. Missing archive days mean partial history, not zero activity. Missing/unreadable files are counted as archive gaps. Empty recorded cards count as available days. Current registry status is not historical status on each pick date.

Last 30 days: 2026-10-15 to 2026-11-13; same-day inclusion: False (local cutoff 2026-11-13). The 30-priced-row provisional flag is reporting only, not an activation gate. Priced ROI can include fallback/quarantined odds; provenance is shown separately. Historical ml-meta is not the live ML ENH selector.

| Rule | Activation / current status | Since activation | Last 30 days | Archive days: since / recent | Stored key |
| --- | --- | --- | --- | --- | --- |
| 1x2 single[scoutingstats] avg_p>=65 | 2026-10-25 / benched | ROI +0.1%; hit 80.3% (110/137); 106 priced; coverage 77.4% | ROI +0.1%; hit 80.3% (110/137); 106 priced; coverage 77.4% | 19/19 / 29/29 | pfc_fdade2e70df4d4bb78a8cd6e |
| ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55 | 2026-10-23 / benched | ROI -2.0%; hit 61.9% (52/84); 79 priced; coverage 94.0% | ROI -2.0%; hit 61.9% (52/84); 79 priced; coverage 94.0% | 21/21 / 29/29 | pfc_27e0f725859bc708f95c58a3 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=35 | 2026-11-03 / certified | ROI -2.8%; hit 53.2% (126/237); 216 priced; coverage 91.1% | ROI -2.8%; hit 53.2% (126/237); 216 priced; coverage 91.1% | 10/10 / 29/29 | pfc_f56fe4a2759e9b17b9bdb116 |
| 1x2 single[scoutingstats] avg_p>=50 | 2026-10-20 / benched | ROI -5.1%; hit 60.7% (150/247); 196 priced; coverage 79.4% | ROI -5.1%; hit 60.7% (150/247); 196 priced; coverage 79.4% | 24/24 / 29/29 | pfc_439097cb9bb700e9996c0b07 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=0 | 2026-11-01 / benched | ROI +148.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | ROI +148.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | 12/12 / 29/29 | pfc_b4407145af67d2f93e48f0ef |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=45 | 2026-11-03 / benched | ROI +102.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | ROI +102.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | 10/10 / 29/29 | pfc_ed44334de1c8307f22b510ab |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=40 | 2026-11-02 / candidate | ROI +100.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | ROI +100.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | 11/11 / 29/29 | pfc_cd84fb2c3ed889c0ae9eb89e |
| 1x2 single[zulubet] avg_p>=50 | 2026-10-20 / benched | ROI +90.0%; hit 50.0% (2/4); 2 priced; coverage 50.0%; provisional | ROI +90.0%; hit 50.0% (2/4); 2 priced; coverage 50.0%; provisional | 24/24 / 29/29 | pfc_4cf3df8552488297d7ccf526 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=60 | 2026-11-12 / certified | ROI +61.4%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | ROI +26.0%; hit 75.0% (6/8); 5 priced; coverage 62.5%; provisional | 1/1 / 29/29 | pfc_54fcf87604b73b87ee6c0a90 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=0 | 2026-10-20 / benched | ROI +55.2%; hit 75.0% (3/4); 4 priced; coverage 100.0%; provisional | ROI +55.2%; hit 75.0% (3/4); 4 priced; coverage 100.0%; provisional | 24/24 / 29/29 | pfc_0ad08cd1b2e75a2c9051189e |
| 1x2 unanimous[statarea+zulubet] avg_p>=40 | 2026-10-20 / benched | ROI +44.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | ROI +44.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | 24/24 / 29/29 | pfc_5208b9e15194a691590430ad |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=55 | 2026-11-09 / certified | ROI +36.5%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | ROI -28.5%; hit 50.0% (3/6); 6 priced; coverage 100.0%; provisional | 4/4 / 29/29 | pfc_fbf508b9c62bae8f281bb6e1 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=50 | 2026-10-20 / benched | ROI +34.6%; hit 81.8% (9/11); 5 priced; coverage 45.5%; provisional | ROI +34.6%; hit 81.8% (9/11); 5 priced; coverage 45.5%; provisional | 24/24 / 29/29 | pfc_234f16641d9893e8ec2a01f0 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=0 | 2026-11-03 / certified | ROI +33.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | ROI +33.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | 10/10 / 29/29 | pfc_cddf4106a3d45b6e455d8c73 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=40 | 2026-11-03 / certified | ROI +31.6%; hit 87.5% (7/8); 7 priced; coverage 87.5%; provisional | ROI +31.6%; hit 87.5% (7/8); 7 priced; coverage 87.5%; provisional | 10/10 / 29/29 | pfc_a7ba6711aeb15b9804a94f06 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35 | 2026-11-07 / candidate | ROI +25.7%; hit 100.0% (2/2); 2 priced; coverage 100.0%; provisional | ROI +1.0%; hit 56.8% (25/44); 42 priced; coverage 95.5% | 6/6 / 29/29 | pfc_73b036a8ee8dd5a4dea48134 |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=70 | 2026-11-09 / certified | ROI +18.5%; hit 85.7% (6/7); 5 priced; coverage 71.4%; provisional | ROI +18.5%; hit 85.7% (6/7); 5 priced; coverage 71.4%; provisional | 4/4 / 29/29 | pfc_4a3e5fbac72b2ebef11632f0 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=50 | 2026-10-20 / benched | ROI +16.5%; hit 50.0% (1/2); 2 priced; coverage 100.0%; provisional | ROI +16.5%; hit 50.0% (1/2); 2 priced; coverage 100.0%; provisional | 24/24 / 29/29 | pfc_0b290b623e2a54ea7df3006c |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=60 | 2026-10-25 / benched | ROI +14.9%; hit 66.7% (6/9); 8 priced; coverage 88.9%; provisional | ROI +14.9%; hit 66.7% (6/9); 8 priced; coverage 88.9%; provisional | 19/19 / 29/29 | pfc_5904b1fc7050646e6321090c |
| ou_2.5 unanimous[scoutingstats+statarea] avg_p>=60 | 2026-11-05 / candidate | ROI +11.6%; hit 75.0% (3/4); 4 priced; coverage 100.0%; provisional | ROI +11.6%; hit 75.0% (3/4); 4 priced; coverage 100.0%; provisional | 8/8 / 29/29 | pfc_ee214d4f2f00846fa78f56e3 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 | 2026-10-20 / benched | ROI +11.1%; hit 57.1% (4/7); 7 priced; coverage 100.0%; provisional | ROI +11.1%; hit 57.1% (4/7); 7 priced; coverage 100.0%; provisional | 24/24 / 29/29 | pfc_4a1f2bb2278d13c8189148d0 |
| 1x2 single[scoutingstats] avg_p>=60 | 2026-10-20 / benched | ROI +9.7%; hit 75.0% (3/4); 4 priced; coverage 100.0%; provisional | ROI +9.7%; hit 75.0% (3/4); 4 priced; coverage 100.0%; provisional | 24/24 / 29/29 | pfc_0f100c9da356ed1c05d9c642 |
| 1x2 single[zulubet] avg_p>=55 | 2026-10-20 / certified | ROI +4.7%; hit 70.0% (28/40); 17 priced; coverage 42.5%; provisional | ROI +4.7%; hit 70.0% (28/40); 17 priced; coverage 42.5%; provisional | 24/24 / 29/29 | pfc_1607fec83282d02c5254c2bf |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=40 | 2026-11-01 / benched | ROI +2.7%; hit 55.6% (10/18); 16 priced; coverage 88.9%; provisional | ROI +2.7%; hit 55.6% (10/18); 16 priced; coverage 88.9%; provisional | 12/12 / 29/29 | pfc_226efd387e217a9d58a11f79 |
| ou_2.5 unanimous[scoutingstats+statarea] avg_p>=65 | 2026-11-02 / candidate | ROI -0.1%; hit 73.1% (19/26); 24 priced; coverage 92.3%; provisional | ROI -0.1%; hit 73.1% (19/26); 24 priced; coverage 92.3%; provisional | 11/11 / 29/29 | pfc_4e8ef1faa47bce63a119fb43 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=40 | 2026-10-21 / benched | ROI -17.4%; hit 38.5% (5/13); 12 priced; coverage 92.3%; provisional | ROI -17.4%; hit 38.5% (5/13); 12 priced; coverage 92.3%; provisional | 23/23 / 29/29 | pfc_d94d447efe0742440e953722 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=40 | 2026-11-03 / benched | ROI -21.8%; hit 66.7% (4/6); 2 priced; coverage 33.3%; provisional | ROI -21.8%; hit 66.7% (4/6); 2 priced; coverage 33.3%; provisional | 10/10 / 29/29 | pfc_c7c9572806b564198f651cee |
| 1x2 unanimous[statarea+zulubet] avg_p>=55 | 2026-10-21 / benched | ROI -34.5%; hit 33.3% (1/3); 2 priced; coverage 66.7%; provisional | ROI -34.5%; hit 33.3% (1/3); 2 priced; coverage 66.7%; provisional | 23/23 / 29/29 | pfc_5a9d3d3426ee7a4e63461d75 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=0 | 2026-11-03 / benched | ROI -100.0%; hit 0.0% (0/1); 1 priced; coverage 100.0%; provisional | ROI -100.0%; hit 0.0% (0/1); 1 priced; coverage 100.0%; provisional | 10/10 / 29/29 | pfc_0187397f26c1f84f6c3a9883 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=55 | 2026-10-20 / benched | ROI -100.0%; hit 50.0% (1/2); 1 priced; coverage 50.0%; provisional | ROI -100.0%; hit 50.0% (1/2); 1 priced; coverage 50.0%; provisional | 24/24 / 29/29 | pfc_2bd498a3472b7bbd71982ece |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 | 2026-10-20 / benched | ROI -100.0%; hit 0.0% (0/1); 1 priced; coverage 100.0%; provisional | ROI -100.0%; hit 0.0% (0/1); 1 priced; coverage 100.0%; provisional | 24/24 / 29/29 | pfc_3bfaf30507905754f7faab2a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=35 | 2026-11-03 / benched | ROI -100.0%; hit 0.0% (0/1); 1 priced; coverage 100.0%; provisional | ROI -100.0%; hit 0.0% (0/1); 1 priced; coverage 100.0%; provisional | 10/10 / 29/29 | pfc_a3afbb848e0c474b683b450f |
| 1x2 unanimous[vitibet+zulubet] avg_p>=45 | 2026-10-27 / benched | ROI -100.0%; hit 0.0% (0/2); 2 priced; coverage 100.0%; provisional | ROI +16.3%; hit 63.6% (7/11); 9 priced; coverage 81.8%; provisional | 17/17 / 29/29 | pfc_b011652ec3e473fbc0afbb6a |
| ml-meta avg_p>=60 | unavailable / unavailable | unavailable | ROI -6.4%; hit 58.6% (41/70); 61 priced; coverage 87.1% | unavailable / 29/29 | ml-meta avg_p>=60 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=0 | 2026-11-07 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 6/6 / 29/29 | pfc_051ee3ee0d476984665d1f43 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=35 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_054448b499623dd39b072b38 |
| 1x2 unanimous[predictz+statarea] avg_p>=0 | 2026-11-11 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 2/2 / 29/29 | pfc_079067dbb6dd2b8a93eb13a6 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=45 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_0aed63f3d04b46330958121d |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=65 | 2026-11-08 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_0d71c5e45469731a1fc4b8d1 |
| 1x2 unanimous[bzzoiro+zulubet] avg_p>=0 | 2026-11-09 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 4/4 / 29/29 | pfc_0ebe3a9a402a26bfa4e53552 |
| 1x2 unanimous[bettingclosed+scoutingstats+statarea] avg_p>=0 | 2026-11-08 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_0fae0b61dd393c289b12b9b8 |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=45 | 2026-10-30 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 14/14 / 29/29 | pfc_144c01b1aa366b88f9c4083a |
| 1x2 unanimous[predictz+scoutingstats+vitibet] avg_p>=0 | 2026-11-07 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 6/6 / 29/29 | pfc_14c827df1f0bd5801d2ef540 |
| 1x2 single[zulubet] avg_p>=45 | 2026-10-20 / benched | ROI unavailable; hit 0.0% (0/1); 0 priced; coverage 0.0%; provisional | ROI unavailable; hit 0.0% (0/1); 0 priced; coverage 0.0%; provisional | 24/24 / 29/29 | pfc_14ee12458803822df3013bcd |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=55 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_1ba3ab3c75e6f3a9680ae43c |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=45 | 2026-11-09 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 4/4 / 29/29 | pfc_1c8a3f09b0a9d1af3f2fc6e9 |
| 1x2 single[zulubet] avg_p>=40 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_1e9cfc6500aaac77afa1eaf9 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=35 | 2026-11-07 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 6/6 / 29/29 | pfc_232a31896c20989d0aa3f999 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=60 | 2026-11-12 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 1/1 / 29/29 | pfc_2a4f2be544cd9d59f3cb7098 |
| 1x2 unanimous[statarea+zulubet] avg_p>=35 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_3072388544a60552346bd162 |
| 1x2 single[zulubet] avg_p>=60 | 2026-10-20 / benched | ROI unavailable; hit 100.0% (1/1); 0 priced; coverage 0.0%; provisional | ROI unavailable; hit 100.0% (1/1); 0 priced; coverage 0.0%; provisional | 24/24 / 29/29 | pfc_35f7e50bf23db96c2d3dd59d |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=35 | 2026-11-04 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 9/9 / 29/29 | pfc_37f18dce9f6de45ee38e4944 |
| 1x2 single[zulubet] avg_p>=0 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_3dc0fa6511953bf09bc4c845 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=50 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_3fbabd0ade3f89853e43fb10 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=60 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_40b163633fc01fd0ff7d0ef1 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=50 | 2026-11-09 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI -3.3%; hit 66.7% (2/3); 2 priced; coverage 66.7%; provisional | 4/4 / 29/29 | pfc_444d408c4ccd3a4bf4fb020c |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=40 | 2026-11-03 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 10/10 / 29/29 | pfc_48e25c370ae15b7d58d6b0d8 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=55 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_4e2583010bf805466e33c2d0 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=0 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_4f2df06575151e798727a6b0 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=55 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_527524a94e98cff9740d499c |
| 1x2 single[zulubet] avg_p>=65 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_5954379f3a12700edcfd8387 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=50 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_5f861bad9f49ebf6d6fe2c16 |
| 1x2 single[zulubet] avg_p>=35 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_61cb1dd2a3157c4231070cdb |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=50 | 2026-11-08 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_626748d56ba5fd423f2f41a3 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=0 | 2026-11-11 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI -42.3%; hit 33.3% (1/3); 3 priced; coverage 100.0%; provisional | 2/2 / 29/29 | pfc_642ac9053223500b638e3451 |
| 1x2 unanimous[predictz+vitibet] avg_p>=0 | 2026-11-10 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 3/3 / 29/29 | pfc_663996383d524cb4a7c24883 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=35 | 2026-11-11 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 2/2 / 29/29 | pfc_66a32773b3535996c572d351 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=40 | 2026-11-09 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 4/4 / 29/29 | pfc_69dd4c8623d4d22d840da318 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=40 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_6cd236448d9fd967f8dcb591 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=0 | 2026-10-24 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 20/20 / 29/29 | pfc_754f7247e83f901ae415b35f |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=35 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_7d20e19c2c26174fa21e9e86 |
| 1x2 unanimous[statarea+zulubet] avg_p>=60 | 2026-11-12 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 1/1 / 29/29 | pfc_7e79a7652db874e451b269cb |
| 1x2 unanimous[statarea+zulubet] avg_p>=45 | 2026-10-21 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 23/23 / 29/29 | pfc_7eb24434123da46374442290 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=45 | 2026-11-09 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 4/4 / 29/29 | pfc_84cede54e10853cd914d57c5 |
| 1x2 unanimous[bzzoiro+zulubet] avg_p>=40 | 2026-11-09 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 4/4 / 29/29 | pfc_8a0a249809c613c08466ced0 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=0 | 2026-11-04 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 9/9 / 29/29 | pfc_8e39a2c5719c5a609c077afd |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=0 | 2026-11-07 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 6/6 / 29/29 | pfc_92ab281aa7c2173e7502ba49 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=45 | 2026-10-24 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 20/20 / 29/29 | pfc_9ae5a305a703bca83fd321b3 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=45 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_a460a0e9dcb1f980cde169c0 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=35 | 2026-10-24 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 20/20 / 29/29 | pfc_a8e99ebc0016f0d0bb95aa70 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=60 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_a90a9b922d2318a2446434ce |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=35 | 2026-11-03 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 10/10 / 29/29 | pfc_ad11db4313c86de27efdde5a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=0 | 2026-11-03 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 10/10 / 29/29 | pfc_ad177634c86053c1c32b77cd |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=35 | 2026-10-30 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 14/14 / 29/29 | pfc_adb24b31e9ca43c42506156a |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=40 | 2026-11-09 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 4/4 / 29/29 | pfc_af020bcd1589e288dccb8d3e |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=50 | 2026-10-30 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 14/14 / 29/29 | pfc_afdf26c0a105a0f5e6ffff27 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=50 | 2026-11-03 / benched | ROI unavailable; hit 0.0% (0/1); 0 priced; coverage 0.0%; provisional | ROI unavailable; hit 0.0% (0/1); 0 priced; coverage 0.0%; provisional | 10/10 / 29/29 | pfc_b0b7a0c1932e3636d2b485d6 |
| 1x2 unanimous[statarea+zulubet] avg_p>=0 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_b11e22bfdd27d85fad78ba74 |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=40 | 2026-10-30 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 14/14 / 29/29 | pfc_b9aa429be62178cc76b1ca8d |
| ou_3.5 unanimous[scoutingstats+statarea] avg_p>=70 | 2026-10-25 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 19/19 / 29/29 | pfc_bdce95a736d6cc8667f7ac31 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=55 | 2026-11-06 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 7/7 / 29/29 | pfc_c0b0989eed26d614ffd9cfaf |
| 1x2 unanimous[statarea+zulubet] avg_p>=50 | 2026-10-21 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 23/23 / 29/29 | pfc_c83d885867c9025a351b9b8c |
| 1x2 unanimous[bzzoiro+zulubet] avg_p>=35 | 2026-11-09 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 4/4 / 29/29 | pfc_c89a3f96c2ce41dd507f7592 |
| 1x2 unanimous[predictz+scoutingstats] avg_p>=0 | 2026-11-12 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 1/1 / 29/29 | pfc_c89f0a80e266476539277636 |
| 1x2 single[zulubet] avg_p>=70 | 2026-10-20 / benched | ROI unavailable; hit 100.0% (1/1); 0 priced; coverage 0.0%; provisional | ROI unavailable; hit 100.0% (1/1); 0 priced; coverage 0.0%; provisional | 24/24 / 29/29 | pfc_c8cbcf76ea758fd6de596ae1 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=55 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_d17123b85e11155f22e40051 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=35 | 2026-11-01 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_d5c311b6e2f37443e3501556 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=45 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_e25602082a90cb64fb9c5451 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=45 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_e37e7d70a4d046d7a07da0a4 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=40 | 2026-11-09 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 4/4 / 29/29 | pfc_e5c10af025fc5071367c9b47 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=55 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_f2b2a2e84093abe72bbc01c0 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=50 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_f51b5fdaf32bcca063f4b2cc |
| ou_3.5 single[scoutingstats] avg_p>=80 | 2026-11-08 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_f8aaa9292b8db7b8ceac0414 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=50 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 24/24 / 29/29 | pfc_fb2e721d2bb8a41fe9fa3713 |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=0 | 2026-10-30 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 14/14 / 29/29 | pfc_fc7adf360790baec2b1ce044 |
| unanimous[betclan+statarea+vitibet] avg_p>=65 | unavailable / unavailable | unavailable | ROI +50.0%; hit 100.0% (2/2); 2 priced; coverage 100.0%; provisional | unavailable / 29/29 | unanimous[betclan+statarea+vitibet] avg_p>=65 |
| unanimous[betclan+vitibet] avg_p>=70 | unavailable / unavailable | unavailable | ROI +33.7%; hit 100.0% (7/7); 6 priced; coverage 85.7%; provisional | unavailable / 29/29 | unanimous[betclan+vitibet] avg_p>=70 |
| unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65 | unavailable / unavailable | unavailable | ROI +18.0%; hit 100.0% (2/2); 2 priced; coverage 100.0%; provisional | unavailable / 29/29 | unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65 |
| unanimous[bzzoiro+statarea+vitibet] avg_p>=65 | unavailable / unavailable | unavailable | ROI -33.5%; hit 60.0% (3/5); 4 priced; coverage 80.0%; provisional | unavailable / 29/29 | unanimous[bzzoiro+statarea+vitibet] avg_p>=65 |
| unanimous[bzzoiro+vitibet+zulubet] avg_p>=65 | unavailable / unavailable | unavailable | ROI +15.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | unavailable / 29/29 | unanimous[bzzoiro+vitibet+zulubet] avg_p>=65 |
| unanimous[bzzoiro+vitibet] avg_p>=70 | unavailable / unavailable | unavailable | ROI -35.2%; hit 50.0% (4/8); 8 priced; coverage 100.0%; provisional | unavailable / 29/29 | unanimous[bzzoiro+vitibet] avg_p>=70 |
| unanimous[statarea+vitibet+zulubet] avg_p>=65 | unavailable / unavailable | unavailable | ROI -2.5%; hit 50.0% (1/2); 2 priced; coverage 100.0%; provisional | unavailable / 29/29 | unanimous[statarea+vitibet+zulubet] avg_p>=65 |
| unanimous[statarea+vitibet] avg_p>=70 | unavailable / unavailable | unavailable | ROI +25.8%; hit 100.0% (18/18); 13 priced; coverage 72.2%; provisional | unavailable / 29/29 | unanimous[statarea+vitibet] avg_p>=70 |
| unanimous[vitibet+zulubet] avg_p>=70 | unavailable / unavailable | unavailable | ROI +38.7%; hit 100.0% (3/3); 3 priced; coverage 100.0%; provisional | unavailable / 29/29 | unanimous[vitibet+zulubet] avg_p>=70 |

### Price provenance — operational windows

Only windows with settled rows are listed below: evidence class, settled/priced rows and quarantine reasons. A priced row alone is not proof of an executable quote.

| Rule | Window | Evidence class: settled / priced | Quarantine reason: settled / priced | Stored key |
| --- | --- | --- | --- | --- |
| 1x2 single[scoutingstats] avg_p>=65 | Since activation | NAMED_BOOKMAKER_PRICE: 94/94; SCOUTINGSTATS_SOLE: 12/12; SUSPECT_ALIAS_FUZZY: 31/0 | NONE: 94/94; alias_fuzzy: 31/0; scoutingstats_sole_source: 12/12 | pfc_fdade2e70df4d4bb78a8cd6e |
| 1x2 single[scoutingstats] avg_p>=65 | Last 30 days | NAMED_BOOKMAKER_PRICE: 94/94; SCOUTINGSTATS_SOLE: 12/12; SUSPECT_ALIAS_FUZZY: 31/0 | NONE: 94/94; alias_fuzzy: 31/0; scoutingstats_sole_source: 12/12 | pfc_fdade2e70df4d4bb78a8cd6e |
| ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55 | Since activation | NAMED_BOOKMAKER_PRICE: 75/75; SCOUTINGSTATS_SOLE: 4/4; SUSPECT_ALIAS_FUZZY: 5/0 | NONE: 75/75; alias_fuzzy: 5/0; scoutingstats_sole_source: 4/4 | pfc_27e0f725859bc708f95c58a3 |
| ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55 | Last 30 days | NAMED_BOOKMAKER_PRICE: 75/75; SCOUTINGSTATS_SOLE: 4/4; SUSPECT_ALIAS_FUZZY: 5/0 | NONE: 75/75; alias_fuzzy: 5/0; scoutingstats_sole_source: 4/4 | pfc_27e0f725859bc708f95c58a3 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=35 | Since activation | NAMED_BOOKMAKER_PRICE: 204/204; SCOUTINGSTATS_SOLE: 12/12; SUSPECT_ALIAS_FUZZY: 21/0 | NONE: 204/204; alias_fuzzy: 21/0; scoutingstats_sole_source: 12/12 | pfc_f56fe4a2759e9b17b9bdb116 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=35 | Last 30 days | NAMED_BOOKMAKER_PRICE: 204/204; SCOUTINGSTATS_SOLE: 12/12; SUSPECT_ALIAS_FUZZY: 21/0 | NONE: 204/204; alias_fuzzy: 21/0; scoutingstats_sole_source: 12/12 | pfc_f56fe4a2759e9b17b9bdb116 |
| 1x2 single[scoutingstats] avg_p>=50 | Since activation | NAMED_BOOKMAKER_PRICE: 168/168; SCOUTINGSTATS_SOLE: 28/28; SUSPECT_ALIAS_FUZZY: 51/0 | NONE: 168/168; alias_fuzzy: 51/0; scoutingstats_sole_source: 28/28 | pfc_439097cb9bb700e9996c0b07 |
| 1x2 single[scoutingstats] avg_p>=50 | Last 30 days | NAMED_BOOKMAKER_PRICE: 168/168; SCOUTINGSTATS_SOLE: 28/28; SUSPECT_ALIAS_FUZZY: 51/0 | NONE: 168/168; alias_fuzzy: 51/0; scoutingstats_sole_source: 28/28 | pfc_439097cb9bb700e9996c0b07 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=0 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_b4407145af67d2f93e48f0ef |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=0 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_b4407145af67d2f93e48f0ef |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=45 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_ed44334de1c8307f22b510ab |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=45 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_ed44334de1c8307f22b510ab |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=40 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_cd84fb2c3ed889c0ae9eb89e |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=40 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_cd84fb2c3ed889c0ae9eb89e |
| 1x2 single[zulubet] avg_p>=50 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1; SCOUTINGSTATS_SOLE: 1/1; UNMATCHED: 2/0 | NONE: 3/1; scoutingstats_sole_source: 1/1 | pfc_4cf3df8552488297d7ccf526 |
| 1x2 single[zulubet] avg_p>=50 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1; SCOUTINGSTATS_SOLE: 1/1; UNMATCHED: 2/0 | NONE: 3/1; scoutingstats_sole_source: 1/1 | pfc_4cf3df8552488297d7ccf526 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=60 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_54fcf87604b73b87ee6c0a90 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=60 | Last 30 days | APPROVED_DONOR_PRICE: 1/1; NAMED_BOOKMAKER_PRICE: 4/4; SUSPECT_ALIAS_FUZZY: 2/0; UNMATCHED: 1/0 | NONE: 6/5; alias_fuzzy: 2/0 | pfc_54fcf87604b73b87ee6c0a90 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=0 | Since activation | NAMED_BOOKMAKER_PRICE: 4/4 | NONE: 4/4 | pfc_0ad08cd1b2e75a2c9051189e |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=0 | Last 30 days | NAMED_BOOKMAKER_PRICE: 4/4 | NONE: 4/4 | pfc_0ad08cd1b2e75a2c9051189e |
| 1x2 unanimous[statarea+zulubet] avg_p>=40 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_5208b9e15194a691590430ad |
| 1x2 unanimous[statarea+zulubet] avg_p>=40 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_5208b9e15194a691590430ad |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=55 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_fbf508b9c62bae8f281bb6e1 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=55 | Last 30 days | NAMED_BOOKMAKER_PRICE: 6/6 | NONE: 6/6 | pfc_fbf508b9c62bae8f281bb6e1 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=50 | Since activation | NAMED_BOOKMAKER_PRICE: 5/5; SUSPECT_ALIAS_FUZZY: 1/0; UNMATCHED: 5/0 | NONE: 10/5; alias_fuzzy: 1/0 | pfc_234f16641d9893e8ec2a01f0 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=50 | Last 30 days | NAMED_BOOKMAKER_PRICE: 5/5; SUSPECT_ALIAS_FUZZY: 1/0; UNMATCHED: 5/0 | NONE: 10/5; alias_fuzzy: 1/0 | pfc_234f16641d9893e8ec2a01f0 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=0 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_cddf4106a3d45b6e455d8c73 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=0 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_cddf4106a3d45b6e455d8c73 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=40 | Since activation | NAMED_BOOKMAKER_PRICE: 7/7; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 7/7; alias_fuzzy: 1/0 | pfc_a7ba6711aeb15b9804a94f06 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=40 | Last 30 days | NAMED_BOOKMAKER_PRICE: 7/7; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 7/7; alias_fuzzy: 1/0 | pfc_a7ba6711aeb15b9804a94f06 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35 | Since activation | NAMED_BOOKMAKER_PRICE: 2/2 | NONE: 2/2 | pfc_73b036a8ee8dd5a4dea48134 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35 | Last 30 days | NAMED_BOOKMAKER_PRICE: 40/40; SCOUTINGSTATS_SOLE: 2/2; SUSPECT_ALIAS_FUZZY: 2/0 | NONE: 40/40; alias_fuzzy: 2/0; scoutingstats_sole_source: 2/2 | pfc_73b036a8ee8dd5a4dea48134 |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=70 | Since activation | NAMED_BOOKMAKER_PRICE: 5/5; SUSPECT_ALIAS_FUZZY: 2/0 | NONE: 5/5; alias_fuzzy: 2/0 | pfc_4a3e5fbac72b2ebef11632f0 |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=70 | Last 30 days | NAMED_BOOKMAKER_PRICE: 5/5; SUSPECT_ALIAS_FUZZY: 2/0 | NONE: 5/5; alias_fuzzy: 2/0 | pfc_4a3e5fbac72b2ebef11632f0 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=50 | Since activation | NAMED_BOOKMAKER_PRICE: 2/2 | NONE: 2/2 | pfc_0b290b623e2a54ea7df3006c |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=50 | Last 30 days | NAMED_BOOKMAKER_PRICE: 2/2 | NONE: 2/2 | pfc_0b290b623e2a54ea7df3006c |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=60 | Since activation | NAMED_BOOKMAKER_PRICE: 8/8; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 8/8; alias_fuzzy: 1/0 | pfc_5904b1fc7050646e6321090c |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=60 | Last 30 days | NAMED_BOOKMAKER_PRICE: 8/8; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 8/8; alias_fuzzy: 1/0 | pfc_5904b1fc7050646e6321090c |
| ou_2.5 unanimous[scoutingstats+statarea] avg_p>=60 | Since activation | NAMED_BOOKMAKER_PRICE: 4/4 | NONE: 4/4 | pfc_ee214d4f2f00846fa78f56e3 |
| ou_2.5 unanimous[scoutingstats+statarea] avg_p>=60 | Last 30 days | NAMED_BOOKMAKER_PRICE: 4/4 | NONE: 4/4 | pfc_ee214d4f2f00846fa78f56e3 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 | Since activation | NAMED_BOOKMAKER_PRICE: 7/7 | NONE: 7/7 | pfc_4a1f2bb2278d13c8189148d0 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 | Last 30 days | NAMED_BOOKMAKER_PRICE: 7/7 | NONE: 7/7 | pfc_4a1f2bb2278d13c8189148d0 |
| 1x2 single[scoutingstats] avg_p>=60 | Since activation | APPROVED_DONOR_PRICE: 1/1; NAMED_BOOKMAKER_PRICE: 3/3 | NONE: 4/4 | pfc_0f100c9da356ed1c05d9c642 |
| 1x2 single[scoutingstats] avg_p>=60 | Last 30 days | APPROVED_DONOR_PRICE: 1/1; NAMED_BOOKMAKER_PRICE: 3/3 | NONE: 4/4 | pfc_0f100c9da356ed1c05d9c642 |
| 1x2 single[zulubet] avg_p>=55 | Since activation | NAMED_BOOKMAKER_PRICE: 17/17; SUSPECT_ALIAS_FUZZY: 1/0; UNMATCHED: 22/0 | NONE: 39/17; alias_fuzzy: 1/0 | pfc_1607fec83282d02c5254c2bf |
| 1x2 single[zulubet] avg_p>=55 | Last 30 days | NAMED_BOOKMAKER_PRICE: 17/17; SUSPECT_ALIAS_FUZZY: 1/0; UNMATCHED: 22/0 | NONE: 39/17; alias_fuzzy: 1/0 | pfc_1607fec83282d02c5254c2bf |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=40 | Since activation | NAMED_BOOKMAKER_PRICE: 14/14; SCOUTINGSTATS_SOLE: 2/2; SUSPECT_ALIAS_FUZZY: 2/0 | NONE: 14/14; alias_fuzzy: 2/0; scoutingstats_sole_source: 2/2 | pfc_226efd387e217a9d58a11f79 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=40 | Last 30 days | NAMED_BOOKMAKER_PRICE: 14/14; SCOUTINGSTATS_SOLE: 2/2; SUSPECT_ALIAS_FUZZY: 2/0 | NONE: 14/14; alias_fuzzy: 2/0; scoutingstats_sole_source: 2/2 | pfc_226efd387e217a9d58a11f79 |
| ou_2.5 unanimous[scoutingstats+statarea] avg_p>=65 | Since activation | NAMED_BOOKMAKER_PRICE: 23/23; SCOUTINGSTATS_SOLE: 1/1; SUSPECT_ALIAS_FUZZY: 2/0 | NONE: 23/23; alias_fuzzy: 2/0; scoutingstats_sole_source: 1/1 | pfc_4e8ef1faa47bce63a119fb43 |
| ou_2.5 unanimous[scoutingstats+statarea] avg_p>=65 | Last 30 days | NAMED_BOOKMAKER_PRICE: 23/23; SCOUTINGSTATS_SOLE: 1/1; SUSPECT_ALIAS_FUZZY: 2/0 | NONE: 23/23; alias_fuzzy: 2/0; scoutingstats_sole_source: 1/1 | pfc_4e8ef1faa47bce63a119fb43 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=40 | Since activation | NAMED_BOOKMAKER_PRICE: 12/12; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 12/12; alias_fuzzy: 1/0 | pfc_d94d447efe0742440e953722 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=40 | Last 30 days | NAMED_BOOKMAKER_PRICE: 12/12; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 12/12; alias_fuzzy: 1/0 | pfc_d94d447efe0742440e953722 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=40 | Since activation | NAMED_BOOKMAKER_PRICE: 2/2; SUSPECT_ALIAS_FUZZY: 4/0 | NONE: 2/2; alias_fuzzy: 4/0 | pfc_c7c9572806b564198f651cee |
| 1x2 unanimous[vitibet+zulubet] avg_p>=40 | Last 30 days | NAMED_BOOKMAKER_PRICE: 2/2; SUSPECT_ALIAS_FUZZY: 4/0 | NONE: 2/2; alias_fuzzy: 4/0 | pfc_c7c9572806b564198f651cee |
| 1x2 unanimous[statarea+zulubet] avg_p>=55 | Since activation | NAMED_BOOKMAKER_PRICE: 2/2; UNMATCHED: 1/0 | NONE: 3/2 | pfc_5a9d3d3426ee7a4e63461d75 |
| 1x2 unanimous[statarea+zulubet] avg_p>=55 | Last 30 days | NAMED_BOOKMAKER_PRICE: 2/2; UNMATCHED: 1/0 | NONE: 3/2 | pfc_5a9d3d3426ee7a4e63461d75 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=0 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_0187397f26c1f84f6c3a9883 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=0 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_0187397f26c1f84f6c3a9883 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=55 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 1/1; alias_fuzzy: 1/0 | pfc_2bd498a3472b7bbd71982ece |
| 1x2 unanimous[vitibet+zulubet] avg_p>=55 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 1/1; alias_fuzzy: 1/0 | pfc_2bd498a3472b7bbd71982ece |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_3bfaf30507905754f7faab2a |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_3bfaf30507905754f7faab2a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=35 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_a3afbb848e0c474b683b450f |
| 1x2 unanimous[vitibet+zulubet] avg_p>=35 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_a3afbb848e0c474b683b450f |
| 1x2 unanimous[vitibet+zulubet] avg_p>=45 | Since activation | NAMED_BOOKMAKER_PRICE: 2/2 | NONE: 2/2 | pfc_b011652ec3e473fbc0afbb6a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=45 | Last 30 days | NAMED_BOOKMAKER_PRICE: 9/9; UNMATCHED: 2/0 | NONE: 11/9 | pfc_b011652ec3e473fbc0afbb6a |
| ml-meta avg_p>=60 | Last 30 days | NAMED_BOOKMAKER_PRICE: 45/45; SCOUTINGSTATS_SOLE: 7/7; SOURCE_FALLBACK: 4/4; SUSPECT_ALIAS_FUZZY: 5/5; UNMATCHED: 9/0 | NONE: 53/45; alias_fuzzy: 5/5; scoutingstats_sole_source: 7/7; source_fallback_not_execution_eligible: 4/4; stale_quote: 1/0 | ml-meta avg_p>=60 |
| 1x2 single[zulubet] avg_p>=45 | Since activation | UNMATCHED: 1/0 | NONE: 1/0 | pfc_14ee12458803822df3013bcd |
| 1x2 single[zulubet] avg_p>=45 | Last 30 days | UNMATCHED: 1/0 | NONE: 1/0 | pfc_14ee12458803822df3013bcd |
| 1x2 single[zulubet] avg_p>=60 | Since activation | UNMATCHED: 1/0 | NONE: 1/0 | pfc_35f7e50bf23db96c2d3dd59d |
| 1x2 single[zulubet] avg_p>=60 | Last 30 days | UNMATCHED: 1/0 | NONE: 1/0 | pfc_35f7e50bf23db96c2d3dd59d |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=50 | Last 30 days | NAMED_BOOKMAKER_PRICE: 2/2; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 2/2; alias_fuzzy: 1/0 | pfc_444d408c4ccd3a4bf4fb020c |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=0 | Last 30 days | NAMED_BOOKMAKER_PRICE: 3/3 | NONE: 3/3 | pfc_642ac9053223500b638e3451 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=50 | Since activation | UNMATCHED: 1/0 | NONE: 1/0 | pfc_b0b7a0c1932e3636d2b485d6 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=50 | Last 30 days | UNMATCHED: 1/0 | NONE: 1/0 | pfc_b0b7a0c1932e3636d2b485d6 |
| 1x2 single[zulubet] avg_p>=70 | Since activation | SUSPECT_ALIAS_FUZZY: 1/0 | alias_fuzzy: 1/0 | pfc_c8cbcf76ea758fd6de596ae1 |
| 1x2 single[zulubet] avg_p>=70 | Last 30 days | SUSPECT_ALIAS_FUZZY: 1/0 | alias_fuzzy: 1/0 | pfc_c8cbcf76ea758fd6de596ae1 |
| unanimous[betclan+statarea+vitibet] avg_p>=65 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1; SCOUTINGSTATS_SOLE: 1/1 | NONE: 1/1; scoutingstats_sole_source: 1/1 | unanimous[betclan+statarea+vitibet] avg_p>=65 |
| unanimous[betclan+vitibet] avg_p>=70 | Last 30 days | NAMED_BOOKMAKER_PRICE: 5/5; SCOUTINGSTATS_SOLE: 1/1; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 5/5; alias_fuzzy: 1/0; scoutingstats_sole_source: 1/1 | unanimous[betclan+vitibet] avg_p>=70 |
| unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65 | Last 30 days | NAMED_BOOKMAKER_PRICE: 2/2 | NONE: 2/2 | unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65 |
| unanimous[bzzoiro+statarea+vitibet] avg_p>=65 | Last 30 days | NAMED_BOOKMAKER_PRICE: 4/4; UNMATCHED: 1/0 | NONE: 5/4 | unanimous[bzzoiro+statarea+vitibet] avg_p>=65 |
| unanimous[bzzoiro+vitibet+zulubet] avg_p>=65 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | unanimous[bzzoiro+vitibet+zulubet] avg_p>=65 |
| unanimous[bzzoiro+vitibet] avg_p>=70 | Last 30 days | NAMED_BOOKMAKER_PRICE: 8/8 | NONE: 8/8 | unanimous[bzzoiro+vitibet] avg_p>=70 |
| unanimous[statarea+vitibet+zulubet] avg_p>=65 | Last 30 days | NAMED_BOOKMAKER_PRICE: 2/2 | NONE: 2/2 | unanimous[statarea+vitibet+zulubet] avg_p>=65 |
| unanimous[statarea+vitibet] avg_p>=70 | Last 30 days | NAMED_BOOKMAKER_PRICE: 12/12; SCOUTINGSTATS_SOLE: 1/1; SUSPECT_ALIAS_FUZZY: 1/0; UNMATCHED: 4/0 | NONE: 16/12; alias_fuzzy: 1/0; scoutingstats_sole_source: 1/1 | unanimous[statarea+vitibet] avg_p>=70 |
| unanimous[vitibet+zulubet] avg_p>=70 | Last 30 days | NAMED_BOOKMAKER_PRICE: 2/2; SOURCE_FALLBACK: 1/1 | NONE: 2/2; source_fallback_not_execution_eligible: 1/1 | unanimous[vitibet+zulubet] avg_p>=70 |

### Historical validation — NOT operational performance

Registry validation is separate research evidence, not extra live observations. Price basis and mining dates are retained; unavailable fields are not inferred.

| Rule | Validation settled / priced | Pricing coverage | Hit rate | ROI | Mining window | Price basis | Stored key |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1x2 single[scoutingstats] avg_p>=65 | 398 / 398 | 100.0% | 80.2% | 0.1% | start: 2026-06-13; split: 2026-09-27; as_of_exclusive: 2026-10-25 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_fdade2e70df4d4bb78a8cd6e |
| ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55 | 347 / 347 | 100.0% | 66.6% | 0.8% | start: 2026-06-13; split: 2026-09-25; as_of_exclusive: 2026-10-23 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_27e0f725859bc708f95c58a3 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=35 | 1257 / 1257 | 100.0% | 56.8% | 0.1% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_f56fe4a2759e9b17b9bdb116 |
| 1x2 single[scoutingstats] avg_p>=50 | 1235 / 1235 | 100.0% | 67.5% | 0.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_439097cb9bb700e9996c0b07 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=0 | 367 / 367 | 100.0% | 60.2% | 3.3% | start: 2026-06-13; split: 2026-10-04; as_of_exclusive: 2026-11-01 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_b4407145af67d2f93e48f0ef |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=45 | 262 / 262 | 100.0% | 64.5% | 1.9% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_ed44334de1c8307f22b510ab |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=40 | 531 / 531 | 100.0% | 58.4% | 0.2% | start: 2026-06-13; split: 2026-10-05; as_of_exclusive: 2026-11-02 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_cd84fb2c3ed889c0ae9eb89e |
| 1x2 single[zulubet] avg_p>=50 | 1241 / 1240 | 99.9% | 57.4% | 0.5% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_4cf3df8552488297d7ccf526 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=60 | 348 / 348 | 100.0% | 71.5% | 0.5% | start: 2026-06-13; split: 2026-10-15; as_of_exclusive: 2026-11-12 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_54fcf87604b73b87ee6c0a90 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=0 | 438 / 438 | 100.0% | 61.2% | 2.9% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_0ad08cd1b2e75a2c9051189e |
| 1x2 unanimous[statarea+zulubet] avg_p>=40 | 278 / 277 | 99.6% | 61.9% | 1.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_5208b9e15194a691590430ad |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=55 | 201 / 201 | 100.0% | 69.7% | 0.4% | start: 2026-06-13; split: 2026-10-12; as_of_exclusive: 2026-11-09 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_fbf508b9c62bae8f281bb6e1 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=50 | 427 / 427 | 100.0% | 66.5% | 4.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_234f16641d9893e8ec2a01f0 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=0 | 1258 / 1258 | 100.0% | 56.8% | 0.1% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_cddf4106a3d45b6e455d8c73 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=40 | 382 / 382 | 100.0% | 64.9% | 1.2% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_a7ba6711aeb15b9804a94f06 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35 | 561 / 561 | 100.0% | 56.9% | 0.1% | start: 2026-06-13; split: 2026-10-10; as_of_exclusive: 2026-11-07 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_73b036a8ee8dd5a4dea48134 |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=70 | 165 / 165 | 100.0% | 79.4% | 0.6% | start: 2026-06-13; split: 2026-10-12; as_of_exclusive: 2026-11-09 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_4a3e5fbac72b2ebef11632f0 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=50 | 201 / 201 | 100.0% | 69.7% | 0.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_0b290b623e2a54ea7df3006c |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=60 | 203 / 203 | 100.0% | 81.3% | 6.8% | start: 2026-06-13; split: 2026-09-27; as_of_exclusive: 2026-10-25 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_5904b1fc7050646e6321090c |
| ou_2.5 unanimous[scoutingstats+statarea] avg_p>=60 | 612 / 612 | 100.0% | 68.3% | 0.1% | start: 2026-06-13; split: 2026-10-08; as_of_exclusive: 2026-11-05 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_ee214d4f2f00846fa78f56e3 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 | 426 / 426 | 100.0% | 62.2% | 4.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_4a1f2bb2278d13c8189148d0 |
| 1x2 single[scoutingstats] avg_p>=60 | 566 / 566 | 100.0% | 76.3% | 0.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_0f100c9da356ed1c05d9c642 |
| 1x2 single[zulubet] avg_p>=55 | 864 / 863 | 99.9% | 64.6% | 4.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_1607fec83282d02c5254c2bf |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=40 | 360 / 360 | 100.0% | 60.8% | 4.0% | start: 2026-06-13; split: 2026-10-04; as_of_exclusive: 2026-11-01 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_226efd387e217a9d58a11f79 |
| ou_2.5 unanimous[scoutingstats+statarea] avg_p>=65 | 321 / 321 | 100.0% | 72.0% | 0.1% | start: 2026-06-13; split: 2026-10-05; as_of_exclusive: 2026-11-02 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_4e8ef1faa47bce63a119fb43 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=40 | 822 / 822 | 100.0% | 59.7% | 0.2% | start: 2026-06-13; split: 2026-09-23; as_of_exclusive: 2026-10-21 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_d94d447efe0742440e953722 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=40 | 649 / 649 | 100.0% | 62.3% | 1.4% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_c7c9572806b564198f651cee |
| 1x2 unanimous[statarea+zulubet] avg_p>=55 | 222 / 221 | 99.5% | 73.4% | 3.6% | start: 2026-06-13; split: 2026-09-23; as_of_exclusive: 2026-10-21 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_5a9d3d3426ee7a4e63461d75 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=0 | 390 / 390 | 100.0% | 64.1% | 0.2% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_0187397f26c1f84f6c3a9883 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=55 | 358 / 358 | 100.0% | 68.2% | 2.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_2bd498a3472b7bbd71982ece |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 | 645 / 645 | 100.0% | 65.1% | 1.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_3bfaf30507905754f7faab2a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=35 | 655 / 655 | 100.0% | 61.8% | 0.7% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_a3afbb848e0c474b683b450f |
| 1x2 unanimous[vitibet+zulubet] avg_p>=45 | 540 / 540 | 100.0% | 62.2% | 0.3% | start: 2026-06-13; split: 2026-09-29; as_of_exclusive: 2026-10-27 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_b011652ec3e473fbc0afbb6a |
| ml-meta avg_p>=60 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | ml-meta avg_p>=60 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=0 | 311 / 311 | 100.0% | 65.0% | 0.2% | start: 2026-06-13; split: 2026-10-10; as_of_exclusive: 2026-11-07 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_051ee3ee0d476984665d1f43 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=35 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_054448b499623dd39b072b38 |
| 1x2 unanimous[predictz+statarea] avg_p>=0 | 166 / 150 | 90.4% | 58.4% | 4623.4% | start: 2026-06-13; split: 2026-10-14; as_of_exclusive: 2026-11-11 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_079067dbb6dd2b8a93eb13a6 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=45 | 540 / 540 | 100.0% | 64.3% | 2.7% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_0aed63f3d04b46330958121d |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=65 | 143 / 143 | 100.0% | 80.4% | 4.8% | start: 2026-06-13; split: 2026-10-11; as_of_exclusive: 2026-11-08 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_0d71c5e45469731a1fc4b8d1 |
| 1x2 unanimous[bzzoiro+zulubet] avg_p>=0 | 264 / 264 | 100.0% | 61.0% | 0.1% | start: 2026-06-13; split: 2026-10-12; as_of_exclusive: 2026-11-09 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_0ebe3a9a402a26bfa4e53552 |
| 1x2 unanimous[bettingclosed+scoutingstats+statarea] avg_p>=0 | 217 / 217 | 100.0% | 64.1% | 1.3% | start: 2026-06-13; split: 2026-10-11; as_of_exclusive: 2026-11-08 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_0fae0b61dd393c289b12b9b8 |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=45 | 240 / 240 | 100.0% | 60.0% | 0.4% | start: 2026-06-13; split: 2026-10-02; as_of_exclusive: 2026-10-30 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_144c01b1aa366b88f9c4083a |
| 1x2 unanimous[predictz+scoutingstats+vitibet] avg_p>=0 | 129 / 129 | 100.0% | 63.6% | 0.8% | start: 2026-06-13; split: 2026-10-10; as_of_exclusive: 2026-11-07 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_14c827df1f0bd5801d2ef540 |
| 1x2 single[zulubet] avg_p>=45 | 1488 / 1487 | 99.9% | 55.6% | 2.5% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_14ee12458803822df3013bcd |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=55 | 248 / 248 | 100.0% | 75.8% | 4.5% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_1ba3ab3c75e6f3a9680ae43c |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=45 | 195 / 195 | 100.0% | 66.7% | 0.7% | start: 2026-06-13; split: 2026-10-12; as_of_exclusive: 2026-11-09 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_1c8a3f09b0a9d1af3f2fc6e9 |
| 1x2 single[zulubet] avg_p>=40 | 1660 / 1659 | 99.9% | 53.2% | 0.9% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_1e9cfc6500aaac77afa1eaf9 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=35 | 311 / 311 | 100.0% | 65.0% | 0.2% | start: 2026-06-13; split: 2026-10-10; as_of_exclusive: 2026-11-07 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_232a31896c20989d0aa3f999 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=60 | 143 / 143 | 100.0% | 72.0% | 0.1% | start: 2026-06-13; split: 2026-10-15; as_of_exclusive: 2026-11-12 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_2a4f2be544cd9d59f3cb7098 |
| 1x2 unanimous[statarea+zulubet] avg_p>=35 | 284 / 283 | 99.6% | 61.3% | 0.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_3072388544a60552346bd162 |
| 1x2 single[zulubet] avg_p>=60 | 633 / 632 | 99.8% | 67.6% | 3.8% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_35f7e50bf23db96c2d3dd59d |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=35 | 248 / 248 | 100.0% | 63.3% | 0.3% | start: 2026-06-13; split: 2026-10-07; as_of_exclusive: 2026-11-04 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_37f18dce9f6de45ee38e4944 |
| 1x2 single[zulubet] avg_p>=0 | 1733 / 1732 | 99.9% | 52.7% | 1.3% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_3dc0fa6511953bf09bc4c845 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=50 | 285 / 285 | 100.0% | 68.4% | 4.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_3fbabd0ade3f89853e43fb10 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=60 | 195 / 195 | 100.0% | 79.0% | 5.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_40b163633fc01fd0ff7d0ef1 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=50 | 200 / 200 | 100.0% | 69.0% | 1.8% | start: 2026-06-13; split: 2026-10-12; as_of_exclusive: 2026-11-09 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_444d408c4ccd3a4bf4fb020c |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=40 | 285 / 285 | 100.0% | 62.8% | 1.5% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_48e25c370ae15b7d58d6b0d8 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=55 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_4e2583010bf805466e33c2d0 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=0 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_4f2df06575151e798727a6b0 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=55 | 215 / 215 | 100.0% | 70.2% | 2.6% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_527524a94e98cff9740d499c |
| 1x2 single[zulubet] avg_p>=65 | 443 / 442 | 99.8% | 70.0% | 2.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_5954379f3a12700edcfd8387 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=50 | 372 / 372 | 100.0% | 68.0% | 0.3% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_5f861bad9f49ebf6d6fe2c16 |
| 1x2 single[zulubet] avg_p>=35 | 1732 / 1731 | 99.9% | 52.7% | 1.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_61cb1dd2a3157c4231070cdb |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=50 | 165 / 165 | 100.0% | 68.5% | 0.3% | start: 2026-06-13; split: 2026-10-11; as_of_exclusive: 2026-11-08 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_626748d56ba5fd423f2f41a3 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=0 | 326 / 326 | 100.0% | 62.3% | 0.3% | start: 2026-06-13; split: 2026-10-14; as_of_exclusive: 2026-11-11 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_642ac9053223500b638e3451 |
| 1x2 unanimous[predictz+vitibet] avg_p>=0 | 215 / 178 | 82.8% | 59.1% | 4921.0% | start: 2026-06-13; split: 2026-10-13; as_of_exclusive: 2026-11-10 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_663996383d524cb4a7c24883 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=35 | 326 / 326 | 100.0% | 62.3% | 0.3% | start: 2026-06-13; split: 2026-10-14; as_of_exclusive: 2026-11-11 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_66a32773b3535996c572d351 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=40 | 316 / 316 | 100.0% | 65.5% | 0.9% | start: 2026-06-13; split: 2026-10-12; as_of_exclusive: 2026-11-09 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_69dd4c8623d4d22d840da318 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=40 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_6cd236448d9fd967f8dcb591 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=0 | 169 / 169 | 100.0% | 67.5% | 1.6% | start: 2026-06-13; split: 2026-09-26; as_of_exclusive: 2026-10-24 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_754f7247e83f901ae415b35f |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=35 | 438 / 438 | 100.0% | 61.2% | 2.9% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_7d20e19c2c26174fa21e9e86 |
| 1x2 unanimous[statarea+zulubet] avg_p>=60 | 194 / 194 | 100.0% | 73.2% | 1.3% | start: 2026-06-13; split: 2026-10-15; as_of_exclusive: 2026-11-12 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_7e79a7652db874e451b269cb |
| 1x2 unanimous[statarea+zulubet] avg_p>=45 | 314 / 313 | 99.7% | 66.9% | 2.5% | start: 2026-06-13; split: 2026-09-23; as_of_exclusive: 2026-10-21 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_7eb24434123da46374442290 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=45 | 246 / 246 | 100.0% | 66.7% | 2.8% | start: 2026-06-13; split: 2026-10-12; as_of_exclusive: 2026-11-09 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_84cede54e10853cd914d57c5 |
| 1x2 unanimous[bzzoiro+zulubet] avg_p>=40 | 259 / 259 | 100.0% | 61.4% | 0.2% | start: 2026-06-13; split: 2026-10-12; as_of_exclusive: 2026-11-09 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_8a0a249809c613c08466ced0 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=0 | 248 / 248 | 100.0% | 63.3% | 0.3% | start: 2026-06-13; split: 2026-10-07; as_of_exclusive: 2026-11-04 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_8e39a2c5719c5a609c077afd |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=0 | 561 / 561 | 100.0% | 56.9% | 0.1% | start: 2026-06-13; split: 2026-10-10; as_of_exclusive: 2026-11-07 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_92ab281aa7c2173e7502ba49 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=45 | 229 / 229 | 100.0% | 67.7% | 0.6% | start: 2026-06-13; split: 2026-09-26; as_of_exclusive: 2026-10-24 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_9ae5a305a703bca83fd321b3 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=45 | 316 / 316 | 100.0% | 69.6% | 1.0% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_a460a0e9dcb1f980cde169c0 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=35 | 169 / 169 | 100.0% | 67.5% | 1.6% | start: 2026-06-13; split: 2026-09-26; as_of_exclusive: 2026-10-24 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_a8e99ebc0016f0d0bb95aa70 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=60 | 128 / 128 | 100.0% | 81.2% | 3.0% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_a90a9b922d2318a2446434ce |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=35 | 390 / 390 | 100.0% | 64.1% | 0.2% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_ad11db4313c86de27efdde5a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=0 | 655 / 655 | 100.0% | 61.8% | 0.7% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_ad177634c86053c1c32b77cd |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=35 | 240 / 240 | 100.0% | 60.0% | 0.4% | start: 2026-06-13; split: 2026-10-02; as_of_exclusive: 2026-10-30 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_adb24b31e9ca43c42506156a |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=40 | 266 / 266 | 100.0% | 65.0% | 2.2% | start: 2026-06-13; split: 2026-10-12; as_of_exclusive: 2026-11-09 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_af020bcd1589e288dccb8d3e |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=50 | 240 / 240 | 100.0% | 60.0% | 0.4% | start: 2026-06-13; split: 2026-10-02; as_of_exclusive: 2026-10-30 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_afdf26c0a105a0f5e6ffff27 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=50 | 230 / 230 | 100.0% | 67.0% | 2.2% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_b0b7a0c1932e3636d2b485d6 |
| 1x2 unanimous[statarea+zulubet] avg_p>=0 | 284 / 283 | 99.6% | 61.3% | 0.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_b11e22bfdd27d85fad78ba74 |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=40 | 240 / 240 | 100.0% | 60.0% | 0.4% | start: 2026-06-13; split: 2026-10-02; as_of_exclusive: 2026-10-30 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_b9aa429be62178cc76b1ca8d |
| ou_3.5 unanimous[scoutingstats+statarea] avg_p>=70 | 366 / 366 | 100.0% | 80.6% | 0.5% | start: 2026-06-13; split: 2026-09-27; as_of_exclusive: 2026-10-25 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_bdce95a736d6cc8667f7ac31 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=55 | 157 / 157 | 100.0% | 72.6% | 2.4% | start: 2026-06-13; split: 2026-10-09; as_of_exclusive: 2026-11-06 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_c0b0989eed26d614ffd9cfaf |
| 1x2 unanimous[statarea+zulubet] avg_p>=50 | 271 / 270 | 99.6% | 70.5% | 3.9% | start: 2026-06-13; split: 2026-09-23; as_of_exclusive: 2026-10-21 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_c83d885867c9025a351b9b8c |
| 1x2 unanimous[bzzoiro+zulubet] avg_p>=35 | 264 / 264 | 100.0% | 61.0% | 0.1% | start: 2026-06-13; split: 2026-10-12; as_of_exclusive: 2026-11-09 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_c89a3f96c2ce41dd507f7592 |
| 1x2 unanimous[predictz+scoutingstats] avg_p>=0 | 160 / 160 | 100.0% | 61.9% | 0.2% | start: 2026-06-13; split: 2026-10-15; as_of_exclusive: 2026-11-12 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_c89f0a80e266476539277636 |
| 1x2 single[zulubet] avg_p>=70 | 242 / 241 | 99.6% | 74.0% | 2.7% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_c8cbcf76ea758fd6de596ae1 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=55 | 177 / 177 | 100.0% | 71.8% | 0.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_d17123b85e11155f22e40051 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=35 | 367 / 367 | 100.0% | 60.2% | 3.3% | start: 2026-06-13; split: 2026-10-04; as_of_exclusive: 2026-11-01 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_d5c311b6e2f37443e3501556 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=45 | 372 / 372 | 100.0% | 63.7% | 2.5% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_e25602082a90cb64fb9c5451 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=45 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_e37e7d70a4d046d7a07da0a4 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=40 | 211 / 211 | 100.0% | 65.4% | 1.1% | start: 2026-06-13; split: 2026-10-12; as_of_exclusive: 2026-11-09 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_e5c10af025fc5071367c9b47 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=55 | 239 / 239 | 100.0% | 74.9% | 4.3% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_f2b2a2e84093abe72bbc01c0 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=50 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_f51b5fdaf32bcca063f4b2cc |
| ou_3.5 single[scoutingstats] avg_p>=80 | 133 / 133 | 100.0% | 89.5% | 1.2% | start: 2026-06-13; split: 2026-10-11; as_of_exclusive: 2026-11-08 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_f8aaa9292b8db7b8ceac0414 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=50 | 291 / 291 | 100.0% | 70.8% | 0.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_fb2e721d2bb8a41fe9fa3713 |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=0 | 240 / 240 | 100.0% | 60.0% | 0.4% | start: 2026-06-13; split: 2026-10-02; as_of_exclusive: 2026-10-30 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_fc7adf360790baec2b1ce044 |
| unanimous[betclan+statarea+vitibet] avg_p>=65 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unanimous[betclan+statarea+vitibet] avg_p>=65 |
| unanimous[betclan+vitibet] avg_p>=70 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unanimous[betclan+vitibet] avg_p>=70 |
| unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65 |
| unanimous[bzzoiro+statarea+vitibet] avg_p>=65 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unanimous[bzzoiro+statarea+vitibet] avg_p>=65 |
| unanimous[bzzoiro+vitibet+zulubet] avg_p>=65 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unanimous[bzzoiro+vitibet+zulubet] avg_p>=65 |
| unanimous[bzzoiro+vitibet] avg_p>=70 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unanimous[bzzoiro+vitibet] avg_p>=70 |
| unanimous[statarea+vitibet+zulubet] avg_p>=65 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unanimous[statarea+vitibet+zulubet] avg_p>=65 |
| unanimous[statarea+vitibet] avg_p>=70 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unanimous[statarea+vitibet] avg_p>=70 |
| unanimous[vitibet+zulubet] avg_p>=70 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | unanimous[vitibet+zulubet] avg_p>=70 |

Fixture-level secondary rates below score the fixture behind every settled pick; they are not enhancement-bet returns.
## Secondary Market Realized Rates

Metrics scored against actual outcomes of the settled consensus picks in this window:
- **Over 2.5 Goals**: occurred in 559 / 964 matches (58.0%)
- **Both Teams to Score (BTTS)**: occurred in 525 / 964 matches (54.5%)
- **Selected Team Over 1.5 Goals**: occurred in 588 / 960 matches (61.3%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 231
- **Total Hits**: 161
- **Overall Hit Rate**: 69.7%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=2, settled=2, hit_rate=50.0% (hits=1/recommended=2), priced_n=0, priced_ROI=None (denominator=0), registry_processed=74, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `away_under_15`: recommended=11, settled=11, hit_rate=72.7% (hits=8/recommended=11), priced_n=1, priced_ROI=-1.0 (denominator=1), registry_processed=25, class=priced
- `away_under_25`: recommended=10, settled=10, hit_rate=90.0% (hits=9/recommended=10), priced_n=0, priced_ROI=None (denominator=0), registry_processed=47, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `btts_no`: recommended=6, settled=6, hit_rate=33.3% (hits=2/recommended=6), priced_n=4, priced_ROI=-0.3125 (denominator=4), registry_processed=12, class=priced
- `btts_yes`: recommended=5, settled=5, hit_rate=100.0% (hits=5/recommended=5), priced_n=3, priced_ROI=0.853333 (denominator=3), registry_processed=23, class=priced
- `home_over_05`: recommended=2, settled=2, hit_rate=100.0% (hits=2/recommended=2), priced_n=0, priced_ROI=None (denominator=0), registry_processed=189, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `home_over_15`: recommended=5, settled=5, hit_rate=100.0% (hits=5/recommended=5), priced_n=1, priced_ROI=0.37 (denominator=1), registry_processed=22, class=priced
- `home_under_25`: recommended=5, settled=5, hit_rate=40.0% (hits=2/recommended=5), priced_n=3, priced_ROI=0.087667 (denominator=3), registry_processed=71, class=priced
- `home_under_35`: recommended=3, settled=3, hit_rate=66.7% (hits=2/recommended=3), priced_n=0, priced_ROI=None (denominator=0), registry_processed=78, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `match_over_15`: recommended=19, settled=19, hit_rate=73.7% (hits=14/recommended=19), priced_n=14, priced_ROI=0.45 (denominator=14), registry_processed=82, class=priced
- `match_over_25`: recommended=133, settled=133, hit_rate=67.7% (hits=90/recommended=133), priced_n=124, priced_ROI=0.070565 (denominator=124), registry_processed=782, class=priced
- `match_over_35`: recommended=1, settled=1, hit_rate=100.0% (hits=1/recommended=1), priced_n=0, priced_ROI=None (denominator=0), registry_processed=49, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `match_under_35`: recommended=8, settled=8, hit_rate=25.0% (hits=2/recommended=8), priced_n=7, priced_ROI=-0.625714 (denominator=7), registry_processed=22, class=priced
- `match_under_45`: recommended=21, settled=21, hit_rate=85.7% (hits=18/recommended=21), priced_n=0, priced_ROI=None (denominator=0), registry_processed=36, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **778** | scored: 778 | without promised % (legacy rows): 324

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 190 | 104 | 66 | 63.5% | 62.5% | +1.0% | 0.234607 |
| `match_over_35` | 89 | 83 | 40 | 48.2% | 43.6% | +4.6% | 0.257061 |
| `btts_yes` | 84 | 79 | 50 | 63.3% | 47.1% | +16.2% | 0.250349 |
| `btts_no` | 76 | 72 | 28 | 38.9% | 54.2% | -15.3% | 0.25468 |
| `match_under_25` | 43 | 27 | 11 | 40.7% | 40.8% | -0.0% | 0.242527 |
| `away_under_15` | 33 | 13 | 9 | 69.2% | 65.4% | +3.8% | 0.105564 |
| `match_over_15` | 24 | 11 | 9 | 81.8% | 82.4% | -0.6% | 0.151937 |
| `match_under_35` | 35 | 10 | 4 | 40.0% | 62.4% | -22.4% | 0.275791 |
| `home_over_15` | 30 | 8 | 2 | 25.0% | 46.9% | -21.9% | 0.241596 |
| `match_over_45` | 9 | 8 | 2 | 25.0% | 31.7% | -6.7% | 0.196881 |
| `home_under_15` | 15 | 7 | 6 | 85.7% | 58.5% | +27.2% | 0.269332 |
| `away_under_25` | 17 | 6 | 3 | 50.0% | 71.2% | -21.2% | 0.264693 |
| `home_over_05` | 8 | 6 | 4 | 66.7% | 69.1% | -2.5% | 0.172189 |
| `match_under_45` | 41 | 6 | 4 | 66.7% | 80.4% | -13.8% | 0.248672 |
| `away_over_15` | 7 | 5 | 4 | 80.0% | 59.7% | +20.3% | 0.215626 |
| `away_over_05` | 26 | 4 | 2 | 50.0% | 66.7% | -16.7% | 0.21772 ⚠️low-n |
| `home_under_25` | 34 | 3 | 2 | 66.7% | 72.3% | -5.6% | 0.33706 ⚠️low-n |
| `away_under_35` | 1 | 1 | 1 | 100.0% | 96.1% | +3.9% | 0.001489 ⚠️low-n |
| `home_under_35` | 4 | 1 | 1 | 100.0% | 83.3% | +16.7% | 0.027759 ⚠️low-n |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 440 | 237 | 53.9% | 54.0% | -0.2% | 0.238301 |
| model | 14 | 11 | 78.6% | 55.4% | +23.2% | 0.274502 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.2-0.3 | 9 | 27.6% | 22.2% | -5.4% |
| 0.3-0.4 | 57 | 37.1% | 43.9% | +6.7% |
| 0.4-0.5 | 122 | 45.4% | 56.6% | +11.1% |
| 0.5-0.6 | 140 | 55.2% | 47.1% | -8.1% |
| 0.6-0.7 | 66 | 63.6% | 59.1% | -4.5% |
| 0.7-0.8 | 35 | 74.1% | 71.4% | -2.7% |
| 0.8-0.9 | 24 | 84.1% | 87.5% | +3.4% |
| 0.9-1.0 | 1 | 96.1% | 100.0% | +3.9% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=1019, MAE=1.455721 goals, bias=-0.095505 (realized − promised), promised avg 3.189715 vs realized 3.09421

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 1019 | 35.5% | 34.5% | -1.0% | 0.207595 |
| BTTS-Yes | 1019 | 52.3% | 54.7% | +2.3% | 0.250798 |
| Home Over 1.5 | 1019 | 53.2% | 51.6% | -1.6% | 0.21693 |
| Over 2.5 | 1019 | 61.2% | 58.5% | -2.7% | 0.240479 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 49 | 8.8% | 22.4% | +13.6% |
| 0.1-0.2 | 215 | 15.7% | 16.3% | +0.6% |
| 0.2-0.3 | 599 | 25.8% | 25.7% | -0.1% |
| 0.3-0.4 | 98 | 33.4% | 36.7% | +3.4% |
| 0.4-0.5 | 256 | 42.7% | 48.8% | +6.1% |
| 0.5-0.6 | 1799 | 55.3% | 55.1% | -0.1% |
| 0.6-0.7 | 693 | 64.0% | 60.2% | -3.8% |
| 0.7-0.8 | 243 | 74.7% | 74.1% | -0.6% |
| 0.8-0.9 | 107 | 85.6% | 64.5% | -21.1% |
| 0.9-1.0 | 17 | 91.7% | 70.6% | -21.1% |

## By rule

Counts are frozen PICK ROWS, not bets: SKIPPED_VETO / WATCHLIST_* rows are included and were never cardable. See the full audit’s `## By bucket` for bucket-level counts. These are not acca returns or bank performance.

ROI uses priced rows only; hit rate uses all settled rows. The 30-priced-row cutoff is a reporting sample flag, not proof of profitability or an activation gate. Registry status/certification are separate from this audit window. Historical ml-meta rules are not the live ML ENH acca selector.

### Positive ROI (2 rules)

| Rule | Priced ROI | Priced sample | Hit rate | Evidence | Registry context | Stored rule ID/key |
| --- | ---: | ---: | --- | --- | --- | --- |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35 | +1.0% | 42 priced | 56.8% (25/44 settled) | 30+ priced rows | contract · candidate, activated 2026-11-07, certified valid n=561 | pfc_73b036a8ee8dd5a4dea48134 |
| 1x2 single[scoutingstats] avg_p>=65 | +0.1% | 106 priced | 80.3% (110/137 settled) | 30+ priced rows | contract · benched, activated 2026-10-25, certified valid n=398 | pfc_fdade2e70df4d4bb78a8cd6e |

### Negative ROI (4 rules)

| Rule | Priced ROI | Priced sample | Hit rate | Evidence | Registry context | Stored rule ID/key |
| --- | ---: | ---: | --- | --- | --- | --- |
| ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55 | -2.0% | 79 priced | 61.9% (52/84 settled) | 30+ priced rows | contract · benched, activated 2026-10-23, certified valid n=347 | pfc_27e0f725859bc708f95c58a3 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=35 | -2.8% | 216 priced | 53.2% (126/237 settled) | 30+ priced rows | contract · certified, activated 2026-11-03, certified valid n=1257 | pfc_f56fe4a2759e9b17b9bdb116 |
| 1x2 single[scoutingstats] avg_p>=50 | -5.1% | 196 priced | 60.7% (150/247 settled) | 30+ priced rows | contract · benched, activated 2026-10-20, certified valid n=1235 | pfc_439097cb9bb700e9996c0b07 |
| ml-meta avg_p>=60 | -6.4% | 61 priced | 58.6% (41/70 settled) | 30+ priced rows | legacy rule key | ml-meta avg_p>=60 |

### Break-even (0 rules)

- none

### Insufficient priced evidence (43 rules)

| Rule | Priced ROI | Priced sample | Hit rate | Evidence | Registry context | Stored rule ID/key |
| --- | ---: | ---: | --- | --- | --- | --- |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=0 | +148.0% | 1 priced | 100.0% (1/1 settled) | PROVISIONAL: 1 priced < 30 | contract · benched, activated 2026-11-01, certified valid n=367 | pfc_b4407145af67d2f93e48f0ef |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=45 | +102.0% | 1 priced | 100.0% (1/1 settled) | PROVISIONAL: 1 priced < 30 | contract · benched, activated 2026-11-03, certified valid n=262 | pfc_ed44334de1c8307f22b510ab |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=40 | +100.0% | 1 priced | 100.0% (1/1 settled) | PROVISIONAL: 1 priced < 30 | contract · candidate, activated 2026-11-02, certified valid n=531 | pfc_cd84fb2c3ed889c0ae9eb89e |
| 1x2 single[zulubet] avg_p>=50 | +90.0% | 2 priced | 50.0% (2/4 settled) | PROVISIONAL: 2 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=1241 | pfc_4cf3df8552488297d7ccf526 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=0 | +55.2% | 4 priced | 75.0% (3/4 settled) | PROVISIONAL: 4 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=438 | pfc_0ad08cd1b2e75a2c9051189e |
| unanimous[betclan+statarea+vitibet] avg_p>=65 | +50.0% | 2 priced | 100.0% (2/2 settled) | PROVISIONAL: 2 priced < 30 | legacy rule key | unanimous[betclan+statarea+vitibet] avg_p>=65 |
| 1x2 unanimous[statarea+zulubet] avg_p>=40 | +44.0% | 1 priced | 100.0% (1/1 settled) | PROVISIONAL: 1 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=278 | pfc_5208b9e15194a691590430ad |
| unanimous[vitibet+zulubet] avg_p>=70 | +38.7% | 3 priced | 100.0% (3/3 settled) | PROVISIONAL: 3 priced < 30 | legacy rule key | unanimous[vitibet+zulubet] avg_p>=70 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=50 | +34.6% | 5 priced | 81.8% (9/11 settled) | PROVISIONAL: 5 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=427 | pfc_234f16641d9893e8ec2a01f0 |
| unanimous[betclan+vitibet] avg_p>=70 | +33.7% | 6 priced | 100.0% (7/7 settled) | PROVISIONAL: 6 priced < 30 | legacy rule key | unanimous[betclan+vitibet] avg_p>=70 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=0 | +33.0% | 1 priced | 100.0% (1/1 settled) | PROVISIONAL: 1 priced < 30 | contract · certified, activated 2026-11-03, certified valid n=1258 | pfc_cddf4106a3d45b6e455d8c73 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=40 | +31.6% | 7 priced | 87.5% (7/8 settled) | PROVISIONAL: 7 priced < 30 | contract · certified, activated 2026-11-03, certified valid n=382 | pfc_a7ba6711aeb15b9804a94f06 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=60 | +26.0% | 5 priced | 75.0% (6/8 settled) | PROVISIONAL: 5 priced < 30 | contract · certified, activated 2026-11-12, certified valid n=348 | pfc_54fcf87604b73b87ee6c0a90 |
| unanimous[statarea+vitibet] avg_p>=70 | +25.8% | 13 priced | 100.0% (18/18 settled) | PROVISIONAL: 13 priced < 30 | legacy rule key | unanimous[statarea+vitibet] avg_p>=70 |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=70 | +18.5% | 5 priced | 85.7% (6/7 settled) | PROVISIONAL: 5 priced < 30 | contract · certified, activated 2026-11-09, certified valid n=165 | pfc_4a3e5fbac72b2ebef11632f0 |
| unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65 | +18.0% | 2 priced | 100.0% (2/2 settled) | PROVISIONAL: 2 priced < 30 | legacy rule key | unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=50 | +16.5% | 2 priced | 50.0% (1/2 settled) | PROVISIONAL: 2 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=201 | pfc_0b290b623e2a54ea7df3006c |
| 1x2 unanimous[vitibet+zulubet] avg_p>=45 | +16.3% | 9 priced | 63.6% (7/11 settled) | PROVISIONAL: 9 priced < 30 | contract · benched, activated 2026-10-27, certified valid n=540 | pfc_b011652ec3e473fbc0afbb6a |
| unanimous[bzzoiro+vitibet+zulubet] avg_p>=65 | +15.0% | 1 priced | 100.0% (1/1 settled) | PROVISIONAL: 1 priced < 30 | legacy rule key | unanimous[bzzoiro+vitibet+zulubet] avg_p>=65 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=60 | +14.9% | 8 priced | 66.7% (6/9 settled) | PROVISIONAL: 8 priced < 30 | contract · benched, activated 2026-10-25, certified valid n=203 | pfc_5904b1fc7050646e6321090c |
| ou_2.5 unanimous[scoutingstats+statarea] avg_p>=60 | +11.6% | 4 priced | 75.0% (3/4 settled) | PROVISIONAL: 4 priced < 30 | contract · candidate, activated 2026-11-05, certified valid n=612 | pfc_ee214d4f2f00846fa78f56e3 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 | +11.1% | 7 priced | 57.1% (4/7 settled) | PROVISIONAL: 7 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=426 | pfc_4a1f2bb2278d13c8189148d0 |
| 1x2 single[scoutingstats] avg_p>=60 | +9.7% | 4 priced | 75.0% (3/4 settled) | PROVISIONAL: 4 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=566 | pfc_0f100c9da356ed1c05d9c642 |
| 1x2 single[zulubet] avg_p>=55 | +4.7% | 17 priced | 70.0% (28/40 settled) | PROVISIONAL: 17 priced < 30 | contract · certified, activated 2026-10-20, certified valid n=864 | pfc_1607fec83282d02c5254c2bf |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=40 | +2.7% | 16 priced | 55.6% (10/18 settled) | PROVISIONAL: 16 priced < 30 | contract · benched, activated 2026-11-01, certified valid n=360 | pfc_226efd387e217a9d58a11f79 |
| ou_2.5 unanimous[scoutingstats+statarea] avg_p>=65 | -0.1% | 24 priced | 73.1% (19/26 settled) | PROVISIONAL: 24 priced < 30 | contract · candidate, activated 2026-11-02, certified valid n=321 | pfc_4e8ef1faa47bce63a119fb43 |
| unanimous[statarea+vitibet+zulubet] avg_p>=65 | -2.5% | 2 priced | 50.0% (1/2 settled) | PROVISIONAL: 2 priced < 30 | legacy rule key | unanimous[statarea+vitibet+zulubet] avg_p>=65 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=50 | -3.3% | 2 priced | 66.7% (2/3 settled) | PROVISIONAL: 2 priced < 30 | contract · certified, activated 2026-11-09, certified valid n=200 | pfc_444d408c4ccd3a4bf4fb020c |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=40 | -17.4% | 12 priced | 38.5% (5/13 settled) | PROVISIONAL: 12 priced < 30 | contract · benched, activated 2026-10-21, certified valid n=822 | pfc_d94d447efe0742440e953722 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=40 | -21.8% | 2 priced | 66.7% (4/6 settled) | PROVISIONAL: 2 priced < 30 | contract · benched, activated 2026-11-03, certified valid n=649 | pfc_c7c9572806b564198f651cee |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=55 | -28.5% | 6 priced | 50.0% (3/6 settled) | PROVISIONAL: 6 priced < 30 | contract · certified, activated 2026-11-09, certified valid n=201 | pfc_fbf508b9c62bae8f281bb6e1 |
| unanimous[bzzoiro+statarea+vitibet] avg_p>=65 | -33.5% | 4 priced | 60.0% (3/5 settled) | PROVISIONAL: 4 priced < 30 | legacy rule key | unanimous[bzzoiro+statarea+vitibet] avg_p>=65 |
| 1x2 unanimous[statarea+zulubet] avg_p>=55 | -34.5% | 2 priced | 33.3% (1/3 settled) | PROVISIONAL: 2 priced < 30 | contract · benched, activated 2026-10-21, certified valid n=222 | pfc_5a9d3d3426ee7a4e63461d75 |
| unanimous[bzzoiro+vitibet] avg_p>=70 | -35.2% | 8 priced | 50.0% (4/8 settled) | PROVISIONAL: 8 priced < 30 | legacy rule key | unanimous[bzzoiro+vitibet] avg_p>=70 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=0 | -42.3% | 3 priced | 33.3% (1/3 settled) | PROVISIONAL: 3 priced < 30 | contract · candidate, activated 2026-11-11, certified valid n=326 | pfc_642ac9053223500b638e3451 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=0 | -100.0% | 1 priced | 0.0% (0/1 settled) | PROVISIONAL: 1 priced < 30 | contract · benched, activated 2026-11-03, certified valid n=390 | pfc_0187397f26c1f84f6c3a9883 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=55 | -100.0% | 1 priced | 50.0% (1/2 settled) | PROVISIONAL: 1 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=358 | pfc_2bd498a3472b7bbd71982ece |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 | -100.0% | 1 priced | 0.0% (0/1 settled) | PROVISIONAL: 1 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=645 | pfc_3bfaf30507905754f7faab2a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=35 | -100.0% | 1 priced | 0.0% (0/1 settled) | PROVISIONAL: 1 priced < 30 | contract · benched, activated 2026-11-03, certified valid n=655 | pfc_a3afbb848e0c474b683b450f |
| 1x2 single[zulubet] avg_p>=45 | unavailable | 0 priced | 0.0% (0/1 settled) | PROVISIONAL: 0 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=1488 | pfc_14ee12458803822df3013bcd |
| 1x2 single[zulubet] avg_p>=60 | unavailable | 0 priced | 100.0% (1/1 settled) | PROVISIONAL: 0 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=633 | pfc_35f7e50bf23db96c2d3dd59d |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=50 | unavailable | 0 priced | 0.0% (0/1 settled) | PROVISIONAL: 0 priced < 30 | contract · benched, activated 2026-11-03, certified valid n=230 | pfc_b0b7a0c1932e3636d2b485d6 |
| 1x2 single[zulubet] avg_p>=70 | unavailable | 0 priced | 100.0% (1/1 settled) | PROVISIONAL: 0 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=242 | pfc_c8cbcf76ea758fd6de596ae1 |


## By bucket

- `CAUTION`: settled=172, wins=120, hit_rate=0.697674 (settled n=172), ROI=0.068637 (priced n=172)
- `CERTIFIED_CLEAN`: settled=62, wins=40, hit_rate=0.645161 (settled n=62), ROI=-0.052385 (priced n=62)
- `SKIPPED_VETO`: settled=654, wins=397, hit_rate=0.607034 (settled n=654), ROI=-0.016957 (priced n=608)
- `WATCHLIST_NO_ODDS`: settled=37, wins=25, hit_rate=0.675676 (settled n=37), ROI=None (priced n=0)
- `WATCHLIST_SUSPECT_PRICE`: settled=103, wins=69, hit_rate=0.669903 (settled n=103), ROI=0.1825 (priced n=4)
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=32, wins=20, hit_rate=0.625 (settled n=32), ROI=-0.07875 (priced n=32)
- `WATCHLIST_UNKNOWN_CTX`: settled=18, wins=12, hit_rate=0.666667 (settled n=18), ROI=-0.202272 (priced n=18)

## By odds source

- `UNKNOWN`: settled=182, wins=124, hit_rate=0.681319 (settled n=182), ROI=None (priced n=0)
- `betexplorer_odds`: settled=95, wins=76, hit_rate=0.8 (settled n=95), ROI=0.055158 (priced n=95)
- `boggio`: settled=2, wins=2, hit_rate=1.0 (settled n=2), ROI=0.41 (priced n=2)
- `oddspapi_odds`: settled=8, wins=3, hit_rate=0.375 (settled n=8), ROI=-0.331875 (priced n=8)
- `pinnapi_odds`: settled=563, wins=334, hit_rate=0.59325 (settled n=563), ROI=-0.01449 (priced n=563)
- `scoutingstats_odds`: settled=72, wins=46, hit_rate=0.638889 (settled n=72), ROI=-0.048611 (priced n=72)
- `theoddsapi`: settled=146, wins=93, hit_rate=0.636986 (settled n=146), ROI=0.019795 (priced n=146)
- `zulubet`: settled=10, wins=5, hit_rate=0.5 (settled n=10), ROI=-0.182 (priced n=10)

## By odds match method

- `alias_fuzzy`: settled=137, wins=93, hit_rate=0.678832 (settled n=137), ROI=-0.054 (priced n=5)
- `alias_time`: settled=4, wins=3, hit_rate=0.75 (settled n=4), ROI=0.371175 (priced n=4)
- `exact`: settled=882, wins=551, hit_rate=0.624717 (settled n=882), ROI=-0.007764 (priced n=882)
- `fallback`: settled=5, wins=2, hit_rate=0.4 (settled n=5), ROI=-0.31 (priced n=5)
- `none`: settled=50, wins=34, hit_rate=0.68 (settled n=50), ROI=None (priced n=0)

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| APPROVED_DONOR_PRICE (`APPROVED_DONOR_PRICE`) | 2 | 2 | 1.0 | 2 | 0.41 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 812 | 506 | 0.623153 | 812 | -0.003304 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 72 | 46 | 0.638889 | 72 | -0.048611 |
| Source fallback (`SOURCE_FALLBACK`) | 5 | 2 | 0.4 | 5 | -0.31 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 137 | 93 | 0.678832 | 5 | -0.054 |
| No usable price (`UNMATCHED`) | 50 | 34 | 0.68 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 654 | 397 | 0.607034 | 608 | -0.016957 |
| **trusted evidence only** | 565 | 337 | 0.59646 | 565 | -0.013911 |
| **soft evidence only** | 89 | 60 | 0.674157 | 43 | -0.056977 |
| evidence: NAMED_BOOKMAKER_PRICE | 565 | 337 | 0.59646 | 565 | -0.013911 |
| evidence: SCOUTINGSTATS_SOLE | 40 | 26 | 0.65 | 40 | -0.0245 |
| evidence: SOURCE_FALLBACK | 2 | 1 | 0.5 | 2 | -0.235 |
| evidence: SUSPECT_ALIAS_FUZZY | 34 | 24 | 0.705882 | 1 | -1.0 |
| evidence: UNMATCHED | 13 | 9 | 0.692308 | 0 | None |
| odds band: <1.50 | 180 | 146 | 0.811111 | 180 | 0.035344 |
| odds band: 1.50-2.00 | 272 | 149 | 0.547794 | 272 | -0.060889 |
| odds band: 2.00-3.00 | 153 | 68 | 0.444444 | 153 | -0.007255 |
| odds band: >=3.00 | 3 | 1 | 0.333333 | 3 | 0.333333 |
| odds band: unpriced | 46 | 33 | 0.717391 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.2 |
| veto reason: context VETO in ['competition_type'] | 37 | 29 | 0.783784 | 26 | -0.019862 |
| veto reason: context VETO in ['league', 'niche'] | 36 | 24 | 0.666667 | 27 | -0.098704 |
| veto reason: context VETO in ['league', 'odds_band', 'competition_type'] | 1 | 1 | 1.0 | 1 | 0.14 |
| veto reason: context VETO in ['league', 'odds_band', 'niche'] | 36 | 16 | 0.444444 | 36 | -0.120978 |
| veto reason: context VETO in ['league', 'odds_band'] | 92 | 48 | 0.521739 | 92 | -0.037538 |
| veto reason: context VETO in ['league', 'team_a', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.6579 |
| veto reason: context VETO in ['league', 'team_h', 'competition_type'] | 1 | 1 | 1.0 | 1 | 0.5 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 5 | 2 | 0.4 | 4 | -0.2325 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 1 | 1 | 1.0 | 1 | 0.6452 |
| veto reason: context VETO in ['league'] | 79 | 49 | 0.620253 | 63 | -0.141605 |
| veto reason: context VETO in ['niche'] | 39 | 31 | 0.794872 | 34 | 0.053424 |
| veto reason: context VETO in ['odds_band', 'competition_type'] | 1 | 1 | 1.0 | 1 | 0.5291 |
| veto reason: context VETO in ['odds_band', 'niche'] | 15 | 5 | 0.333333 | 15 | -0.2964 |
| veto reason: context VETO in ['odds_band'] | 242 | 133 | 0.549587 | 242 | 0.012272 |
| veto reason: context VETO in ['team_a', 'competition_type'] | 3 | 3 | 1.0 | 3 | 0.485267 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 1 | 1 | 1.0 | 1 | 1.1 |
| veto reason: context VETO in ['team_a'] | 9 | 9 | 1.0 | 9 | 0.359411 |
| veto reason: context VETO in ['team_h', 'competition_type'] | 11 | 9 | 0.818182 | 10 | 0.02542 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 2 | 0.42 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a', 'competition_type'] | 1 | 1 | 1.0 | 1 | 0.23 |
| veto reason: context VETO in ['team_h', 'team_a'] | 2 | 1 | 0.5 | 2 | -0.14285 |
| veto reason: context VETO in ['team_h'] | 9 | 6 | 0.666667 | 7 | 0.31 |
| veto reason: short-odds away favourite 1.04 | 1 | 1 | 1.0 | 1 | 0.041 |
| veto reason: short-odds away favourite 1.05 | 1 | 1 | 1.0 | 1 | 0.05 |
| veto reason: short-odds away favourite 1.08 | 2 | 2 | 1.0 | 2 | 0.08 |
| veto reason: short-odds away favourite 1.09 | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: short-odds away favourite 1.10 | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: short-odds away favourite 1.16 | 1 | 1 | 1.0 | 1 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 1 | 1 | 1.0 | 1 | 0.1845 |
| veto reason: short-odds away favourite 1.20 | 1 | 1 | 1.0 | 1 | 0.2 |
| veto reason: short-odds away favourite 1.22 | 3 | 3 | 1.0 | 3 | 0.22 |
| veto reason: short-odds away favourite 1.23 | 1 | 1 | 1.0 | 1 | 0.2342 |
| veto reason: short-odds away favourite 1.24 | 2 | 0 | 0.0 | 2 | -1.0 |
| veto reason: short-odds away favourite 1.25 | 4 | 4 | 1.0 | 4 | 0.25 |
| veto reason: short-odds away favourite 1.26 | 1 | 1 | 1.0 | 1 | 0.2591 |
| veto reason: short-odds away favourite 1.27 | 3 | 2 | 0.666667 | 3 | -0.153333 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.277 |
| veto reason: short-odds away favourite 1.29 | 2 | 2 | 1.0 | 2 | 0.29205 |
| contrast CAUTION: APPROVED_DONOR_PRICE | 2 | 2 | 1.0 | 2 | 0.41 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 169 | 117 | 0.692308 | 169 | 0.05956 |
| contrast CAUTION: SOURCE_FALLBACK | 1 | 1 | 1.0 | 1 | 0.92 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 863 | 541 | 0.626883 | 814 | -0.002289 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 137 | 93 | 0.678832 | 5 | -0.054 | 137 | 1.57242 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 72 | 46 | 0.638889 | 72 | -0.048611 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 5 | 2 | 0.4 | 5 | -0.31 | 0 | None |
| stale_quote (`stale_quote`) | 1 | 1 | 1.0 | 0 | None | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-11-12: Águila vs Municipal Limeño (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.6135 -> 🟢 WON (Expected prob: 62.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 62.9% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 51.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 70.2% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 77.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-12: Senegal vs Sudan (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.1 -> 🟢 WON (Expected prob: 81.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.0% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 77.2% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 5 goals)

### 2026-11-12: Guinea vs Eritrea (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.1764 -> 🟢 WON (Expected prob: 77.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 77.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-12: Czech Republic vs Spain (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.22 -> 🟢 WON (Expected prob: 76.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 62.0% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 85.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 75.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected n/a (Actual: 2 goals)

### 2026-11-12: San Marino vs Belarus (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.17 -> 🟢 WON (Expected prob: 76.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 62.0% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 45.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 85.1% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 75.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected n/a (Actual: 2 goals)

### 2026-11-12: England vs Croatia (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.26 -> 🟢 WON (Expected prob: 71.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 68.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 77.2% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 3 goals)

### 2026-11-12: Barcelona W vs Arsenal W (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 72.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 55.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 55.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 71.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-12: Navalcarnero vs Real Betis (Actual Score: **2-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.1195 -> 🟢 WON (Expected prob: 68.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 54.0% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 72.6% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 53.2% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-12: Italy vs France (Actual Score: **3-1**)
- **1X2 Pick**: Selected `AWAY` @ 2.0 -> 🔴 LOST (Expected prob: 49.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 54.0% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 72.6% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 53.2% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-12: Albania vs Finland (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 2.06 -> 🟢 WON (Expected prob: 49.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 55.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 55.2% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.6% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 71.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-12: Türkiye vs Belgium (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.8475 -> 🟢 WON (Expected prob: 47.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 54.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.2% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 72.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 53.2% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-12: Armenia vs Cyprus (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 2.58 -> 🔴 LOST (Expected prob: 39.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 55.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 55.2% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 71.0% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-12: Germany U19 vs Sweden U19 (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 74.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.9% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 51.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 63.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-12: Portugal U19 vs Lithuania U19 (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 71.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.9% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 51.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 63.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 9 |
- 2026-10-23 `POSTPONED` `CAUTION` — Gateshead vs Tamworth (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-10-23 `POSTPONED` `SKIPPED_VETO` — Holywell vs Penybont (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-10-24 `POSTPONED` `CAUTION` — Glentoran vs Ballymena United (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-10-24 `POSTPONED` `CAUTION` — Slovan Liberec vs Baník Ostrava (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-10-28 `POSTPONED` `SKIPPED_VETO` — Navalcarnero vs Real Betis (verified_disposition); excluded from win/loss/ROI
- 2026-10-28 `POSTPONED` `WATCHLIST_SUSPECT_PRICE` — Salamanca CF UDS vs Celta de Vigo (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-11-05 `POSTPONED` `SKIPPED_VETO` — Al Kholood vs Al Khaleej (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-11-07 `POSTPONED` `SKIPPED_VETO` — Granada vs Tenerife (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-11-08 `POSTPONED` `SKIPPED_VETO` — Estoril vs Marítimo (source_status:scoutingstats); excluded from win/loss/ROI

## Rescheduled Fixture Examples

- 2026-10-18 `SKIPPED_VETO` `unanimous[bzzoiro+vitibet] avg_p>=70` — Hartford Athletic vs Brooklyn -> HOME @ 1.44 (rescheduled → 2026-10-17; actual Hartford Athletic 2-3 Brooklyn [away])
- 2026-10-21 `WATCHLIST_UNCORROBORATED_PRICE` `1x2 single[scoutingstats] avg_p>=50` — Cerro Porteño vs Sportivo Ameliano -> HOME @ 1.65 (rescheduled → 2026-10-18; actual Cerro Porteno 2-2 Sportivo Ameliano [draw])
- 2026-10-25 `WATCHLIST_SUSPECT_PRICE` `1x2 single[scoutingstats] avg_p>=65` — Paris Saint Germain vs Olympique Lyonnais -> HOME @ None (rescheduled → 2026-10-26; actual Paris Saint Germain 2-0 Olympique Lyonnais [home])

## Pending / Unmatched Result Examples

- 2026-10-18 `SKIPPED_VETO` `unanimous[betclan+vitibet] avg_p>=70` — Wolfurt vs Schwaz -> AWAY @ None (pending_or_unmatched_result); keys=['wolfurt']/['schwaz']
- 2026-10-18 `SKIPPED_VETO` `unanimous[betclan+vitibet] avg_p>=70` — Rheindorf Altach II vs Imst -> AWAY @ None (pending_or_unmatched_result); keys=['rheindorf']/['imst']
- 2026-10-21 `CAUTION` `1x2 single[scoutingstats] avg_p>=50` — Sporting JAX vs Louisville City -> AWAY @ 1.37 (pending_or_unmatched_result); keys=['jax']/['louisvill']
- 2026-10-21 `WATCHLIST_UNCORROBORATED_PRICE` `1x2 single[scoutingstats] avg_p>=50` — Olimpia vs 2 de Mayo -> HOME @ 1.44 (pending_or_unmatched_result); keys=['olimpia']/['demayo']
- 2026-10-21 `WATCHLIST_UNKNOWN_CTX` `1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=50` — Sporting CP vs LASK Linz -> HOME @ 1.2101 (pending_or_unmatched_result); keys=['cp', 'lisbon']/['lasklinz']
- 2026-10-22 `SKIPPED_VETO` `1x2 unanimous[vitibet+zulubet] avg_p>=50` — Sporting JAX vs Louisville City FC -> AWAY @ 1.27 (pending_or_unmatched_result); keys=['jax']/['louisvill']
- 2026-10-23 `SKIPPED_VETO` `1x2 single[scoutingstats] avg_p>=50` — Operário PR vs Athletic Club -> HOME @ None (pending_or_unmatched_result); keys=['operariop']/[]
- 2026-10-24 `SKIPPED_VETO` `1x2 single[scoutingstats] avg_p>=50` — Tampa Bay Rowdies vs Sporting JAX -> HOME @ None (pending_or_unmatched_result); keys=['tampabayr']/['jax']
- 2026-10-25 `CAUTION` `ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55` — Sporting CP vs Académico Viseu FC -> OVER @ 1.3953 (pending_or_unmatched_result); keys=['cp', 'lisbon']/['academico']
- 2026-10-25 `WATCHLIST_UNCORROBORATED_PRICE` `1x2 single[scoutingstats] avg_p>=65` — Sporting CP vs Academico Viseu -> HOME @ 1.22 (pending_or_unmatched_result); keys=['cp', 'lisbon']/['academico']
- 2026-10-28 `SKIPPED_VETO` `1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35` — Liverpool FC vs Chelsea -> HOME @ 2.3 (pending_or_unmatched_result); keys=['liverpool']/['chelsea']
- 2026-11-07 `SKIPPED_VETO` `1x2 unanimous[scoutingstats+statarea] avg_p>=35` — Sporting CP vs Moreirense -> HOME @ 1.1536 (pending_or_unmatched_result); keys=['cp', 'lisbon']/['moreirens']

## Ambiguous result examples

- 2026-10-21 `WATCHLIST_NO_ODDS` `1x2 single[zulubet] avg_p>=65` — Guadalajara W vs Necaxa W (ambiguous_alias_result)
