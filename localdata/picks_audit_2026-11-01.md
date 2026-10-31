# Edge Factory — Recent picks audit (2026-10-03 to 2026-11-01)

## Overall

- archived pick rows: 1095
- archived pick dates: 30
- immutable morning-baseline rows: 963
- late-slate additions (regular-ledger rows not in the morning baseline): 133, of which on days whose regular ledger was rewritten: 105
- regular-ledger-only legacy rows: 0
- unsafe regular ledgers ignored: 26
- empty regular ledgers (morning-baseline coverage only): 0
- settled picks: 1006
- eligible prior picks: 1030
- pending/unmatched result picks: 16
- rescheduled result picks (settled ±3d): 6
- voided postponed/cancelled/abandoned events: 7
- ambiguous event-disposition rows: 0
- settled via shared overlay facts: 2
- ambiguous result picks: 1
- wins: 668
- hit rate: +66.4% (wins/settled: 668/1006)
- priced picks: 802
- ROI: +1.6% (P&L / 802 priced picks)

## Settlement policy

- include same-day picks: False
- same-day cutoff date: 2026-11-01
- same-day rows excluded: 39

## Rule performance — since activation vs last 30 days

Primary view: recorded post-activation PICK ROWS, including vetoed/watchlist rows; not placed bets or acca returns. No retrospective rule replay. Missing activation dates remain unavailable. Missing archive days mean partial history, not zero activity. Missing/unreadable files are counted as archive gaps. Empty recorded cards count as available days. Current registry status is not historical status on each pick date.

Last 30 days: 2026-10-03 to 2026-11-01; same-day inclusion: False (local cutoff 2026-11-01). The 30-priced-row provisional flag is reporting only, not an activation gate. Priced ROI can include fallback/quarantined odds; provenance is shown separately. Historical ml-meta is not the live ML ENH selector.

| Rule | Activation / current status | Since activation | Last 30 days | Archive days: since / recent | Stored key |
| --- | --- | --- | --- | --- | --- |
| ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55 | 2026-10-23 / benched | ROI -2.0%; hit 61.9% (52/84); 79 priced; coverage 94.0% | ROI -2.0%; hit 61.9% (52/84); 79 priced; coverage 94.0% | 9/9 / 29/29 | pfc_27e0f725859bc708f95c58a3 |
| 1x2 single[scoutingstats] avg_p>=65 | 2026-10-25 / certified | ROI -2.1%; hit 78.9% (90/114); 86 priced; coverage 75.4% | ROI -2.1%; hit 78.9% (90/114); 86 priced; coverage 75.4% | 7/7 / 29/29 | pfc_fdade2e70df4d4bb78a8cd6e |
| 1x2 single[scoutingstats] avg_p>=50 | 2026-10-20 / benched | ROI -5.1%; hit 60.7% (150/247); 196 priced; coverage 79.4% | ROI -5.1%; hit 60.7% (150/247); 196 priced; coverage 79.4% | 12/12 / 29/29 | pfc_439097cb9bb700e9996c0b07 |
| 1x2 single[zulubet] avg_p>=50 | 2026-10-20 / benched | ROI +90.0%; hit 50.0% (2/4); 2 priced; coverage 50.0%; provisional | ROI +90.0%; hit 50.0% (2/4); 2 priced; coverage 50.0%; provisional | 12/12 / 29/29 | pfc_4cf3df8552488297d7ccf526 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=0 | 2026-10-20 / benched | ROI +55.2%; hit 75.0% (3/4); 4 priced; coverage 100.0%; provisional | ROI +55.2%; hit 75.0% (3/4); 4 priced; coverage 100.0%; provisional | 12/12 / 29/29 | pfc_0ad08cd1b2e75a2c9051189e |
| 1x2 unanimous[statarea+zulubet] avg_p>=40 | 2026-10-20 / benched | ROI +44.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | ROI +44.0%; hit 100.0% (1/1); 1 priced; coverage 100.0%; provisional | 12/12 / 29/29 | pfc_5208b9e15194a691590430ad |
| 1x2 unanimous[vitibet+zulubet] avg_p>=50 | 2026-10-20 / benched | ROI +34.6%; hit 81.8% (9/11); 5 priced; coverage 45.5%; provisional | ROI +34.6%; hit 81.8% (9/11); 5 priced; coverage 45.5%; provisional | 12/12 / 29/29 | pfc_234f16641d9893e8ec2a01f0 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=50 | 2026-10-20 / benched | ROI +16.5%; hit 50.0% (1/2); 2 priced; coverage 100.0%; provisional | ROI +16.5%; hit 50.0% (1/2); 2 priced; coverage 100.0%; provisional | 12/12 / 29/29 | pfc_0b290b623e2a54ea7df3006c |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=60 | 2026-10-25 / benched | ROI +14.9%; hit 66.7% (6/9); 8 priced; coverage 88.9%; provisional | ROI +14.9%; hit 66.7% (6/9); 8 priced; coverage 88.9%; provisional | 7/7 / 29/29 | pfc_5904b1fc7050646e6321090c |
| 1x2 single[zulubet] avg_p>=55 | 2026-10-20 / certified | ROI +13.3%; hit 61.9% (13/21); 10 priced; coverage 47.6%; provisional | ROI +13.3%; hit 61.9% (13/21); 10 priced; coverage 47.6%; provisional | 12/12 / 29/29 | pfc_1607fec83282d02c5254c2bf |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 | 2026-10-20 / benched | ROI +11.1%; hit 57.1% (4/7); 7 priced; coverage 100.0%; provisional | ROI +11.1%; hit 57.1% (4/7); 7 priced; coverage 100.0%; provisional | 12/12 / 29/29 | pfc_4a1f2bb2278d13c8189148d0 |
| 1x2 single[scoutingstats] avg_p>=60 | 2026-10-20 / benched | ROI +9.7%; hit 75.0% (3/4); 4 priced; coverage 100.0%; provisional | ROI +9.7%; hit 75.0% (3/4); 4 priced; coverage 100.0%; provisional | 12/12 / 29/29 | pfc_0f100c9da356ed1c05d9c642 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=50 | 2026-10-26 / candidate | ROI -3.3%; hit 66.7% (2/3); 2 priced; coverage 66.7%; provisional | ROI -3.3%; hit 66.7% (2/3); 2 priced; coverage 66.7%; provisional | 6/6 / 29/29 | pfc_444d408c4ccd3a4bf4fb020c |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=40 | 2026-10-21 / benched | ROI -17.4%; hit 38.5% (5/13); 12 priced; coverage 92.3%; provisional | ROI -17.4%; hit 38.5% (5/13); 12 priced; coverage 92.3%; provisional | 11/11 / 29/29 | pfc_d94d447efe0742440e953722 |
| 1x2 unanimous[statarea+zulubet] avg_p>=55 | 2026-10-21 / benched | ROI -34.5%; hit 33.3% (1/3); 2 priced; coverage 66.7%; provisional | ROI -34.5%; hit 33.3% (1/3); 2 priced; coverage 66.7%; provisional | 11/11 / 29/29 | pfc_5a9d3d3426ee7a4e63461d75 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=55 | 2026-10-20 / benched | ROI -100.0%; hit 50.0% (1/2); 1 priced; coverage 50.0%; provisional | ROI -100.0%; hit 50.0% (1/2); 1 priced; coverage 50.0%; provisional | 12/12 / 29/29 | pfc_2bd498a3472b7bbd71982ece |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 | 2026-10-20 / benched | ROI -100.0%; hit 0.0% (0/1); 1 priced; coverage 100.0%; provisional | ROI -100.0%; hit 0.0% (0/1); 1 priced; coverage 100.0%; provisional | 12/12 / 29/29 | pfc_3bfaf30507905754f7faab2a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=45 | 2026-10-27 / benched | ROI -100.0%; hit 0.0% (0/2); 2 priced; coverage 100.0%; provisional | ROI +16.3%; hit 63.6% (7/11); 9 priced; coverage 81.8%; provisional | 5/5 / 29/29 | pfc_b011652ec3e473fbc0afbb6a |
| 2way-unanimous avg_p>=60 | unavailable / unavailable | unavailable | ROI -14.7%; hit 57.1% (28/49); 25 priced; coverage 51.0%; provisional | unavailable / 29/29 | 2way-unanimous avg_p>=60 |
| 2way-unanimous avg_p>=70 | unavailable / unavailable | unavailable | ROI +3.8%; hit 79.2% (19/24); 17 priced; coverage 70.8%; provisional | unavailable / 29/29 | 2way-unanimous avg_p>=70 |
| ml-meta avg_p>=55 | unavailable / unavailable | unavailable | ROI +22.0%; hit 73.3% (88/120); 94 priced; coverage 78.3% | unavailable / 29/29 | ml-meta avg_p>=55 |
| ml-meta avg_p>=60 | unavailable / unavailable | unavailable | ROI -4.0%; hit 60.7% (88/145); 129 priced; coverage 89.0% | unavailable / 29/29 | ml-meta avg_p>=60 |
| ml-meta avg_p>=65 | unavailable / unavailable | unavailable | ROI -8.2%; hit 76.9% (10/13); 8 priced; coverage 61.5%; provisional | unavailable / 29/29 | ml-meta avg_p>=65 |
| ml-meta avg_p>=80 | unavailable / unavailable | unavailable | ROI +9.0%; hit 100.0% (5/5); 4 priced; coverage 80.0%; provisional | unavailable / 29/29 | ml-meta avg_p>=80 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=35 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_054448b499623dd39b072b38 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=45 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_0aed63f3d04b46330958121d |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=45 | 2026-10-30 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 2/2 / 29/29 | pfc_144c01b1aa366b88f9c4083a |
| 1x2 single[zulubet] avg_p>=45 | 2026-10-20 / benched | ROI unavailable; hit 0.0% (0/1); 0 priced; coverage 0.0%; provisional | ROI unavailable; hit 0.0% (0/1); 0 priced; coverage 0.0%; provisional | 12/12 / 29/29 | pfc_14ee12458803822df3013bcd |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=55 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_1ba3ab3c75e6f3a9680ae43c |
| 1x2 single[zulubet] avg_p>=40 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_1e9cfc6500aaac77afa1eaf9 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=40 | 2026-11-01 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 0/0 / 29/29 | pfc_226efd387e217a9d58a11f79 |
| 1x2 unanimous[statarea+zulubet] avg_p>=35 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_3072388544a60552346bd162 |
| 1x2 single[zulubet] avg_p>=60 | 2026-10-20 / benched | ROI unavailable; hit 100.0% (1/1); 0 priced; coverage 0.0%; provisional | ROI unavailable; hit 100.0% (1/1); 0 priced; coverage 0.0%; provisional | 12/12 / 29/29 | pfc_35f7e50bf23db96c2d3dd59d |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=35 | 2026-10-28 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 4/4 / 29/29 | pfc_37f18dce9f6de45ee38e4944 |
| 1x2 single[zulubet] avg_p>=0 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_3dc0fa6511953bf09bc4c845 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=50 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_3fbabd0ade3f89853e43fb10 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=60 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_40b163633fc01fd0ff7d0ef1 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=55 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_4e2583010bf805466e33c2d0 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=0 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_4f2df06575151e798727a6b0 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=55 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_527524a94e98cff9740d499c |
| 1x2 single[zulubet] avg_p>=65 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_5954379f3a12700edcfd8387 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=50 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_5f861bad9f49ebf6d6fe2c16 |
| 1x2 single[zulubet] avg_p>=35 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_61cb1dd2a3157c4231070cdb |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=40 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_6cd236448d9fd967f8dcb591 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35 | 2026-10-31 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI -4.9%; hit 52.6% (20/38); 36 priced; coverage 94.7% | 1/1 / 29/29 | pfc_73b036a8ee8dd5a4dea48134 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=0 | 2026-10-24 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 8/8 / 29/29 | pfc_754f7247e83f901ae415b35f |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=35 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_7d20e19c2c26174fa21e9e86 |
| 1x2 unanimous[statarea+zulubet] avg_p>=45 | 2026-10-21 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 11/11 / 29/29 | pfc_7eb24434123da46374442290 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=45 | 2026-10-28 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 4/4 / 29/29 | pfc_84cede54e10853cd914d57c5 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=0 | 2026-10-28 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 4/4 / 29/29 | pfc_8e39a2c5719c5a609c077afd |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=0 | 2026-10-31 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 1/1 / 29/29 | pfc_92ab281aa7c2173e7502ba49 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=45 | 2026-10-24 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 8/8 / 29/29 | pfc_9ae5a305a703bca83fd321b3 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=45 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_a460a0e9dcb1f980cde169c0 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=40 | 2026-10-30 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 2/2 / 29/29 | pfc_a7ba6711aeb15b9804a94f06 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=35 | 2026-10-24 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 8/8 / 29/29 | pfc_a8e99ebc0016f0d0bb95aa70 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=60 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_a90a9b922d2318a2446434ce |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=35 | 2026-10-30 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 2/2 / 29/29 | pfc_adb24b31e9ca43c42506156a |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=50 | 2026-10-30 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 2/2 / 29/29 | pfc_afdf26c0a105a0f5e6ffff27 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=50 | 2026-10-28 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 4/4 / 29/29 | pfc_b0b7a0c1932e3636d2b485d6 |
| 1x2 unanimous[statarea+zulubet] avg_p>=0 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_b11e22bfdd27d85fad78ba74 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=0 | 2026-11-01 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 0/0 / 29/29 | pfc_b4407145af67d2f93e48f0ef |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=40 | 2026-10-30 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 2/2 / 29/29 | pfc_b9aa429be62178cc76b1ca8d |
| ou_3.5 unanimous[scoutingstats+statarea] avg_p>=70 | 2026-10-25 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 7/7 / 29/29 | pfc_bdce95a736d6cc8667f7ac31 |
| 1x2 unanimous[statarea+zulubet] avg_p>=50 | 2026-10-21 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 11/11 / 29/29 | pfc_c83d885867c9025a351b9b8c |
| 1x2 single[zulubet] avg_p>=70 | 2026-10-20 / benched | ROI unavailable; hit 100.0% (1/1); 0 priced; coverage 0.0%; provisional | ROI unavailable; hit 100.0% (1/1); 0 priced; coverage 0.0%; provisional | 12/12 / 29/29 | pfc_c8cbcf76ea758fd6de596ae1 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=40 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_cd84fb2c3ed889c0ae9eb89e |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=0 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_cddf4106a3d45b6e455d8c73 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=55 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_d17123b85e11155f22e40051 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=35 | 2026-11-01 / certified | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 0/0 / 29/29 | pfc_d5c311b6e2f37443e3501556 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=45 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_e25602082a90cb64fb9c5451 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=45 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_e37e7d70a4d046d7a07da0a4 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=40 | 2026-10-28 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 4/4 / 29/29 | pfc_e5c10af025fc5071367c9b47 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=55 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_f2b2a2e84093abe72bbc01c0 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=50 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_f51b5fdaf32bcca063f4b2cc |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=35 | 2026-10-20 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_f56fe4a2759e9b17b9bdb116 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=50 | 2026-10-20 / benched | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 12/12 / 29/29 | pfc_fb2e721d2bb8a41fe9fa3713 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=55 | 2026-10-21 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 11/11 / 29/29 | pfc_fbf508b9c62bae8f281bb6e1 |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=0 | 2026-10-30 / candidate | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | ROI unavailable; hit unavailable (0/0); 0 priced; coverage unavailable; provisional | 2/2 / 29/29 | pfc_fc7adf360790baec2b1ce044 |
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
| ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55 | Since activation | NAMED_BOOKMAKER_PRICE: 75/75; SCOUTINGSTATS_SOLE: 4/4; SUSPECT_ALIAS_FUZZY: 5/0 | NONE: 75/75; alias_fuzzy: 5/0; scoutingstats_sole_source: 4/4 | pfc_27e0f725859bc708f95c58a3 |
| ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55 | Last 30 days | NAMED_BOOKMAKER_PRICE: 75/75; SCOUTINGSTATS_SOLE: 4/4; SUSPECT_ALIAS_FUZZY: 5/0 | NONE: 75/75; alias_fuzzy: 5/0; scoutingstats_sole_source: 4/4 | pfc_27e0f725859bc708f95c58a3 |
| 1x2 single[scoutingstats] avg_p>=65 | Since activation | NAMED_BOOKMAKER_PRICE: 75/75; SCOUTINGSTATS_SOLE: 11/11; SUSPECT_ALIAS_FUZZY: 28/0 | NONE: 75/75; alias_fuzzy: 28/0; scoutingstats_sole_source: 11/11 | pfc_fdade2e70df4d4bb78a8cd6e |
| 1x2 single[scoutingstats] avg_p>=65 | Last 30 days | NAMED_BOOKMAKER_PRICE: 75/75; SCOUTINGSTATS_SOLE: 11/11; SUSPECT_ALIAS_FUZZY: 28/0 | NONE: 75/75; alias_fuzzy: 28/0; scoutingstats_sole_source: 11/11 | pfc_fdade2e70df4d4bb78a8cd6e |
| 1x2 single[scoutingstats] avg_p>=50 | Since activation | NAMED_BOOKMAKER_PRICE: 168/168; SCOUTINGSTATS_SOLE: 28/28; SUSPECT_ALIAS_FUZZY: 51/0 | NONE: 168/168; alias_fuzzy: 51/0; scoutingstats_sole_source: 28/28 | pfc_439097cb9bb700e9996c0b07 |
| 1x2 single[scoutingstats] avg_p>=50 | Last 30 days | NAMED_BOOKMAKER_PRICE: 168/168; SCOUTINGSTATS_SOLE: 28/28; SUSPECT_ALIAS_FUZZY: 51/0 | NONE: 168/168; alias_fuzzy: 51/0; scoutingstats_sole_source: 28/28 | pfc_439097cb9bb700e9996c0b07 |
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
| 1x2 unanimous[scoutingstats+statarea] avg_p>=60 | Since activation | NAMED_BOOKMAKER_PRICE: 8/8; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 8/8; alias_fuzzy: 1/0 | pfc_5904b1fc7050646e6321090c |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=60 | Last 30 days | NAMED_BOOKMAKER_PRICE: 8/8; SUSPECT_ALIAS_FUZZY: 1/0 | NONE: 8/8; alias_fuzzy: 1/0 | pfc_5904b1fc7050646e6321090c |
| 1x2 single[zulubet] avg_p>=55 | Since activation | NAMED_BOOKMAKER_PRICE: 10/10; SUSPECT_ALIAS_FUZZY: 1/0; UNMATCHED: 10/0 | NONE: 20/10; alias_fuzzy: 1/0 | pfc_1607fec83282d02c5254c2bf |
| 1x2 single[zulubet] avg_p>=55 | Last 30 days | NAMED_BOOKMAKER_PRICE: 10/10; SUSPECT_ALIAS_FUZZY: 1/0; UNMATCHED: 10/0 | NONE: 20/10; alias_fuzzy: 1/0 | pfc_1607fec83282d02c5254c2bf |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 | Since activation | NAMED_BOOKMAKER_PRICE: 7/7 | NONE: 7/7 | pfc_4a1f2bb2278d13c8189148d0 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 | Last 30 days | NAMED_BOOKMAKER_PRICE: 7/7 | NONE: 7/7 | pfc_4a1f2bb2278d13c8189148d0 |
| 1x2 single[scoutingstats] avg_p>=60 | Since activation | APPROVED_DONOR_PRICE: 1/1; NAMED_BOOKMAKER_PRICE: 3/3 | NONE: 4/4 | pfc_0f100c9da356ed1c05d9c642 |
| 1x2 single[scoutingstats] avg_p>=60 | Last 30 days | APPROVED_DONOR_PRICE: 1/1; NAMED_BOOKMAKER_PRICE: 3/3 | NONE: 4/4 | pfc_0f100c9da356ed1c05d9c642 |
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
| 2way-unanimous avg_p>=60 | Last 30 days | NAMED_BOOKMAKER_PRICE: 6/6; SCOUTINGSTATS_SOLE: 15/15; SOURCE_FALLBACK: 2/2; SUSPECT_ALIAS_FUZZY: 3/2; UNMATCHED: 23/0 | NONE: 30/7; alias_fuzzy: 3/2; scoutingstats_sole_source: 15/15; source_fallback_not_execution_eligible: 1/1 | 2way-unanimous avg_p>=60 |
| 2way-unanimous avg_p>=70 | Last 30 days | NAMED_BOOKMAKER_PRICE: 12/12; SCOUTINGSTATS_SOLE: 4/4; SUSPECT_ALIAS_FUZZY: 3/1; UNMATCHED: 5/0 | NONE: 17/12; alias_fuzzy: 3/1; scoutingstats_sole_source: 4/4 | 2way-unanimous avg_p>=70 |
| ml-meta avg_p>=55 | Last 30 days | APPROVED_DONOR_PRICE: 1/1; NAMED_BOOKMAKER_PRICE: 57/57; SCOUTINGSTATS_SOLE: 27/27; SOURCE_FALLBACK: 5/5; SUSPECT_ALIAS_FUZZY: 4/4; UNMATCHED: 26/0 | NONE: 84/58; alias_fuzzy: 4/4; scoutingstats_sole_source: 27/27; source_fallback_not_execution_eligible: 5/5 | ml-meta avg_p>=55 |
| ml-meta avg_p>=60 | Last 30 days | NAMED_BOOKMAKER_PRICE: 84/84; SCOUTINGSTATS_SOLE: 18/18; SOURCE_FALLBACK: 11/11; SUSPECT_ALIAS_FUZZY: 16/16; UNMATCHED: 16/0 | NONE: 99/84; alias_fuzzy: 16/16; scoutingstats_sole_source: 18/18; source_fallback_not_execution_eligible: 11/11; stale_quote: 1/0 | ml-meta avg_p>=60 |
| ml-meta avg_p>=65 | Last 30 days | NAMED_BOOKMAKER_PRICE: 4/4; SCOUTINGSTATS_SOLE: 3/3; SOURCE_FALLBACK: 1/1; UNMATCHED: 5/0 | NONE: 9/4; scoutingstats_sole_source: 3/3; source_fallback_not_execution_eligible: 1/1 | ml-meta avg_p>=65 |
| ml-meta avg_p>=80 | Last 30 days | NAMED_BOOKMAKER_PRICE: 3/3; SCOUTINGSTATS_SOLE: 1/1; UNMATCHED: 1/0 | NONE: 4/3; scoutingstats_sole_source: 1/1 | ml-meta avg_p>=80 |
| 1x2 single[zulubet] avg_p>=45 | Since activation | UNMATCHED: 1/0 | NONE: 1/0 | pfc_14ee12458803822df3013bcd |
| 1x2 single[zulubet] avg_p>=45 | Last 30 days | UNMATCHED: 1/0 | NONE: 1/0 | pfc_14ee12458803822df3013bcd |
| 1x2 single[zulubet] avg_p>=60 | Since activation | UNMATCHED: 1/0 | NONE: 1/0 | pfc_35f7e50bf23db96c2d3dd59d |
| 1x2 single[zulubet] avg_p>=60 | Last 30 days | UNMATCHED: 1/0 | NONE: 1/0 | pfc_35f7e50bf23db96c2d3dd59d |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35 | Last 30 days | NAMED_BOOKMAKER_PRICE: 35/35; SCOUTINGSTATS_SOLE: 1/1; SUSPECT_ALIAS_FUZZY: 2/0 | NONE: 35/35; alias_fuzzy: 2/0; scoutingstats_sole_source: 1/1 | pfc_73b036a8ee8dd5a4dea48134 |
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
| 1x2 single[scoutingstats] avg_p>=65 | 398 / 398 | 100.0% | 80.2% | 0.1% | start: 2026-06-13; split: 2026-09-27; as_of_exclusive: 2026-10-25 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_fdade2e70df4d4bb78a8cd6e |
| 1x2 single[scoutingstats] avg_p>=50 | 1235 / 1235 | 100.0% | 67.5% | 0.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_439097cb9bb700e9996c0b07 |
| 1x2 single[zulubet] avg_p>=50 | 1241 / 1240 | 99.9% | 57.4% | 0.5% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_4cf3df8552488297d7ccf526 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=0 | 438 / 438 | 100.0% | 61.2% | 2.9% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_0ad08cd1b2e75a2c9051189e |
| 1x2 unanimous[statarea+zulubet] avg_p>=40 | 278 / 277 | 99.6% | 61.9% | 1.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_5208b9e15194a691590430ad |
| 1x2 unanimous[vitibet+zulubet] avg_p>=50 | 427 / 427 | 100.0% | 66.5% | 4.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_234f16641d9893e8ec2a01f0 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=50 | 201 / 201 | 100.0% | 69.7% | 0.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_0b290b623e2a54ea7df3006c |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=60 | 203 / 203 | 100.0% | 81.3% | 6.8% | start: 2026-06-13; split: 2026-09-27; as_of_exclusive: 2026-10-25 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_5904b1fc7050646e6321090c |
| 1x2 single[zulubet] avg_p>=55 | 864 / 863 | 99.9% | 64.6% | 4.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_1607fec83282d02c5254c2bf |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 | 426 / 426 | 100.0% | 62.2% | 4.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_4a1f2bb2278d13c8189148d0 |
| 1x2 single[scoutingstats] avg_p>=60 | 566 / 566 | 100.0% | 76.3% | 0.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_0f100c9da356ed1c05d9c642 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=50 | 182 / 182 | 100.0% | 70.3% | 0.2% | start: 2026-06-13; split: 2026-09-28; as_of_exclusive: 2026-10-26 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_444d408c4ccd3a4bf4fb020c |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=40 | 822 / 822 | 100.0% | 59.7% | 0.2% | start: 2026-06-13; split: 2026-09-23; as_of_exclusive: 2026-10-21 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_d94d447efe0742440e953722 |
| 1x2 unanimous[statarea+zulubet] avg_p>=55 | 222 / 221 | 99.5% | 73.4% | 3.6% | start: 2026-06-13; split: 2026-09-23; as_of_exclusive: 2026-10-21 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_5a9d3d3426ee7a4e63461d75 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=55 | 358 / 358 | 100.0% | 68.2% | 2.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_2bd498a3472b7bbd71982ece |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 | 645 / 645 | 100.0% | 65.1% | 1.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_3bfaf30507905754f7faab2a |
| 1x2 unanimous[vitibet+zulubet] avg_p>=45 | 540 / 540 | 100.0% | 62.2% | 0.3% | start: 2026-06-13; split: 2026-09-29; as_of_exclusive: 2026-10-27 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_b011652ec3e473fbc0afbb6a |
| 2way-unanimous avg_p>=60 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 2way-unanimous avg_p>=60 |
| 2way-unanimous avg_p>=70 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | 2way-unanimous avg_p>=70 |
| ml-meta avg_p>=55 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | ml-meta avg_p>=55 |
| ml-meta avg_p>=60 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | ml-meta avg_p>=60 |
| ml-meta avg_p>=65 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | ml-meta avg_p>=65 |
| ml-meta avg_p>=80 | unavailable | unavailable | unavailable | unavailable | unavailable | unavailable | ml-meta avg_p>=80 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=35 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_054448b499623dd39b072b38 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=45 | 540 / 540 | 100.0% | 64.3% | 2.7% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_0aed63f3d04b46330958121d |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=45 | 240 / 240 | 100.0% | 60.0% | 0.4% | start: 2026-06-13; split: 2026-10-02; as_of_exclusive: 2026-10-30 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_144c01b1aa366b88f9c4083a |
| 1x2 single[zulubet] avg_p>=45 | 1488 / 1487 | 99.9% | 55.6% | 2.5% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_14ee12458803822df3013bcd |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=55 | 248 / 248 | 100.0% | 75.8% | 4.5% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_1ba3ab3c75e6f3a9680ae43c |
| 1x2 single[zulubet] avg_p>=40 | 1660 / 1659 | 99.9% | 53.2% | 0.9% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_1e9cfc6500aaac77afa1eaf9 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=40 | 360 / 360 | 100.0% | 60.8% | 4.0% | start: 2026-06-13; split: 2026-10-04; as_of_exclusive: 2026-11-01 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_226efd387e217a9d58a11f79 |
| 1x2 unanimous[statarea+zulubet] avg_p>=35 | 284 / 283 | 99.6% | 61.3% | 0.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_3072388544a60552346bd162 |
| 1x2 single[zulubet] avg_p>=60 | 633 / 632 | 99.8% | 67.6% | 3.8% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_35f7e50bf23db96c2d3dd59d |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=35 | 230 / 230 | 100.0% | 65.2% | 0.2% | start: 2026-06-13; split: 2026-09-30; as_of_exclusive: 2026-10-28 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_37f18dce9f6de45ee38e4944 |
| 1x2 single[zulubet] avg_p>=0 | 1733 / 1732 | 99.9% | 52.7% | 1.3% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_3dc0fa6511953bf09bc4c845 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=50 | 285 / 285 | 100.0% | 68.4% | 4.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_3fbabd0ade3f89853e43fb10 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=60 | 195 / 195 | 100.0% | 79.0% | 5.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_40b163633fc01fd0ff7d0ef1 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=55 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_4e2583010bf805466e33c2d0 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=0 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_4f2df06575151e798727a6b0 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=55 | 215 / 215 | 100.0% | 70.2% | 2.6% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_527524a94e98cff9740d499c |
| 1x2 single[zulubet] avg_p>=65 | 443 / 442 | 99.8% | 70.0% | 2.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_5954379f3a12700edcfd8387 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=50 | 372 / 372 | 100.0% | 68.0% | 0.3% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_5f861bad9f49ebf6d6fe2c16 |
| 1x2 single[zulubet] avg_p>=35 | 1732 / 1731 | 99.9% | 52.7% | 1.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_61cb1dd2a3157c4231070cdb |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=40 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_6cd236448d9fd967f8dcb591 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35 | 530 / 530 | 100.0% | 57.4% | 0.5% | start: 2026-06-13; split: 2026-10-03; as_of_exclusive: 2026-10-31 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_73b036a8ee8dd5a4dea48134 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=0 | 169 / 169 | 100.0% | 67.5% | 1.6% | start: 2026-06-13; split: 2026-09-26; as_of_exclusive: 2026-10-24 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_754f7247e83f901ae415b35f |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=35 | 438 / 438 | 100.0% | 61.2% | 2.9% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_7d20e19c2c26174fa21e9e86 |
| 1x2 unanimous[statarea+zulubet] avg_p>=45 | 314 / 313 | 99.7% | 66.9% | 2.5% | start: 2026-06-13; split: 2026-09-23; as_of_exclusive: 2026-10-21 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_7eb24434123da46374442290 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=45 | 208 / 208 | 100.0% | 67.3% | 0.4% | start: 2026-06-13; split: 2026-09-30; as_of_exclusive: 2026-10-28 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_84cede54e10853cd914d57c5 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=0 | 230 / 230 | 100.0% | 65.2% | 0.2% | start: 2026-06-13; split: 2026-09-30; as_of_exclusive: 2026-10-28 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_8e39a2c5719c5a609c077afd |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=0 | 530 / 530 | 100.0% | 57.4% | 0.5% | start: 2026-06-13; split: 2026-10-03; as_of_exclusive: 2026-10-31 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_92ab281aa7c2173e7502ba49 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=45 | 229 / 229 | 100.0% | 67.7% | 0.6% | start: 2026-06-13; split: 2026-09-26; as_of_exclusive: 2026-10-24 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_9ae5a305a703bca83fd321b3 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=45 | 316 / 316 | 100.0% | 69.6% | 1.0% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_a460a0e9dcb1f980cde169c0 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=40 | 354 / 354 | 100.0% | 65.0% | 0.3% | start: 2026-06-13; split: 2026-10-02; as_of_exclusive: 2026-10-30 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_a7ba6711aeb15b9804a94f06 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=35 | 169 / 169 | 100.0% | 67.5% | 1.6% | start: 2026-06-13; split: 2026-09-26; as_of_exclusive: 2026-10-24 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_a8e99ebc0016f0d0bb95aa70 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=60 | 128 / 128 | 100.0% | 81.2% | 3.0% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_a90a9b922d2318a2446434ce |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=35 | 240 / 240 | 100.0% | 60.0% | 0.4% | start: 2026-06-13; split: 2026-10-02; as_of_exclusive: 2026-10-30 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_adb24b31e9ca43c42506156a |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=50 | 240 / 240 | 100.0% | 60.0% | 0.4% | start: 2026-06-13; split: 2026-10-02; as_of_exclusive: 2026-10-30 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_afdf26c0a105a0f5e6ffff27 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=50 | 210 / 210 | 100.0% | 65.7% | 0.1% | start: 2026-06-13; split: 2026-09-30; as_of_exclusive: 2026-10-28 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_b0b7a0c1932e3636d2b485d6 |
| 1x2 unanimous[statarea+zulubet] avg_p>=0 | 284 / 283 | 99.6% | 61.3% | 0.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_b11e22bfdd27d85fad78ba74 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=0 | 367 / 367 | 100.0% | 60.2% | 3.3% | start: 2026-06-13; split: 2026-10-04; as_of_exclusive: 2026-11-01 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_b4407145af67d2f93e48f0ef |
| btts disagree_follow[bettingclosed+scoutingstats] follow=scoutingstats avg_p>=40 | 240 / 240 | 100.0% | 60.0% | 0.4% | start: 2026-06-13; split: 2026-10-02; as_of_exclusive: 2026-10-30 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_b9aa429be62178cc76b1ca8d |
| ou_3.5 unanimous[scoutingstats+statarea] avg_p>=70 | 366 / 366 | 100.0% | 80.6% | 0.5% | start: 2026-06-13; split: 2026-09-27; as_of_exclusive: 2026-10-25 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_bdce95a736d6cc8667f7ac31 |
| 1x2 unanimous[statarea+zulubet] avg_p>=50 | 271 / 270 | 99.6% | 70.5% | 3.9% | start: 2026-06-13; split: 2026-09-23; as_of_exclusive: 2026-10-21 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_c83d885867c9025a351b9b8c |
| 1x2 single[zulubet] avg_p>=70 | 242 / 241 | 99.6% | 74.0% | 2.7% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_c8cbcf76ea758fd6de596ae1 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=40 | 287 / 287 | 100.0% | 61.0% | 2.7% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_cd84fb2c3ed889c0ae9eb89e |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=0 | 138 / 138 | 100.0% | 60.1% | 1.9% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_cddf4106a3d45b6e455d8c73 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=55 | 177 / 177 | 100.0% | 71.8% | 0.4% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_d17123b85e11155f22e40051 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea+vitibet] avg_p>=35 | 367 / 367 | 100.0% | 60.2% | 3.3% | start: 2026-06-13; split: 2026-10-04; as_of_exclusive: 2026-11-01 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_d5c311b6e2f37443e3501556 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=45 | 372 / 372 | 100.0% | 63.7% | 2.5% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_e25602082a90cb64fb9c5451 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=45 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_e37e7d70a4d046d7a07da0a4 |
| 1x2 unanimous[scoutingstats+statarea+vitibet+zulubet] avg_p>=40 | 174 / 174 | 100.0% | 66.1% | 0.5% | start: 2026-06-13; split: 2026-09-30; as_of_exclusive: 2026-10-28 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_e5c10af025fc5071367c9b47 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=55 | 239 / 239 | 100.0% | 74.9% | 4.3% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_f2b2a2e84093abe72bbc01c0 |
| ou_1.5 unanimous[scoutingstats+statarea] avg_p>=50 | 129 / 129 | 100.0% | 80.6% | 2.2% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_f51b5fdaf32bcca063f4b2cc |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=35 | 137 / 137 | 100.0% | 60.6% | 2.7% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_f56fe4a2759e9b17b9bdb116 |
| 1x2 unanimous[scoutingstats+zulubet] avg_p>=50 | 291 / 291 | 100.0% | 70.8% | 0.1% | start: 2026-06-13; split: 2026-09-22; as_of_exclusive: 2026-10-20 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_fb2e721d2bb8a41fe9fa3713 |
| 1x2 unanimous[statarea+vitibet+zulubet] avg_p>=55 | 156 / 156 | 100.0% | 69.9% | 0.6% | start: 2026-06-13; split: 2026-09-23; as_of_exclusive: 2026-10-21 | retrospective_same_side_donor; live prices require existing evidence gates | pfc_fbf508b9c62bae8f281bb6e1 |
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
- **Over 2.5 Goals**: occurred in 559 / 922 matches (60.6%)
- **Both Teams to Score (BTTS)**: occurred in 491 / 922 matches (53.3%)
- **Selected Team Over 1.5 Goals**: occurred in 594 / 918 matches (64.7%)

## Recommended Enhancements Audit

Performance of deep context-derived recommended enhancements overlay:
- **Total Recommended Enhancements**: 482
- **Total Hits**: 366
- **Overall Hit Rate**: 75.9%

### Breakdown by Enhancement Type:
- `away_over_05`: recommended=18, settled=18, hit_rate=88.9% (hits=16/recommended=18), priced_n=1, priced_ROI=0.64 (denominator=1), registry_processed=63, class=priced
- `away_under_15`: recommended=7, settled=7, hit_rate=85.7% (hits=6/recommended=7), priced_n=6, priced_ROI=1.508333 (denominator=6), registry_processed=11, class=priced
- `away_under_25`: recommended=13, settled=13, hit_rate=84.6% (hits=11/recommended=13), priced_n=13, priced_ROI=0.469154 (denominator=13), registry_processed=45, class=priced
- `away_under_35`: recommended=91, settled=91, hit_rate=97.8% (hits=89/recommended=91), priced_n=1, priced_ROI=0.435 (denominator=1), registry_processed=305, class=priced
- `btts_no`: recommended=8, settled=8, hit_rate=37.5% (hits=3/recommended=8), priced_n=5, priced_ROI=-0.45 (denominator=5), registry_processed=12, class=priced
- `btts_yes`: recommended=5, settled=5, hit_rate=100.0% (hits=5/recommended=5), priced_n=3, priced_ROI=0.853333 (denominator=3), registry_processed=22, class=priced
- `home_over_05`: recommended=24, settled=24, hit_rate=87.5% (hits=21/recommended=24), priced_n=2, priced_ROI=0.345 (denominator=2), registry_processed=189, class=priced
- `home_over_15`: recommended=2, settled=2, hit_rate=100.0% (hits=2/recommended=2), priced_n=1, priced_ROI=1.8 (denominator=1), registry_processed=9, class=priced
- `home_under_15`: recommended=2, settled=2, hit_rate=100.0% (hits=2/recommended=2), priced_n=2, priced_ROI=0.381 (denominator=2), registry_processed=9, class=priced
- `home_under_25`: recommended=1, settled=1, hit_rate=0.0% (hits=0/recommended=1), priced_n=1, priced_ROI=-1.0 (denominator=1), registry_processed=56, class=priced
- `home_under_35`: recommended=23, settled=23, hit_rate=95.7% (hits=22/recommended=23), priced_n=1, priced_ROI=1.66 (denominator=1), registry_processed=76, class=priced
- `match_over_15`: recommended=27, settled=27, hit_rate=85.2% (hits=23/recommended=27), priced_n=20, priced_ROI=0.16525 (denominator=20), registry_processed=74, class=priced
- `match_over_25`: recommended=222, settled=222, hit_rate=62.6% (hits=139/recommended=222), priced_n=181, priced_ROI=0.04037 (denominator=181), registry_processed=754, class=priced
- `match_over_35`: recommended=18, settled=18, hit_rate=77.8% (hits=14/recommended=18), priced_n=11, priced_ROI=1.036364 (denominator=11), registry_processed=49, class=priced
- `match_over_45`: recommended=2, settled=2, hit_rate=100.0% (hits=2/recommended=2), priced_n=2, priced_ROI=4.0 (denominator=2), registry_processed=3, class=priced
- `match_under_35`: recommended=8, settled=8, hit_rate=25.0% (hits=2/recommended=8), priced_n=7, priced_ROI=-0.625714 (denominator=7), registry_processed=10, class=priced
- `match_under_45`: recommended=11, settled=11, hit_rate=81.8% (hits=9/recommended=11), priced_n=6, priced_ROI=0.276667 (denominator=6), registry_processed=22, class=priced

## Possible Events (🔥) Full-Surface Audit

> ⚠️ **Calibration ≠ edge.** No prices in this section — a hit-rate is not value. Certification and staking remain gated by the enhancement registry.

> ⚠️ **Winner's-curse display effect (Addendum 27.17):** LINE_THRESHOLDS show only high-side notes (e.g. home_under_35 iff p≥0.90), so realized systematically trails promised on display-filtered markets — part of any promised−realized gap here is the selection effect of the display filter, not engine error.

Every machine-readable 🔥 note on every settled pick in the window, scored against the final score (plain-market: a note hits iff its market lands in the final score (selection-independent for match totals and BTTS; the 1X2 selection only picks the team for team totals and the double-chance leg)).

- notes on settled picks: **1900** | scored: 1900 | without promised % (legacy rows): 192

### Per-market hit table

| market | notes | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `match_over_25` | 449 | 394 | 232 | 58.9% | 50.0% | +8.9% | 0.251949 |
| `match_over_45` | 230 | 229 | 47 | 20.5% | 24.0% | -3.5% | 0.166792 |
| `away_under_35` | 207 | 207 | 204 | 98.6% | 95.9% | +2.7% | 0.015103 |
| `away_under_25` | 214 | 205 | 190 | 92.7% | 89.5% | +3.1% | 0.064235 |
| `match_over_35` | 134 | 128 | 68 | 53.1% | 42.7% | +10.4% | 0.269825 |
| `btts_yes` | 96 | 92 | 55 | 59.8% | 47.1% | +12.7% | 0.248418 |
| `btts_no` | 89 | 85 | 36 | 42.4% | 54.1% | -11.7% | 0.252474 |
| `home_under_35` | 85 | 84 | 79 | 94.0% | 97.0% | -2.9% | 0.055595 |
| `home_under_25` | 83 | 68 | 62 | 91.2% | 87.7% | +3.5% | 0.08458 |
| `away_over_05` | 52 | 42 | 35 | 83.3% | 79.5% | +3.9% | 0.127338 |
| `home_over_05` | 41 | 39 | 33 | 84.6% | 86.0% | -1.4% | 0.118549 |
| `away_under_15` | 44 | 38 | 26 | 68.4% | 75.9% | -7.4% | 0.189504 |
| `match_over_15` | 33 | 30 | 24 | 80.0% | 84.3% | -4.3% | 0.160763 |
| `match_under_25` | 43 | 27 | 11 | 40.7% | 40.8% | -0.0% | 0.242527 |
| `home_under_15` | 18 | 11 | 9 | 81.8% | 67.0% | +14.8% | 0.242189 |
| `match_under_35` | 21 | 10 | 4 | 40.0% | 62.4% | -22.4% | 0.275791 |
| `home_over_15` | 17 | 8 | 2 | 25.0% | 46.9% | -21.9% | 0.241596 |
| `match_under_45` | 25 | 6 | 4 | 66.7% | 80.4% | -13.8% | 0.248672 |
| `away_over_15` | 7 | 5 | 4 | 80.0% | 59.7% | +20.3% | 0.215626 |

Labels render plain-market exactly as promised, priced and scored: `match_over_15` → "Match Over 1.5 Goals"; `match_over_25` → "Match Over 2.5 Goals"; `btts_yes` → "Both Teams to Score - Yes (BTTS-Yes)". Raw archive labels written before 2026-08-03 may still carry the old "Win + …" wording in their stored label field; the render normalizes them.

### By probability engine (🔥)

> `model` = blended rates + Poisson prior · `hybrid_cohort` = outcome-unconditioned empirical cohort anchor · `legacy` = archived before engine tagging.

| engine | n | hits | realized | promised avg | Δ | Brier |
| --- | --- | --- | --- | --- | --- | --- |
| hybrid_cohort | 1633 | 1067 | 65.3% | 62.8% | +2.5% | 0.164243 |
| model | 75 | 58 | 77.3% | 67.2% | +10.2% | 0.177223 |


### Promised-vs-realized calibration (all 🔥 notes pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.1-0.2 | 52 | 19.1% | 25.0% | +5.9% |
| 0.2-0.3 | 159 | 24.5% | 19.5% | -5.0% |
| 0.3-0.4 | 108 | 36.0% | 45.4% | +9.4% |
| 0.4-0.5 | 399 | 44.8% | 55.6% | +10.8% |
| 0.5-0.6 | 183 | 54.6% | 51.4% | -3.2% |
| 0.6-0.7 | 73 | 63.5% | 58.9% | -4.6% |
| 0.7-0.8 | 37 | 74.0% | 70.3% | -3.7% |
| 0.8-0.9 | 284 | 86.1% | 88.0% | +1.9% |
| 0.9-1.0 | 413 | 94.7% | 96.1% | +1.4% |

## Statistical Line (📊) Calibration

> ⚠️ **Calibration ≠ edge.** The 📊 line promises historical frequencies, not prices — this section scores promise vs realization only and must not drive staking.

Scored as probabilistic forecasts per settled pick (each active metric is scored as a probabilistic forecast of its event (Over 2.5 / BTTS-Yes / Home|Away Over 1.5) — calibration, not a direction call; the retired exact-score field remains in machine history only).

- **Avg Goals forecast**: n=946, MAE=1.498446 goals, bias=-0.185719 (realized − promised), promised avg 3.361195 vs realized 3.175476

### Per-metric calibration

| metric | n | promised avg | realized | Δ | Brier |
| --- | --- | --- | --- | --- | --- |
| Away Over 1.5 | 946 | 33.2% | 33.6% | +0.4% | 0.198973 |
| BTTS-Yes | 946 | 47.8% | 53.3% | +5.4% | 0.254332 |
| Home Over 1.5 | 946 | 58.5% | 53.3% | -5.3% | 0.223789 |
| Over 2.5 | 946 | 65.1% | 60.5% | -4.6% | 0.242222 |

### Promised-vs-realized calibration (all 📊 metrics pooled)

| promised bucket | n | promised avg | realized | Δ |
| --- | --- | --- | --- | --- |
| 0.0-0.1 | 160 | 8.7% | 21.9% | +13.2% |
| 0.1-0.2 | 380 | 12.8% | 16.3% | +3.5% |
| 0.2-0.3 | 298 | 23.7% | 27.2% | +3.5% |
| 0.3-0.4 | 131 | 35.3% | 43.5% | +8.2% |
| 0.4-0.5 | 466 | 42.3% | 48.9% | +6.6% |
| 0.5-0.6 | 897 | 55.6% | 58.1% | +2.5% |
| 0.6-0.7 | 742 | 64.9% | 59.0% | -5.9% |
| 0.7-0.8 | 269 | 75.0% | 70.3% | -4.7% |
| 0.8-0.9 | 389 | 84.8% | 63.5% | -21.3% |
| 0.9-1.0 | 52 | 92.1% | 76.9% | -15.2% |

## By rule

Counts are frozen PICK ROWS, not bets: SKIPPED_VETO / WATCHLIST_* rows are included and were never cardable. See the full audit’s `## By bucket` for bucket-level counts. These are not acca returns or bank performance.

ROI uses priced rows only; hit rate uses all settled rows. The 30-priced-row cutoff is a reporting sample flag, not proof of profitability or an activation gate. Registry status/certification are separate from this audit window. Historical ml-meta rules are not the live ML ENH acca selector.

### Positive ROI (1 rule)

| Rule | Priced ROI | Priced sample | Hit rate | Evidence | Registry context | Stored rule ID/key |
| --- | ---: | ---: | --- | --- | --- | --- |
| ml-meta avg_p>=55 | +22.0% | 94 priced | 73.3% (88/120 settled) | 30+ priced rows | legacy rule key | ml-meta avg_p>=55 |

### Negative ROI (5 rules)

| Rule | Priced ROI | Priced sample | Hit rate | Evidence | Registry context | Stored rule ID/key |
| --- | ---: | ---: | --- | --- | --- | --- |
| ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55 | -2.0% | 79 priced | 61.9% (52/84 settled) | 30+ priced rows | contract · benched, activated 2026-10-23, certified valid n=347 | pfc_27e0f725859bc708f95c58a3 |
| 1x2 single[scoutingstats] avg_p>=65 | -2.1% | 86 priced | 78.9% (90/114 settled) | 30+ priced rows | contract · certified, activated 2026-10-25, certified valid n=398 | pfc_fdade2e70df4d4bb78a8cd6e |
| ml-meta avg_p>=60 | -4.0% | 129 priced | 60.7% (88/145 settled) | 30+ priced rows | legacy rule key | ml-meta avg_p>=60 |
| 1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35 | -4.9% | 36 priced | 52.6% (20/38 settled) | 30+ priced rows | contract · certified, activated 2026-10-31, certified valid n=530 | pfc_73b036a8ee8dd5a4dea48134 |
| 1x2 single[scoutingstats] avg_p>=50 | -5.1% | 196 priced | 60.7% (150/247 settled) | 30+ priced rows | contract · benched, activated 2026-10-20, certified valid n=1235 | pfc_439097cb9bb700e9996c0b07 |

### Break-even (0 rules)

- none

### Insufficient priced evidence (31 rules)

| Rule | Priced ROI | Priced sample | Hit rate | Evidence | Registry context | Stored rule ID/key |
| --- | ---: | ---: | --- | --- | --- | --- |
| 1x2 single[zulubet] avg_p>=50 | +90.0% | 2 priced | 50.0% (2/4 settled) | PROVISIONAL: 2 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=1241 | pfc_4cf3df8552488297d7ccf526 |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=0 | +55.2% | 4 priced | 75.0% (3/4 settled) | PROVISIONAL: 4 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=438 | pfc_0ad08cd1b2e75a2c9051189e |
| unanimous[betclan+statarea+vitibet] avg_p>=65 | +50.0% | 2 priced | 100.0% (2/2 settled) | PROVISIONAL: 2 priced < 30 | legacy rule key | unanimous[betclan+statarea+vitibet] avg_p>=65 |
| 1x2 unanimous[statarea+zulubet] avg_p>=40 | +44.0% | 1 priced | 100.0% (1/1 settled) | PROVISIONAL: 1 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=278 | pfc_5208b9e15194a691590430ad |
| unanimous[vitibet+zulubet] avg_p>=70 | +39.2% | 5 priced | 100.0% (5/5 settled) | PROVISIONAL: 5 priced < 30 | legacy rule key | unanimous[vitibet+zulubet] avg_p>=70 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=50 | +34.6% | 5 priced | 81.8% (9/11 settled) | PROVISIONAL: 5 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=427 | pfc_234f16641d9893e8ec2a01f0 |
| unanimous[betclan+vitibet] avg_p>=70 | +34.1% | 13 priced | 94.1% (16/17 settled) | PROVISIONAL: 13 priced < 30 | legacy rule key | unanimous[betclan+vitibet] avg_p>=70 |
| unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65 | +18.0% | 2 priced | 100.0% (2/2 settled) | PROVISIONAL: 2 priced < 30 | legacy rule key | unanimous[bzzoiro+statarea+vitibet+zulubet] avg_p>=65 |
| unanimous[statarea+vitibet] avg_p>=70 | +17.2% | 16 priced | 90.5% (19/21 settled) | PROVISIONAL: 16 priced < 30 | legacy rule key | unanimous[statarea+vitibet] avg_p>=70 |
| 1x2 unanimous[scoutingstats+vitibet+zulubet] avg_p>=50 | +16.5% | 2 priced | 50.0% (1/2 settled) | PROVISIONAL: 2 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=201 | pfc_0b290b623e2a54ea7df3006c |
| 1x2 unanimous[vitibet+zulubet] avg_p>=45 | +16.3% | 9 priced | 63.6% (7/11 settled) | PROVISIONAL: 9 priced < 30 | contract · benched, activated 2026-10-27, certified valid n=540 | pfc_b011652ec3e473fbc0afbb6a |
| unanimous[bzzoiro+vitibet+zulubet] avg_p>=65 | +15.0% | 1 priced | 100.0% (1/1 settled) | PROVISIONAL: 1 priced < 30 | legacy rule key | unanimous[bzzoiro+vitibet+zulubet] avg_p>=65 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=60 | +14.9% | 8 priced | 66.7% (6/9 settled) | PROVISIONAL: 8 priced < 30 | contract · benched, activated 2026-10-25, certified valid n=203 | pfc_5904b1fc7050646e6321090c |
| 1x2 single[zulubet] avg_p>=55 | +13.3% | 10 priced | 61.9% (13/21 settled) | PROVISIONAL: 10 priced < 30 | contract · certified, activated 2026-10-20, certified valid n=864 | pfc_1607fec83282d02c5254c2bf |
| 1x2 unanimous[scoutingstats+statarea+vitibet] avg_p>=40 | +11.1% | 7 priced | 57.1% (4/7 settled) | PROVISIONAL: 7 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=426 | pfc_4a1f2bb2278d13c8189148d0 |
| 1x2 single[scoutingstats] avg_p>=60 | +9.7% | 4 priced | 75.0% (3/4 settled) | PROVISIONAL: 4 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=566 | pfc_0f100c9da356ed1c05d9c642 |
| ml-meta avg_p>=80 | +9.0% | 4 priced | 100.0% (5/5 settled) | PROVISIONAL: 4 priced < 30 | legacy rule key | ml-meta avg_p>=80 |
| 2way-unanimous avg_p>=70 | +3.8% | 17 priced | 79.2% (19/24 settled) | PROVISIONAL: 17 priced < 30 | legacy rule key | 2way-unanimous avg_p>=70 |
| unanimous[statarea+vitibet+zulubet] avg_p>=65 | -2.5% | 2 priced | 50.0% (1/2 settled) | PROVISIONAL: 2 priced < 30 | legacy rule key | unanimous[statarea+vitibet+zulubet] avg_p>=65 |
| 1x2 unanimous[scoutingstats+statarea+zulubet] avg_p>=50 | -3.3% | 2 priced | 66.7% (2/3 settled) | PROVISIONAL: 2 priced < 30 | contract · candidate, activated 2026-10-26, certified valid n=182 | pfc_444d408c4ccd3a4bf4fb020c |
| unanimous[bzzoiro+vitibet] avg_p>=70 | -3.6% | 13 priced | 69.2% (9/13 settled) | PROVISIONAL: 13 priced < 30 | legacy rule key | unanimous[bzzoiro+vitibet] avg_p>=70 |
| ml-meta avg_p>=65 | -8.2% | 8 priced | 76.9% (10/13 settled) | PROVISIONAL: 8 priced < 30 | legacy rule key | ml-meta avg_p>=65 |
| 2way-unanimous avg_p>=60 | -14.7% | 25 priced | 57.1% (28/49 settled) | PROVISIONAL: 25 priced < 30 | legacy rule key | 2way-unanimous avg_p>=60 |
| 1x2 unanimous[scoutingstats+statarea] avg_p>=40 | -17.4% | 12 priced | 38.5% (5/13 settled) | PROVISIONAL: 12 priced < 30 | contract · benched, activated 2026-10-21, certified valid n=822 | pfc_d94d447efe0742440e953722 |
| unanimous[bzzoiro+statarea+vitibet] avg_p>=65 | -33.5% | 4 priced | 60.0% (3/5 settled) | PROVISIONAL: 4 priced < 30 | legacy rule key | unanimous[bzzoiro+statarea+vitibet] avg_p>=65 |
| 1x2 unanimous[statarea+zulubet] avg_p>=55 | -34.5% | 2 priced | 33.3% (1/3 settled) | PROVISIONAL: 2 priced < 30 | contract · benched, activated 2026-10-21, certified valid n=222 | pfc_5a9d3d3426ee7a4e63461d75 |
| 1x2 unanimous[vitibet+zulubet] avg_p>=55 | -100.0% | 1 priced | 50.0% (1/2 settled) | PROVISIONAL: 1 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=358 | pfc_2bd498a3472b7bbd71982ece |
| 1x2 unanimous[scoutingstats+vitibet] avg_p>=50 | -100.0% | 1 priced | 0.0% (0/1 settled) | PROVISIONAL: 1 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=645 | pfc_3bfaf30507905754f7faab2a |
| 1x2 single[zulubet] avg_p>=45 | unavailable | 0 priced | 0.0% (0/1 settled) | PROVISIONAL: 0 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=1488 | pfc_14ee12458803822df3013bcd |
| 1x2 single[zulubet] avg_p>=60 | unavailable | 0 priced | 100.0% (1/1 settled) | PROVISIONAL: 0 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=633 | pfc_35f7e50bf23db96c2d3dd59d |
| 1x2 single[zulubet] avg_p>=70 | unavailable | 0 priced | 100.0% (1/1 settled) | PROVISIONAL: 0 priced < 30 | contract · benched, activated 2026-10-20, certified valid n=242 | pfc_c8cbcf76ea758fd6de596ae1 |


## By bucket

- `CAUTION`: settled=153, wins=104, hit_rate=0.679739 (settled n=153), ROI=0.061074 (priced n=153)
- `CERTIFIED_CLEAN`: settled=92, wins=57, hit_rate=0.619565 (settled n=92), ROI=-0.027133 (priced n=92)
- `SKIPPED_VETO`: settled=517, wins=351, hit_rate=0.678917 (settled n=517), ROI=0.025389 (priced n=464)
- `WATCHLIST_NO_ODDS`: settled=73, wins=46, hit_rate=0.630137 (settled n=73), ROI=None (priced n=0)
- `WATCHLIST_SUSPECT_PRICE`: settled=88, wins=55, hit_rate=0.625 (settled n=88), ROI=-0.068 (priced n=10)
- `WATCHLIST_UNCORROBORATED_PRICE`: settled=66, wins=43, hit_rate=0.651515 (settled n=66), ROI=-0.03803 (priced n=66)
- `WATCHLIST_UNKNOWN_CTX`: settled=17, wins=12, hit_rate=0.705882 (settled n=17), ROI=-0.159665 (priced n=17)

## By odds source

- `UNKNOWN`: settled=204, wins=133, hit_rate=0.651961 (settled n=204), ROI=None (priced n=0)
- `betexplorer_odds`: settled=136, wins=108, hit_rate=0.794118 (settled n=136), ROI=0.046618 (priced n=136)
- `boggio`: settled=2, wins=2, hit_rate=1.0 (settled n=2), ROI=0.486 (priced n=2)
- `oddspapi_odds`: settled=10, wins=5, hit_rate=0.5 (settled n=10), ROI=-0.1325 (priced n=10)
- `pinnapi_odds`: settled=367, wins=224, hit_rate=0.610354 (settled n=367), ROI=-0.016059 (priced n=367)
- `scoutingstats_odds`: settled=116, wins=79, hit_rate=0.681034 (settled n=116), ROI=-0.011466 (priced n=116)
- `sharpapi_odds`: settled=1, wins=1, hit_rate=1.0 (settled n=1), ROI=0.741 (priced n=1)
- `theoddsapi`: settled=127, wins=91, hit_rate=0.716535 (settled n=127), ROI=0.113622 (priced n=127)
- `zulubet`: settled=43, wins=25, hit_rate=0.581395 (settled n=43), ROI=-0.02814 (priced n=43)

## By odds match method

- `alias_fuzzy`: settled=122, wins=80, hit_rate=0.655738 (settled n=122), ROI=-0.042609 (priced n=23)
- `alias_time`: settled=3, wins=2, hit_rate=0.666667 (settled n=3), ROI=0.081567 (priced n=3)
- `exact`: settled=756, wins=508, hit_rate=0.671958 (settled n=756), ROI=0.018108 (priced n=756)
- `fallback`: settled=20, wins=11, hit_rate=0.55 (settled n=20), ROI=-0.0115 (priced n=20)
- `none`: settled=105, wins=67, hit_rate=0.638095 (settled n=105), ROI=None (priced n=0)

## Price Evidence / Corroboration Audit

> Price provenance is not model quality. `SCOUTINGSTATS_SOLE` is retained for audit but quarantined from push eligibility; `SUSPECT_ALIAS_FUZZY` is never allowed to replace operational best odds.

| price evidence | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| APPROVED_DONOR_PRICE (`APPROVED_DONOR_PRICE`) | 2 | 2 | 1.0 | 2 | 0.486 |
| NAMED_BOOKMAKER_PRICE (`NAMED_BOOKMAKER_PRICE`) | 641 | 429 | 0.669267 | 641 | 0.022297 |
| ScoutingStats sole fallback (`SCOUTINGSTATS_SOLE`) | 116 | 79 | 0.681034 | 116 | -0.011466 |
| Source fallback (`SOURCE_FALLBACK`) | 20 | 11 | 0.55 | 20 | -0.0115 |
| Suspect alias_fuzzy candidate (`SUSPECT_ALIAS_FUZZY`) | 122 | 80 | 0.655738 | 23 | -0.042609 |
| No usable price (`UNMATCHED`) | 105 | 67 | 0.638095 | 0 | None |

## Veto Deep Dive

> SKIPPED_VETO cross-cut by price evidence, odds band and veto reason, > computed from the SAME settled rows as the bucket table. > `trusted evidence only` excludes the soft labels: > SCOUTINGSTATS_SOLE, SOURCE_FALLBACK, SUSPECT_ALIAS_FUZZY, UNMATCHED.

| cut | settled | wins | hit rate | priced | ROI |
| --- | --- | --- | --- | --- | --- |
| **overall (SKIPPED_VETO)** | 517 | 351 | 0.678917 | 464 | 0.025389 |
| **trusted evidence only** | 395 | 265 | 0.670886 | 395 | 0.027849 |
| **soft evidence only** | 122 | 86 | 0.704918 | 69 | 0.011304 |
| evidence: NAMED_BOOKMAKER_PRICE | 395 | 265 | 0.670886 | 395 | 0.027849 |
| evidence: SCOUTINGSTATS_SOLE | 50 | 36 | 0.72 | 50 | 0.0236 |
| evidence: SOURCE_FALLBACK | 6 | 4 | 0.666667 | 6 | -0.016667 |
| evidence: SUSPECT_ALIAS_FUZZY | 34 | 25 | 0.735294 | 13 | -0.023077 |
| evidence: UNMATCHED | 32 | 21 | 0.65625 | 0 | None |
| odds band: <1.50 | 201 | 162 | 0.80597 | 201 | 0.022929 |
| odds band: 1.50-2.00 | 210 | 125 | 0.595238 | 210 | 0.003674 |
| odds band: 2.00-3.00 | 49 | 25 | 0.510204 | 49 | 0.130612 |
| odds band: >=3.00 | 4 | 1 | 0.25 | 4 | 0.0 |
| odds band: unpriced | 53 | 38 | 0.716981 | 0 | None |
| veto reason: UNRECORDED | 1 | 1 | 1.0 | 1 | 0.2 |
| veto reason: context VETO in ['competition_type'] | 47 | 39 | 0.829787 | 37 | 0.099557 |
| veto reason: context VETO in ['league', 'niche'] | 33 | 22 | 0.666667 | 25 | -0.14022 |
| veto reason: context VETO in ['league', 'odds_band', 'niche'] | 6 | 2 | 0.333333 | 6 | -0.40825 |
| veto reason: context VETO in ['league', 'odds_band'] | 51 | 29 | 0.568627 | 51 | -0.003408 |
| veto reason: context VETO in ['league', 'team_a'] | 3 | 0 | 0.0 | 3 | -1.0 |
| veto reason: context VETO in ['league', 'team_h', 'competition_type'] | 2 | 2 | 1.0 | 2 | 0.3881 |
| veto reason: context VETO in ['league', 'team_h', 'niche'] | 6 | 4 | 0.666667 | 5 | 0.186 |
| veto reason: context VETO in ['league', 'team_h', 'team_a'] | 2 | 2 | 1.0 | 2 | 0.7476 |
| veto reason: context VETO in ['league', 'team_h'] | 1 | 1 | 1.0 | 1 | 0.29 |
| veto reason: context VETO in ['league'] | 65 | 39 | 0.6 | 54 | -0.168119 |
| veto reason: context VETO in ['niche'] | 38 | 29 | 0.763158 | 35 | 0.033474 |
| veto reason: context VETO in ['odds_band', 'niche'] | 6 | 3 | 0.5 | 6 | -0.022667 |
| veto reason: context VETO in ['odds_band'] | 106 | 59 | 0.556604 | 106 | -0.026606 |
| veto reason: context VETO in ['team_a', 'competition_type'] | 6 | 5 | 0.833333 | 6 | 0.20035 |
| veto reason: context VETO in ['team_a', 'niche'] | 3 | 2 | 0.666667 | 3 | 0.146667 |
| veto reason: context VETO in ['team_a', 'odds_band'] | 6 | 6 | 1.0 | 6 | 0.466667 |
| veto reason: context VETO in ['team_a'] | 43 | 34 | 0.790698 | 36 | 0.2528 |
| veto reason: context VETO in ['team_h', 'competition_type'] | 13 | 11 | 0.846154 | 12 | 0.082017 |
| veto reason: context VETO in ['team_h', 'niche'] | 4 | 3 | 0.75 | 3 | 0.446667 |
| veto reason: context VETO in ['team_h', 'odds_band'] | 4 | 3 | 0.75 | 4 | 0.01 |
| veto reason: context VETO in ['team_h', 'team_a', 'competition_type'] | 1 | 1 | 1.0 | 1 | 0.23 |
| veto reason: context VETO in ['team_h', 'team_a', 'niche'] | 1 | 1 | 1.0 | 1 | 0.62 |
| veto reason: context VETO in ['team_h', 'team_a'] | 14 | 11 | 0.785714 | 13 | 0.307254 |
| veto reason: context VETO in ['team_h'] | 32 | 22 | 0.6875 | 22 | 0.126364 |
| veto reason: short-odds away favourite 1.02 | 1 | 1 | 1.0 | 1 | 0.02 |
| veto reason: short-odds away favourite 1.04 | 1 | 1 | 1.0 | 1 | 0.041 |
| veto reason: short-odds away favourite 1.05 | 1 | 1 | 1.0 | 1 | 0.05 |
| veto reason: short-odds away favourite 1.08 | 1 | 1 | 1.0 | 1 | 0.08 |
| veto reason: short-odds away favourite 1.10 | 1 | 0 | 0.0 | 1 | -1.0 |
| veto reason: short-odds away favourite 1.16 | 2 | 2 | 1.0 | 2 | 0.16 |
| veto reason: short-odds away favourite 1.17 | 1 | 1 | 1.0 | 1 | 0.17 |
| veto reason: short-odds away favourite 1.18 | 1 | 1 | 1.0 | 1 | 0.1845 |
| veto reason: short-odds away favourite 1.20 | 1 | 1 | 1.0 | 1 | 0.2 |
| veto reason: short-odds away favourite 1.22 | 2 | 2 | 1.0 | 2 | 0.22 |
| veto reason: short-odds away favourite 1.23 | 1 | 1 | 1.0 | 1 | 0.2342 |
| veto reason: short-odds away favourite 1.24 | 2 | 0 | 0.0 | 2 | -1.0 |
| veto reason: short-odds away favourite 1.25 | 3 | 3 | 1.0 | 3 | 0.25 |
| veto reason: short-odds away favourite 1.26 | 1 | 1 | 1.0 | 1 | 0.2591 |
| veto reason: short-odds away favourite 1.27 | 1 | 1 | 1.0 | 1 | 0.27 |
| veto reason: short-odds away favourite 1.28 | 2 | 2 | 1.0 | 2 | 0.2785 |
| veto reason: short-odds away favourite 1.29 | 1 | 1 | 1.0 | 1 | 0.29 |
| contrast CAUTION: APPROVED_DONOR_PRICE | 1 | 1 | 1.0 | 1 | 0.452 |
| contrast CAUTION: NAMED_BOOKMAKER_PRICE | 150 | 102 | 0.68 | 150 | 0.059815 |
| contrast CAUTION: SOURCE_FALLBACK | 2 | 1 | 0.5 | 2 | -0.04 |

## Suspect-price Quarantine Audit

> Rows remain in the frozen ledger and are scored here. Quarantine removes push eligibility; it does not erase adverse evidence from the audit window.

| quarantine reason | settled | wins | hit rate | priced | ROI | suspect captures | avg suspect price |
| --- | --- | --- | --- | --- | --- | --- | --- |
| No price quarantine (`NONE`) | 748 | 497 | 0.664439 | 644 | 0.022149 | 0 | None |
| alias_fuzzy match (`alias_fuzzy`) | 122 | 80 | 0.655738 | 23 | -0.042609 | 122 | 1.557257 |
| ScoutingStats sole source (`scoutingstats_sole_source`) | 116 | 79 | 0.681034 | 116 | -0.011466 | 0 | None |
| source_fallback_not_execution_eligible (`source_fallback_not_execution_eligible`) | 19 | 11 | 0.578947 | 19 | 0.040526 | 0 | None |
| stale_quote (`stale_quote`) | 1 | 1 | 1.0 | 0 | None | 0 | None |
## Settled Picks Granular Expectations Audit

Visual audit of expected historical stats (from the `📊` line) against actual realized scores:

### 2026-10-31: San Martín San Juan vs Gimnasia Jujuy (Actual Score: **5-1**)
- **1X2 Pick**: Selected `HOME` @ 1.5848 -> 🟢 WON (Expected prob: 67.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 6 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Nanjing City vs Dalian Kuncheng City (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.5208 -> 🟢 WON (Expected prob: 67.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.8% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 50.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Acassuso vs Club Ferro Carril Oeste (Actual Score: **0-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.3268 -> 🔴 LOST (Expected prob: 75.4%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.4% (Actual: 0 goals)
  - [🟢 HIT] **BTTS-No**: expected 46.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 84.7% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 75.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Middlesbrough vs Charlton Athletic (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.29 -> 🟢 WON (Expected prob: 75.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 50.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 3 goals)

### 2026-10-31: Stockport County vs AFC Wimbledon (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.2488 -> 🟢 WON (Expected prob: 75.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Real Betis vs Málaga (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.3436 -> 🟢 WON (Expected prob: 72.4%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Boreham Wood vs Hartlepool United (Actual Score: **4-3**)
- **1X2 Pick**: Selected `HOME` @ 1.2793 -> 🟢 WON (Expected prob: 71.7%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 7 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 4 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Godoy Cruz vs Almirante Brown (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.4149 -> 🟢 WON (Expected prob: 71.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: FC Bayern München vs Borussia Dortmund (Actual Score: **2-2**)
- **1X2 Pick**: Selected `HOME` @ 1.3401 -> 🔴 LOST (Expected prob: 70.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 4 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: The New Saints vs Connah's Quay (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.2882 -> 🔴 LOST (Expected prob: 70.5%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.8% (Actual: 0 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 50.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: LASK Linz vs WSG Tirol (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.3448 -> 🟢 WON (Expected prob: 69.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Hegelmann Litauen vs Kauno Žalgiris (Actual Score: **1-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.3322 -> 🟢 WON (Expected prob: 69.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.4% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-No**: expected 46.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 84.7% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 75.1% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Mito Hollyhock vs Sanfrecce Hiroshima (Actual Score: **0-3**)
- **1X2 Pick**: Selected `AWAY` @ 1.4274 -> 🟢 WON (Expected prob: 68.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.4% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-No**: expected 46.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 84.7% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 75.1% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Fenerbahçe vs Göztepe (Actual Score: **1-2**)
- **1X2 Pick**: Selected `HOME` @ 1.3195 -> 🔴 LOST (Expected prob: 67.5%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 2 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Maidstone United vs Slough Town (Actual Score: **2-1**)
- **1X2 Pick**: Selected `HOME` @ 1.4016 -> 🟢 WON (Expected prob: 66.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 3 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Al Hilal vs Al Fateh (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ 1.1 -> 🟢 WON (Expected prob: 85.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.8% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 50.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Mačva Šabac vs Crvena Zvezda (Actual Score: **2-4**)
- **1X2 Pick**: Selected `AWAY` @ 1.1845 -> 🟢 WON (Expected prob: 77.8%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 64.4% (Actual: 6 goals)
  - [🔴 MISS] **BTTS-No**: expected 46.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Under 1.5 Goals**: expected 84.7% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Over 1.5 Goals**: expected 75.1% (Actual: 4 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Rudeš vs Dinamo Zagreb (Actual Score: **1-0**)
- **1X2 Pick**: Selected `AWAY` @ 1.2353 -> 🔴 LOST (Expected prob: 74.2%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.4% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 46.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 84.7% (Actual: 1 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 75.1% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Columbus Crew vs DC United (Actual Score: **3-0**)
- **1X2 Pick**: Selected `HOME` @ 1.3356 -> 🟢 WON (Expected prob: 69.9%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 3 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 50.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 3 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: New York City vs CF Montréal (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.4049 -> 🔴 LOST (Expected prob: 67.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.8% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Radnik Bijeljina vs Siroki Brijeg (Actual Score: **2-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 59.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 59.7% (Actual: 2 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 51.5% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 62.8% (Actual: 2 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 76.8% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Dunav 2010 vs Levski Sofia (Actual Score: **0-1**)
- **1X2 Pick**: Selected `AWAY` @ n/a -> 🟢 WON (Expected prob: 75.6%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 64.4% (Actual: 1 goals)
  - [🟢 HIT] **BTTS-No**: expected 46.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Under 1.5 Goals**: expected 84.7% (Actual: 0 goals)
  - [🔴 MISS] **Away Team Over 1.5 Goals**: expected 75.1% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Hajduk Split vs Gorica (Actual Score: **5-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 68.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 5 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 50.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 5 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Beitar Jerusalem vs Ironi Kiryat Shmona (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🔴 LOST (Expected prob: 67.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.8% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Wydad Casablanca vs Moghreb Tétouan (Actual Score: **1-0**)
- **1X2 Pick**: Selected `HOME` @ n/a -> 🟢 WON (Expected prob: 66.0%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.8% (Actual: 1 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 50.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Mamelodi Sundowns vs Durban City (Actual Score: **4-1**)
- **1X2 Pick**: Selected `HOME` @ 1.25 -> 🟢 WON (Expected prob: 71.6%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: FC Barcelona vs Deportivo Alavés (Actual Score: **6-1**)
- **1X2 Pick**: Selected `HOME` @ 1.1045 -> 🟢 WON (Expected prob: 86.0%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 7 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 6 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Feyenoord vs Fortuna Sittard (Actual Score: **1-1**)
- **1X2 Pick**: Selected `HOME` @ 1.2 -> 🔴 LOST (Expected prob: 81.7%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.8% (Actual: 2 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.4% (Actual: BTTS-Yes)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 1 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 1 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Porto vs Estoril (Actual Score: **4-0**)
- **1X2 Pick**: Selected `HOME` @ 1.24 -> 🟢 WON (Expected prob: 81.1%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 4 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 50.4% (Actual: BTTS-No)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 4 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**:
    - [🟢 HIT] **Match Over 2.5 Goals**: expected n/a (Actual: 4 goals)

### 2026-10-31: CSKA Sofia vs Slavia Sofia (Actual Score: **0-0**)
- **1X2 Pick**: Selected `HOME` @ 1.2155 -> 🔴 LOST (Expected prob: 78.3%)
  - [🔴 MISS] **Over 2.5 Goals**: expected 65.8% (Actual: 0 goals)
  - [🔴 MISS] **BTTS-Yes**: expected 50.4% (Actual: BTTS-No)
  - [🔴 MISS] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 0 goals)
  - [🟢 HIT] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 0 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick

### 2026-10-31: Partick Thistle vs Greenock Morton (Actual Score: **2-3**)
- **1X2 Pick**: Selected `HOME` @ 1.1976 -> 🔴 LOST (Expected prob: 75.3%)
  - [🟢 HIT] **Over 2.5 Goals**: expected 65.8% (Actual: 5 goals)
  - [🟢 HIT] **BTTS-Yes**: expected 50.4% (Actual: BTTS-Yes)
  - [🟢 HIT] **Home Team Over 1.5 Goals**: expected 74.9% (Actual: 2 goals)
  - [🔴 MISS] **Away Team Under 1.5 Goals**: expected 80.5% (Actual: 3 goals)
  - **🔥 Possible Events (graded)**: none recorded on the archived pick


## Event Disposition / Void Audit

| disposition | voided picks |
| --- | --- |
| CANCELLED | 1 |
| POSTPONED | 6 |
- 2026-10-03 `CANCELLED` `CAUTION` — Sri Lanka vs Djibouti (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-10-23 `POSTPONED` `CAUTION` — Gateshead vs Tamworth (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-10-23 `POSTPONED` `SKIPPED_VETO` — Holywell vs Penybont (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-10-24 `POSTPONED` `CAUTION` — Glentoran vs Ballymena United (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-10-24 `POSTPONED` `CAUTION` — Slovan Liberec vs Baník Ostrava (source_status:scoutingstats); excluded from win/loss/ROI
- 2026-10-28 `POSTPONED` `SKIPPED_VETO` — Navalcarnero vs Real Betis (verified_disposition); excluded from win/loss/ROI
- 2026-10-28 `POSTPONED` `WATCHLIST_SUSPECT_PRICE` — Salamanca CF UDS vs Celta de Vigo (source_status:scoutingstats); excluded from win/loss/ROI

## Rescheduled Fixture Examples

- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Tampa Bay Rowdies vs Miami FC -> HOME @ None (rescheduled → 2026-10-03; actual Tampa Bay Rowdies 1-2 Miami FC [away])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Brooklyn vs Rhode Island FC -> AWAY @ None (rescheduled → 2026-10-03; actual Brooklyn 1-3 Rhode Island [away])
- 2026-10-04 `WATCHLIST_NO_ODDS` `2way-unanimous avg_p>=60` — Kano Pillars FC vs Sporting Lagos -> HOME @ None (rescheduled → 2026-10-03; actual Kano Pillars 1-1 Sporting Lagos [draw])
- 2026-10-18 `SKIPPED_VETO` `unanimous[bzzoiro+vitibet] avg_p>=70` — Hartford Athletic vs Brooklyn -> HOME @ 1.44 (rescheduled → 2026-10-17; actual Hartford Athletic 2-3 Brooklyn [away])
- 2026-10-21 `WATCHLIST_UNCORROBORATED_PRICE` `1x2 single[scoutingstats] avg_p>=50` — Cerro Porteño vs Sportivo Ameliano -> HOME @ 1.65 (rescheduled → 2026-10-18; actual Cerro Porteno 2-2 Sportivo Ameliano [draw])
- 2026-10-25 `WATCHLIST_SUSPECT_PRICE` `1x2 single[scoutingstats] avg_p>=65` — Paris Saint Germain vs Olympique Lyonnais -> HOME @ None (rescheduled → 2026-10-26; actual Paris Saint Germain 2-0 Olympique Lyonnais [home])

## Pending / Unmatched Result Examples

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
- 2026-10-25 `CAUTION` `ou_2.5 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=55` — Sporting CP vs Académico Viseu FC -> OVER @ 1.3953 (pending_or_unmatched_result); keys=['cp', 'lisbon']/['academico']
- 2026-10-25 `WATCHLIST_UNCORROBORATED_PRICE` `1x2 single[scoutingstats] avg_p>=65` — Sporting CP vs Academico Viseu -> HOME @ 1.22 (pending_or_unmatched_result); keys=['cp', 'lisbon']/['academico']
- 2026-10-28 `SKIPPED_VETO` `1x2 unanimous[bzzoiro+scoutingstats+statarea] avg_p>=35` — Liverpool FC vs Chelsea -> HOME @ 2.3 (pending_or_unmatched_result); keys=['liverpool']/['chelsea']

## Ambiguous result examples

- 2026-10-21 `WATCHLIST_NO_ODDS` `1x2 single[zulubet] avg_p>=65` — Guadalajara W vs Necaxa W (ambiguous_alias_result)
