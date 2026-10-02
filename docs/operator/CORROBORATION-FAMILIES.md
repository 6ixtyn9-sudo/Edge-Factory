# Bookmaker corroboration families (SHADOW-03 W3-T3)

Independence is counted per **bookmaker**, not per API donor. Different
transports carrying the same book are one family and never create a second
corroborating voice.

| donor rows | family |
|---|---|
| `pinnapi_odds` | `pinnacle` |
| `sharpapi_odds` | the row's `book` value |
| `scoutingstats` | `scoutingstats` (unnamed) |
| `theoddsapi_odds` | the recorded `book`/`bookmaker` value |
| KDobrev or another Pinnacle relay | `pinnacle` |

The documentation-grade helper `edgefactory.corroboration.bookmaker_family`
is tested but is deliberately not called by live corroboration. Promotion code
must opt in only after settled evidence and an explicit operator decision.
Multiple donors for one family are deduplicated, never counted as independent.
