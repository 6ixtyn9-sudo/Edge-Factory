# Edge Factory — Recent picks audit (2026-09-26 to 2026-10-25)

## Overall

- archived pick rows: 1051
- archived pick dates: 30
- immutable morning-baseline rows: 894
- late-slate additions (regular-ledger rows not in the morning baseline): 159, of which on days whose regular ledger was rewritten: 131
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 26
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 929
- eligible prior picks: 953
- pending/unmatched result picks: 17
- rescheduled result picks (settled ±3d): 7
- voided postponed/cancelled/abandoned events: 6
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 19
- ambiguous result picks: 1
- wins: 614
- hit rate: +66.1% (wins/settled: 614/929)
- priced picks: 756
- ROI: +1.5% (P&L / 756 priced picks)

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-10-25
- same-day rows excluded: 98

## Rule performance — since activation vs last 30 days

Primary view: recorded post-activation PICK ROWS, including vetoed/watchlist rows; not placed bets or acca returns. No retrospective rule replay. Missing activation dates remain unavailable. Missing archive days mean partial history, not zero activity. Missing/unreadable files are counted as archive gaps. Empty recorded cards count as available days. Current registry status is not historical status on each pick date.

Last 30 days: 2026-09-26 to 2026-10-25; same-day inclusion: False (local cutoff 2026-10-25). The 30-priced-row provisional flag is reporting only, not an activation gate. Priced ROI can include fallback/quarantined odds; provenance is shown separately. Historical ml-meta is not the live ML ENH selector.

| Rule | Activation / current status | Since activation | Last 30 days | Archive days: since / recent | Stored key |
| --- | --- | --- | --- | --- | --- |
| ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55 | 2026-10-23 / benched | ROI +7.1%; hit 65.2% (30/46); 45 priced; coverage 97.8% | ROI +7.1%; hit 65.2% (30/46); 45 priced; coverage 97.8% | 2/2 / 29/29 | pfc_27e0f725859bc708f95c58a3 |
| 1x2 single[scoutingstats] avg_p>=50 | 2026-10-20 / benched | ROI -5.3%; hit 60.6% (149/246); 195 priced; coverage 79.3% | ROI -5.3%; hit 60.6% (149/246); 195 priced; coverage 79.3% | 5/5 / 29/29 | pfc_439097cb9bb700e9996c0b07 |
| 1x2 single[zulubet] avg_p>=50 | 2026-10-20 / benched | ROI +90.0%; hit 50.0% (2/4); 2 priced; coverage 50.0%; provisional | ROI +90.0%; hit 50.0% (2/4); 2 priced; coverage 50.0%; provisional | 5/5 / 29/29 | pfc_4cf3df8552488297d7ccf526 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=0 | 2026-10-20 / benched | ROI +55.2%; hit 75.0% (3/4); 4 priced; coverage 100.0%; provisional | ROI +55.2%; hit 75.0% (3/4); 4 priced; coverage 100.0%; provisional | 5/5 / 29/29 | pfc_0ad08cd1b2e75a2c9051189e |
| 1x2 unanimous[statarea+zulubet] avg_p>=40 | 2026-10-20 / benched | ROI +44.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | ROI +44.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | 5/5 / 29/29 | pfc_5208b9e15194a691590430ad |
| 1x2 unanimous[vitibet+zulubet] avg_p>=50 | 2026-10-20 / benched | ROI +34.6%; hit 81.8% (9/11); 5 priced; coverage 45.5%; provisional | ROI +34.6%; hit 81.8% (9/11); 5 priced; coverage 45.5%; provisional | 5/5 / 29/29 | pfc_234f16641d9893e8ec2a01f0 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=50 | 2026-10-20 / certified | ROI +16.5%; hit 50.0% (1/2); 2 priced; coverage 100.0%; provisional | ROI +16.5%; hit 50.0% (1/2); 2 priced; coverage 100.0%; provisional | 5/5 / 29/29 | pfc_0b290b623e2a54ea7df3006c |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 | 2026-10-20 / benched | ROI +11.1%; hit 57.1% (4/7); 7 priced; coverage 100.0%; provisional | ROI +11.1%; hit 57.1% (4/7); 7 priced; coverage 100.0%; provisional | 5/5 / 29/29 | pfc_4a1f2bb2278d13c8189148d0 |
| 1x2 single[scoutingstats] avg_p>=60 | 2026-10-20 / benched | ROI +9.7%; hit 75.0% (3/4); 4 priced; coverage 100.0%; provisional | ROI +9.7%; hit 75.0% (3/4); 4 priced; coverage 100.0%; provisional | 5/5 / 29/29 | pfc_0f100c9da356ed1c05d9c642 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=40 | 2026-10-21 / benched | ROI -17.4%; hit 38.5% (5/13); 12 priced; coverage 92.3%; provisional | ROI -17.4%; hit 38.5% (5/13); 12 priced; coverage 92.3%; provisional | 4/4 / 29/29 | pfc_d94d447efe0742440e953722 |
| 1x2 single[zulubet] avg_p>=55 | 2026-10-20 / certified | ROI -26.7%; hit 50.0% (4/8); 4 priced; coverage 50.0%; provisional | ROI -26.7%; hit 50.0% (4/8); 4 priced; coverage 50.0%; provisional | 5/5 / 29/29 | pfc_1607fec83282d02c5254c2bf |
| 1x2 unanimous[statarea+zulubet] avg_p>=55 | 2026-10-21 / benched | ROI -34.5%; hit 33.3% (1/3); 2 priced; coverage 66.7%; provisional | ROI -34.5%; hit 33.3% (1/3); 2 priced; coverage 66.7%; provisional | 4/4 / 29/29 | pfc_5a9d3d3426ee7a4e63461d75 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35 | 2026-10-23 / candidate | ROI -36.1%; hit 33.3% (3/9); 9 priced; coverage 100.0%; provisional | ROI -36.1%; hit 33.3% (3/9); 9 priced; coverage 100.0%; provisional | 2/2 / 29/29 | pfc_73b036a8ee8dd5a4dea48134 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=55 | 2026-10-20 / benched | ROI -100.0%; hit 50.0% (1/2); 1 priced; coverage 50.0%; provisional | ROI -100.0%; hit 50.0% (1/2); 1 priced; coverage 50.0%; provisional | 5/5 / 29/29 | pfc_2bd498a3472b7bbd71982ece |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 | 2026-10-20 / benched | ROI -100.0%; hit 0.0% (0/1); 1 priced; coverage 100.0%; provisional | ROI -100.0%; hit 0.0% (0/1); 1 priced; coverage 100.0%; provisional | 5/5 / 29/29 | pfc_3bfaf30507905754f7faab2a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=45 | 2026-10-24 / candidate | ROI -100.0%; hit 0.0% (0/1); 1 priced; coverage 100.0%; provisional | ROI +76.0%; hit 66.7% (2/3); 3 priced; coverage 100.0%; provisional | 1/1 / 29/29 | pfc_b011652ec3e473fbc0afbb6a |
| 2way-unanimous avg_p>=60 | unavailable / unavailable | unavailable | ROI -12.0%; hit 63.3% (81/128); 93 priced; coverage 72.7% | unavailable / 29/29 | 2way-unanimous avg_p>=60 |
| 2way-unanimous avg_p>=70 | unavailable / unavailable | unavailable | ROI +3.8%; hit 79.2% (19/24); 17 priced; coverage 70.8%; provisional | unavailable / 29/29 | 2way-unanimous avg_p>=70 |
| ml-meta avg_p>=55 | unavailable / unavailable | unavailable | ROI +17.8%; hit 73.0% (119/163); 136 priced; coverage 83.4% | unavailable / 29/29 | ml-meta avg_p>=55 |
| ml-meta avg_p>=60 | unavailable / unavailable | unavailable | ROI -4.2%; hit 60.7% (91/150); 134 priced; coverage 89.3% | unavailable / 29/29 | ml-meta avg_p>=60 |
| ml-meta avg_p>=65 | unavailable / unavailable | unavailable | ROI +3.3%; hit 85.7% (18/21); 15 priced; coverage 71.4%; provisional | unavailable / 29/29 | ml-meta avg_p>=65 |
| ml-meta avg_p>=80 | unavailable / unavailable | unavailable | ROI +7.5%; hit 100.0% (7/7); 6 priced; coverage 85.7%; provisional | unavailable / 29/29 | ml-meta avg_p>=80 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=35 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_054448b499623dd39b072b38 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=45 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_0aed63f3d04b46330958121d |
| 1x2 single[zulubet] avg_p>=45 | 2026-10-20 / benched | ROI unavailable; hit 0.0% (0/1); 0 priced; coverage 0.0%; provisional | ROI unavailable; hit 0.0% (0/1); 0 priced; coverage 0.0%; provisional | 5/5 / 29/29 | pfc_14ee12458803822df3013bcd |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=55 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_1ba3ab3c75e6f3a9680ae43c |
| 1x2 single[zulubet] avg_p>=40 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_1e9cfc6500aaac77afa1eaf9 |
| 1x2 unanimous[statarea+zulubet] avg_p>=35 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_3072388544a60552346bd162 |
| 1x2 single[zulubet] avg_p>=60 | 2026-10-20 / benched | ROI unavailable; hit 100.0% (1/1); 0 priced; coverage 0.0%; provisional | ROI unavailable; hit 100.0% (1/1); 0 priced; coverage 0.0%; provisional | 5/5 / 29/29 | pfc_35f7e50bf23db96c2d3dd59d |
| 1x2 single[zulubet] avg_p>=0 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_3dc0fa6511953bf09bc4c845 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=50 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_3fbabd0ade3f89853e43fb10 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=60 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_40b163633fc01fd0ff7d0ef1 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=50 | 2026-10-21 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 4/4 / 29/29 | pfc_444d408c4ccd3a4bf4fb020c |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=55 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_4e2583010bf805466e33c2d0 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=0 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_4f2df06575151e798727a6b0 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=55 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_527524a94e98cff9740d499c |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=60 | 2026-10-25 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 0/0 / 29/29 | pfc_5904b1fc7050646e6321090c |
| 1x2 single[zulubet] avg_p>=65 | 2026-10-20 / benched | ROI unavailable; hit 100.0% (1/1); 0 priced; coverage 0.0%; provisional | ROI unavailable; hit 100.0% (1/1); 0 priced; coverage 0.0%; provisional | 5/5 / 29/29 | pfc_5954379f3a12700edcfd8387 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=50 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_5f861bad9f49ebf6d6fe2c16 |
| 1x2 single[zulubet] avg_p>=35 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_61cb1dd2a3157c4231070cdb |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=40 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_6cd236448d9fd967f8dcb591 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=0 | 2026-10-24 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 1/1 / 29/29 | pfc_754f7247e83f901ae415b35f |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=35 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_7d20e19c2c26174fa21e9e86 |
| 1x2 unanimous[statarea+zulubet] avg_p>=45 | 2026-10-21 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 4/4 / 29/29 | pfc_7eb24434123da46374442290 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=0 | 2026-10-23 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 2/2 / 29/29 | pfc_92ab281aa7c2173e7502ba49 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=45 | 2026-10-24 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 1/1 / 29/29 | pfc_9ae5a305a703bca83fd321b3 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=45 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_a460a0e9dcb1f980cde169c0 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=35 | 2026-10-24 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 1/1 / 29/29 | pfc_a8e99ebc0016f0d0bb95aa70 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=60 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_a90a9b922d2318a2446434ce |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=50 | 2026-10-24 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 1/1 / 29/29 | pfc_b0b7a0c1932e3636d2b485d6 |
| 1x2 unanimous[statarea+zulubet] avg_p>=0 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_b11e22bfdd27d85fad78ba74 |
| ou_3.5 unanimous[scoutingstats+statarea] avg_p>=70 | 2026-10-25 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 0/0 / 29/29 | pfc_bdce95a736d6cc8667f7ac31 |
| 1x2 unanimous[statarea+zulubet] avg_p>=50 | 2026-10-21 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 4/4 / 29/29 | pfc_c83d885867c9025a351b9b8c |
| 1x2 single[zulubet] avg_p>=70 | 2026-10-20 / benched | ROI unavailable; hit 100.0% (1/1); 0 priced; coverage 0.0%; provisional | ROI unavailable; hit 100.0% (1/1); 0 priced; coverage 0.0%; provisional | 5/5 / 29/29 | pfc_c8cbcf76ea758fd6de596ae1 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=40 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_cd84fb2c3ed889c0ae9eb89e |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=0 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_cddf4106a3d45b6e455d8c73 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=55 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_d17123b85e11155f22e40051 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=45 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_e25602082a90cb64fb9c5451 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=45 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_e37e7d70a4d046d7a07da0a4 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=40 | 2026-10-25 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 0/0 / 29/29 | pfc_e5c10af025fc5071367c9b47 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=55 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_f2b2a2e84093abe72bbc01c0 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=50 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_f51b5fdaf32bcca063f4b2cc |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=35 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_f56fe4a2759e9b17b9bdb116 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=50 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_fb2e721d2bb8a41fe9fa3713 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=55 | 2026-10-21 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 4/4 / 29/29 | pfc_fbf508b9c62bae8f281bb6e1 |
| 1x2 single[scoutingstats] avg_p>=65 | 2026-10-25 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 0/0 / 29/29 | pfc_fdade2e70df4d4bb78a8cd6e |
| unanimous[betclan+statarea+vitibet] avg_p>=65 | unavailable / unavailable | unavailable | ROI +50.0%; hit 100.0% (2/2); 2 priced; coverage 100.0%; provisional | unavailable / 29/29 | unanimous[betclan+statarea+vitibet] avg_p>=65 |
| unanimous[betclan+vitibet] avg_p>=70 | unavailable / unavailable | unavailable | ROI +34.1%; hit 94.1% (16/17); 13 priced; coverage 76.5%; provisional | unavailable / 29/29 | unanimous[betclan+vitibet] avg_p>=70 |
| unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65 | unavailable / unavailable | unavailable | ROI +18.0%; hit 100.0% (2/2); 2 priced; coverage 100.0%; provisional | unavailable / 29/29 | unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65 |
| unanimous[bzzoiro+statarea+vitibet] avg_p>=65 | unavailable / unavailable | unavailable | ROI -33.5%; hit 60.0% (3/5); 4 priced; coverage 80.0%; provisional | unavailable / 29/29 | unanimous[bzzoiro+statarea+vitibet] avg_p>=65 |
| unanimous[bzzoiro+vitibet+zulubet] avg_p>=65 | unavailable / unavailable | unavailable | ROI +15.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | unavailable / 29/29 | unanimous[bzzoiro+vitibet+zulubet] avg_p>=65 |
| unanimous[bzzoiro+vitibet] avg_p>=70 | unavailable / unavailable | unavailable | ROI -3.6%; hit 69.2% (9/13); 13 priced; coverage 100.0%; provisional | unavailable / 29/29 | unanimous[bzzoiro+vitibet] avg_p>=70 |
| unanimous[statarea+vitibet+zulubet] avg_p>=65 | unavailable / unavailable | unavailable | ROI -2.5%; hit 50.0% (1/2); 2 priced; coverage 100.0%; provisional | unavailable / 29/29 | unanimous[statarea+vitibet+zulubet] avg_p>=65 |
| unanimous[statarea+vitibet] avg_p>=70 | unavailable / unavailable | unavailable | ROI +17.2%; hit 90.5% (19/21); 16 priced; coverage 76.2%; provisional | unavailable / 29/29 | unanimous[statarea+vitibet] avg_p>=70 |
| unanimous[vitibet+zulubet] avg_p>=70 | unavailable / unavailable | unavailable | ROI +39.2%; hit 100.0% (5/5); 5 priced; coverage 100.0%; provisional | unavailable / 29/29 | unanimous[vitibet+zulubet] avg_p>=70 |

### Price provenance — operational windows

Only windows with settled rows are listed below: evidence class, settled/priced rows and quarantine reasons. A priced row alone is not proof of an executable quote.

| Rule | Window | Evidence class: settled / priced | Quarantine reason: settled / priced | Stored key |
| --- | --- | --- | --- | --- |
| ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55 | Since activation | NAMED_BOOKMAKER_PRICE: 43/43; SCOUTINGSTATS_SOLE: 2/2; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 43/43; alias_fuzzy: 1/0; scoutingstats_sole_source: 2/2 | pfc_27e0f725859bc708f95c58a3 |
| ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55 | Last 30 days | NAMED_BOOKMAKER_PRICE: 43/43; SCOUTINGSTATS_SOLE: 2/2; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 43/43; alias_fuzzy: 1/0; scoutingstats_sole_source: 2/2 | pfc_27e0f725859bc708f95c58a3 |
| 1x2 single[scoutingstats] avg_p>=50 | Since activation | NAMED_BOOKMAKER_PRICE: 167/167; SCOUTINGSTATS_SOLE: 28/28; SUSPECT_ALIAS_FUZZY: 51/0 | NONE: 167/167; alias_fuzzy: 51/0; scoutingstats_sole_source: 28/28 | pfc_439097cb9bb700e9996c0b07 |
| 1x2 single[scoutingstats] avg_p>=50 | Last 30 days | NAMED_BOOKMAKER_PRICE: 167/167; SCOUTINGSTATS_SOLE: 28/28; SUSPECT_ALIAS_FUZZY: 51/0 | NONE: 167/167; alias_fuzzy: 51/0; scoutingstats_sole_source: 28/28 | pfc_439097cb9bb700e9996c0b07 |
| 1x2 single[zulubet] avg_p>=50 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1; SCOUTINGSTATS_SOLE: 1/1; UNMATCHED: 2/0 | NONE: 3/1; scoutingstats_sole_source: 1/1 | pfc_4cf3df8552488297d7ccf526 |
| 1x2 single[zulubet] avg_p>=50 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1; SCOUTINGSTATS_SOLE: 1/1; UNMATCHED: 2/0 | NONE: 3/1; scoutingstats_sole_source: 1/1 | pfc_4cf3df8552488297d7ccf526 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=0 | Since activation | NAMED_BOOKMAKER_PRICE: 4/4 | NONE: 4/4 | pfc_0ad08cd1b2e75a2c9051189e |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=0 | Last 30 days | NAMED_BOOKMAKER_PRICE: 4/4 | NONE: 4/4 | pfc_0ad08cd1b2e75a2c9051189e |
| 1x2 unanimous[statarea+zulubet] avg_p>=40 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_5208b9e15194a691590430ad |
| 1x2 unanimous[statarea+zulubet] avg_p>=40 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_5208b9e15194a691590430ad |
| 1x2 unanimous[vitibet+zulubet] avg_p>=50 | Since activation | NAMED_BOOKMAKER_PRICE: 5/5; SUSPECT_ALIAS_FUZZY: 1/0; UNMATCHED: 5/0 | NONE: 10/5; alias_fuzzy: 1/0 | pfc_234f16641d9893e8ec2a01f0 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=50 | Last 30 days | NAMED_BOOKMAKER_PRICE: 5/5; SUSPECT_ALIAS_FUZZY: 1/0; UNMATCHED: 5/0 | NONE: 10/5; alias_fuzzy: 1/0 | pfc_234f16641d9893e8ec2a01f0 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=50 | Since activation | NAMED_BOOKMAKER_PRICE: 2/2 | NONE: 2/2 | pfc_0b290b623e2a54ea7df3006c |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=50 | Last 30 days | NAMED_BOOKMAKER_PRICE: 2/2 | NONE: 2/2 | pfc_0b290b623e2a54ea7df3006c |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 | Since activation | NAMED_BOOKMAKER_PRICE: 7/7 | NONE: 7/7 | pfc_4a1f2bb2278d13c8189148d0 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 | Last 30 days | NAMED_BOOKMAKER_PRICE: 7/7 | NONE: 7/7 | pfc_4a1f2bb2278d13c8189148d0 |
| 1x2 single[scoutingstats] avg_p>=60 | Since activation | APPROVED_DONOR_PRICE: 1/1; NAMED_BOOKMAKER_PRICE: 3/3 | NONE: 4/4 | pfc_0f100c9da356ed1c05d9c642 |
| 1x2 single[scoutingstats] avg_p>=60 | Last 30 days | APPROVED_DONOR_PRICE: 1/1; NAMED_BOOKMAKER_PRICE: 3/3 | NONE: 4/4 | pfc_0f100c9da356ed1c05d9c642 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=40 | Since activation | NAMED_BOOKMAKER_PRICE: 12/12; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 12/12; alias_fuzzy: 1/0 | pfc_d94d447efe0742440e953722 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=40 | Last 30 days | NAMED_BOOKMAKER_PRICE: 12/12; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 12/12; alias_fuzzy: 1/0 | pfc_d94d447efe0742440e953722 |
| 1x2 single[zulubet] avg_p>=55 | Since activation | NAMED_BOOKMAKER_PRICE: 4/4; UNMATCHED: 4/0 | NONE: 8/4 | pfc_1607fec83282d02c5254c2bf |
| 1x2 single[zulubet] avg_p>=55 | Last 30 days | NAMED_BOOKMAKER_PRICE: 4/4; UNMATCHED: 4/0 | NONE: 8/4 | pfc_1607fec83282d02c5254c2bf |
| 1x2 unanimous[statarea+zulubet] avg_p>=55 | Since activation | NAMED_BOOKMAKER_PRICE: 2/2; UNMATCHED: 1/0 | NONE: 3/2 | pfc_5a9d3d3426ee7a4e63461d75 |
| 1x2 unanimous[statarea+zulubet] avg_p>=55 | Last 30 days | NAMED_BOOKMAKER_PRICE: 2/2; UNMATCHED: 1/0 | NONE: 3/2 | pfc_5a9d3d3426ee7a4e63461d75 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35 | Since activation | NAMED_BOOKMAKER_PRICE: 8/8; SCOUTINGSTATS_SOLE: 1/1 | NONE: 8/8; scoutingstats_sole_source: 1/1 | pfc_73b036a8ee8dd5a4dea48134 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35 | Last 30 days | NAMED_BOOKMAKER_PRICE: 8/8; SCOUTINGSTATS_SOLE: 1/1 | NONE: 8/8; scoutingstats_sole_source: 1/1 | pfc_73b036a8ee8dd5a4dea48134 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=55 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 1/1; alias_fuzzy: 1/0 | pfc_2bd498a3472b7bbd71982ece |
| 1x2 unanimous[vitibet+zulubet] avg_p>=55 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 1/1; alias_fuzzy: 1/0 | pfc_2bd498a3472b7bbd71982ece |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_3bfaf30507905754f7faab2a |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_3bfaf30507905754f7faab2a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=45 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_b011652ec3e473fbc0afbb6a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=45 | Last 30 days | NAMED_BOOKMAKER_PRICE: 3/3 | NONE: 3/3 | pfc_b011652ec3e473fbc0afbb6a |
| 2way-unanimous avg_p>=60 | Last 30 days | BETEXPLORER_RESCUE: 39/39; NAMED_BOOKMAKER_PRICE: 6/6; SCOUTINGSTATS_SOLE: 30/30; SOURCE_FALLBACK: 16/16; SUSPECT_ALIAS_FUZZY: 4/2; UNMATCHED: 33/0 | NONE: 93/60; alias_fuzzy: 4/2; scoutingstats_sole_source: 30/30; source_fallback_not_execution_eligible: 1/1 | 2way-unanimous avg_p>=60 |
| 2way-unanimous avg_p>=70 | Last 30 days | NAMED_BOOKMAKER_PRICE: 12/12; SCOUTINGSTATS_SOLE: 4/4; SUSPECT_ALIAS_FUZZY: 3/1; UNMATCHED: 5/0 | NONE: 17/12; alias_fuzzy: 3/1; scoutingstats_sole_source: 4/4 | 2way-unanimous avg_p>=70 |
| ml-meta avg_p>=55 | Last 30 days | APPROVED_DONOR_PRICE: 1/1; BETEXPLORER_RESCUE: 12/12; BZZOIRO_PRIMARY: 2/2; NAMED_BOOKMAKER_PRICE: 57/57; SCOUTINGSTATS_SOLE: 38/38; SOURCE_FALLBACK: 22/22; SUSPECT_ALIAS_FUZZY: 4/4; UNMATCHED: 27/0 | NONE: 116/89; alias_fuzzy: 4/4; scoutingstats_sole_source: 38/38; source_fallback_not_execution_eligible: 5/5 | ml-meta avg_p>=55 |
| ml-meta avg_p>=60 | Last 30 days | BETEXPLORER_RESCUE: 1/1; BZZOIRO_PRIMARY: 1/1; NAMED_BOOKMAKER_PRICE: 84/84; SCOUTINGSTATS_SOLE: 19/19; SOURCE_FALLBACK: 13/13; SUSPECT_ALIAS_FUZZY: 16/16; UNMATCHED: 16/0 | NONE: 103/88; alias_fuzzy: 16/16; scoutingstats_sole_source: 19/19; source_fallback_not_execution_eligible: 11/11; stale_quote: 1/0 | ml-meta avg_p>=60 |
| ml-meta avg_p>=65 | Last 30 days | BETEXPLORER_RESCUE: 3/3; BZZOIRO_PRIMARY: 1/1; NAMED_BOOKMAKER_PRICE: 4/4; SCOUTINGSTATS_SOLE: 4/4; SOURCE_FALLBACK: 2/2; SUSPECT_ALIAS_FUZZY: 1/1; UNMATCHED: 6/0 | NONE: 15/9; alias_fuzzy: 1/1; scoutingstats_sole_source: 4/4; source_fallback_not_execution_eligible: 1/1 | ml-meta avg_p>=65 |
| ml-meta avg_p>=80 | Last 30 days | BETEXPLORER_RESCUE: 2/2; NAMED_BOOKMAKER_PRICE: 3/3; SCOUTINGSTATS_SOLE: 1/1; UNMATCHED: 1/0 | NONE: 6/5; scoutingstats_sole_source: 1/1 | ml-meta avg_p>=80 |
| 1x2 single[zulubet] avg_p>=45 | Since activation | UNMATCHED: 1/0 | NONE: 1/0 | pfc_14ee12458803822df3013bcd |
| 1x2 single[zulubet] avg_p>=45 | Last 30 days | UNMATCHED: 1/0 | NONE: 1/0 | pfc_14ee12458803822df3013bcd |
| 1x2 single[zulubet] avg_p>=60 | Since activation | UNMATCHED: 1/0 | NONE: 1/0 | pfc_35f7e50bf23db96c2d3dd59d |
| 1x2 single[zulubet] avg_p>=60 | Last 30 days | UNMATCHED: 1/0 | NONE: 1/0 | pfc_35f7e50bf23db96c2d3dd59d |
| 1x2 single[zulubet] avg_p>=65 | Since activation | UNMATCHED: 1/0 | NONE: 1/0 | pfc_5954379f3a12700edcfd8387 |
| 1x2 single[zulubet] avg_p>=65 | Last 30 days | UNMATCHED: 1/0 | NONE: 1/0 | pfc_5954379f3a12700edcfd8387 |
| 1x2 single[zulubet] avg_p>=70 | Since activation | SUSPECT_ALIAS_FUZZY: 1/0 | alias_fuzzy: 1/0 | pfc_c8cbcf76ea758fd6de596ae1 |
| 1x2 single[zulubet] avg_p>=70 | Last 30 days | SUSPECT_ALIAS_FUZZY: 1/0 | alias_fuzzy: 1/0 | pfc_c8cbcf76ea758fd6de596ae1 |
| unanimous[betclan+statarea+vitibet] avg_p>=65 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1; SCOUTINGSTATS_SOLE: 1/1 | NONE: 1/1; scoutingstats_sole_source: 1/1 | unanimous[betclan+statarea+vitibet] avg_p>=65 |
| unanimous[betclan+vitibet] avg_p>=70 | Last 30 days | NAMED_BOOKMAKER_PRICE: 12/12; SCOUTINGSTATS_SOLE: 1/1; SUSPECT_ALIAS_FUZZY: 2/0; UNMATCHED: 2/0 | NONE: 14/12; alias_fuzzy: 2/0; scoutingstats_sole_source: 1/1 | unanimous[betclan+vitibet] avg_p>=70 |
| unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65 | Last 30 days | NAMED_BOOKMAKER_PRICE: 2/2 | NONE: 2/2 | unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65 |
| unanimous[bzzoiro+statarea+vitibet] avg_p>=65 | Last 30 days | NAMED_BOOKMAKER_PRICE: 4/4; UNMATCHED: 1/0 | NONE: 5/4 | unanimous[bzzoiro+statarea+vitibet] avg_p>=65 |
| unanimous[bzzoiro+vitibet+zulubet] avg_p>=65 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | unanimous[bzzoiro+vitibet+zulubet] avg_p>=65 |
| unanimous[bzzoiro+vitibet] avg_p>=70 | Last 30 days | NAMED_BOOKMAKER_PRICE: 13/13 | NONE: 13/13 | unanimous[bzzoiro+vitibet] avg_p>=70 |
| unanimous[statarea+vitibet+zulubet] avg_p>=65 | Last 30 days | NAMED_BOOKMAKER_PRICE: 2/2 | NONE: 2/2 | unanimous[statarea+vitibet+zulubet] avg_p>=65 |
| unanimous[statarea+vitibet] avg_p>=70 | Last 30 days | NAMED_BOOKMAKER_PRICE: 15/15; SCOUTINGSTATS_SOLE: 1/1; SUSPECT_ALIAS_FUZZY: 1/0; UNMATCHED: 4/0 | NONE: 19/15; alias_fuzzy: 1/0; scoutingstats_sole_source: 1/1 | unanimous[statarea+vitibet] avg_p>=70 |
| unanimous[vitibet+zulubet] avg_p>=70 | Last 30 days | NAMED_BOOKMAKER_PRICE: 4/4; SOURCE_FALLBACK: 1/1 | NONE: 4/4; source_fallback_not_execution_eligible: 1/1 | unanimous[vitibet+zulubet] avg_p>=70 |

### Historical validation — NOT operational performance

Registry validation is separate research evidence, not extra live observations. Price basis and mining dates are retained; unavailable fields are not inferred.

| Rule | Validation settled / priced | Pricing coverage | Hit rate | ROI | Mining window | Price basis | Stored key |
| --- | --- | --- | --- | --- | --- | --- | --- |
| ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55 | 347 / 347 | 100.0% | 66.6% | 0.8% | start: 2026-06-13; split: 2026-09-25; as_of_exclusive: 2026-10-23 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_27e0f725859bc708f95c58a3 |
| 1x2 single[scoutingstats] avg_p>=50 | 1235 / 1235 | 100.0% | 67.5% | 0.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_439097cb9bb700e9996c0b07 |
| 1x2 single[zulubet] avg_p>=50 | 1241 / 1240 | 99.9% | 57.4% | 0.5% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_4cf3df8552488297d7ccf526 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=0 | 438 / 438 | 100.0% | 61.2% | 2.9% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_0ad08cd1b2e75a2c9051189e |
| 1x2 unanimous[statarea+zulubet] avg_p>=40 | 278 / 277 | 99.6% | 61.9% | 1.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_5208b9e15194a691590430ad |
| 1x2 unanimous[vitibet+zulubet] avg_p>=50 | 427 / 427 | 100.0% | 66.5% | 4.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_234f16641d9893e8ec2a01f0 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=50 | 201 / 201 | 100.0% | 69.7% | 0.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_0b290b623e2a54ea7df3006c |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 | 426 / 426 | 100.0% | 62.2% | 4.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_4a1f2bb2278d13c8189148d0 |
| 1x2 single[scoutingstats] avg_p>=60 | 566 / 566 | 100.0% | 76.3% | 0.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_0f100c9da356ed1c05d9c642 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=40 | 822 / 822 | 100.0% | 59.7% | 0.2% | start: 2026-06-13; split: 2026-09-23; as_of_exclusive: 2026-10-21 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_d94d447efe0742440e953722 |
| 1x2 single[zulubet] avg_p>=55 | 864 / 863 | 99.9% | 64.6% | 4.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_1607fec83282d02c5254c2bf |
| 1x2 unanimous[statarea+zulubet] avg_p>=55 | 222 / 221 | 99.5% | 73.4% | 3.6% | start: 2026-06-13; split: 2026-09-23; as_of_exclusive: 2026-10-21 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_5a9d3d3426ee7a4e63461d75 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35 | 436 / 436 | 100.0% | 58.5% | 1.3% | start: 2026-06-13; split: 2026-09-25; as_of_exclusive: 2026-10-23 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_73b036a8ee8dd5a4dea48134 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=55 | 358 / 358 | 100.0% | 68.2% | 2.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_2bd498a3472b7bbd71982ece |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 | 645 / 645 | 100.0% | 65.1% | 1.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_3bfaf30507905754f7faab2a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=45 | 511 / 511 | 100.0% | 62.2% | 0.1% | start: 2026-06-13; split: 2026-09-26; as_of_exclusive: 2026-10-24 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_b011652ec3e473fbc0afbb6a |
| 2way-unanimous avg_p>=60 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 2way-unanimous avg_p>=60 |
| 2way-unanimous avg_p>=70 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 2way-unanimous avg_p>=70 |
| ml-meta avg_p>=55 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | ml-meta avg_p>=55 |
| ml-meta avg_p>=60 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | ml-meta avg_p>=60 |
| ml-meta avg_p>=65 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | ml-meta avg_p>=65 |
| ml-meta avg_p>=80 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | ml-meta avg_p>=80 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=35 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_054448b499623dd39b072b38 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=45 | 540 / 540 | 100.0% | 64.3% | 2.7% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_0aed63f3d04b46330958121d |
| 1x2 single[zulubet] avg_p>=45 | 1488 / 1487 | 99.9% | 55.6% | 2.5% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_14ee12458803822df3013bcd |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=55 | 248 / 248 | 100.0% | 75.8% | 4.5% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_1ba3ab3c75e6f3a9680ae43c |
| 1x2 single[zulubet] avg_p>=40 | 1660 / 1659 | 99.9% | 53.2% | 0.9% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_1e9cfc6500aaac77afa1eaf9 |
| 1x2 unanimous[statarea+zulubet] avg_p>=35 | 284 / 283 | 99.6% | 61.3% | 0.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_3072388544a60552346bd162 |
| 1x2 single[zulubet] avg_p>=60 | 633 / 632 | 99.8% | 67.6% | 3.8% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_35f7e50bf23db96c2d3dd59d |
| 1x2 single[zulubet] avg_p>=0 | 1733 / 1732 | 99.9% | 52.7% | 1.3% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_3dc0fa6511953bf09bc4c845 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=50 | 285 / 285 | 100.0% | 68.4% | 4.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_3fbabd0ade3f89853e43fb10 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=60 | 195 / 195 | 100.0% | 79.0% | 5.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_40b163633fc01fd0ff7d0ef1 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=50 | 164 / 164 | 100.0% | 71.3% | 0.7% | start: 2026-06-13; split: 2026-09-23; as_of_exclusive: 2026-10-21 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_444d408c4ccd3a4bf4fb020c |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=55 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_4e2583010bf805466e33c2d0 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=0 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_4f2df06575151e798727a6b0 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=55 | 215 / 215 | 100.0% | 70.2% | 2.6% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_527524a94e98cff9740d499c |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=60 | 203 / 203 | 100.0% | 81.3% | 6.8% | start: 2026-06-13; split: 2026-09-27; as_of_exclusive: 2026-10-25 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_5904b1fc7050646e6321090c |
| 1x2 single[zulubet] avg_p>=65 | 443 / 442 | 99.8% | 70.0% | 2.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_5954379f3a12700edcfd8387 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=50 | 372 / 372 | 100.0% | 68.0% | 0.3% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_5f861bad9f49ebf6d6fe2c16 |
| 1x2 single[zulubet] avg_p>=35 | 1732 / 1731 | 99.9% | 52.7% | 1.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_61cb1dd2a3157c4231070cdb |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=40 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_6cd236448d9fd967f8dcb591 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=0 | 169 / 169 | 100.0% | 67.5% | 1.6% | start: 2026-06-13; split: 2026-09-26; as_of_exclusive: 2026-10-24 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_754f7247e83f901ae415b35f |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=35 | 438 / 438 | 100.0% | 61.2% | 2.9% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_7d20e19c2c26174fa21e9e86 |
| 1x2 unanimous[statarea+zulubet] avg_p>=45 | 314 / 313 | 99.7% | 66.9% | 2.5% | start: 2026-06-13; split: 2026-09-23; as_of_exclusive: 2026-10-21 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_7eb24434123da46374442290 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=0 | 436 / 436 | 100.0% | 58.5% | 1.3% | start: 2026-06-13; split: 2026-09-25; as_of_exclusive: 2026-10-23 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_92ab281aa7c2173e7502ba49 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=45 | 229 / 229 | 100.0% | 67.7% | 0.6% | start: 2026-06-13; split: 2026-09-26; as_of_exclusive: 2026-10-24 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_9ae5a305a703bca83fd321b3 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=45 | 316 / 316 | 100.0% | 69.6% | 1.0% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_a460a0e9dcb1f980cde169c0 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=35 | 169 / 169 | 100.0% | 67.5% | 1.6% | start: 2026-06-13; split: 2026-09-26; as_of_exclusive: 2026-10-24 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_a8e99ebc0016f0d0bb95aa70 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=60 | 128 / 128 | 100.0% | 81.2% | 3.0% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_a90a9b922d2318a2446434ce |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=50 | 194 / 194 | 100.0% | 66.5% | 0.1% | start: 2026-06-13; split: 2026-09-26; as_of_exclusive: 2026-10-24 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_b0b7a0c1932e3636d2b485d6 |
| 1x2 unanimous[statarea+zulubet] avg_p>=0 | 284 / 283 | 99.6% | 61.3% | 0.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_b11e22bfdd27d85fad78ba74 |
| ou_3.5 unanimous[scoutingstats+statarea] avg_p>=70 | 366 / 366 | 100.0% | 80.6% | 0.5% | start: 2026-06-13; split: 2026-09-27; as_of_exclusive: 2026-10-25 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_bdce95a736d6cc8667f7ac31 |
| 1x2 unanimous[statarea+zulubet] avg_p>=50 | 271 / 270 | 99.6% | 70.5% | 3.9% | start: 2026-06-13; split: 2026-09-23; as_of_exclusive: 2026-10-21 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_c83d885867c9025a351b9b8c |
| 1x2 single[zulubet] avg_p>=70 | 242 / 241 | 99.6% | 74.0% | 2.7% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_c8cbcf76ea758fd6de596ae1 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=40 | 287 / 287 | 100.0% | 61.0% | 2.7% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_cd84fb2c3ed889c0ae9eb89e |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=0 | 138 / 138 | 100.0% | 60.1% | 1.9% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_cddf4106a3d45b6e455d8c73 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=55 | 177 / 177 | 100.0% | 71.8% | 0.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_d17123b85e11155f22e40051 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=45 | 372 / 372 | 100.0% | 63.7% | 2.5% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_e25602082a90cb64fb9c5451 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=45 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_e37e7d70a4d046d7a07da0a4 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=40 | 172 / 172 | 100.0% | 66.9% | 0.7% | start: 2026-06-13; split: 2026-09-27; as_of_exclusive: 2026-10-25 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_e5c10af025fc5071367c9b47 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=55 | 239 / 239 | 100.0% | 74.9% | 4.3% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_f2b2a2e84093abe72bbc01c0 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=50 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_f51b5fdaf32bcca063f4b2cc |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=35 | 137 / 137 | 100.0% | 60.6% | 2.7% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_f56fe4a2759e9b17b9bdb116 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=50 | 291 / 291 | 100.0% | 70.8% | 0.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_fb2e721d2bb8a41fe9fa3713 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=55 | 156 / 156 | 100.0% | 69.9% | 0.6% | start: 2026-06-13; split: 2026-09-23; as_of_exclusive: 2026-10-21 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_fbf508b9c62bae8f281bb6e1 |
| 1x2 single[scoutingstats] avg_p>=65 | 398 / 398 | 100.0% | 80.2% | 0.1% | start: 2026-06-13; split: 2026-09-27; as_of_exclusive: 2026-10-25 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_fdade2e70df4d4bb78a8cd6e |
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
- **Over 2.5 Goals**: occurred in 535 / 883 matches (60.6%)
- **Both Teams to Score (BTTS)**: occurred in 470 / 883 matches (53.2%)
- **Selected Team Over 1.5 Goals**: occurred in 565 / 879 matches (64.3%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 586
- **Total Hits**: 453
- **Overall Hit Rate**: 77.3%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=19, settled=19, hit_rate=89.5% (hits=17/recommended=19), priced_n=1, priced_ROI=0.64 (denominator=1), registry_processed=61, class=priced
- `away_under_15`: recommended=6, settled=6, hit_rate=100.0% (hits=6/recommended=6), priced_n=5, priced_ROI=2.01 (denominator=5), registry_processed=10, class=priced
- `away_under_25`: recommended=7, settled=7, hit_rate=71.4% (hits=5/recommended=7), priced_n=7, priced_ROI=0.318429 (denominator=7), registry_processed=39, class=priced
- `away_under_35`: recommended=155, settled=155, hit_rate=96.1% (hits=149/recommended=155), priced_n=1, priced_ROI=0.435 (denominator=1), registry_processed=305, class=priced
- `btts_no`: recommended=8, settled=8, hit_rate=37.5% (hits=3/recommended=8), priced_n=5, priced_ROI=-0.45 (denominator=5), registry_processed=12, class=priced
- `btts_yes`: recommended=5, settled=5, hit_rate=100.0% (hits=5/recommended=5), priced_n=3, priced_ROI=0.853333 (denominator=3), registry_processed=22, class=priced
- `home_over_05`: recommended=24, settled=24, hit_rate=87.5% (hits=21/recommended=24), priced_n=2, priced_ROI=0.345 (denominator=2), registry_processed=188, class=priced
- `home_over_15`: recommended=1, settled=1, hit_rate=100.0% (hits=1/recommended=1), priced_n=0, priced_ROI=None (denominator=0), registry_processed=6, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `home_under_15`: recommended=2, settled=2, hit_rate=100.0% (hits=2/recommended=2), priced_n=2, priced_ROI=0.381 (denominator=2), registry_processed=9, class=priced
- `home_under_25`: recommended=1, settled=1, hit_rate=0.0% (hits=0/recommended=1), priced_n=1, priced_ROI=-1.0 (denominator=1), registry_processed=50, class=priced
- `home_under_35`: recommended=47, settled=47, hit_rate=97.9% (hits=46/recommended=47), priced_n=0, priced_ROI=None (denominator=0), registry_processed=75, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `match_over_15`: recommended=25, settled=25, hit_rate=88.0% (hits=22/recommended=25), priced_n=18, priced_ROI=0.155222 (denominator=18), registry_processed=72, class=priced
- `match_over_25`: recommended=255, settled=255, hit_rate=61.2% (hits=156/recommended=255), priced_n=193, priced_ROI=-0.014518 (denominator=193), registry_processed=729, class=priced
- `match_over_35`: recommended=18, settled=18, hit_rate=77.8% (hits=14/recommended=18), priced_n=11, priced_ROI=1.036364 (denominator=11), registry_processed=49, class=priced
- `match_over_45`: recommended=2, settled=2, hit_rate=100.0% (hits=2/recommended=2), priced_n=2, priced_ROI=4.0 (denominator=2), registry_processed=3, class=priced
- `match_under_35`: recommended=5, settled=5, hit_rate=0.0% (hits=0/recommended=5), priced_n=5, priced_ROI=-1.0 (denominator=5), registry_processed=7, class=priced
- `match_under_45`: recommended=6, settled=6, hit_rate=66.7% (hits=4/recommended=6), priced_n=5, priced_ROI=0.242 (denominator=5), registry_processed=10, class=priced

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **2350** | scored: 2350 | without promised % (legacy rows): 127

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 557 | 530 | 318 | 60.0% | 48.5% | +11.5% | 0.256544 |
| `match_over_45` | 346 | 345 | 77 | 22.3% | 23.8% | -1.5% | 0.17492 |
| `away_under_35` | 303 | 303 | 295 | 97.4% | 96.0% | +1.4% | 0.025734 |
| `away_under_25` | 297 | 294 | 270 | 91.8% | 89.5% | +2.3% | 0.072494 |
| `match_over_35` | 133 | 127 | 68 | 53.5% | 42.8% | +10.8% | 0.270867 |
| `home_under_35` | 127 | 126 | 121 | 96.0% | 96.0% | -0.0% | 0.038275 |
| `home_under_25` | 109 | 100 | 93 | 93.0% | 87.8% | +5.2% | 0.069141 |
| `btts_yes` | 96 | 92 | 55 | 59.8% | 47.1% | +12.7% | 0.248418 |
| `btts_no` | 89 | 85 | 36 | 42.4% | 54.1% | -11.7% | 0.252474 |
| `away_over_05` | 53 | 45 | 39 | 86.7% | 80.0% | +6.6% | 0.114247 |
| `away_under_15` | 50 | 45 | 31 | 68.9% | 77.3% | -8.4% | 0.194701 |
| `home_over_05` | 40 | 39 | 33 | 84.6% | 86.0% | -1.4% | 0.118549 |
| `match_over_15` | 31 | 30 | 24 | 80.0% | 84.3% | -4.3% | 0.160763 |
| `match_under_25` | 42 | 26 | 10 | 38.5% | 40.8% | -2.3% | 0.238415 |
| `home_under_15` | 17 | 10 | 8 | 80.0% | 69.9% | +10.1% | 0.22758 |
| `match_under_35` | 17 | 9 | 3 | 33.3% | 62.4% | -29.0% | 0.291151 |
| `home_over_15` | 13 | 7 | 2 | 28.6% | 44.7% | -16.1% | 0.22064 |
| `away_over_15` | 7 | 5 | 4 | 80.0% | 59.7% | +20.3% | 0.215626 |
| `match_under_45` | 11 | 5 | 3 | 60.0% | 80.6% | -20.6% | 0.28987 |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 2127 | 1416 | 66.6% | 63.2% | +3.4% | 0.158377 |
| model | 96 | 74 | 77.1% | 67.3% | +9.8% | 0.182554 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 69 | 19.1% | 26.1% | +7.0% |
| 0.2-0.3 | 252 | 24.2% | 21.0% | -3.2% |
| 0.3-0.4 | 119 | 35.9% | 47.9% | +12.0% |
| 0.4-0.5 | 519 | 44.7% | 57.0% | +12.3% |
| 0.5-0.6 | 190 | 54.4% | 52.1% | -2.3% |
| 0.6-0.7 | 70 | 63.5% | 58.6% | -4.9% |
| 0.7-0.8 | 35 | 73.8% | 68.6% | -5.2% |
| 0.8-0.9 | 393 | 86.6% | 89.3% | +2.7% |
| 0.9-1.0 | 576 | 94.7% | 95.7% | +0.9% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=868, MAE=1.510184 goals, bias=-0.228018 (realized − promised), promised avg 3.404286 vs realized 3.176267

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 868 | 32.1% | 33.5% | +1.5% | 0.197573 |
| BTTS-Yes | 868 | 45.6% | 52.9% | +7.3% | 0.259013 |
| Home Over 1.5 | 868 | 60.3% | 52.4% | -7.9% | 0.230666 |
| Over 2.5 | 868 | 66.2% | 60.3% | -6.0% | 0.243344 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 235 | 8.6% | 22.1% | +13.5% |
| 0.1-0.2 | 325 | 10.5% | 17.2% | +6.7% |
| 0.2-0.3 | 266 | 23.6% | 26.3% | +2.7% |
| 0.3-0.4 | 119 | 36.5% | 45.4% | +8.8% |
| 0.4-0.5 | 494 | 41.9% | 51.8% | +9.9% |
| 0.5-0.6 | 620 | 56.1% | 57.1% | +0.9% |
| 0.6-0.7 | 653 | 65.2% | 57.9% | -7.3% |
| 0.7-0.8 | 179 | 74.6% | 68.2% | -6.4% |
| 0.8-0.9 | 520 | 84.8% | 65.2% | -19.6% |
| 0.9-1.0 | 61 | 92.1% | 77.0% | -15.1% |

## By rule

Counts are frozen PICK ROWS, not bets: SKIPPED_VETO / WATCHLIST_* rows are included and were never cardable. See the full audit’s `## By bucket` for bucket-level counts. These are not acca returns or bank performance.

ROI uses priced rows only; hit rate uses all settled rows. The 30-priced-row cutoff is a reporting sample flag, not proof of profitability or an activation gate. Registry status/certification are separate from this audit window. Historical ml-meta rules are not the live ML ENH acca selector.

### Positive ROI (2 rules)

| Rule | Priced ROI | Priced sample | Hit rate | Evidence | Registry context | Stored rule ID/key |
| --- | ---: | ---: | --- | --- | --- | --- |
| ml-meta avg_p>=55 | +17.8% | 136 priced | 73.0% (119/163 settled) | 30+ priced rows | legacy rule key | ml-meta avg_p>=55 |
| ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55 | +7.1% | 45 priced | 65.2% (30/46 settled) | 30+ priced rows | contract · benched, activated 2026-10-23, certified valid n=347 | pfc_27e0f725859bc708f95c58a3 |

### Negative ROI (3 rules)

| Rule | Priced ROI | Priced sample | Hit rate | Evidence | Registry context | Stored rule ID/key |
| --- | ---: | ---: | --- | --- | --- | --- |
| ml-meta avg_p>=60 | -4.2% | 134 priced | 60.7% (91/150 settled) | 30+ priced rows | legacy rule key | ml-meta avg_p>=60 |
| 1x2 single[scoutingstats] avg_p>=50 | -5.3% | 195 priced | 60.6% (149/246 settled) | 30+ priced rows | contract · benched, activated 2026-10-20, certified valid n=1235 | pfc_439097cb9bb700e9996c0b07 |
| 2way-unanimous avg_p>=60 | -12.0% | 93 priced | 63.3% (81/128 settled) | 30+ priced rows | legacy rule key | 2way-unanimous avg_p>=60 |

### Break-even (0 rules)

- none

### Insufficient priced evidence (30 rules)

| Rule | Priced ROI | Priced sample | Hit rate | Evidence | Registry context | Stored rule ID/key |
| --- | ---: | ---: | --- | --- | --- | --- |
| 1x2 single[zulubet] avg_p>=50 | +90.0% | 2 priced | 50.0% (2/4 settled) | PROVISIONAL: 2 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=1241 | pfc_4cf3df8552488297d7ccf526 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=45 | +76.0% | 3 priced | 66.7% (2/3 settled) | PROVISIONAL: 3 priced < 30 | contract · candidate, activated 2026-10-24, certified valid n=511 | pfc_b011652ec3e473fbc0afbb6a |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=0 | +55.2% | 4 priced | 75.0% (3/4 settled) | PROVISIONAL: 4 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=438 | pfc_0ad08cd1b2e75a2c9051189e |
| unanimous[betclan+statarea+vitibet] avg_p>=65 | +50.0% | 2 priced | 100.0% (2/2 settled) | PROVISIONAL: 2 priced < 30 | legacy rule key | unanimous[betclan+statarea+vitibet] avg_p>=65 |
| 1x2 unanimous[statarea+zulubet] avg_p>=40 | +44.0% | 1 priced | 100.0% (1/1 settled) | PROVISIONAL: 1 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=278 | pfc_5208b9e15194a691590430ad |
| unanimous[vitibet+zulubet] avg_p>=70 | +39.2% | 5 priced | 100.0% (5/5 settled) | PROVISIONAL: 5 priced < 30 | legacy rule key | unanimous[vitibet+zulubet] avg_p>=70 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=50 | +34.6% | 5 priced | 81.8% (9/11 settled) | PROVISIONAL: 5 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=427 | pfc_234f16641d9893e8ec2a01f0 |
| unanimous[betclan+vitibet] avg_p>=70 | +34.1% | 13 priced | 94.1% (16/17 settled) | PROVISIONAL: 13 priced < 30 | legacy rule key | unanimous[betclan+vitibet] avg_p>=70 |
| unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65 | +18.0% | 2 priced | 100.0% (2/2 settled) | PROVISIONAL: 2 priced < 30 | legacy rule key | unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65 |
| unanimous[statarea+vitibet] avg_p>=70 | +17.2% | 16 priced | 90.5% (19/21 settled) | PROVISIONAL: 16 priced < 30 | legacy rule key | unanimous[statarea+vitibet] avg_p>=70 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=50 | +16.5% | 2 priced | 50.0% (1/2 settled) | PROVISIONAL: 2 priced < 30 | contract · certified, activated 2026-10-20, certified valid n=201 | pfc_0b290b623e2a54ea7df3006c |
| unanimous[bzzoiro+vitibet+zulubet] avg_p>=65 | +15.0% | 1 priced | 100.0% (1/1 settled) | PROVISIONAL: 1 priced < 30 | legacy rule key | unanimous[bzzoiro+vitibet+zulubet] avg_p>=65 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 | +11.1% | 7 priced | 57.1% (4/7 settled) | PROVISIONAL: 7 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=426 | pfc_4a1f2bb2278d13c8189148d0 |
| 1x2 single[scoutingstats] avg_p>=60 | +9.7% | 4 priced | 75.0% (3/4 settled) | PROVISIONAL: 4 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=566 | pfc_0f100c9da356ed1c05d9c642 |
| ml-meta avg_p>=80 | +7.5% | 6 priced | 100.0% (7/7 settled) | PROVISIONAL: 6 priced < 30 | legacy rule key | ml-meta avg_p>=80 |
| 2way-unanimous avg_p>=70 | +3.8% | 17 priced | 79.2% (19/24 settled) | PROVISIONAL: 17 priced < 30 | legacy rule key | 2way-unanimous avg_p>=70 |
| ml-meta avg_p>=65 | +3.3% | 15 priced | 85.7% (18/21 settled) | PROVISIONAL: 15 priced < 30 | legacy rule key | ml-meta avg_p>=65 |
| unanimous[statarea+vitibet+zulubet] avg_p>=65 | -2.5% | 2 priced | 50.0% (1/2 settled) | PROVISIONAL: 2 priced < 30 | legacy rule key | unanimous[statarea+vitibet+zulubet] avg_p>=65 |
| unanimous[bzzoiro+vitibet] avg_p>=70 | -3.6% | 13 priced | 69.2% (9/13 settled) | PROVISIONAL: 13 priced < 30 | legacy rule key | unanimous[bzzoiro+vitibet] avg_p>=70 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=40 | -17.4% | 12 priced | 38.5% (5/13 settled) | PROVISIONAL: 12 priced < 30 | contract · benched, activated 2026-10-21, certified valid n=822 | pfc_d94d447efe0742440e953722 |
| 1x2 single[zulubet] avg_p>=55 | -26.7% | 4 priced | 50.0% (4/8 settled) | PROVISIONAL: 4 priced < 30 | contract · certified, activated 2026-10-20, certified valid n=864 | pfc_1607fec83282d02c5254c2bf |
| unanimous[bzzoiro+statarea+vitibet] avg_p>=65 | -33.5% | 4 priced | 60.0% (3/5 settled) | PROVISIONAL: 4 priced < 30 | legacy rule key | unanimous[bzzoiro+statarea+vitibet] avg_p>=65 |
| 1x2 unanimous[statarea+zulubet] avg_p>=55 | -34.5% | 2 priced | 33.3% (1/3 settled) | PROVISIONAL: 2 priced < 30 | contract · benched, activated 2026-10-21, certified valid n=222 | pfc_5a9d3d3426ee7a4e63461d75 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35 | -36.1% | 9 priced | 33.3% (3/9 settled) | PROVISIONAL: 9 priced < 30 | contract · candidate, activated 2026-10-23, certified valid n=436 | pfc_73b036a8ee8dd5a4dea48134 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=55 | -100.0% | 1 priced | 50.0% (1/2 settled) | PROVISIONAL: 1 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=358 | pfc_2bd498a3472b7bbd71982ece |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 | -100.0% | 1 priced | 0.0% (0/1 settled) | PROVISIONAL: 1 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=645 | pfc_3bfaf30507905754f7faab2a |
| 1x2 single[zulubet] avg_p>=45 | unavailable | 0 priced | 0.0% (0/1 settled) | PROVISIONAL: 0 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=1488 | pfc_14ee12458803822df3013bcd |
| 1x2 single[zulubet] avg_p>=60 | unavailable | 0 priced | 100.0% (1/1 settled) | PROVISIONAL: 0 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=633 | pfc_35f7e50bf23db96c2d3dd59d |
| 1x2 single[zulubet] avg_p>=65 | unavailable | 0 priced | 100.0% (1/1 settled) | PROVISIONAL: 0 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=443 | pfc_5954379f3a12700edcfd8387 |
| 1x2 single[zulubet] avg_p>=70 | unavailable | 0 priced | 100.0% (1/1 settled) | PROVISIONAL: 0 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=242 | pfc_c8cbcf76ea758fd6de596ae1 |


## By bucket

- `CAUTION`: settled=132, wins=85, hit_rate=0.643939 (settled n=132), ROI=0.032967 (priced n=132)
- `CERTIFIED_CLEAN`: settled=85, wins=51, hit_rate=0.6 (settled n=85), ROI=-0.036092 (priced n=85)
- `SKIPPED_VETO`: settled=509, wins=352, hit_rate=0.691552 (settled n=509), ROI=0.024036 (priced n=455)
- `WATCHLIST_NO_ODDS`: settled=74, wins=48, hit_rate=0.648649 (settled n=74), ROI=None (priced n=0)
- `WATCHLIST_SUSPECT_PRICE`: settled=55, wins=28, hit_rate=0.509091 (settled n=55), ROI=-0.068 (priced n=10)
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=68, wins=45, hit_rate=0.661765 (settled n=68), ROI=0.000735 (priced n=68)
- `WATCHLIST_UNKNOWN_CTX`: settled=6, wins=5, hit_rate=0.833333 (settled n=6), ROI=-0.01 (priced n=6)

## By odds source

- `UNKNOWN`: settled=173, wins=109, hit_rate=0.630058 (settled n=173), ROI=None (priced n=0)
- `betexplorer_odds`: settled=161, wins=123, hit_rate=0.763975 (settled n=161), ROI=0.02205 (priced n=161)
- `boggio`: settled=2, wins=2, hit_rate=1.0 (settled n=2), ROI=0.486 (priced n=2)
- `bzzoiro_odds`: settled=4, wins=4, hit_rate=1.0 (settled n=4), ROI=0.4625 (priced n=4)
- `forebet_best`: settled=34, wins=23, hit_rate=0.676471 (settled n=34), ROI=-0.04 (priced n=34)
- `oddspapi_odds`: settled=9, wins=5, hit_rate=0.555556 (settled n=9), ROI=-0.036111 (priced n=9)
- `pinnapi_odds`: settled=261, wins=156, hit_rate=0.597701 (settled n=261), ROI=-0.012481 (priced n=261)
- `scoutingstats_odds`: settled=131, wins=90, hit_rate=0.687023 (settled n=131), ROI=0.011298 (priced n=131)
- `sharpapi_odds`: settled=1, wins=1, hit_rate=1.0 (settled n=1), ROI=0.741 (priced n=1)
- `theoddsapi`: settled=109, wins=76, hit_rate=0.697248 (settled n=109), ROI=0.092569 (priced n=109)
- `zulubet`: settled=44, wins=25, hit_rate=0.568182 (settled n=44), ROI=-0.050227 (priced n=44)

## By odds match method

- `alias_fuzzy`: settled=87, wins=51, hit_rate=0.586207 (settled n=87), ROI=-0.039167 (priced n=24)
- `alias_time`: settled=1, wins=0, hit_rate=0.0 (settled n=1), ROI=-1.0 (priced n=1)
- `betexplorer`: settled=57, wins=40, hit_rate=0.701754 (settled n=57), ROI=-0.037368 (priced n=57)
- `exact`: settled=620, wins=417, hit_rate=0.672581 (settled n=620), ROI=0.029404 (priced n=620)
- `fallback`: settled=54, wins=33, hit_rate=0.611111 (settled n=54), ROI=-0.048704 (priced n=54)
- `none`: settled=110, wins=73, hit_rate=0.663636 (settled n=110), ROI=None (priced n=0)

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| APPROVED_DONOR_PRICE (`APPROVED_DONOR_PRICE`) | 2 | 2 | 1.0 | 2 | 0.486 |
| BetExplorer rescue (`BETEXPLORER_RESCUE`) | 57 | 40 | 0.701754 | 57 | -0.037368 |
| Bzzoiro primary match (`BZZOIRO_PRIMARY`) | 4 | 4 | 1.0 | 4 | 0.4625 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 484 | 321 | 0.663223 | 484 | 0.026712 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 131 | 90 | 0.687023 | 131 | 0.011298 |
| Source fallback (`SOURCE_FALLBACK`) | 54 | 33 | 0.611111 | 54 | -0.048704 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 87 | 51 | 0.586207 | 24 | -0.039167 |
| No usable price (`UNMATCHED`) | 110 | 73 | 0.663636 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 509 | 352 | 0.691552 | 455 | 0.024036 |
| **trusted evidence only** | 355 | 244 | 0.687324 | 355 | 0.032723 |
| **soft evidence only** | 154 | 108 | 0.701299 | 100 | -0.0068 |
| evidence: BETEXPLORER_RESCUE | 35 | 26 | 0.742857 | 35 | -0.031429 |
| evidence: BZZOIRO_PRIMARY | 3 | 3 | 1.0 | 3 | 0.4 |
| evidence: NAMED_BOOKMAKER_PRICE | 317 | 215 | 0.678233 | 317 | 0.03633 |
| evidence: SCOUTINGSTATS_SOLE | 63 | 45 | 0.714286 | 63 | 0.022698 |
| evidence: SOURCE_FALLBACK | 23 | 15 | 0.652174 | 23 | -0.080435 |
| evidence: SUSPECT_ALIAS_FUZZY | 32 | 23 | 0.71875 | 14 | -0.018571 |
| evidence: UNMATCHED | 36 | 25 | 0.694444 | 0 | None |
| odds band: <1.50 | 217 | 177 | 0.815668 | 217 | 0.039547 |
| odds band: 1.50-2.00 | 197 | 117 | 0.593909 | 197 | -0.003731 |
| odds band: 2.00-3.00 | 37 | 18 | 0.486486 | 37 | 0.083514 |
| odds band: >=3.00 | 4 | 1 | 0.25 | 4 | 0.0 |
| odds band: unpriced | 54 | 39 | 0.722222 | 0 | None |
| veto reason: context VETO in ['competition_type'] | 47 | 39 | 0.829787 | 37 | 0.099557 |
| veto reason: context VETO in ['league', 'niche'] | 27 | 18 | 0.666667 | 20 | -0.127325 |
| veto reason: context VETO in ['league', 'odds_band', 'niche'] | 6 | 2 | 0.333333 | 6 | -0.40825 |
| veto reason: context VETO in ['league', 'odds_band'] | 37 | 22 | 0.594595 | 37 | 0.031405 |
| veto reason: context VETO in ['league', 'team_a'] | 4 | 0 | 0.0 | 4 | -1.0 |
| veto reason: context VETO in ['league', 'team_h', 'competition_type'] | 2 | 2 | 1.0 | 2 | 0.3881 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 6 | 4 | 0.666667 | 5 | 0.186 |
| veto reason: context VETO in ['league', 'team_h', 'odds_band'] | 1 | 1 | 1.0 | 1 | 0.45 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 2 | 1.0 | 2 | 0.7476 |
| veto reason: context VETO in ['league', 'team_h'] | 3 | 2 | 0.666667 | 3 | -0.176667 |
| veto reason: context VETO in ['league'] | 68 | 42 | 0.617647 | 56 | -0.15812 |
| veto reason: context VETO in ['niche'] | 29 | 20 | 0.689655 | 28 | -0.026832 |
| veto reason: context VETO in ['odds_band', 'niche'] | 2 | 1 | 0.5 | 2 | -0.10315 |
| veto reason: context VETO in ['odds_band'] | 105 | 65 | 0.619048 | 105 | -0.023072 |
| veto reason: context VETO in ['team_a', 'competition_type'] | 6 | 5 | 0.833333 | 6 | 0.20035 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.146667 |
| veto reason: context VETO in ['team_a', 'odds_band', 'niche'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 9 | 8 | 0.888889 | 9 | 0.212222 |
| veto reason: context VETO in ['team_a'] | 52 | 41 | 0.788462 | 43 | 0.233507 |
| veto reason: context VETO in ['team_h', 'competition_type'] | 13 | 11 | 0.846154 | 12 | 0.082017 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 3 | 0.75 | 3 | 0.446667 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 6 | 4 | 0.666667 | 6 | -0.123333 |
| veto reason: context VETO in ['team_h', 'team_a', 'competition_type'] | 1 | 1 | 1.0 | 1 | 0.23 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.62 |
| veto reason: context VETO in ['team_h', 'team_a', 'odds_band'] | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: context VETO in ['team_h', 'team_a'] | 16 | 12 | 0.75 | 15 | 0.23762 |
| veto reason: context VETO in ['team_h'] | 44 | 32 | 0.727273 | 33 | 0.155758 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.08 | 1 | 1 | 1.0 | 1 | 0.08 |
| veto reason: short-odds away favourite 1.16 | 1 | 1 | 1.0 | 1 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.21 | 1 | 1 | 1.0 | 1 | 0.21 |
| veto reason: short-odds away favourite 1.24 | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: short-odds away favourite 1.25 | 3 | 3 | 1.0 | 3 | 0.25 |
| veto reason: short-odds away favourite 1.26 | 1 | 1 | 1.0 | 1 | 0.2591 |
| veto reason: short-odds away favourite 1.27 | 2 | 2 | 1.0 | 2 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.28 |
| contrast CAUTION: APPROVED_DONOR_PRICE | 1 | 1 | 1.0 | 1 | 0.452 |
| contrast CAUTION: BETEXPLORER_RESCUE | 15 | 8 | 0.533333 | 15 | -0.146 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 108 | 72 | 0.666667 | 108 | 0.072681 |
| contrast CAUTION: SOURCE_FALLBACK | 8 | 4 | 0.5 | 8 | -0.22 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 691 | 461 | 0.667149 | 582 | 0.017561 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 87 | 51 | 0.586207 | 24 | -0.039167 | 87 | 1.59941 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 131 | 90 | 0.687023 | 131 | 0.011298 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 19 | 11 | 0.578947 | 19 | 0.040526 | 0 | None |
| stale_quote (`stale_quote`) | 1 | 1 | 1.0 | 0 | None | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-24: Vis Pesaro vs Ravenna (Actual Score: **0-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.4065 -> 🟢 WON (Expected prob: 69.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 52.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: TransINVEST Vilnius vs Hegelmann Litauen (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 69.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Bangor vs Larne (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.3367 -> 🟢 WON (Expected prob: 68.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Sanfrecce Hiroshima vs Shimizu S-Pulse (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3891 -> 🟢 WON (Expected prob: 66.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Häcken vs Degerfors (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3906 -> 🟢 WON (Expected prob: 66.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: RB Leipzig vs Elversberg (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.4348 -> 🟢 WON (Expected prob: 66.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Spezia vs Latina (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.5405 -> 🔴 LOST (Expected prob: 66.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Arsenal vs Everton (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.4608 -> 🟢 WON (Expected prob: 65.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Como vs Sassuolo (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5319 -> 🟢 WON (Expected prob: 65.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Deportivo Madryn vs San Telmo (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.3745 -> 🟢 WON (Expected prob: 65.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Connah's Quay vs Llandudno (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.4237 -> 🟢 WON (Expected prob: 65.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Gil Vicente vs Porto (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.45 -> 🟢 WON (Expected prob: 65.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 58.0% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 52.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Shakhtar Donetsk vs Zorya Luhansk (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3937 -> 🔴 LOST (Expected prob: 64.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 0 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Hapoel Jerusalem vs Hapoel Tel Aviv (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.4464 -> 🟢 WON (Expected prob: 64.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 52.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Borussia Dortmund vs Eintracht Frankfurt (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.4785 -> 🟢 WON (Expected prob: 63.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Mladost Lučani vs Vojvodina (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.4695 -> 🔴 LOST (Expected prob: 63.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 58.0% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Palmeiras vs Bragantino (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5319 -> 🟢 WON (Expected prob: 61.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Club Ferro Carril Oeste vs Chaco For Ever (Actual Score: **0-3**)
- **1X2 Pick**: Selected `HOME` @ 1.4673 -> 🔴 LOST (Expected prob: 60.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Sarajevo vs Zeljeznicar (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5128 -> 🟢 WON (Expected prob: 60.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: CF Montréal vs Nashville SC (Actual Score: **0-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.6098 -> 🟢 WON (Expected prob: 59.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 58.0% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 52.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: NEOM SC vs Abha (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.56 -> 🟢 WON (Expected prob: 59.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Carrick Rangers vs Limavady United (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.5181 -> 🔴 LOST (Expected prob: 59.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Notts County vs Stockport County (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.578 -> 🔴 LOST (Expected prob: 59.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 58.0% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Queen's Park vs Dunfermline Athletic (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.5319 -> 🟢 WON (Expected prob: 59.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 58.0% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 52.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Eyüpspor vs Kasımpaşa (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.5587 -> 🟢 WON (Expected prob: 58.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 58.0% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 52.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Bristol Rovers vs Swindon Town (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5814 -> 🔴 LOST (Expected prob: 58.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 0 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Solihull Moors vs Carlisle United (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.5682 -> 🟢 WON (Expected prob: 58.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Aston Villa vs Manchester City (Actual Score: **2-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.6494 -> 🔴 LOST (Expected prob: 58.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Ironi Tiberias vs Maccabi Netanya (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.5988 -> 🔴 LOST (Expected prob: 57.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 58.0% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: O'Higgins vs Cobresal (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.6369 -> 🔴 LOST (Expected prob: 57.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: LDU Quito vs Macará (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.6536 -> 🔴 LOST (Expected prob: 57.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Raufoss vs Ranheim (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.7463 -> 🟢 WON (Expected prob: 56.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: KR Reykjavík vs Breidablik (Actual Score: **8-3**)
- **1X2 Pick**: Selected `HOME` @ 1.6211 -> 🟢 WON (Expected prob: 56.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 11 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 8 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Slough Town vs Dorking Wanderers (Actual Score: **1-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.6536 -> 🟢 WON (Expected prob: 56.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Chesterfield vs Crewe Alexandra (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.6135 -> 🟢 WON (Expected prob: 55.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Jeonnam Dragons vs Daegu (Actual Score: **2-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.6173 -> 🟢 WON (Expected prob: 55.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Almería vs Real Oviedo (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.6452 -> 🔴 LOST (Expected prob: 55.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Vasco da Gama vs Corinthians (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ 1.6849 -> 🟢 WON (Expected prob: 55.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: King's Lynn Town vs Southport (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.6289 -> 🔴 LOST (Expected prob: 55.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 0 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Barnet vs Oldham Athletic (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.6849 -> 🔴 LOST (Expected prob: 54.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Almagro vs Tristán Suárez (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.7042 -> 🔴 LOST (Expected prob: 54.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 58.0% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Pogoń Szczecin vs Radomiak Radom (Actual Score: **4-3**)
- **1X2 Pick**: Selected `HOME` @ 1.74 -> 🟢 WON (Expected prob: 53.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 7 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Chelsea vs Tottenham Hotspur (Actual Score: **0-2**)
- **1X2 Pick**: Selected `HOME` @ 1.7463 -> 🔴 LOST (Expected prob: 52.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Skalica vs Spartak Trnava (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.6452 -> 🔴 LOST (Expected prob: 52.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 58.0% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Saint-Étienne vs Nantes (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.6667 -> 🟢 WON (Expected prob: 52.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: DC United vs FC Cincinnati (Actual Score: **0-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.4032 -> 🔴 LOST (Expected prob: 71.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.2% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 59.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Borussia Dortmund vs Eintracht Frankfurt (Actual Score: **1-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.3534 -> 🔴 LOST (Expected prob: 71.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.2% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 59.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: FC Zürich vs FC Luzern (Actual Score: **2-1**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.3774 -> 🟢 WON (Expected prob: 71.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 59.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Atlanta United vs Chicago Fire (Actual Score: **2-3**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.4545 -> 🟢 WON (Expected prob: 69.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 59.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Como vs Sassuolo (Actual Score: **2-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.4405 -> 🔴 LOST (Expected prob: 68.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.2% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 59.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Columbus Crew vs Toronto FC (Actual Score: **4-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.4484 -> 🟢 WON (Expected prob: 67.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 59.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Reading vs Barnsley (Actual Score: **2-1**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.4525 -> 🟢 WON (Expected prob: 67.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 59.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Servette FC vs FC Vaduz (Actual Score: **2-1**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.4484 -> 🟢 WON (Expected prob: 67.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 59.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Orlando City SC vs New York City FC (Actual Score: **2-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.4202 -> 🟢 WON (Expected prob: 66.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 59.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Tokyo Verdy vs Avispa Fukuoka (Actual Score: **3-1**)
- **Over/Under 2.5 Pick**: Selected `UNDER` @ 1.4673 -> 🔴 LOST (Expected prob: 61.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 40.4% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-No**: expected 48.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 63.6% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Under 3.5 Goals**: expected n/a (Actual: 4 goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected n/a (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Over 0.5 Goals**: expected n/a (Actual: 3 home goals)
    - [🟢 HIT] **Match Over 1.5 Goals**: expected n/a (Actual: 4 goals)
    - [🔴 MISS] **Home Team Under 1.5 Goals**: expected n/a (Actual: 3 home goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected n/a (Actual: 1 away goals)

### 2026-10-24: Bucheon FC 1995 vs Gwangju FC (Actual Score: **0-3**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 2.0 -> 🟢 WON (Expected prob: 55.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 59.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 3 goals)

### 2026-10-24: Lazio vs Parma (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.4115 -> 🟢 WON (Expected prob: 79.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.5% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.9% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 77.3% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Pyramids FC vs El Merriekh Bentiu (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.03 -> 🟢 WON (Expected prob: 92.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: AEK Athens vs Panaitolikos (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 84.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Bodø / Glimt vs Vålerenga (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.16 -> 🔴 LOST (Expected prob: 81.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Djurgården vs Örgryte (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.1431 -> 🔴 LOST (Expected prob: 80.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Chongqing Tonglianglong FC vs Qingdao Hainiu (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3 -> 🟢 WON (Expected prob: 75.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Ponte Preta vs Fortaleza (Actual Score: **2-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.2427 -> 🔴 LOST (Expected prob: 75.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Atlético Madrid vs Deportivo La Coruña (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.2841 -> 🟢 WON (Expected prob: 74.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Buriram United vs Sisaket United (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ 1.22 -> 🔴 LOST (Expected prob: 73.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Ross County vs Airdrieonians (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.2591 -> 🟢 WON (Expected prob: 72.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: América de Cali vs Cúcuta Deportivo (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.2994 -> 🟢 WON (Expected prob: 70.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Crusaders vs Coleraine (Actual Score: **0-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.2591 -> 🟢 WON (Expected prob: 70.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 52.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Dunajská Streda vs Ružomberok (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 70.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Hamilton Academical vs East Fife (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.3012 -> 🟢 WON (Expected prob: 70.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Slovan Bratislava vs Banská Bystrica (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 69.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Wolverhampton Wanderers vs Watford (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.42 -> 🟢 WON (Expected prob: 68.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Brighton W vs West Ham W (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 68.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Huddersfield Town vs Wigan Athletic (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.304 -> 🟢 WON (Expected prob: 68.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Port FC vs Rayong (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.33 -> 🟢 WON (Expected prob: 68.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Livingston vs Arbroath (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3356 -> 🟢 WON (Expected prob: 67.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Boreham Wood vs Fylde (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 65.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Paredes vs Trofense (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 63.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: De Treffers vs Jong Sparta (Actual Score: **3-3**)
- **1X2 Pick**: Selected `HOME` @ 1.42 -> 🔴 LOST (Expected prob: 63.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Partick Thistle vs Stenhousemuir (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.4202 -> 🟢 WON (Expected prob: 62.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Quick Boys vs HSV Hoek (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.44 -> 🟢 WON (Expected prob: 62.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Philadelphia Union vs New England (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.5236 -> 🔴 LOST (Expected prob: 61.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Sport Huancayo vs Alianza Atlético (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.4878 -> 🟢 WON (Expected prob: 61.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Ratchaburi Mitrphol FC vs Chonburi FC (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.48 -> 🔴 LOST (Expected prob: 60.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Vejle Boldklub vs Aarhus Fremad (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 60.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 0 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Salisbury vs Dover Athletic (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.5435 -> 🔴 LOST (Expected prob: 60.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Al Duhail vs Lusail City (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.48 -> 🟢 WON (Expected prob: 60.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Changchun Yatai vs Meizhou Hakka (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.5714 -> 🟢 WON (Expected prob: 59.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Modena vs Cesena (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5495 -> 🟢 WON (Expected prob: 59.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Reading vs Barnsley (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.6173 -> 🟢 WON (Expected prob: 59.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: HamKam vs Rosenborg (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.63 -> 🟢 WON (Expected prob: 58.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 52.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Treviso vs Dolomiti Bellunesi (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.5556 -> 🟢 WON (Expected prob: 58.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Al Merreikh vs Horoya (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.53 -> 🟢 WON (Expected prob: 58.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Horsham vs Walton & Hersham (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 58.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: FC Utrecht vs PEC Zwolle (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.6024 -> 🔴 LOST (Expected prob: 58.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Columbus Crew vs Toronto (Actual Score: **4-2**)
- **1X2 Pick**: Selected `HOME` @ 1.5714 -> 🟢 WON (Expected prob: 58.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: BG Pathum United vs Singha Chiangrai United (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.55 -> 🟢 WON (Expected prob: 57.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Ebbsfleet United vs Maidenhead United (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5435 -> 🟢 WON (Expected prob: 57.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Hemel Hempstead Town vs AFC Totton (Actual Score: **1-3**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 57.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Loudoun United vs Brooklyn FC (Actual Score: **4-3**)
- **1X2 Pick**: Selected `HOME` @ 1.5682 -> 🟢 WON (Expected prob: 57.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 7 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: West Ham United vs Southampton (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ 1.73 -> 🔴 LOST (Expected prob: 56.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Teuta Durrës vs AF Elbasani (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.6 -> 🔴 LOST (Expected prob: 56.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 0 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Viktoria Köln vs Verl (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.6173 -> 🟢 WON (Expected prob: 56.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Kozakken Boys vs Barendrecht (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.6 -> 🔴 LOST (Expected prob: 56.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Necaxa vs Juárez (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.7463 -> 🔴 LOST (Expected prob: 55.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Under 4.5 Goals**: expected n/a (Actual: 2 goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected n/a (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected n/a (Actual: 1 home goals)
    - [🟢 HIT] **Match Under 3.5 Goals**: expected n/a (Actual: 2 goals)
    - [🔴 MISS] **Home Team Over 1.5 Goals**: expected n/a (Actual: 1 home goals)

### 2026-10-24: Southend United vs Halifax Town (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.6667 -> 🔴 LOST (Expected prob: 55.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Charleston Battery vs Indy Eleven (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.6024 -> 🟢 WON (Expected prob: 55.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Harrogate Town vs Sutton United (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.6711 -> 🟢 WON (Expected prob: 55.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Rayo Vallecano vs Elche (Actual Score: **0-3**)
- **1X2 Pick**: Selected `HOME` @ 1.813 -> 🔴 LOST (Expected prob: 54.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Heidenheim vs Energie Cottbus (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.6803 -> 🔴 LOST (Expected prob: 54.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Tigre vs Atlético Tucumán (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.6849 -> 🔴 LOST (Expected prob: 53.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Rijnsburgse Boys vs RKAV Volendam (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.66 -> 🔴 LOST (Expected prob: 53.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Alloa Athletic vs Queen of the South (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.7353 -> 🔴 LOST (Expected prob: 53.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Young Boys vs St. Gallen (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.7692 -> 🟢 WON (Expected prob: 53.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Folkestone Invicta vs Farnborough (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.7692 -> 🟢 WON (Expected prob: 53.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Sheffield United vs Derby County (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.85 -> 🔴 LOST (Expected prob: 53.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Nantong Zhiyun vs Shenzhen Juniors FC (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.8772 -> 🟢 WON (Expected prob: 53.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Dagenham & Redbridge vs Chesham United (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 53.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Hertha BSC vs DSC Arminia Bielefeld (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 53.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Magdeburg vs Karlsruher SC (Actual Score: **6-1**)
- **1X2 Pick**: Selected `HOME` @ 1.813 -> 🟢 WON (Expected prob: 53.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 7 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Scarborough Athletic vs Bedford Town (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.7813 -> 🔴 LOST (Expected prob: 52.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Seoul vs Gangwon (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.93 -> 🔴 LOST (Expected prob: 52.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Chapecoense vs Fluminense (Actual Score: **2-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.8333 -> 🔴 LOST (Expected prob: 52.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Kuressaare vs Paide (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 52.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 58.0% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 52.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Cremonese vs Juve Stabia (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ 1.8621 -> 🔴 LOST (Expected prob: 52.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Dalian Kuncheng City vs Guangxi Hengchen (Actual Score: **3-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.813 -> 🔴 LOST (Expected prob: 52.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: FC Augsburg vs FC Union Berlin (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.8696 -> 🔴 LOST (Expected prob: 52.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Wisła Kraków vs Raków Częstochowa (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.86 -> 🟢 WON (Expected prob: 52.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Pittsburgh Riverhounds vs Birmingham Legion (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.7937 -> 🟢 WON (Expected prob: 51.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Servette vs Vaduz (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.8475 -> 🟢 WON (Expected prob: 51.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Farnham Town vs Braintree Town (Actual Score: **6-0**)
- **1X2 Pick**: Selected `HOME` @ 1.7813 -> 🟢 WON (Expected prob: 51.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: GVVV vs Koninklijke HFC (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.75 -> 🟢 WON (Expected prob: 51.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Kalmar vs Brommapojkarna (Actual Score: **0-3**)
- **1X2 Pick**: Selected `HOME` @ 1.8264 -> 🔴 LOST (Expected prob: 51.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Macclesfield vs Hereford (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.885 -> 🔴 LOST (Expected prob: 51.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Falkirk vs Kilmarnock (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.8547 -> 🟢 WON (Expected prob: 50.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Wuhan Three Towns vs Shandong Taishan (Actual Score: **3-5**)
- **1X2 Pick**: Selected `AWAY` @ 1.9259 -> 🟢 WON (Expected prob: 50.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 8 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: AFC Wimbledon vs Wycombe Wanderers (Actual Score: **1-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.7937 -> 🔴 LOST (Expected prob: 50.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 58.0% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Shenzhen Peng City vs Shanghai Shenhua (Actual Score: **2-1**)
- **1X2 Pick**: Selected `AWAY` @ 1.92 -> 🔴 LOST (Expected prob: 50.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Savoia vs Cosenza (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.8621 -> 🔴 LOST (Expected prob: 50.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Cruzeiro vs Remo (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3846 -> 🟢 WON (Expected prob: 72.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.0% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 51.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.8% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: 1. FC Heidenheim vs Energie Cottbus (Actual Score: **1-1**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.2801 -> 🔴 LOST (Expected prob: 76.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.2% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 59.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected n/a (Actual: 1 away goals)
    - [🟢 HIT] **Match Under 4.5 Goals**: expected n/a (Actual: 2 goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected n/a (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected n/a (Actual: 2 goals)

### 2026-10-24: Rangers vs St. Johnstone (Actual Score: **4-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.4444 -> 🟢 WON (Expected prob: 65.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 59.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: HamKam vs Rosenborg BK (Actual Score: **0-3**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.55 -> 🟢 WON (Expected prob: 64.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 59.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 3 goals)

### 2026-10-24: Wisła Kraków vs Raków Częstochowa (Actual Score: **2-1**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.52 -> 🟢 WON (Expected prob: 63.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 59.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 3 goals)

### 2026-10-24: SC Paderborn 07 vs Hamburger SV (Actual Score: **1-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.6024 -> 🔴 LOST (Expected prob: 63.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.2% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 59.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Chelsea vs Tottenham Hotspur (Actual Score: **0-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.5181 -> 🔴 LOST (Expected prob: 62.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.2% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 59.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Aston Villa vs Manchester City (Actual Score: **2-1**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.5348 -> 🟢 WON (Expected prob: 62.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 59.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Club León vs CD Toluca (Actual Score: **1-1**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.5682 -> 🔴 LOST (Expected prob: 62.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.2% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 59.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: 1. FC Köln vs FC Schalke 04 (Actual Score: **0-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.6494 -> 🔴 LOST (Expected prob: 60.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.2% (Actual: 0 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 59.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: BK Häcken vs Degerfors IF (Actual Score: **4-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.56 -> 🟢 WON (Expected prob: 59.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 59.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 4 goals)

### 2026-10-24: Kalmar FF vs IF Brommapojkarna (Actual Score: **0-3**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.76 -> 🟢 WON (Expected prob: 59.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 59.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 3 goals)

### 2026-10-24: Leganés vs Mallorca (Actual Score: **1-1**)
- **Over/Under 2.5 Pick**: Selected `UNDER` @ 1.74 -> 🟢 WON (Expected prob: 59.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 40.4% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 48.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 63.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Aldershot Town vs Wealdstone (Actual Score: **0-1**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.6024 -> 🔴 LOST (Expected prob: 59.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.2% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 59.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Wolverhampton vs Watford (Actual Score: **1-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.62 -> 🔴 LOST (Expected prob: 58.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.2% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 59.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected n/a (Actual: 1 goals)

### 2026-10-24: Bristol Rovers vs Swindon Town (Actual Score: **0-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.6173 -> 🔴 LOST (Expected prob: 58.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.2% (Actual: 0 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 59.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Al-Kholood vs Al-Ettifaq (Actual Score: **0-3**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.66 -> 🟢 WON (Expected prob: 58.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 59.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 3 goals)

### 2026-10-24: Charleston Battery vs Indy Eleven (Actual Score: **1-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.6536 -> 🔴 LOST (Expected prob: 58.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.2% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 59.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Eastleigh vs Boston United (Actual Score: **4-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.6536 -> 🟢 WON (Expected prob: 57.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 59.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Neom SC vs Abha (Actual Score: **2-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.7 -> 🔴 LOST (Expected prob: 57.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.2% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 59.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🔴 MISS] **Match Over 2.5 Goals**: expected n/a (Actual: 2 goals)

### 2026-10-24: Valencia vs Villarreal (Actual Score: **1-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.7634 -> 🟢 WON (Expected prob: 57.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 59.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Falkirk FC vs Kilmarnock (Actual Score: **3-0**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.6623 -> 🟢 WON (Expected prob: 57.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 59.7% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Melbourne Victory vs Melbourne City (Actual Score: **1-1**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.8065 -> 🔴 LOST (Expected prob: 57.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.2% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 59.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 2.5 Goals**: expected n/a (Actual: 1 away goals)
    - [🟢 HIT] **Match Under 4.5 Goals**: expected n/a (Actual: 2 goals)
    - [🟢 HIT] **Away Team Over 0.5 Goals**: expected n/a (Actual: 1 away goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected n/a (Actual: 1 home goals)
    - [🔴 MISS] **Match Over 2.5 Goals**: expected n/a (Actual: 2 goals)

### 2026-10-24: Scunthorpe United vs Woking (Actual Score: **2-3**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.6536 -> 🟢 WON (Expected prob: 57.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 59.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: St. Mirren vs Dundee FC (Actual Score: **2-1**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.6536 -> 🟢 WON (Expected prob: 57.2%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 59.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Ulsan HD vs Pohang Steelers (Actual Score: **2-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.7576 -> 🟢 WON (Expected prob: 56.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 59.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Pogoń Szczecin vs Radomiak Radom (Actual Score: **4-3**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.63 -> 🟢 WON (Expected prob: 56.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 7 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 59.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 7 goals)

### 2026-10-24: Südtirol vs Sampdoria (Actual Score: **1-1**)
- **Over/Under 2.5 Pick**: Selected `UNDER` @ 1.7353 -> 🟢 WON (Expected prob: 56.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 40.4% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-No**: expected 48.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 63.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Harrogate Town vs Sutton United (Actual Score: **3-1**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.8696 -> 🟢 WON (Expected prob: 55.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.2% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 59.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Cagliari vs Bologna (Actual Score: **0-2**)
- **Over/Under 2.5 Pick**: Selected `UNDER` @ 1.6803 -> 🟢 WON (Expected prob: 55.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 40.4% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-No**: expected 48.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 63.6% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.8% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Sport Recife vs Criciuma (Actual Score: **2-1**)
- **1X2 Pick**: Selected `AWAY` @ 2.48 -> 🔴 LOST (Expected prob: 46.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 71.1% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 60.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: VfB Oldenburg vs HSC Hannover (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 74.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 51.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Oleksandria vs Probiy Horodenka (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 67.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.1% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 51.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.9% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Metalac GM vs Javor (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 66.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.5% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.5% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 71.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 62.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Greuther Furth II vs Schwaben Augsburg (Actual Score: **0-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 55.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.1% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 51.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.8% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.9% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Astoria Walldorf vs Hessen Kassel (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 53.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.1% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 51.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.8% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Kyzyl vs Zhar - Ulytau (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 73.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.5% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 50.9% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 77.3% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: SK Rapid vs Austria Lustenau (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 78.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Levadia vs Harju Jalgpallikool (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 72.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Girona vs Celta de Vigo II (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 69.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Östersunds FK vs United Nordic (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 61.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Tottenham W vs Arsenal W (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 60.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Víkingur Reykjavík vs Fram (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 60.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Esbjerg vs Fredericia (Actual Score: **2-1**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🔴 LOST (Expected prob: 59.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Partizan vs Čukarički (Actual Score: **0-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 57.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Hampton & Richmond vs Truro City (Actual Score: **3-4**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 56.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 7 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Gimpo vs Gimhae City (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 54.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Foshan Nashi FC vs Nanjing City (Actual Score: **2-5**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 54.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 7 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 5 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Teplice vs SK Artis Brno (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 54.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 0 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: FSV Mainz 05 vs Werder Bremen (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 54.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Estrela Amadora vs Casa Pia (Actual Score: **0-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 53.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Colegiales vs Atlético Rafaela (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 53.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Antwerp vs Sporting Charleroi (Actual Score: **3-0**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🔴 LOST (Expected prob: 52.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 52.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Zalaegerszegi TE vs Várda SE (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 52.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: New York RB vs Inter Miami (Actual Score: **2-0**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🔴 LOST (Expected prob: 50.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 58.0% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 52.7% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: SK Slavia Praha vs Mladá Boleslav (Actual Score: **1-1**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ n/a -> 🔴 LOST (Expected prob: 71.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.2% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 59.7% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.4% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 58.9% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: ES Sétif vs CR Temouchent (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🔴 LOST (Expected prob: 63.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Epitsentr Dunayivtsi vs Metalist 1925 Kharkiv (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.55 -> 🟢 WON (Expected prob: 57.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.0% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.7% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 78.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 63.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Varaždin vs Slaven Koprivnica (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.6 -> 🔴 LOST (Expected prob: 56.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: KSC Lokeren vs Jong Gent (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.6 -> 🟢 WON (Expected prob: 55.9%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.6% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-24: Slavia Praha vs Mladá Boleslav (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.2451 -> 🔴 LOST (Expected prob: 72.8%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.3% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.6% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| CANCELLED | 1 |
| POSTPONED | 5 |
- 2026-09-26 `POSTPONED` `SKIPPED_VETO` — Crawley Town vs Barnet (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-10-03 `CANCELLED` `CAUTION` — Sri Lanka vs Djibouti (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-10-23 `POSTPONED` `CAUTION` — Gateshead vs Tamworth (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-10-23 `POSTPONED` `SKIPPED_VETO` — Holywell vs Penybont (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-10-24 `POSTPONED` `CAUTION` — Glentoran vs Ballymena United (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-10-24 `POSTPONED` `CAUTION` — Slovan Liberec vs Baník Ostrava (source_status:scoutingstats); excluded from win/loss/ROI

## Rescheduled Fixture Examples

- 2026-09-26 `CAUTION` `2way-unanimous avg_p>=60` — Vila Nova FC vs Londrina -> HOME @ 1.58 (rescheduled → 2026-09-25; actual Vila Nova 2-0 Londrina [home])
- 2026-09-27 `CERTIFIED_CLEAN` `ml-meta avg_p>=65` — Pachuca W vs Santos Laguna W -> HOME @ 1.19 (rescheduled → 2026-09-26; actual Pachuca (w) 4-1 Santos Laguna (w) [home])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Tampa Bay Rowdies vs Miami FC -> HOME @ None (rescheduled → 2026-10-03; actual Tampa Bay Rowdies 1-2 Miami FC [away])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Brooklyn vs Rhode Island FC -> AWAY @ None (rescheduled → 2026-10-03; actual Brooklyn 1-3 Rhode Island [away])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Kano Pillars FC vs Sporting Lagos -> HOME @ None (rescheduled → 2026-10-03; actual Kano Pillars 1-1 Sporting Lagos [draw])
- 2026-10-18 `SKIPPED_VETO` `unanimous[bzzoiro+vitibet] avg_p>=70` — Hartford Athletic vs Brooklyn -> HOME @ 1.44 (rescheduled → 2026-10-17; actual Hartford Athletic 2-3 Brooklyn [away])
- 2026-10-21 `WATCHLIST_UNCORROBORATED_PRICE` `1x2 single[scoutingstats] avg_p>=50` — Cerro Porteño vs Sportivo Ameliano -> HOME @ 1.65 (rescheduled → 2026-10-18; actual Cerro Porteno 2-2 Sportivo Ameliano [draw])

## Pending / Unmatched Result Examples

- 2026-09-27 `CAUTION` `2way-unanimous avg_p>=60` — Milevsko vs Spartak Sobeslav -> AWAY @ 1.57 (pending_or_unmatched_result); keys=['milevsko']/['spartakso']
- 2026-09-27 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — Polanka nad Odrou vs Frydek-Mistek -> AWAY @ 1.48 (pending_or_unmatched_result); keys=['polankana']/['frydekmis']
- 2026-09-27 `SKIPPED_VETO` `2way-unanimous avg_p>=60` — Brommapojkarna W vs Malmö FF W -> AWAY @ 1.4 (pending_or_unmatched_result); keys=['brommapoj']/['malmoff', 'malmoffww']
- 2026-09-27 `SKIPPED_VETO` `ml-meta avg_p>=55` — Plateau United vs Inter Lagos -> HOME @ 1.33 (pending_or_unmatched_result); keys=['plateauun']/['interlago']
- 2026-10-03 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Rheindorf Altach II vs Hohenems -> AWAY @ None (pending_or_unmatched_result); keys=['rheindorf']/['hohenems']
- 2026-10-03 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Kufstein vs Imst -> AWAY @ None (pending_or_unmatched_result); keys=['kufstein']/['imst']
- 2026-10-09 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=70` — Real Cundinamarca vs Real Santander -> HOME @ None (pending_or_unmatched_result); keys=['cundinama']/['santander']
- 2026-10-11 `SKIPPED_VETO` `ml-meta avg_p>=60` — Atletico Nacional vs Deportivo Pasto -> HOME @ 2.1 (pending_or_unmatched_result); keys=['nacional']/['pasto']
- 2026-10-11 `SKIPPED_VETO` `unanimous[betclan+vitibet] avg_p>=70` — Ranger's vs Carroi -> HOME @ None (pending_or_unmatched_result); keys=['rangers']/['carroi']
- 2026-10-18 `SKIPPED_VETO` `unanimous[betclan+vitibet] avg_p>=70` — Wolfurt vs Schwaz -> AWAY @ None (pending_or_unmatched_result); keys=['wolfurt']/['schwaz']
- 2026-10-18 `SKIPPED_VETO` `unanimous[betclan+vitibet] avg_p>=70` — Rheindorf Altach II vs Imst -> AWAY @ None (pending_or_unmatched_result); keys=['rheindorf']/['imst']
- 2026-10-21 `CAUTION` `1x2 single[scoutingstats] avg_p>=50` — Sporting JAX vs Louisville City -> AWAY @ 1.37 (pending_or_unmatched_result); keys=['jax']/['louisvill']
- 2026-10-21 `WATCHLIST_UNCORROBORATED_PRICE` `1x2 single[scoutingstats] avg_p>=50` — Olimpia vs 2 de Mayo -> HOME @ 1.44 (pending_or_unmatched_result); keys=['olimpia']/['demayo']
- 2026-10-21 `WATCHLIST_UNKNOWN_CTX` `1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=50` — Sporting CP vs LASK Linz -> HOME @ 1.2101 (pending_or_unmatched_result); keys=['cp', 'lisbon']/['lasklinz']
- 2026-10-22 `SKIPPED_VETO` `1x2 unanimous[vitibet+zulubet] avg_p>=50` — Sporting JAX vs Louisville City FC -> AWAY @ 1.27 (pending_or_unmatched_result); keys=['jax']/['louisvill']
- 2026-10-23 `SKIPPED_VETO` `1x2 single[scoutingstats] avg_p>=50` — Operário PR vs Athletic Club -> HOME @ None (pending_or_unmatched_result); keys=['operariop']/[]
- 2026-10-24 `SKIPPED_VETO` `1x2 single[scoutingstats] avg_p>=50` — Tampa Bay Rowdies vs Sporting JAX -> HOME @ None (pending_or_unmatched_result); keys=['tampabayr']/['jax']

## Ambiguous result examples

- 2026-10-21 `SKIPPED_VETO` `1x2 single[scoutingstats] avg_p>=50` — Guadalajara vs Necaxa (ambiguous_alias_result)
