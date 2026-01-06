# PRESENTATIONS - KNOWLEDGE BASE

**Parent:** [../AGENTS.md](../AGENTS.md)

## OVERVIEW

PPT-style infographic generation for Korean R&D proposals. Extracts `<caption>` patterns, generates prompts, creates images via Gemini API.

## STRUCTURE

```
presentations/
├── figure-generator/           # Full pipeline: extract → prompt → image
│   ├── scripts/                # Python: generate_images.py
│   └── skills/                 # SKILL.md + references
├── slide-prompt-generator/     # Prompt-only generation
│   └── skills/                 # Layout types, style guide
└── slide-image-generator/      # Image generation from prompts
    └── scripts/                # generate_slide_images.py
```

## WHERE TO LOOK

| Task | Location |
|------|----------|
| Generate figures from docs | `figure-generator/skills/SKILL.md` |
| Prompt writing guide | `figure-generator/skills/references/prompt_guide.md` |
| Layout type selection | `slide-prompt-generator/skills/references/layout_types.md` |
| Example prompts (1040 lines) | `figure-generator/skills/references/example_prompts.md` |
| Python image generator | `figure-generator/scripts/generate_images.py` |

## CONVENTIONS

### Caption Pattern
```
<이미지명>                           # Basic
<이미지명, 출처: 기관명 (연도)>       # With source
```

### 9 Caption Types
| Type | Keywords | Layout |
|------|----------|--------|
| 비전/목표 | 목표, 비전, 개념도 | Pyramid |
| 로드맵 | 로드맵, 일정, 타임라인 | Timeline |
| 연차별 | 연차별, 단계별 | Table/Timeline |
| 추진체계 | 추진체계, 조직, 역할 | Org chart |
| 투자계획 | 투자, 예산, 재원 | Bar chart |
| 협력체계 | 협력, 네트워크 | Network diagram |
| 사업화 | 사업화, 상용화 | Flow chart |
| 개념도 | 개념, 구조, 아키텍처 | Block diagram |
| 기술분류 | 기술분류, 체계 | Tech tree |

### 4-Color Palette (Default)
| Role | HEX | Use |
|------|-----|-----|
| Primary | #1E3A5F | Titles, key boxes |
| Secondary | #4A90A4 | Arrows, processes |
| Accent | #2E7D5A | Achievements |
| Background | #F5F7FA | Background |

### Prompt Quality Requirements
- **500+ lines** per prompt
- **14 mandatory sections** (all required)
- **6 ASCII layouts** (full, top, left, right-top, right-bottom, bottom)
- **50+ text items** categorized
- **8+ data tables** with sources
- **10+ tech term checklist**
- **NO placeholders** (`[내용]`, `[항목]` forbidden)

## ANTI-PATTERNS

| Forbidden | Reason |
|-----------|--------|
| `"텍스트" (24pt)` in ASCII | Font size renders in image |
| `← 네이비 배경` arrows | Annotations render in image |
| `[설명 텍스트]` brackets | Instructions render in image |
| Placeholders `[내용]` | Gemini renders literally |
| < 500 lines prompt | Quality gate fails |

## API SETTINGS

```python
MODEL_NAME = "gemini-3-pro-image-preview"
ASPECT_RATIO = "16:9"
IMAGE_SIZE = "4K"
# Rate limit: 2s delay between calls
# Max retries: 3 with 5s backoff
```

## NOTES

- Gemini API key in scripts - replace for production
- Sections 13-14 (sources, checklist) excluded from API call to save tokens
- `auto_mode=true` skips user confirmation
- `parallel_mode=true` spawns subagents for 5+ captions
