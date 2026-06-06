# HWPX Form Fixture Addressing Findings

## Fixtures

- `form_simple.hwpx`: 3×2 form table. Two label/input pairs are left→right; the third pair is top→bottom inside a `colSpan=2` cell, followed by one body empty paragraph.
- `form_merged.hwpx`: 3×2 table with a merged header cell (`colSpan=2`) and empty input cells.
- `form_edge.hwpx`: 2×2 table with two byte-similar empty input cells plus a body placeholder paragraph.

## Paragraph ID uniqueness spike

CONFIRMED: All <hp:p> elements in all 3 fixtures have unique `id` attributes, including empty cells inside table subLists.

| Fixture | `<hp:p>` IDs found | Result | ID range |
|---|---:|---|---|
| `form_simple.hwpx` | 9 | unique | `1000000001`–`1000000009` |
| `form_merged.hwpx` | 7 | unique | `1000000001`–`1000000007` |
| `form_edge.hwpx` | 7 | unique | `1000000001`–`1000000007` |

The required `grep -c '<hp:p id=' /tmp/sec.xml` command returns `2` for each fixture because the generated section XML is pretty-printed into two physical lines that contain one or more `<hp:p id=` occurrences. The regex spike counts actual occurrences and confirms uniqueness.

## Empty-cell addressing result

- Empty table cells have unique paragraph IDs.
- `form_simple.hwpx` empty input IDs: `1000000004`, `1000000006`, `1000000008`; body placeholder ID: `1000000009`.
- `form_merged.hwpx` empty input IDs: `1000000005`, `1000000007`.
- `form_edge.hwpx` contains two empty input paragraphs with identical `paraPrIDRef="22"` and `charPrIDRef="0"` structure, but different IDs: `1000000004`, `1000000006`.

## Exceptions / fallback needed

No addressing fallback is needed for these fixtures. Paragraph-id addressing is sufficient for exact slot targeting, including byte-similar empty cells in table subLists.

## Evidence

- `.omo/evidence/task-2-fixture-ids.txt`: uniqueness check output for `form_simple.hwpx`.
- `.omo/evidence/task-2-merged.txt`: `analyze_template.py form_merged.hwpx` output showing `colSpan=2`.
- All three fixtures pass `validate.py` in standard mode with exit code 0.
