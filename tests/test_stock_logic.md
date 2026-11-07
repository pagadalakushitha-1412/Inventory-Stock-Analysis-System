# Manual test evidence template

| Test | Action | Expected result | Actual result |
|---|---|---|---|
| T01 | Add product with valid unique SKU | Saved | Pending |
| T02 | Add duplicate SKU | Rejected; no duplicate row | Pending |
| T03 | Stock in 10 units | Current stock increases by 10 | Pending |
| T04 | Stock out within available balance | Current stock decreases | Pending |
| T05 | Stock out above available balance | Rejected; stock unchanged | Pending |
| T06 | Zero quantity movement | Rejected | Pending |
| T07 | Adjustment -2 when available stock is 1 | Rejected | Pending |
| T08 | Current stock equals reorder level | Marked low stock | Pending |
| T09 | Export report CSV | Downloaded report has expected columns | Pending |
| T10 | Database unavailable | Health endpoint returns error | Pending |

Replace Pending with Pass/Fail and attach screenshots from your own run before submission.
