# Visual Generator Recovery — Decisions

## Architecture Decisions
- Style Sheet 메커니즘: 첫 슬라이드에서 `{output_path}/style_sheet.md` 생성, 이후 슬라이드는 Follow
- prompt-validator: 7차원으로 재설계 (4개 유지 + 3개 신규 - 2개 제거)
  - 제거: v1.11.0 Compliance, Korean Text Quality
  - 신규: Font Name Leakage Detection, Text Density Validation, Palette Consistency Check
- 밀도 기준: 본문 슬라이드 ≥ 8항목, 타이틀 슬라이드 ≥ 3항목
- 버전: visual-generator → 2.2.0, AGENTS.md → 2.7.0

## Audit Decision (F4, 2026-03-09)
- Scope fidelity is rejected until T6 warning-parity is restored across all 6 theme SKILL.md files.
