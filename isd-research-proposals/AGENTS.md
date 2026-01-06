# ISD RESEARCH PROPOSALS - KNOWLEDGE BASE

**Parent:** [../AGENTS.md](../AGENTS.md)

## OVERVIEW

Korean government R&D proposal (국책과제 연구계획서) auto-generation system with 5 chapters and master orchestrator.

## STRUCTURE

```
isd-research-proposals/
├── isd-orchestrator/           # Master: invokes chapter generators in order
├── chapter1-generator/         # 개발 대상 및 필요성 (from Ch3)
├── chapter2-generator/         # 국내외 시장 및 기술 동향
├── chapter3-generator/         # 사업 목표 및 추진 전략 (FIRST)
├── chapter4-generator/         # 기대효과 및 활용방안
└── chapter5-generator/         # 기타 참고자료 (NTIS check)
```

## WHERE TO LOOK

| Task | Location |
|------|----------|
| Full auto-generation | `isd-orchestrator/skills/SKILL.md` |
| Input template | `isd-orchestrator/skills/references/input_template.md` |
| Chapter output templates | `chapter{N}-generator/skills/assets/output_template/` |
| Example documents | `chapter{N}-generator/skills/references/example_*.md` |

## CONVENTIONS

### Generation Order (CRITICAL)
```
Chapter 3 → Chapter 1 → Chapter 2 → Chapter 4 → Chapter 5
```
- Chapter 3 defines core goals/tech → Chapter 1 derives necessity
- Chapter 1/3 inform market analysis (Ch2) and expected effects (Ch4)
- Chapter 5 collects all references + NTIS similarity check

### Verification Documents (절대 스킵 금지)
| Chapter | Verification File | Phase |
|---------|-------------------|-------|
| Ch3 | `chapter3_research_verification.md` | Phase 1-4 |
| Ch1 | `chapter1_research_verification.md` | Phase 2-6 |
| Ch2 | `chapter2_research_verification.md` | Phase 3-5 |
| Ch4 | `chapter4_analysis_verification.md` | Phase 1-VERIFY |
| Ch5 | `chapter5_ntis_verification.md` | Phase 0-3 |

### Output Structure
```
output/[프로젝트명]/
├── chapter_{1-5}/          # Main documents
├── verification/           # All verification docs
├── figures/                # Generated images
├── prompts/                # Image prompts
└── execution_report.md     # Final report
```

### Document Requirements
| Chapter | Lines | Tables | Images |
|---------|-------|--------|--------|
| Ch1 | 300-400 | 8+ | 5-8 |
| Ch2 | 500-600 | 15-25 | - |
| Ch3 | varies | varies | Yes (prompts) |
| Ch4 | varies | varies | - |
| Ch5 | varies | varies | - |

## ANTI-PATTERNS

- Starting with Chapter 1 (must start Chapter 3)
- Skipping verification doc generation
- Mismatched data between chapters (정합성 위반)
- Using placeholder text in Korean documents

## CROSS-CHAPTER VALIDATION

| Source | Target | Check |
|--------|--------|-------|
| Ch3 정량목표 | Ch4 기대성과 | Numbers match |
| Ch1 VoC 기업 | Ch4 수요기업 | Included |
| Ch3 참여기관 | Ch5 참여의향서 | All listed |
| Ch2 인용번호 | Ch5 참고문헌 | All present |
