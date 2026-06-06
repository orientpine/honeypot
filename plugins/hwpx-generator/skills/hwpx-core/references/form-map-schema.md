# Form Map Schema Contract (v1.0.0)

This document defines the `form_map.json` schema used by the `hwpx-generator` form-comprehension pipeline (Workflow 7). It serves as the shared contract between the deterministic `form_mapper.py` script and the reasoning-capable `HWPX-form-analyzer` agent.

## 1. Schema Overview

The `form_map.json` file maps semantic slots in a HWPX template to specific paragraph or cell addresses.

```json
{
  "schema_version": "1.0.0",
  "source_template": "template.hwpx",
  "slots": [
    {
      "slot_id": "research_goal",
      "slot_type": "empty_input",
      "addressing": {
        "method": "paragraph_id",
        "paragraph_id": "9000000001",
        "cell": null
      },
      "label_association": "연구 목표",
      "zone": "detail",
      "confidence": "high",
      "expected_content_hint": "연구의 최종 목표 및 핵심 기술"
    }
  ],
  "unresolved": [],
  "confidence": "high"
}
```

## 2. Field Definitions

### Top-level Fields
- `schema_version` (string): Semantic version of the schema.
- `source_template` (string): Filename of the HWPX template analyzed.
- `slots` (array): List of successfully mapped slots.
- `unresolved` (array): List of potential slots found but not successfully addressed.
- `confidence` (enum): Overall confidence in the mapping.

### Slot Fields
- `slot_id` (string): Unique identifier for the slot (usually derived from the label).
- `slot_type` (enum): The semantic role of the slot.
  - `empty_input`: A placeholder paragraph intended to be replaced by user content.
    - Criteria: `<hp:t/>`, whitespace only, or single symbol (◦, ○, •, -, ※, ·, □, ■).
  - `label`: A static label identifying a field (e.g., "Project Name:").
  - `instruction`: Guidance text (e.g., "[Write at least 200 words]").
  - `summary`: A slot in a summary table (요약표).
  - `detail`: A slot in the main body (본문 상세).
  - `inline_after_label`: Content to be appended immediately after a label in the same paragraph.
- `addressing` (object): Technical location of the slot.
  - `method` (enum): `paragraph_id` | `sentinel` | `unresolved`.
  - `paragraph_id` (string|null): The unique ID of the `<hp:p>` element (e.g., "9000000001").
  - `cell` (object|null): Table coordinates if the slot is inside a table.
    - `{ "table_index": int, "row": int, "col": int }`
- `label_association` (string): The text of the nearest label or header associated with this slot.
- `zone` (enum): Mapping to builder's Dual-Zone behavior.
  - `summary`: Maps to "요약표 셀: 200자 요약" rule.
  - `detail`: Maps to "본문 상세: 전체" rule.
  - `none`: No specific zone behavior applied.
- `confidence` (enum): `high` | `medium` | `low`.
- `expected_content_hint` (string, optional): Description of what content should go here.

## 3. Responsibility Split

| Component | Ownership | Role |
|-----------|-----------|------|
| `form_mapper.py` | `addressing` payloads | Deterministic extraction of paragraph IDs and table structures. |
| `HWPX-form-analyzer` (Agent) | `slot_type`, `label_association`, `zone`, `confidence` | Semantic reasoning to determine what a slot represents and which zone it belongs to. |

**Determinism Contract**: Given an identical `form_map.json`, the `slot_filler.py` output must be byte-reproducible. Agent reasoning occurs only during the **creation** of the map, never during its consumption by the builder.

## 4. Dual-Zone Reconciliation

The `zone` field reconciles with the existing `hwpx-builder` Dual-Zone 3 rules:
1. **Summary Zone**: If `zone: "summary"`, the filler extracts a 200-character summary from the source markdown section.
2. **Detail Zone**: If `zone: "detail"`, the filler inserts the full markdown content.
3. **Order**: Detail zones are processed first to provide context for summary extraction.

## 5. Role Boundaries

- **form_map.json**: Defines **where** content goes (addressing) and **what** it represents (semantics).
- **style-map.json**: Defines **how** content looks (charPr/paraPr/borderFill IDs).
These files are siblings and must not be merged.

## 6. Complete Example

```json
{
  "schema_version": "1.0.0",
  "source_template": "isd_template_v3.hwpx",
  "slots": [
    {
      "slot_id": "summary_table_goal",
      "slot_type": "summary",
      "addressing": {
        "method": "paragraph_id",
        "paragraph_id": "1000000005",
        "cell": { "table_index": 0, "row": 1, "col": 1 }
      },
      "label_association": "연구개발 목표",
      "zone": "summary",
      "confidence": "high"
    },
    {
      "slot_id": "main_content_tech",
      "slot_type": "empty_input",
      "addressing": {
        "method": "sentinel",
        "paragraph_id": null,
        "cell": null
      },
      "label_association": "2. 기술개발 내용",
      "zone": "detail",
      "confidence": "medium",
      "expected_content_hint": "Detailed technical implementation"
    }
  ],
  "unresolved": [
    {
      "slot_id": "unknown_placeholder",
      "slot_type": "empty_input",
      "addressing": {
        "method": "unresolved",
        "paragraph_id": null,
        "cell": null
      },
      "label_association": null,
      "zone": "none",
      "confidence": "low"
    }
  ],
  "confidence": "medium"
}
```
