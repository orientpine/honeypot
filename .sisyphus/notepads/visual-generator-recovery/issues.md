# Visual Generator Recovery — Issues

## Known Issues
1. 폰트명 유출: korean-typography-spec.md, scene-richness-spec.md, 6개 테마 SKILL.md, prompt-designer.md에 걸쳐 총 10개 파일에 산재
2. 최소 텍스트 밀도 강제 메커니즘 부재 — 파이프라인의 구조적 근본 원인
3. 슬라이드 간 일관성 보장 메커니즘 부재 (Style Sheet 없음)
4. prompt-validator의 일부 차원이 중복/시대착오적

## Resolved
(will be updated as tasks complete)

## Audit Findings (F4, 2026-03-09)
1. T6 partial failure: `plugins/visual-generator/skills/theme-concept/SKILL.md` does not include explicit font-name warning marker (for example, TYPOGRAPHY CRITICAL / warning block) while other theme files do.
