# Edge Factory — Recent picks audit (2026-10-07 to 2026-11-05)

## Overall

- archived pick rows: 1082
- archived pick dates: 30
- immutable morning-baseline rows: 971
- late-slate additions (regular-ledger rows not in the morning baseline): 111, of which on days whose regular ledger was rewritten: 83
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 27
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 1002
- eligible prior picks: 1023
- pending/unmatched result picks: 14
- rescheduled result picks (settled ±3d): 3
- voided postponed/cancelled/abandoned events: 6
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 1
- ambiguous result picks: 1
- wins: 676
- hit rate: +67.5% (wins/settled: 676/1002)
- priced picks: 814
- ROI: +4.4% (P&L / 814 priced picks)

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-11-05
- same-day rows excluded: 33

## Rule performance — since activation vs last 30 days

Primary view: recorded post-activation PICK ROWS, including vetoed/watchlist rows; not placed bets or acca returns. No retrospective rule replay. Missing activation dates remain unavailable. Missing archive days mean partial history, not zero activity. Missing/unreadable files are counted as archive gaps. Empty recorded cards count as available days. Current registry status is not historical status on each pick date.

Last 30 days: 2026-10-07 to 2026-11-05; same-day inclusion: False (local cutoff 2026-11-05). The 30-priced-row provisional flag is reporting only, not an activation gate. Priced ROI can include fallback/quarantined odds; provenance is shown separately. Historical ml-meta is not the live ML ENH selector.

| Rule | Activation / current status | Since activation | Last 30 days | Archive days: since / recent | Stored key |
| --- | --- | --- | --- | --- | --- |
| 1x2 single[scoutingstats] avg_p>=65 | 2026-10-25 / benched | ROI +0.1%; hit 80.3% (110/137); 106 priced; coverage 77.4% | ROI +0.1%; hit 80.3% (110/137); 106 priced; coverage 77.4% | 11/11 / 29/29 | pfc_fdade2e70df4d4bb78a8cd6e |
| ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55 | 2026-10-23 / benched | ROI -2.0%; hit 61.9% (52/84); 79 priced; coverage 94.0% | ROI -2.0%; hit 61.9% (52/84); 79 priced; coverage 94.0% | 13/13 / 29/29 | pfc_27e0f725859bc708f95c58a3 |
| 1x2 single[scoutingstats] avg_p>=50 | 2026-10-20 / benched | ROI -5.1%; hit 60.7% (150/247); 196 priced; coverage 79.4% | ROI -5.1%; hit 60.7% (150/247); 196 priced; coverage 79.4% | 16/16 / 29/29 | pfc_439097cb9bb700e9996c0b07 |
| 1x2 single[zulubet] avg_p>=50 | 2026-10-20 / benched | ROI +90.0%; hit 50.0% (2/4); 2 priced; coverage 50.0%; provisional | ROI +90.0%; hit 50.0% (2/4); 2 priced; coverage 50.0%; provisional | 16/16 / 29/29 | pfc_4cf3df8552488297d7ccf526 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=0 | 2026-11-02 / certified | ROI +73.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | ROI +73.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | 3/3 / 29/29 | pfc_642ac9053223500b638e3451 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=35 | 2026-11-03 / certified | ROI +65.1%; hit 76.2% (16/21); 19 priced; coverage 90.5%; provisional | ROI +65.1%; hit 76.2% (16/21); 19 priced; coverage 90.5%; provisional | 2/2 / 29/29 | pfc_f56fe4a2759e9b17b9bdb116 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=60 | 2026-11-02 / certified | ROI +56.3%; hit 100.0% (3/3); 3 priced; coverage 100.0%; provisional | ROI +56.3%; hit 100.0% (3/3); 3 priced; coverage 100.0%; provisional | 3/3 / 29/29 | pfc_54fcf87604b73b87ee6c0a90 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=0 | 2026-10-20 / benched | ROI +55.2%; hit 75.0% (3/4); 4 priced; coverage 100.0%; provisional | ROI +55.2%; hit 75.0% (3/4); 4 priced; coverage 100.0%; provisional | 16/16 / 29/29 | pfc_0ad08cd1b2e75a2c9051189e |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=40 | 2026-11-03 / certified | ROI +53.7%; hit 100.0% (4/4); 4 priced; coverage 100.0%; provisional | ROI +53.7%; hit 100.0% (4/4); 4 priced; coverage 100.0%; provisional | 2/2 / 29/29 | pfc_a7ba6711aeb15b9804a94f06 |
| 1x2 unanimous[statarea+zulubet] avg_p>=40 | 2026-10-20 / benched | ROI +44.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | ROI +44.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | 16/16 / 29/29 | pfc_5208b9e15194a691590430ad |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35 | 2026-10-31 / certified | ROI +41.6%; hit 75.0% (3/4); 4 priced; coverage 100.0%; provisional | ROI -0.3%; hit 54.8% (23/42); 40 priced; coverage 95.2% | 5/5 / 29/29 | pfc_73b036a8ee8dd5a4dea48134 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=50 | 2026-10-20 / benched | ROI +34.6%; hit 81.8% (9/11); 5 priced; coverage 45.5%; provisional | ROI +34.6%; hit 81.8% (9/11); 5 priced; coverage 45.5%; provisional | 16/16 / 29/29 | pfc_234f16641d9893e8ec2a01f0 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=0 | 2026-11-03 / certified | ROI +33.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | ROI +33.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | 2/2 / 29/29 | pfc_cddf4106a3d45b6e455d8c73 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=50 | 2026-10-20 / benched | ROI +16.5%; hit 50.0% (1/2); 2 priced; coverage 100.0%; provisional | ROI +16.5%; hit 50.0% (1/2); 2 priced; coverage 100.0%; provisional | 16/16 / 29/29 | pfc_0b290b623e2a54ea7df3006c |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=40 | 2026-11-01 / certified | ROI +15.5%; hit 58.3% (7/12); 10 priced; coverage 83.3%; provisional | ROI +15.5%; hit 58.3% (7/12); 10 priced; coverage 83.3%; provisional | 4/4 / 29/29 | pfc_226efd387e217a9d58a11f79 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=60 | 2026-10-25 / benched | ROI +14.9%; hit 66.7% (6/9); 8 priced; coverage 88.9%; provisional | ROI +14.9%; hit 66.7% (6/9); 8 priced; coverage 88.9%; provisional | 11/11 / 29/29 | pfc_5904b1fc7050646e6321090c |
| 1x2 single[zulubet] avg_p>=55 | 2026-10-20 / certified | ROI +13.7%; hit 67.9% (19/28); 13 priced; coverage 46.4%; provisional | ROI +13.7%; hit 67.9% (19/28); 13 priced; coverage 46.4%; provisional | 16/16 / 29/29 | pfc_1607fec83282d02c5254c2bf |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 | 2026-10-20 / benched | ROI +11.1%; hit 57.1% (4/7); 7 priced; coverage 100.0%; provisional | ROI +11.1%; hit 57.1% (4/7); 7 priced; coverage 100.0%; provisional | 16/16 / 29/29 | pfc_4a1f2bb2278d13c8189148d0 |
| 1x2 single[scoutingstats] avg_p>=60 | 2026-10-20 / benched | ROI +9.7%; hit 75.0% (3/4); 4 priced; coverage 100.0%; provisional | ROI +9.7%; hit 75.0% (3/4); 4 priced; coverage 100.0%; provisional | 16/16 / 29/29 | pfc_0f100c9da356ed1c05d9c642 |
| ou_2.5 unanimous[scoutingstats+statarea] avg_p>=65 | 2026-11-02 / certified | ROI +8.9%; hit 77.8% (14/18); 17 priced; coverage 94.4%; provisional | ROI +8.9%; hit 77.8% (14/18); 17 priced; coverage 94.4%; provisional | 3/3 / 29/29 | pfc_4e8ef1faa47bce63a119fb43 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=50 | 2026-10-26 / candidate | ROI -3.3%; hit 66.7% (2/3); 2 priced; coverage 66.7%; provisional | ROI -3.3%; hit 66.7% (2/3); 2 priced; coverage 66.7%; provisional | 10/10 / 29/29 | pfc_444d408c4ccd3a4bf4fb020c |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=40 | 2026-10-21 / benched | ROI -17.4%; hit 38.5% (5/13); 12 priced; coverage 92.3%; provisional | ROI -17.4%; hit 38.5% (5/13); 12 priced; coverage 92.3%; provisional | 15/15 / 29/29 | pfc_d94d447efe0742440e953722 |
| 1x2 unanimous[statarea+zulubet] avg_p>=55 | 2026-10-21 / benched | ROI -34.5%; hit 33.3% (1/3); 2 priced; coverage 66.7%; provisional | ROI -34.5%; hit 33.3% (1/3); 2 priced; coverage 66.7%; provisional | 15/15 / 29/29 | pfc_5a9d3d3426ee7a4e63461d75 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=55 | 2026-10-20 / benched | ROI -100.0%; hit 50.0% (1/2); 1 priced; coverage 50.0%; provisional | ROI -100.0%; hit 50.0% (1/2); 1 priced; coverage 50.0%; provisional | 16/16 / 29/29 | pfc_2bd498a3472b7bbd71982ece |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 | 2026-10-20 / benched | ROI -100.0%; hit 0.0% (0/1); 1 priced; coverage 100.0%; provisional | ROI -100.0%; hit 0.0% (0/1); 1 priced; coverage 100.0%; provisional | 16/16 / 29/29 | pfc_3bfaf30507905754f7faab2a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=45 | 2026-10-27 / benched | ROI -100.0%; hit 0.0% (0/2); 2 priced; coverage 100.0%; provisional | ROI +16.3%; hit 63.6% (7/11); 9 priced; coverage 81.8%; provisional | 9/9 / 29/29 | pfc_b011652ec3e473fbc0afbb6a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=40 | 2026-11-03 / certified | ROI -100.0%; hit 75.0% (3/4); 1 priced; coverage 25.0%; provisional | ROI -100.0%; hit 75.0% (3/4); 1 priced; coverage 25.0%; provisional | 2/2 / 29/29 | pfc_c7c9572806b564198f651cee |
| 2way-unanimous avg_p>=70 | unavailable / unavailable | unavailable | ROI +10.0%; hit 80.0% (16/20); 13 priced; coverage 65.0%; provisional | unavailable / 29/29 | 2way-unanimous avg_p>=70 |
| ml-meta avg_p>=55 | unavailable / unavailable | unavailable | ROI +24.0%; hit 71.1% (59/83); 63 priced; coverage 75.9% | unavailable / 29/29 | ml-meta avg_p>=55 |
| ml-meta avg_p>=60 | unavailable / unavailable | unavailable | ROI -3.5%; hit 59.9% (82/137); 121 priced; coverage 88.3% | unavailable / 29/29 | ml-meta avg_p>=60 |
| ml-meta avg_p>=65 | unavailable / unavailable | unavailable | ROI -14.7%; hit 72.7% (8/11); 6 priced; coverage 54.5%; provisional | unavailable / 29/29 | ml-meta avg_p>=65 |
| ml-meta avg_p>=80 | unavailable / unavailable | unavailable | ROI +10.3%; hit 100.0% (3/3); 3 priced; coverage 100.0%; provisional | unavailable / 29/29 | ml-meta avg_p>=80 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=0 | 2026-11-03 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 2/2 / 29/29 | pfc_0187397f26c1f84f6c3a9883 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=35 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_054448b499623dd39b072b38 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=45 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_0aed63f3d04b46330958121d |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=45 | 2026-10-30 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 6/6 / 29/29 | pfc_144c01b1aa366b88f9c4083a |
| 1x2 single[zulubet] avg_p>=45 | 2026-10-20 / benched | ROI unavailable; hit 0.0% (0/1); 0 priced; coverage 0.0%; provisional | ROI unavailable; hit 0.0% (0/1); 0 priced; coverage 0.0%; provisional | 16/16 / 29/29 | pfc_14ee12458803822df3013bcd |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=55 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_1ba3ab3c75e6f3a9680ae43c |
| 1x2 single[zulubet] avg_p>=40 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_1e9cfc6500aaac77afa1eaf9 |
| 1x2 unanimous[statarea+zulubet] avg_p>=35 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_3072388544a60552346bd162 |
| 1x2 single[zulubet] avg_p>=60 | 2026-10-20 / benched | ROI unavailable; hit 100.0% (1/1); 0 priced; coverage 0.0%; provisional | ROI unavailable; hit 100.0% (1/1); 0 priced; coverage 0.0%; provisional | 16/16 / 29/29 | pfc_35f7e50bf23db96c2d3dd59d |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=35 | 2026-11-04 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 1/1 / 29/29 | pfc_37f18dce9f6de45ee38e4944 |
| 1x2 single[zulubet] avg_p>=0 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_3dc0fa6511953bf09bc4c845 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=50 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_3fbabd0ade3f89853e43fb10 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=60 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_40b163633fc01fd0ff7d0ef1 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=40 | 2026-11-03 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 2/2 / 29/29 | pfc_48e25c370ae15b7d58d6b0d8 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=55 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_4e2583010bf805466e33c2d0 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=0 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_4f2df06575151e798727a6b0 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=55 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_527524a94e98cff9740d499c |
| 1x2 single[zulubet] avg_p>=65 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_5954379f3a12700edcfd8387 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=50 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_5f861bad9f49ebf6d6fe2c16 |
| 1x2 single[zulubet] avg_p>=35 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_61cb1dd2a3157c4231070cdb |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=35 | 2026-11-02 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 3/3 / 29/29 | pfc_66a32773b3535996c572d351 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=40 | 2026-11-04 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 1/1 / 29/29 | pfc_69dd4c8623d4d22d840da318 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=40 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_6cd236448d9fd967f8dcb591 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=0 | 2026-10-24 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_754f7247e83f901ae415b35f |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=35 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_7d20e19c2c26174fa21e9e86 |
| 1x2 unanimous[statarea+zulubet] avg_p>=45 | 2026-10-21 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 15/15 / 29/29 | pfc_7eb24434123da46374442290 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=45 | 2026-11-05 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 0/0 / 29/29 | pfc_84cede54e10853cd914d57c5 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=0 | 2026-11-04 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 1/1 / 29/29 | pfc_8e39a2c5719c5a609c077afd |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=0 | 2026-10-31 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 5/5 / 29/29 | pfc_92ab281aa7c2173e7502ba49 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=45 | 2026-10-24 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_9ae5a305a703bca83fd321b3 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=35 | 2026-11-03 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 2/2 / 29/29 | pfc_a3afbb848e0c474b683b450f |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=45 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_a460a0e9dcb1f980cde169c0 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=35 | 2026-10-24 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_a8e99ebc0016f0d0bb95aa70 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=60 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_a90a9b922d2318a2446434ce |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=35 | 2026-11-03 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 2/2 / 29/29 | pfc_ad11db4313c86de27efdde5a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=0 | 2026-11-03 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 2/2 / 29/29 | pfc_ad177634c86053c1c32b77cd |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=35 | 2026-10-30 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 6/6 / 29/29 | pfc_adb24b31e9ca43c42506156a |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=40 | 2026-11-05 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 0/0 / 29/29 | pfc_af020bcd1589e288dccb8d3e |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=50 | 2026-10-30 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 6/6 / 29/29 | pfc_afdf26c0a105a0f5e6ffff27 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=50 | 2026-11-03 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 2/2 / 29/29 | pfc_b0b7a0c1932e3636d2b485d6 |
| 1x2 unanimous[statarea+zulubet] avg_p>=0 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_b11e22bfdd27d85fad78ba74 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=0 | 2026-11-01 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 4/4 / 29/29 | pfc_b4407145af67d2f93e48f0ef |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=40 | 2026-10-30 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 6/6 / 29/29 | pfc_b9aa429be62178cc76b1ca8d |
| ou_3.5 unanimous[scoutingstats+statarea] avg_p>=70 | 2026-10-25 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 11/11 / 29/29 | pfc_bdce95a736d6cc8667f7ac31 |
| 1x2 unanimous[statarea+zulubet] avg_p>=50 | 2026-10-21 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 15/15 / 29/29 | pfc_c83d885867c9025a351b9b8c |
| 1x2 single[zulubet] avg_p>=70 | 2026-10-20 / benched | ROI unavailable; hit 100.0% (1/1); 0 priced; coverage 0.0%; provisional | ROI unavailable; hit 100.0% (1/1); 0 priced; coverage 0.0%; provisional | 16/16 / 29/29 | pfc_c8cbcf76ea758fd6de596ae1 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=40 | 2026-11-02 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 3/3 / 29/29 | pfc_cd84fb2c3ed889c0ae9eb89e |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=55 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_d17123b85e11155f22e40051 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=35 | 2026-11-01 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 4/4 / 29/29 | pfc_d5c311b6e2f37443e3501556 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=45 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_e25602082a90cb64fb9c5451 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=45 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_e37e7d70a4d046d7a07da0a4 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=40 | 2026-11-04 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 1/1 / 29/29 | pfc_e5c10af025fc5071367c9b47 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=45 | 2026-11-03 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 2/2 / 29/29 | pfc_ed44334de1c8307f22b510ab |
| ou_2.5 unanimous[scoutingstats+statarea] avg_p>=60 | 2026-11-05 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 0/0 / 29/29 | pfc_ee214d4f2f00846fa78f56e3 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=55 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_f2b2a2e84093abe72bbc01c0 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=50 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_f51b5fdaf32bcca063f4b2cc |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=50 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 16/16 / 29/29 | pfc_fb2e721d2bb8a41fe9fa3713 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=55 | 2026-11-04 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 1/1 / 29/29 | pfc_fbf508b9c62bae8f281bb6e1 |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=0 | 2026-10-30 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 6/6 / 29/29 | pfc_fc7adf360790baec2b1ce044 |
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
| 1x2 single[scoutingstats] avg_p>=65 | Since activation | NAMED_BOOKMAKER_PRICE: 94/94; SCOUTINGSTATS_SOLE: 12/12; SUSPECT_ALIAS_FUZZY: 31/0 | NONE: 94/94; alias_fuzzy: 31/0; scoutingstats_sole_source: 12/12 | pfc_fdade2e70df4d4bb78a8cd6e |
| 1x2 single[scoutingstats] avg_p>=65 | Last 30 days | NAMED_BOOKMAKER_PRICE: 94/94; SCOUTINGSTATS_SOLE: 12/12; SUSPECT_ALIAS_FUZZY: 31/0 | NONE: 94/94; alias_fuzzy: 31/0; scoutingstats_sole_source: 12/12 | pfc_fdade2e70df4d4bb78a8cd6e |
| ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55 | Since activation | NAMED_BOOKMAKER_PRICE: 75/75; SCOUTINGSTATS_SOLE: 4/4; SUSPECT_ALIAS_FUZZY: 5/0 | NONE: 75/75; alias_fuzzy: 5/0; scoutingstats_sole_source: 4/4 | pfc_27e0f725859bc708f95c58a3 |
| ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55 | Last 30 days | NAMED_BOOKMAKER_PRICE: 75/75; SCOUTINGSTATS_SOLE: 4/4; SUSPECT_ALIAS_FUZZY: 5/0 | NONE: 75/75; alias_fuzzy: 5/0; scoutingstats_sole_source: 4/4 | pfc_27e0f725859bc708f95c58a3 |
| 1x2 single[scoutingstats] avg_p>=50 | Since activation | NAMED_BOOKMAKER_PRICE: 168/168; SCOUTINGSTATS_SOLE: 28/28; SUSPECT_ALIAS_FUZZY: 51/0 | NONE: 168/168; alias_fuzzy: 51/0; scoutingstats_sole_source: 28/28 | pfc_439097cb9bb700e9996c0b07 |
| 1x2 single[scoutingstats] avg_p>=50 | Last 30 days | NAMED_BOOKMAKER_PRICE: 168/168; SCOUTINGSTATS_SOLE: 28/28; SUSPECT_ALIAS_FUZZY: 51/0 | NONE: 168/168; alias_fuzzy: 51/0; scoutingstats_sole_source: 28/28 | pfc_439097cb9bb700e9996c0b07 |
| 1x2 single[zulubet] avg_p>=50 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1; SCOUTINGSTATS_SOLE: 1/1; UNMATCHED: 2/0 | NONE: 3/1; scoutingstats_sole_source: 1/1 | pfc_4cf3df8552488297d7ccf526 |
| 1x2 single[zulubet] avg_p>=50 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1; SCOUTINGSTATS_SOLE: 1/1; UNMATCHED: 2/0 | NONE: 3/1; scoutingstats_sole_source: 1/1 | pfc_4cf3df8552488297d7ccf526 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=0 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_642ac9053223500b638e3451 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=0 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_642ac9053223500b638e3451 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=35 | Since activation | NAMED_BOOKMAKER_PRICE: 17/17; SCOUTINGSTATS_SOLE: 2/2; SUSPECT_ALIAS_FUZZY: 2/0 | NONE: 17/17; alias_fuzzy: 2/0; scoutingstats_sole_source: 2/2 | pfc_f56fe4a2759e9b17b9bdb116 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=35 | Last 30 days | NAMED_BOOKMAKER_PRICE: 17/17; SCOUTINGSTATS_SOLE: 2/2; SUSPECT_ALIAS_FUZZY: 2/0 | NONE: 17/17; alias_fuzzy: 2/0; scoutingstats_sole_source: 2/2 | pfc_f56fe4a2759e9b17b9bdb116 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=60 | Since activation | APPROVED_DONOR_PRICE: 1/1; NAMED_BOOKMAKER_PRICE: 2/2 | NONE: 3/3 | pfc_54fcf87604b73b87ee6c0a90 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=60 | Last 30 days | APPROVED_DONOR_PRICE: 1/1; NAMED_BOOKMAKER_PRICE: 2/2 | NONE: 3/3 | pfc_54fcf87604b73b87ee6c0a90 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=0 | Since activation | NAMED_BOOKMAKER_PRICE: 4/4 | NONE: 4/4 | pfc_0ad08cd1b2e75a2c9051189e |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=0 | Last 30 days | NAMED_BOOKMAKER_PRICE: 4/4 | NONE: 4/4 | pfc_0ad08cd1b2e75a2c9051189e |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=40 | Since activation | NAMED_BOOKMAKER_PRICE: 4/4 | NONE: 4/4 | pfc_a7ba6711aeb15b9804a94f06 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=40 | Last 30 days | NAMED_BOOKMAKER_PRICE: 4/4 | NONE: 4/4 | pfc_a7ba6711aeb15b9804a94f06 |
| 1x2 unanimous[statarea+zulubet] avg_p>=40 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_5208b9e15194a691590430ad |
| 1x2 unanimous[statarea+zulubet] avg_p>=40 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_5208b9e15194a691590430ad |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35 | Since activation | NAMED_BOOKMAKER_PRICE: 3/3; SCOUTINGSTATS_SOLE: 1/1 | NONE: 3/3; scoutingstats_sole_source: 1/1 | pfc_73b036a8ee8dd5a4dea48134 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35 | Last 30 days | NAMED_BOOKMAKER_PRICE: 38/38; SCOUTINGSTATS_SOLE: 2/2; SUSPECT_ALIAS_FUZZY: 2/0 | NONE: 38/38; alias_fuzzy: 2/0; scoutingstats_sole_source: 2/2 | pfc_73b036a8ee8dd5a4dea48134 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=50 | Since activation | NAMED_BOOKMAKER_PRICE: 5/5; SUSPECT_ALIAS_FUZZY: 1/0; UNMATCHED: 5/0 | NONE: 10/5; alias_fuzzy: 1/0 | pfc_234f16641d9893e8ec2a01f0 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=50 | Last 30 days | NAMED_BOOKMAKER_PRICE: 5/5; SUSPECT_ALIAS_FUZZY: 1/0; UNMATCHED: 5/0 | NONE: 10/5; alias_fuzzy: 1/0 | pfc_234f16641d9893e8ec2a01f0 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=0 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_cddf4106a3d45b6e455d8c73 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=0 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_cddf4106a3d45b6e455d8c73 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=50 | Since activation | NAMED_BOOKMAKER_PRICE: 2/2 | NONE: 2/2 | pfc_0b290b623e2a54ea7df3006c |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=50 | Last 30 days | NAMED_BOOKMAKER_PRICE: 2/2 | NONE: 2/2 | pfc_0b290b623e2a54ea7df3006c |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=40 | Since activation | NAMED_BOOKMAKER_PRICE: 8/8; SCOUTINGSTATS_SOLE: 2/2; SUSPECT_ALIAS_FUZZY: 2/0 | NONE: 8/8; alias_fuzzy: 2/0; scoutingstats_sole_source: 2/2 | pfc_226efd387e217a9d58a11f79 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=40 | Last 30 days | NAMED_BOOKMAKER_PRICE: 8/8; SCOUTINGSTATS_SOLE: 2/2; SUSPECT_ALIAS_FUZZY: 2/0 | NONE: 8/8; alias_fuzzy: 2/0; scoutingstats_sole_source: 2/2 | pfc_226efd387e217a9d58a11f79 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=60 | Since activation | NAMED_BOOKMAKER_PRICE: 8/8; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 8/8; alias_fuzzy: 1/0 | pfc_5904b1fc7050646e6321090c |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=60 | Last 30 days | NAMED_BOOKMAKER_PRICE: 8/8; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 8/8; alias_fuzzy: 1/0 | pfc_5904b1fc7050646e6321090c |
| 1x2 single[zulubet] avg_p>=55 | Since activation | NAMED_BOOKMAKER_PRICE: 13/13; SUSPECT_ALIAS_FUZZY: 1/0; UNMATCHED: 14/0 | NONE: 27/13; alias_fuzzy: 1/0 | pfc_1607fec83282d02c5254c2bf |
| 1x2 single[zulubet] avg_p>=55 | Last 30 days | NAMED_BOOKMAKER_PRICE: 13/13; SUSPECT_ALIAS_FUZZY: 1/0; UNMATCHED: 14/0 | NONE: 27/13; alias_fuzzy: 1/0 | pfc_1607fec83282d02c5254c2bf |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 | Since activation | NAMED_BOOKMAKER_PRICE: 7/7 | NONE: 7/7 | pfc_4a1f2bb2278d13c8189148d0 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 | Last 30 days | NAMED_BOOKMAKER_PRICE: 7/7 | NONE: 7/7 | pfc_4a1f2bb2278d13c8189148d0 |
| 1x2 single[scoutingstats] avg_p>=60 | Since activation | APPROVED_DONOR_PRICE: 1/1; NAMED_BOOKMAKER_PRICE: 3/3 | NONE: 4/4 | pfc_0f100c9da356ed1c05d9c642 |
| 1x2 single[scoutingstats] avg_p>=60 | Last 30 days | APPROVED_DONOR_PRICE: 1/1; NAMED_BOOKMAKER_PRICE: 3/3 | NONE: 4/4 | pfc_0f100c9da356ed1c05d9c642 |
| ou_2.5 unanimous[scoutingstats+statarea] avg_p>=65 | Since activation | NAMED_BOOKMAKER_PRICE: 16/16; SCOUTINGSTATS_SOLE: 1/1; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 16/16; alias_fuzzy: 1/0; scoutingstats_sole_source: 1/1 | pfc_4e8ef1faa47bce63a119fb43 |
| ou_2.5 unanimous[scoutingstats+statarea] avg_p>=65 | Last 30 days | NAMED_BOOKMAKER_PRICE: 16/16; SCOUTINGSTATS_SOLE: 1/1; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 16/16; alias_fuzzy: 1/0; scoutingstats_sole_source: 1/1 | pfc_4e8ef1faa47bce63a119fb43 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=50 | Since activation | NAMED_BOOKMAKER_PRICE: 2/2; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 2/2; alias_fuzzy: 1/0 | pfc_444d408c4ccd3a4bf4fb020c |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=50 | Last 30 days | NAMED_BOOKMAKER_PRICE: 2/2; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 2/2; alias_fuzzy: 1/0 | pfc_444d408c4ccd3a4bf4fb020c |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=40 | Since activation | NAMED_BOOKMAKER_PRICE: 12/12; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 12/12; alias_fuzzy: 1/0 | pfc_d94d447efe0742440e953722 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=40 | Last 30 days | NAMED_BOOKMAKER_PRICE: 12/12; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 12/12; alias_fuzzy: 1/0 | pfc_d94d447efe0742440e953722 |
| 1x2 unanimous[statarea+zulubet] avg_p>=55 | Since activation | NAMED_BOOKMAKER_PRICE: 2/2; UNMATCHED: 1/0 | NONE: 3/2 | pfc_5a9d3d3426ee7a4e63461d75 |
| 1x2 unanimous[statarea+zulubet] avg_p>=55 | Last 30 days | NAMED_BOOKMAKER_PRICE: 2/2; UNMATCHED: 1/0 | NONE: 3/2 | pfc_5a9d3d3426ee7a4e63461d75 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=55 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 1/1; alias_fuzzy: 1/0 | pfc_2bd498a3472b7bbd71982ece |
| 1x2 unanimous[vitibet+zulubet] avg_p>=55 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 1/1; alias_fuzzy: 1/0 | pfc_2bd498a3472b7bbd71982ece |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_3bfaf30507905754f7faab2a |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1 | NONE: 1/1 | pfc_3bfaf30507905754f7faab2a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=45 | Since activation | NAMED_BOOKMAKER_PRICE: 2/2 | NONE: 2/2 | pfc_b011652ec3e473fbc0afbb6a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=45 | Last 30 days | NAMED_BOOKMAKER_PRICE: 9/9; UNMATCHED: 2/0 | NONE: 11/9 | pfc_b011652ec3e473fbc0afbb6a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=40 | Since activation | NAMED_BOOKMAKER_PRICE: 1/1; SUSPECT_ALIAS_FUZZY: 3/0 | NONE: 1/1; alias_fuzzy: 3/0 | pfc_c7c9572806b564198f651cee |
| 1x2 unanimous[vitibet+zulubet] avg_p>=40 | Last 30 days | NAMED_BOOKMAKER_PRICE: 1/1; SUSPECT_ALIAS_FUZZY: 3/0 | NONE: 1/1; alias_fuzzy: 3/0 | pfc_c7c9572806b564198f651cee |
| 2way-unanimous avg_p>=70 | Last 30 days | NAMED_BOOKMAKER_PRICE: 9/9; SCOUTINGSTATS_SOLE: 3/3; SUSPECT_ALIAS_FUZZY: 3/1; UNMATCHED: 5/0 | NONE: 14/9; alias_fuzzy: 3/1; scoutingstats_sole_source: 3/3 | 2way-unanimous avg_p>=70 |
| ml-meta avg_p>=55 | Last 30 days | APPROVED_DONOR_PRICE: 1/1; NAMED_BOOKMAKER_PRICE: 41/41; SCOUTINGSTATS_SOLE: 14/14; SOURCE_FALLBACK: 4/4; SUSPECT_ALIAS_FUZZY: 3/3; UNMATCHED: 20/0 | NONE: 62/42; alias_fuzzy: 3/3; scoutingstats_sole_source: 14/14; source_fallback_not_execution_eligible: 4/4 | ml-meta avg_p>=55 |
| ml-meta avg_p>=60 | Last 30 days | NAMED_BOOKMAKER_PRICE: 79/79; SCOUTINGSTATS_SOLE: 15/15; SOURCE_FALLBACK: 11/11; SUSPECT_ALIAS_FUZZY: 16/16; UNMATCHED: 16/0 | NONE: 94/79; alias_fuzzy: 16/16; scoutingstats_sole_source: 15/15; source_fallback_not_execution_eligible: 11/11; stale_quote: 1/0 | ml-meta avg_p>=60 |
| ml-meta avg_p>=65 | Last 30 days | NAMED_BOOKMAKER_PRICE: 3/3; SCOUTINGSTATS_SOLE: 2/2; SOURCE_FALLBACK: 1/1; UNMATCHED: 5/0 | NONE: 8/3; scoutingstats_sole_source: 2/2; source_fallback_not_execution_eligible: 1/1 | ml-meta avg_p>=65 |
| ml-meta avg_p>=80 | Last 30 days | NAMED_BOOKMAKER_PRICE: 3/3 | NONE: 3/3 | ml-meta avg_p>=80 |
| 1x2 single[zulubet] avg_p>=45 | Since activation | UNMATCHED: 1/0 | NONE: 1/0 | pfc_14ee12458803822df3013bcd |
| 1x2 single[zulubet] avg_p>=45 | Last 30 days | UNMATCHED: 1/0 | NONE: 1/0 | pfc_14ee12458803822df3013bcd |
| 1x2 single[zulubet] avg_p>=60 | Since activation | UNMATCHED: 1/0 | NONE: 1/0 | pfc_35f7e50bf23db96c2d3dd59d |
| 1x2 single[zulubet] avg_p>=60 | Last 30 days | UNMATCHED: 1/0 | NONE: 1/0 | pfc_35f7e50bf23db96c2d3dd59d |
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
| 1x2 single[scoutingstats] avg_p>=65 | 398 / 398 | 100.0% | 80.2% | 0.1% | start: 2026-06-13; split: 2026-09-27; as_of_exclusive: 2026-10-25 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_fdade2e70df4d4bb78a8cd6e |
| ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55 | 347 / 347 | 100.0% | 66.6% | 0.8% | start: 2026-06-13; split: 2026-09-25; as_of_exclusive: 2026-10-23 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_27e0f725859bc708f95c58a3 |
| 1x2 single[scoutingstats] avg_p>=50 | 1235 / 1235 | 100.0% | 67.5% | 0.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_439097cb9bb700e9996c0b07 |
| 1x2 single[zulubet] avg_p>=50 | 1241 / 1240 | 99.9% | 57.4% | 0.5% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_4cf3df8552488297d7ccf526 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=0 | 271 / 271 | 100.0% | 62.0% | 0.2% | start: 2026-06-13; split: 2026-10-05; as_of_exclusive: 2026-11-02 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_642ac9053223500b638e3451 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=35 | 1257 / 1257 | 100.0% | 56.8% | 0.1% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_f56fe4a2759e9b17b9bdb116 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=60 | 333 / 333 | 100.0% | 69.7% | 0.1% | start: 2026-06-13; split: 2026-10-05; as_of_exclusive: 2026-11-02 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_54fcf87604b73b87ee6c0a90 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=0 | 438 / 438 | 100.0% | 61.2% | 2.9% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_0ad08cd1b2e75a2c9051189e |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=40 | 382 / 382 | 100.0% | 64.9% | 1.2% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_a7ba6711aeb15b9804a94f06 |
| 1x2 unanimous[statarea+zulubet] avg_p>=40 | 278 / 277 | 99.6% | 61.9% | 1.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_5208b9e15194a691590430ad |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35 | 530 / 530 | 100.0% | 57.4% | 0.5% | start: 2026-06-13; split: 2026-10-03; as_of_exclusive: 2026-10-31 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_73b036a8ee8dd5a4dea48134 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=50 | 427 / 427 | 100.0% | 66.5% | 4.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_234f16641d9893e8ec2a01f0 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=0 | 1258 / 1258 | 100.0% | 56.8% | 0.1% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_cddf4106a3d45b6e455d8c73 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=50 | 201 / 201 | 100.0% | 69.7% | 0.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_0b290b623e2a54ea7df3006c |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=40 | 360 / 360 | 100.0% | 60.8% | 4.0% | start: 2026-06-13; split: 2026-10-04; as_of_exclusive: 2026-11-01 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_226efd387e217a9d58a11f79 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=60 | 203 / 203 | 100.0% | 81.3% | 6.8% | start: 2026-06-13; split: 2026-09-27; as_of_exclusive: 2026-10-25 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_5904b1fc7050646e6321090c |
| 1x2 single[zulubet] avg_p>=55 | 864 / 863 | 99.9% | 64.6% | 4.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_1607fec83282d02c5254c2bf |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 | 426 / 426 | 100.0% | 62.2% | 4.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_4a1f2bb2278d13c8189148d0 |
| 1x2 single[scoutingstats] avg_p>=60 | 566 / 566 | 100.0% | 76.3% | 0.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_0f100c9da356ed1c05d9c642 |
| ou_2.5 unanimous[scoutingstats+statarea] avg_p>=65 | 321 / 321 | 100.0% | 72.0% | 0.1% | start: 2026-06-13; split: 2026-10-05; as_of_exclusive: 2026-11-02 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_4e8ef1faa47bce63a119fb43 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=50 | 182 / 182 | 100.0% | 70.3% | 0.2% | start: 2026-06-13; split: 2026-09-28; as_of_exclusive: 2026-10-26 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_444d408c4ccd3a4bf4fb020c |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=40 | 822 / 822 | 100.0% | 59.7% | 0.2% | start: 2026-06-13; split: 2026-09-23; as_of_exclusive: 2026-10-21 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_d94d447efe0742440e953722 |
| 1x2 unanimous[statarea+zulubet] avg_p>=55 | 222 / 221 | 99.5% | 73.4% | 3.6% | start: 2026-06-13; split: 2026-09-23; as_of_exclusive: 2026-10-21 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_5a9d3d3426ee7a4e63461d75 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=55 | 358 / 358 | 100.0% | 68.2% | 2.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_2bd498a3472b7bbd71982ece |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 | 645 / 645 | 100.0% | 65.1% | 1.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_3bfaf30507905754f7faab2a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=45 | 540 / 540 | 100.0% | 62.2% | 0.3% | start: 2026-06-13; split: 2026-09-29; as_of_exclusive: 2026-10-27 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_b011652ec3e473fbc0afbb6a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=40 | 649 / 649 | 100.0% | 62.3% | 1.4% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_c7c9572806b564198f651cee |
| 2way-unanimous avg_p>=70 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 2way-unanimous avg_p>=70 |
| ml-meta avg_p>=55 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | ml-meta avg_p>=55 |
| ml-meta avg_p>=60 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | ml-meta avg_p>=60 |
| ml-meta avg_p>=65 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | ml-meta avg_p>=65 |
| ml-meta avg_p>=80 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | ml-meta avg_p>=80 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=0 | 390 / 390 | 100.0% | 64.1% | 0.2% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_0187397f26c1f84f6c3a9883 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=35 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_054448b499623dd39b072b38 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=45 | 540 / 540 | 100.0% | 64.3% | 2.7% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_0aed63f3d04b46330958121d |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=45 | 240 / 240 | 100.0% | 60.0% | 0.4% | start: 2026-06-13; split: 2026-10-02; as_of_exclusive: 2026-10-30 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_144c01b1aa366b88f9c4083a |
| 1x2 single[zulubet] avg_p>=45 | 1488 / 1487 | 99.9% | 55.6% | 2.5% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_14ee12458803822df3013bcd |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=55 | 248 / 248 | 100.0% | 75.8% | 4.5% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_1ba3ab3c75e6f3a9680ae43c |
| 1x2 single[zulubet] avg_p>=40 | 1660 / 1659 | 99.9% | 53.2% | 0.9% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_1e9cfc6500aaac77afa1eaf9 |
| 1x2 unanimous[statarea+zulubet] avg_p>=35 | 284 / 283 | 99.6% | 61.3% | 0.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_3072388544a60552346bd162 |
| 1x2 single[zulubet] avg_p>=60 | 633 / 632 | 99.8% | 67.6% | 3.8% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_35f7e50bf23db96c2d3dd59d |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=35 | 248 / 248 | 100.0% | 63.3% | 0.3% | start: 2026-06-13; split: 2026-10-07; as_of_exclusive: 2026-11-04 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_37f18dce9f6de45ee38e4944 |
| 1x2 single[zulubet] avg_p>=0 | 1733 / 1732 | 99.9% | 52.7% | 1.3% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_3dc0fa6511953bf09bc4c845 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=50 | 285 / 285 | 100.0% | 68.4% | 4.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_3fbabd0ade3f89853e43fb10 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=60 | 195 / 195 | 100.0% | 79.0% | 5.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_40b163633fc01fd0ff7d0ef1 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=40 | 285 / 285 | 100.0% | 62.8% | 1.5% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_48e25c370ae15b7d58d6b0d8 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=55 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_4e2583010bf805466e33c2d0 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=0 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_4f2df06575151e798727a6b0 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=55 | 215 / 215 | 100.0% | 70.2% | 2.6% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_527524a94e98cff9740d499c |
| 1x2 single[zulubet] avg_p>=65 | 443 / 442 | 99.8% | 70.0% | 2.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_5954379f3a12700edcfd8387 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=50 | 372 / 372 | 100.0% | 68.0% | 0.3% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_5f861bad9f49ebf6d6fe2c16 |
| 1x2 single[zulubet] avg_p>=35 | 1732 / 1731 | 99.9% | 52.7% | 1.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_61cb1dd2a3157c4231070cdb |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=35 | 271 / 271 | 100.0% | 62.0% | 0.2% | start: 2026-06-13; split: 2026-10-05; as_of_exclusive: 2026-11-02 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_66a32773b3535996c572d351 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=40 | 276 / 276 | 100.0% | 64.9% | 0.1% | start: 2026-06-13; split: 2026-10-07; as_of_exclusive: 2026-11-04 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_69dd4c8623d4d22d840da318 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=40 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_6cd236448d9fd967f8dcb591 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=0 | 169 / 169 | 100.0% | 67.5% | 1.6% | start: 2026-06-13; split: 2026-09-26; as_of_exclusive: 2026-10-24 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_754f7247e83f901ae415b35f |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=35 | 438 / 438 | 100.0% | 61.2% | 2.9% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_7d20e19c2c26174fa21e9e86 |
| 1x2 unanimous[statarea+zulubet] avg_p>=45 | 314 / 313 | 99.7% | 66.9% | 2.5% | start: 2026-06-13; split: 2026-09-23; as_of_exclusive: 2026-10-21 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_7eb24434123da46374442290 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=45 | 234 / 234 | 100.0% | 65.4% | 0.8% | start: 2026-06-13; split: 2026-10-08; as_of_exclusive: 2026-11-05 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_84cede54e10853cd914d57c5 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=0 | 248 / 248 | 100.0% | 63.3% | 0.3% | start: 2026-06-13; split: 2026-10-07; as_of_exclusive: 2026-11-04 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_8e39a2c5719c5a609c077afd |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=0 | 530 / 530 | 100.0% | 57.4% | 0.5% | start: 2026-06-13; split: 2026-10-03; as_of_exclusive: 2026-10-31 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_92ab281aa7c2173e7502ba49 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=45 | 229 / 229 | 100.0% | 67.7% | 0.6% | start: 2026-06-13; split: 2026-09-26; as_of_exclusive: 2026-10-24 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_9ae5a305a703bca83fd321b3 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=35 | 655 / 655 | 100.0% | 61.8% | 0.7% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_a3afbb848e0c474b683b450f |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=45 | 316 / 316 | 100.0% | 69.6% | 1.0% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_a460a0e9dcb1f980cde169c0 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=35 | 169 / 169 | 100.0% | 67.5% | 1.6% | start: 2026-06-13; split: 2026-09-26; as_of_exclusive: 2026-10-24 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_a8e99ebc0016f0d0bb95aa70 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=60 | 128 / 128 | 100.0% | 81.2% | 3.0% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_a90a9b922d2318a2446434ce |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=35 | 390 / 390 | 100.0% | 64.1% | 0.2% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_ad11db4313c86de27efdde5a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=0 | 655 / 655 | 100.0% | 61.8% | 0.7% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_ad177634c86053c1c32b77cd |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=35 | 240 / 240 | 100.0% | 60.0% | 0.4% | start: 2026-06-13; split: 2026-10-02; as_of_exclusive: 2026-10-30 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_adb24b31e9ca43c42506156a |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=40 | 252 / 252 | 100.0% | 63.9% | 0.4% | start: 2026-06-13; split: 2026-10-08; as_of_exclusive: 2026-11-05 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_af020bcd1589e288dccb8d3e |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=50 | 240 / 240 | 100.0% | 60.0% | 0.4% | start: 2026-06-13; split: 2026-10-02; as_of_exclusive: 2026-10-30 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_afdf26c0a105a0f5e6ffff27 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=50 | 230 / 230 | 100.0% | 67.0% | 2.2% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_b0b7a0c1932e3636d2b485d6 |
| 1x2 unanimous[statarea+zulubet] avg_p>=0 | 284 / 283 | 99.6% | 61.3% | 0.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_b11e22bfdd27d85fad78ba74 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=0 | 367 / 367 | 100.0% | 60.2% | 3.3% | start: 2026-06-13; split: 2026-10-04; as_of_exclusive: 2026-11-01 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_b4407145af67d2f93e48f0ef |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=40 | 240 / 240 | 100.0% | 60.0% | 0.4% | start: 2026-06-13; split: 2026-10-02; as_of_exclusive: 2026-10-30 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_b9aa429be62178cc76b1ca8d |
| ou_3.5 unanimous[scoutingstats+statarea] avg_p>=70 | 366 / 366 | 100.0% | 80.6% | 0.5% | start: 2026-06-13; split: 2026-09-27; as_of_exclusive: 2026-10-25 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_bdce95a736d6cc8667f7ac31 |
| 1x2 unanimous[statarea+zulubet] avg_p>=50 | 271 / 270 | 99.6% | 70.5% | 3.9% | start: 2026-06-13; split: 2026-09-23; as_of_exclusive: 2026-10-21 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_c83d885867c9025a351b9b8c |
| 1x2 single[zulubet] avg_p>=70 | 242 / 241 | 99.6% | 74.0% | 2.7% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_c8cbcf76ea758fd6de596ae1 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=40 | 531 / 531 | 100.0% | 58.4% | 0.2% | start: 2026-06-13; split: 2026-10-05; as_of_exclusive: 2026-11-02 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_cd84fb2c3ed889c0ae9eb89e |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=55 | 177 / 177 | 100.0% | 71.8% | 0.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_d17123b85e11155f22e40051 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=35 | 367 / 367 | 100.0% | 60.2% | 3.3% | start: 2026-06-13; split: 2026-10-04; as_of_exclusive: 2026-11-01 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_d5c311b6e2f37443e3501556 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=45 | 372 / 372 | 100.0% | 63.7% | 2.5% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_e25602082a90cb64fb9c5451 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=45 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_e37e7d70a4d046d7a07da0a4 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=40 | 190 / 190 | 100.0% | 64.7% | 0.2% | start: 2026-06-13; split: 2026-10-07; as_of_exclusive: 2026-11-04 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_e5c10af025fc5071367c9b47 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=45 | 262 / 262 | 100.0% | 64.5% | 1.9% | start: 2026-06-13; split: 2026-10-06; as_of_exclusive: 2026-11-03 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_ed44334de1c8307f22b510ab |
| ou_2.5 unanimous[scoutingstats+statarea] avg_p>=60 | 612 / 612 | 100.0% | 68.3% | 0.1% | start: 2026-06-13; split: 2026-10-08; as_of_exclusive: 2026-11-05 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_ee214d4f2f00846fa78f56e3 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=55 | 239 / 239 | 100.0% | 74.9% | 4.3% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_f2b2a2e84093abe72bbc01c0 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=50 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_f51b5fdaf32bcca063f4b2cc |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=50 | 291 / 291 | 100.0% | 70.8% | 0.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_fb2e721d2bb8a41fe9fa3713 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=55 | 189 / 189 | 100.0% | 68.8% | 0.5% | start: 2026-06-13; split: 2026-10-07; as_of_exclusive: 2026-11-04 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_fbf508b9c62bae8f281bb6e1 |
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
- **Over 2.5 Goals**: occurred in 542 / 900 matches (60.2%)
- **Both Teams to Score (BTTS)**: occurred in 481 / 900 matches (53.4%)
- **Selected Team Over 1.5 Goals**: occurred in 584 / 896 matches (65.2%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 406
- **Total Hits**: 303
- **Overall Hit Rate**: 74.6%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=15, settled=15, hit_rate=86.7% (hits=13/recommended=15), priced_n=0, priced_ROI=None (denominator=0), registry_processed=67, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `away_under_15`: recommended=8, settled=8, hit_rate=87.5% (hits=7/recommended=8), priced_n=0, priced_ROI=None (denominator=0), registry_processed=16, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `away_under_25`: recommended=11, settled=11, hit_rate=81.8% (hits=9/recommended=11), priced_n=0, priced_ROI=None (denominator=0), registry_processed=46, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `away_under_35`: recommended=56, settled=56, hit_rate=98.2% (hits=55/recommended=56), priced_n=0, priced_ROI=None (denominator=0), registry_processed=305, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `btts_no`: recommended=8, settled=8, hit_rate=37.5% (hits=3/recommended=8), priced_n=5, priced_ROI=-0.45 (denominator=5), registry_processed=12, class=priced
- `btts_yes`: recommended=5, settled=5, hit_rate=100.0% (hits=5/recommended=5), priced_n=3, priced_ROI=0.853333 (denominator=3), registry_processed=23, class=priced
- `home_over_05`: recommended=19, settled=19, hit_rate=84.2% (hits=16/recommended=19), priced_n=0, priced_ROI=None (denominator=0), registry_processed=189, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `home_over_15`: recommended=2, settled=2, hit_rate=100.0% (hits=2/recommended=2), priced_n=0, priced_ROI=None (denominator=0), registry_processed=13, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `home_under_15`: recommended=2, settled=2, hit_rate=100.0% (hits=2/recommended=2), priced_n=0, priced_ROI=None (denominator=0), registry_processed=9, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `home_under_25`: recommended=2, settled=2, hit_rate=0.0% (hits=0/recommended=2), priced_n=0, priced_ROI=None (denominator=0), registry_processed=62, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `home_under_35`: recommended=20, settled=20, hit_rate=90.0% (hits=18/recommended=20), priced_n=0, priced_ROI=None (denominator=0), registry_processed=77, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window
- `match_over_15`: recommended=21, settled=21, hit_rate=81.0% (hits=17/recommended=21), priced_n=14, priced_ROI=0.165 (denominator=14), registry_processed=75, class=priced
- `match_over_25`: recommended=190, settled=190, hit_rate=64.2% (hits=122/recommended=190), priced_n=167, priced_ROI=0.040659 (denominator=167), registry_processed=768, class=priced
- `match_over_35`: recommended=18, settled=18, hit_rate=77.8% (hits=14/recommended=18), priced_n=10, priced_ROI=0.937 (denominator=10), registry_processed=49, class=priced
- `match_under_35`: recommended=8, settled=8, hit_rate=25.0% (hits=2/recommended=8), priced_n=7, priced_ROI=-0.625714 (denominator=7), registry_processed=15, class=priced
- `match_under_45`: recommended=21, settled=21, hit_rate=85.7% (hits=18/recommended=21), priced_n=0, priced_ROI=None (denominator=0), registry_processed=35, class=no_price_observed — hit-rate only: a mapped feed quoted no price for it in this window

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **1528** | scored: 1528 | without promised % (legacy rows): 252

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 369 | 298 | 175 | 58.7% | 51.5% | +7.3% | 0.249821 |
| `match_over_45` | 145 | 144 | 31 | 21.5% | 23.9% | -2.4% | 0.173757 |
| `away_under_35` | 131 | 131 | 130 | 99.2% | 95.9% | +3.4% | 0.008909 |
| `away_under_25` | 140 | 130 | 121 | 93.1% | 89.4% | +3.7% | 0.058696 |
| `match_over_35` | 134 | 128 | 68 | 53.1% | 42.7% | +10.4% | 0.269825 |
| `btts_yes` | 97 | 92 | 55 | 59.8% | 47.1% | +12.7% | 0.248418 |
| `btts_no` | 89 | 85 | 36 | 42.4% | 54.1% | -11.7% | 0.252474 |
| `home_under_35` | 63 | 61 | 58 | 95.1% | 96.9% | -1.8% | 0.045141 |
| `home_under_25` | 70 | 48 | 44 | 91.7% | 87.3% | +4.4% | 0.081074 |
| `away_over_05` | 43 | 28 | 24 | 85.7% | 78.8% | +6.9% | 0.10661 |
| `home_over_05` | 30 | 28 | 23 | 82.1% | 85.6% | -3.4% | 0.133238 |
| `match_under_25` | 43 | 27 | 11 | 40.7% | 40.8% | -0.0% | 0.242527 |
| `match_over_15` | 27 | 23 | 18 | 78.3% | 84.8% | -6.5% | 0.172881 |
| `away_under_15` | 24 | 13 | 9 | 69.2% | 65.4% | +3.8% | 0.105564 |
| `home_under_15` | 18 | 11 | 9 | 81.8% | 67.0% | +14.8% | 0.242189 |
| `match_under_35` | 26 | 10 | 4 | 40.0% | 62.4% | -22.4% | 0.275791 |
| `home_over_15` | 21 | 8 | 2 | 25.0% | 46.9% | -21.9% | 0.241596 |
| `match_under_45` | 39 | 6 | 4 | 66.7% | 80.4% | -13.8% | 0.248672 |
| `away_over_15` | 7 | 5 | 4 | 80.0% | 59.7% | +20.3% | 0.215626 |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 1229 | 789 | 64.2% | 61.4% | +2.8% | 0.173781 |
| model | 47 | 37 | 78.7% | 63.2% | +15.6% | 0.185616 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 42 | 19.1% | 26.2% | +7.1% |
| 0.2-0.3 | 93 | 24.9% | 20.4% | -4.5% |
| 0.3-0.4 | 98 | 36.3% | 48.0% | +11.6% |
| 0.4-0.5 | 310 | 44.8% | 54.5% | +9.7% |
| 0.5-0.6 | 177 | 54.7% | 50.8% | -3.9% |
| 0.6-0.7 | 73 | 63.5% | 58.9% | -4.6% |
| 0.7-0.8 | 37 | 74.0% | 70.3% | -3.7% |
| 0.8-0.9 | 165 | 86.4% | 90.9% | +4.5% |
| 0.9-1.0 | 281 | 94.7% | 96.4% | +1.7% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=942, MAE=1.484161 goals, bias=-0.145966 (realized − promised), promised avg 3.320064 vs realized 3.174098

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 942 | 34.4% | 34.3% | -0.1% | 0.200022 |
| BTTS-Yes | 942 | 49.2% | 53.5% | +4.3% | 0.253167 |
| Home Over 1.5 | 942 | 56.8% | 53.7% | -3.1% | 0.217705 |
| Over 2.5 | 942 | 64.2% | 60.5% | -3.7% | 0.241617 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 105 | 8.7% | 21.0% | +12.3% |
| 0.1-0.2 | 356 | 13.5% | 17.1% | +3.6% |
| 0.2-0.3 | 343 | 24.1% | 25.9% | +1.9% |
| 0.3-0.4 | 125 | 34.5% | 37.6% | +3.1% |
| 0.4-0.5 | 409 | 42.5% | 49.9% | +7.4% |
| 0.5-0.6 | 1063 | 55.5% | 57.3% | +1.7% |
| 0.6-0.7 | 756 | 64.5% | 59.8% | -4.7% |
| 0.7-0.8 | 278 | 74.9% | 71.6% | -3.3% |
| 0.8-0.9 | 297 | 84.9% | 65.3% | -19.5% |
| 0.9-1.0 | 36 | 91.9% | 72.2% | -19.7% |

## By rule

Counts are frozen PICK ROWS, not bets: SKIPPED_VETO / WATCHLIST_* rows are included and were never cardable. See the full audit’s `## By bucket` for bucket-level counts. These are not acca returns or bank performance.

ROI uses priced rows only; hit rate uses all settled rows. The 30-priced-row cutoff is a reporting sample flag, not proof of profitability or an activation gate. Registry status/certification are separate from this audit window. Historical ml-meta rules are not the live ML ENH acca selector.

### Positive ROI (2 rules)

| Rule | Priced ROI | Priced sample | Hit rate | Evidence | Registry context | Stored rule ID/key |
| --- | ---: | ---: | --- | --- | --- | --- |
| ml-meta avg_p>=55 | +24.0% | 63 priced | 71.1% (59/83 settled) | 30+ priced rows | legacy rule key | ml-meta avg_p>=55 |
| 1x2 single[scoutingstats] avg_p>=65 | +0.1% | 106 priced | 80.3% (110/137 settled) | 30+ priced rows | contract · benched, activated 2026-10-25, certified valid n=398 | pfc_fdade2e70df4d4bb78a8cd6e |

### Negative ROI (4 rules)

| Rule | Priced ROI | Priced sample | Hit rate | Evidence | Registry context | Stored rule ID/key |
| --- | ---: | ---: | --- | --- | --- | --- |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35 | -0.3% | 40 priced | 54.8% (23/42 settled) | 30+ priced rows | contract · certified, activated 2026-10-31, certified valid n=530 | pfc_73b036a8ee8dd5a4dea48134 |
| ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55 | -2.0% | 79 priced | 61.9% (52/84 settled) | 30+ priced rows | contract · benched, activated 2026-10-23, certified valid n=347 | pfc_27e0f725859bc708f95c58a3 |
| ml-meta avg_p>=60 | -3.5% | 121 priced | 59.9% (82/137 settled) | 30+ priced rows | legacy rule key | ml-meta avg_p>=60 |
| 1x2 single[scoutingstats] avg_p>=50 | -5.1% | 196 priced | 60.7% (150/247 settled) | 30+ priced rows | contract · benched, activated 2026-10-20, certified valid n=1235 | pfc_439097cb9bb700e9996c0b07 |

### Break-even (0 rules)

- none

### Insufficient priced evidence (38 rules)

| Rule | Priced ROI | Priced sample | Hit rate | Evidence | Registry context | Stored rule ID/key |
| --- | ---: | ---: | --- | --- | --- | --- |
| 1x2 single[zulubet] avg_p>=50 | +90.0% | 2 priced | 50.0% (2/4 settled) | PROVISIONAL: 2 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=1241 | pfc_4cf3df8552488297d7ccf526 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=0 | +73.0% | 1 priced | 100.0% (1/1 settled) | PROVISIONAL: 1 priced < 30 | contract · certified, activated 2026-11-02, certified valid n=271 | pfc_642ac9053223500b638e3451 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=35 | +65.1% | 19 priced | 76.2% (16/21 settled) | PROVISIONAL: 19 priced < 30 | contract · certified, activated 2026-11-03, certified valid n=1257 | pfc_f56fe4a2759e9b17b9bdb116 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=60 | +56.3% | 3 priced | 100.0% (3/3 settled) | PROVISIONAL: 3 priced < 30 | contract · certified, activated 2026-11-02, certified valid n=333 | pfc_54fcf87604b73b87ee6c0a90 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=0 | +55.2% | 4 priced | 75.0% (3/4 settled) | PROVISIONAL: 4 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=438 | pfc_0ad08cd1b2e75a2c9051189e |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=40 | +53.7% | 4 priced | 100.0% (4/4 settled) | PROVISIONAL: 4 priced < 30 | contract · certified, activated 2026-11-03, certified valid n=382 | pfc_a7ba6711aeb15b9804a94f06 |
| unanimous[betclan+statarea+vitibet] avg_p>=65 | +50.0% | 2 priced | 100.0% (2/2 settled) | PROVISIONAL: 2 priced < 30 | legacy rule key | unanimous[betclan+statarea+vitibet] avg_p>=65 |
| 1x2 unanimous[statarea+zulubet] avg_p>=40 | +44.0% | 1 priced | 100.0% (1/1 settled) | PROVISIONAL: 1 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=278 | pfc_5208b9e15194a691590430ad |
| unanimous[vitibet+zulubet] avg_p>=70 | +39.2% | 5 priced | 100.0% (5/5 settled) | PROVISIONAL: 5 priced < 30 | legacy rule key | unanimous[vitibet+zulubet] avg_p>=70 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=50 | +34.6% | 5 priced | 81.8% (9/11 settled) | PROVISIONAL: 5 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=427 | pfc_234f16641d9893e8ec2a01f0 |
| unanimous[betclan+vitibet] avg_p>=70 | +34.1% | 13 priced | 94.1% (16/17 settled) | PROVISIONAL: 13 priced < 30 | legacy rule key | unanimous[betclan+vitibet] avg_p>=70 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=0 | +33.0% | 1 priced | 100.0% (1/1 settled) | PROVISIONAL: 1 priced < 30 | contract · certified, activated 2026-11-03, certified valid n=1258 | pfc_cddf4106a3d45b6e455d8c73 |
| unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65 | +18.0% | 2 priced | 100.0% (2/2 settled) | PROVISIONAL: 2 priced < 30 | legacy rule key | unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65 |
| unanimous[statarea+vitibet] avg_p>=70 | +17.2% | 16 priced | 90.5% (19/21 settled) | PROVISIONAL: 16 priced < 30 | legacy rule key | unanimous[statarea+vitibet] avg_p>=70 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=50 | +16.5% | 2 priced | 50.0% (1/2 settled) | PROVISIONAL: 2 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=201 | pfc_0b290b623e2a54ea7df3006c |
| 1x2 unanimous[vitibet+zulubet] avg_p>=45 | +16.3% | 9 priced | 63.6% (7/11 settled) | PROVISIONAL: 9 priced < 30 | contract · benched, activated 2026-10-27, certified valid n=540 | pfc_b011652ec3e473fbc0afbb6a |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=40 | +15.5% | 10 priced | 58.3% (7/12 settled) | PROVISIONAL: 10 priced < 30 | contract · certified, activated 2026-11-01, certified valid n=360 | pfc_226efd387e217a9d58a11f79 |
| unanimous[bzzoiro+vitibet+zulubet] avg_p>=65 | +15.0% | 1 priced | 100.0% (1/1 settled) | PROVISIONAL: 1 priced < 30 | legacy rule key | unanimous[bzzoiro+vitibet+zulubet] avg_p>=65 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=60 | +14.9% | 8 priced | 66.7% (6/9 settled) | PROVISIONAL: 8 priced < 30 | contract · benched, activated 2026-10-25, certified valid n=203 | pfc_5904b1fc7050646e6321090c |
| 1x2 single[zulubet] avg_p>=55 | +13.7% | 13 priced | 67.9% (19/28 settled) | PROVISIONAL: 13 priced < 30 | contract · certified, activated 2026-10-20, certified valid n=864 | pfc_1607fec83282d02c5254c2bf |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 | +11.1% | 7 priced | 57.1% (4/7 settled) | PROVISIONAL: 7 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=426 | pfc_4a1f2bb2278d13c8189148d0 |
| ml-meta avg_p>=80 | +10.3% | 3 priced | 100.0% (3/3 settled) | PROVISIONAL: 3 priced < 30 | legacy rule key | ml-meta avg_p>=80 |
| 2way-unanimous avg_p>=70 | +10.0% | 13 priced | 80.0% (16/20 settled) | PROVISIONAL: 13 priced < 30 | legacy rule key | 2way-unanimous avg_p>=70 |
| 1x2 single[scoutingstats] avg_p>=60 | +9.7% | 4 priced | 75.0% (3/4 settled) | PROVISIONAL: 4 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=566 | pfc_0f100c9da356ed1c05d9c642 |
| ou_2.5 unanimous[scoutingstats+statarea] avg_p>=65 | +8.9% | 17 priced | 77.8% (14/18 settled) | PROVISIONAL: 17 priced < 30 | contract · certified, activated 2026-11-02, certified valid n=321 | pfc_4e8ef1faa47bce63a119fb43 |
| unanimous[statarea+vitibet+zulubet] avg_p>=65 | -2.5% | 2 priced | 50.0% (1/2 settled) | PROVISIONAL: 2 priced < 30 | legacy rule key | unanimous[statarea+vitibet+zulubet] avg_p>=65 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=50 | -3.3% | 2 priced | 66.7% (2/3 settled) | PROVISIONAL: 2 priced < 30 | contract · candidate, activated 2026-10-26, certified valid n=182 | pfc_444d408c4ccd3a4bf4fb020c |
| unanimous[bzzoiro+vitibet] avg_p>=70 | -3.6% | 13 priced | 69.2% (9/13 settled) | PROVISIONAL: 13 priced < 30 | legacy rule key | unanimous[bzzoiro+vitibet] avg_p>=70 |
| ml-meta avg_p>=65 | -14.7% | 6 priced | 72.7% (8/11 settled) | PROVISIONAL: 6 priced < 30 | legacy rule key | ml-meta avg_p>=65 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=40 | -17.4% | 12 priced | 38.5% (5/13 settled) | PROVISIONAL: 12 priced < 30 | contract · benched, activated 2026-10-21, certified valid n=822 | pfc_d94d447efe0742440e953722 |
| unanimous[bzzoiro+statarea+vitibet] avg_p>=65 | -33.5% | 4 priced | 60.0% (3/5 settled) | PROVISIONAL: 4 priced < 30 | legacy rule key | unanimous[bzzoiro+statarea+vitibet] avg_p>=65 |
| 1x2 unanimous[statarea+zulubet] avg_p>=55 | -34.5% | 2 priced | 33.3% (1/3 settled) | PROVISIONAL: 2 priced < 30 | contract · benched, activated 2026-10-21, certified valid n=222 | pfc_5a9d3d3426ee7a4e63461d75 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=55 | -100.0% | 1 priced | 50.0% (1/2 settled) | PROVISIONAL: 1 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=358 | pfc_2bd498a3472b7bbd71982ece |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 | -100.0% | 1 priced | 0.0% (0/1 settled) | PROVISIONAL: 1 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=645 | pfc_3bfaf30507905754f7faab2a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=40 | -100.0% | 1 priced | 75.0% (3/4 settled) | PROVISIONAL: 1 priced < 30 | contract · certified, activated 2026-11-03, certified valid n=649 | pfc_c7c9572806b564198f651cee |
| 1x2 single[zulubet] avg_p>=45 | unavailable | 0 priced | 0.0% (0/1 settled) | PROVISIONAL: 0 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=1488 | pfc_14ee12458803822df3013bcd |
| 1x2 single[zulubet] avg_p>=60 | unavailable | 0 priced | 100.0% (1/1 settled) | PROVISIONAL: 0 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=633 | pfc_35f7e50bf23db96c2d3dd59d |
| 1x2 single[zulubet] avg_p>=70 | unavailable | 0 priced | 100.0% (1/1 settled) | PROVISIONAL: 0 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=242 | pfc_c8cbcf76ea758fd6de596ae1 |


## By bucket

- `CAUTION`: settled=165, wins=115, hit_rate=0.69697 (settled n=165), ROI=0.083052 (priced n=165)
- `CERTIFIED_CLEAN`: settled=91, wins=58, hit_rate=0.637363 (settled n=91), ROI=0.002333 (priced n=91)
- `SKIPPED_VETO`: settled=536, wins=362, hit_rate=0.675373 (settled n=536), ROI=0.050144 (priced n=484)
- `WATCHLIST_NO_ODDS`: settled=52, wins=37, hit_rate=0.711538 (settled n=52), ROI=None (priced n=0)
- `WATCHLIST_SUSPECT_PRICE`: settled=93, wins=60, hit_rate=0.645161 (settled n=93), ROI=0.035556 (priced n=9)
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=48, wins=32, hit_rate=0.666667 (settled n=48), ROI=-0.00875 (priced n=48)
- `WATCHLIST_UNKNOWN_CTX`: settled=17, wins=12, hit_rate=0.705882 (settled n=17), ROI=-0.155347 (priced n=17)

## By odds source

- `UNKNOWN`: settled=188, wins=128, hit_rate=0.680851 (settled n=188), ROI=None (priced n=0)
- `betexplorer_odds`: settled=134, wins=104, hit_rate=0.776119 (settled n=134), ROI=0.040597 (priced n=134)
- `boggio`: settled=3, wins=3, hit_rate=1.0 (settled n=3), ROI=0.446667 (priced n=3)
- `oddspapi_odds`: settled=8, wins=4, hit_rate=0.5 (settled n=8), ROI=-0.13625 (priced n=8)
- `pinnapi_odds`: settled=405, wins=256, hit_rate=0.632099 (settled n=405), ROI=0.027219 (priced n=405)
- `scoutingstats_odds`: settled=89, wins=61, hit_rate=0.685393 (settled n=89), ROI=0.012809 (priced n=89)
- `sharpapi_odds`: settled=1, wins=1, hit_rate=1.0 (settled n=1), ROI=0.741 (priced n=1)
- `theoddsapi`: settled=137, wins=98, hit_rate=0.715328 (settled n=137), ROI=0.130219 (priced n=137)
- `zulubet`: settled=37, wins=21, hit_rate=0.567568 (settled n=37), ROI=-0.026757 (priced n=37)

## By odds match method

- `alias_fuzzy`: settled=129, wins=86, hit_rate=0.666667 (settled n=129), ROI=-0.071 (priced n=20)
- `alias_time`: settled=3, wins=2, hit_rate=0.666667 (settled n=3), ROI=0.081567 (priced n=3)
- `exact`: settled=774, wins=525, hit_rate=0.678295 (settled n=774), ROI=0.046757 (priced n=774)
- `fallback`: settled=17, wins=9, hit_rate=0.529412 (settled n=17), ROI=0.025294 (priced n=17)
- `none`: settled=79, wins=54, hit_rate=0.683544 (settled n=79), ROI=None (priced n=0)

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| APPROVED_DONOR_PRICE (`APPROVED_DONOR_PRICE`) | 3 | 3 | 1.0 | 3 | 0.446667 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 685 | 463 | 0.675912 | 685 | 0.049569 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 89 | 61 | 0.685393 | 89 | 0.012809 |
| Source fallback (`SOURCE_FALLBACK`) | 17 | 9 | 0.529412 | 17 | 0.025294 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 129 | 86 | 0.666667 | 20 | -0.071 |
| No usable price (`UNMATCHED`) | 79 | 54 | 0.683544 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 536 | 362 | 0.675373 | 484 | 0.050144 |
| **trusted evidence only** | 428 | 288 | 0.672897 | 428 | 0.058154 |
| **soft evidence only** | 108 | 74 | 0.685185 | 56 | -0.011071 |
| evidence: NAMED_BOOKMAKER_PRICE | 428 | 288 | 0.672897 | 428 | 0.058154 |
| evidence: SCOUTINGSTATS_SOLE | 41 | 29 | 0.707317 | 41 | 0.038049 |
| evidence: SOURCE_FALLBACK | 4 | 2 | 0.5 | 4 | -0.11 |
| evidence: SUSPECT_ALIAS_FUZZY | 36 | 26 | 0.722222 | 11 | -0.158182 |
| evidence: UNMATCHED | 27 | 17 | 0.62963 | 0 | None |
| odds band: <1.50 | 197 | 157 | 0.796954 | 197 | 0.020707 |
| odds band: 1.50-2.00 | 218 | 130 | 0.59633 | 218 | 0.010094 |
| odds band: 2.00-3.00 | 65 | 37 | 0.569231 | 65 | 0.276769 |
| odds band: >=3.00 | 4 | 1 | 0.25 | 4 | 0.0 |
| odds band: unpriced | 52 | 37 | 0.711538 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.2 |
| veto reason: context VETO in ['competition_type'] | 47 | 39 | 0.829787 | 37 | 0.099557 |
| veto reason: context VETO in ['league', 'niche'] | 33 | 22 | 0.666667 | 26 | -0.119442 |
| veto reason: context VETO in ['league', 'odds_band', 'niche'] | 10 | 5 | 0.5 | 10 | -0.01242 |
| veto reason: context VETO in ['league', 'odds_band'] | 53 | 30 | 0.566038 | 53 | -0.004006 |
| veto reason: context VETO in ['league', 'team_a'] | 3 | 0 | 0.0 | 3 | -1.0 |
| veto reason: context VETO in ['league', 'team_h', 'competition_type'] | 2 | 2 | 1.0 | 2 | 0.3881 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 6 | 4 | 0.666667 | 5 | 0.186 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 2 | 1.0 | 2 | 0.7476 |
| veto reason: context VETO in ['league', 'team_h'] | 1 | 1 | 1.0 | 1 | 0.29 |
| veto reason: context VETO in ['league'] | 72 | 44 | 0.611111 | 57 | -0.155549 |
| veto reason: context VETO in ['niche'] | 42 | 32 | 0.761905 | 38 | 0.018463 |
| veto reason: context VETO in ['odds_band', 'niche'] | 6 | 3 | 0.5 | 6 | -0.022667 |
| veto reason: context VETO in ['odds_band'] | 128 | 77 | 0.601562 | 128 | 0.10797 |
| veto reason: context VETO in ['team_a', 'competition_type'] | 6 | 5 | 0.833333 | 6 | 0.20035 |
| veto reason: context VETO in ['team_a', 'niche'] | 2 | 2 | 1.0 | 2 | 0.72 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 2 | 2 | 1.0 | 2 | 0.665 |
| veto reason: context VETO in ['team_a'] | 36 | 28 | 0.777778 | 32 | 0.222212 |
| veto reason: context VETO in ['team_h', 'competition_type'] | 13 | 11 | 0.846154 | 12 | 0.082017 |
| veto reason: context VETO in ['team_h', 'niche'] | 3 | 2 | 0.666667 | 2 | 0.42 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 3 | 1 | 0.333333 | 3 | -0.576667 |
| veto reason: context VETO in ['team_h', 'team_a', 'competition_type'] | 1 | 1 | 1.0 | 1 | 0.23 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.62 |
| veto reason: context VETO in ['team_h', 'team_a'] | 12 | 9 | 0.75 | 11 | 0.303118 |
| veto reason: context VETO in ['team_h'] | 27 | 18 | 0.666667 | 19 | 0.128947 |
| veto reason: short-odds away favourite 1.04 | 1 | 1 | 1.0 | 1 | 0.041 |
| veto reason: short-odds away favourite 1.05 | 1 | 1 | 1.0 | 1 | 0.05 |
| veto reason: short-odds away favourite 1.08 | 2 | 2 | 1.0 | 2 | 0.08 |
| veto reason: short-odds away favourite 1.09 | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: short-odds away favourite 1.10 | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: short-odds away favourite 1.16 | 1 | 1 | 1.0 | 1 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 1 | 1 | 1.0 | 1 | 0.1845 |
| veto reason: short-odds away favourite 1.20 | 1 | 1 | 1.0 | 1 | 0.2 |
| veto reason: short-odds away favourite 1.22 | 2 | 2 | 1.0 | 2 | 0.22 |
| veto reason: short-odds away favourite 1.23 | 1 | 1 | 1.0 | 1 | 0.2342 |
| veto reason: short-odds away favourite 1.24 | 2 | 0 | 0.0 | 2 | -1.0 |
| veto reason: short-odds away favourite 1.25 | 4 | 4 | 1.0 | 4 | 0.25 |
| veto reason: short-odds away favourite 1.26 | 1 | 1 | 1.0 | 1 | 0.2591 |
| veto reason: short-odds away favourite 1.27 | 2 | 2 | 1.0 | 2 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 1 | 1 | 1.0 | 1 | 0.277 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: APPROVED_DONOR_PRICE | 2 | 2 | 1.0 | 2 | 0.41 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 162 | 112 | 0.691358 | 162 | 0.073849 |
| contrast CAUTION: SOURCE_FALLBACK | 1 | 1 | 1.0 | 1 | 0.92 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 766 | 519 | 0.677546 | 688 | 0.0513 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 129 | 86 | 0.666667 | 20 | -0.071 | 129 | 1.569936 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 89 | 61 | 0.685393 | 89 | 0.012809 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 17 | 9 | 0.529412 | 17 | 0.025294 | 0 | None |
| stale_quote (`stale_quote`) | 1 | 1 | 1.0 | 0 | None | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-11-04: Fenerbahçe vs Liverpool (Actual Score: **3-2**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.39 -> 🟢 WON (Expected prob: 69.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.5% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 61.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 60.2% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 57.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 5 goals)

### 2026-11-04: Sporting San Jose vs Perez Zeledon (Actual Score: **3-1**)
- **1X2 Pick**: Selected `HOME` @ 1.368 -> 🟢 WON (Expected prob: 66.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 63.2% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 51.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 70.1% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 77.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-04: Internacional vs Coritiba (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.62 -> 🟢 WON (Expected prob: 66.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.4% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 52.0% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 62.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Under 4.5 Goals**: expected n/a (Actual: 1 goals)
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected n/a (Actual: 0 away goals)
    - [🔴 MISS] **Home Team Over 1.5 Goals**: expected n/a (Actual: 1 home goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected n/a (Actual: 1 home goals)

### 2026-11-04: AEK Athens vs Real Madrid (Actual Score: **2-3**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.29 -> 🟢 WON (Expected prob: 76.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.5% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 61.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 60.2% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 57.5% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-04: RB Leipzig vs Manchester City (Actual Score: **2-3**)
- **Over/Under 2.5 Pick**: Selected `OVER` @ 1.32 -> 🟢 WON (Expected prob: 69.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 71.5% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 61.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 60.2% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 57.5% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 5 goals)

### 2026-11-04: Slavia Praha vs Arsenal (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.27 -> 🟢 WON (Expected prob: 80.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.3% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 74.0% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 59.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-04: Borussia Dortmund vs Real Betis (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.82 -> 🟢 WON (Expected prob: 62.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 59.4% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 52.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.8% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-04: Deportivo Pasto vs Jaguares (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 62.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 58.8% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.0% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 61.1% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 75.0% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-04: Alianza Lima vs Cienciano (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ 1.4 -> 🟢 WON (Expected prob: 63.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 55.5% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 55.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.5% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 70.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Away Team Under 1.5 Goals**: expected n/a (Actual: 0 away goals)
    - [🟢 HIT] **Home Team Under 2.5 Goals**: expected n/a (Actual: 1 home goals)
    - [🔴 MISS] **Away Team Over 0.5 Goals**: expected n/a (Actual: 0 away goals)
    - [🟢 HIT] **Match Under 3.5 Goals**: expected n/a (Actual: 1 goals)

### 2026-11-04: Fenerbahçe vs Liverpool (Actual Score: **3-2**)
- **1X2 Pick**: Selected `AWAY` @ 1.68 -> 🔴 LOST (Expected prob: 60.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 54.8% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 71.9% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 53.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-04: MC Alger vs MC Oran (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.57 -> 🟢 WON (Expected prob: 55.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 55.5% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 55.3% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.5% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 70.7% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-04: RB Leipzig vs Manchester City (Actual Score: **2-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.6 -> 🟢 WON (Expected prob: 54.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 54.8% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 71.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 53.5% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-04: Porto vs Napoli (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 2.06 -> 🟢 WON (Expected prob: 45.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 55.5% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 55.3% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 54.5% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 70.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-04: Lens vs Como (Actual Score: **1-9**)
- **1X2 Pick**: Selected `AWAY` @ 2.18 -> 🟢 WON (Expected prob: 41.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 54.8% (Actual: 10 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 71.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 53.5% (Actual: 9 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-04: Libertad vs Cerro Porteño (Actual Score: **0-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 37.1%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 55.5% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 55.3% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 54.5% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 70.7% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-04: Sportivo Ameliano vs Guaraní (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ 2.41 -> 🟢 WON (Expected prob: 36.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 54.8% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 53.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 71.9% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 53.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-04: AEK Athens vs Real Madrid (Actual Score: **2-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.33 -> 🟢 WON (Expected prob: 71.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 54.8% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.5% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 71.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 53.6% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-04: Enisey vs Nizhny Novgorod (Actual Score: **1-2**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 72.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 60.6% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.8% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 74.6% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 61.7% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-11-04: Deportivo Tachira FC vs Puerto Cabello (Actual Score: **3-2**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 59.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 58.8% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 53.0% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 61.1% (Actual: 3 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 75.0% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| POSTPONED | 6 |
- 2026-10-23 `POSTPONED` `CAUTION` — Gateshead vs Tamworth (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-10-23 `POSTPONED` `SKIPPED_VETO` — Holywell vs Penybont (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-10-24 `POSTPONED` `CAUTION` — Glentoran vs Ballymena United (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-10-24 `POSTPONED` `CAUTION` — Slovan Liberec vs Baník Ostrava (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-10-28 `POSTPONED` `SKIPPED_VETO` — Navalcarnero vs Real Betis (verified_disposition); excluded from win/loss/ROI
- 2026-10-28 `POSTPONED` `WATCHLIST_SUSPECT_PRICE` — Salamanca CF UDS vs Celta de Vigo (source_status:scoutingstats); excluded from win/loss/ROI

## Rescheduled Fixture Examples

- 2026-10-18 `SKIPPED_VETO` `unanimous[bzzoiro+vitibet] avg_p>=70` — Hartford Athletic vs Brooklyn -> HOME @ 1.44 (rescheduled → 2026-10-17; actual Hartford Athletic 2-3 Brooklyn [away])
- 2026-10-21 `WATCHLIST_UNCORROBORATED_PRICE` `1x2 single[scoutingstats] avg_p>=50` — Cerro Porteño vs Sportivo Ameliano -> HOME @ 1.65 (rescheduled → 2026-10-18; actual Cerro Porteno 2-2 Sportivo Ameliano [draw])
- 2026-10-25 `WATCHLIST_SUSPECT_PRICE` `1x2 single[scoutingstats] avg_p>=65` — Paris Saint Germain vs Olympique Lyonnais -> HOME @ None (rescheduled → 2026-10-26; actual Paris Saint Germain 2-0 Olympique Lyonnais [home])

## Pending / Unmatched Result Examples

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
- 2026-10-25 `CAUTION` `ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55` — Sporting CP vs Académico Viseu FC -> OVER @ 1.3953 (pending_or_unmatched_result); keys=['cp', 'lisbon']/['academico']
- 2026-10-25 `WATCHLIST_UNCORROBORATED_PRICE` `1x2 single[scoutingstats] avg_p>=65` — Sporting CP vs Academico Viseu -> HOME @ 1.22 (pending_or_unmatched_result); keys=['cp', 'lisbon']/['academico']
- 2026-10-28 `SKIPPED_VETO` `1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35` — Liverpool FC vs Chelsea -> HOME @ 2.3 (pending_or_unmatched_result); keys=['liverpool']/['chelsea']

## Ambiguous result examples

- 2026-10-21 `WATCHLIST_NO_ODDS` `1x2 single[zulubet] avg_p>=65` — Guadalajara W vs Necaxa W (ambiguous_alias_result)
