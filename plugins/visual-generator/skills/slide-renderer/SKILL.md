---
name: slide-renderer
description: "Gemini API를 사용한 슬라이드 이미지 렌더링 스킬. renderer-agent가 프롬프트 파일을 이미지로 변환할 때 사용. generate_slide_images.py 스크립트 실행 가이드, 환경 요구사항, 출력 해석, 에러 처리 방법을 포함합니다."
---

# Slide Renderer

Gemini API를 사용하여 프롬프트 파일(.md)을 4K 16:9 JPEG 이미지로 변환하는 스크립트 실행 가이드.

## 스크립트 참조 및 실행 (CRITICAL)

스크립트는 이 스킬의 상대경로에 위치합니다:

scripts/generate_slide_images.py

**실행 순서:**

**Step 1. 상대경로로 실행** (최우선)
```bash
python scripts/generate_slide_images.py \
  --prompts-dir [프롬프트 폴더 경로] \
  --output-dir [이미지 출력 폴더 경로]
```

**Step 2. 상대경로 실패 시 Glob 폴백**
```
Glob: **/visual-generator/skills/slide-renderer/scripts/generate_slide_images.py
```

**Step 3. Glob도 실패 시 확장 탐색**
```
Glob: **/generate_slide_images.py
```

**절대 금지**: 스크립트를 찾지 못했을 때 자체적으로 Python 코드를 작성하지 마세요.
반드시 에러를 보고하고 사용자에게 경로 확인을 요청하세요.

## 환경 요구사항

| 항목 | 설명 |
|------|------|
| Python | 3.8+ |
| 패키지 | google-genai, Pillow |
| 환경변수 | `GEMINI_API_KEY` 필수 |
| 모델 | gemini-3-pro-image-preview |
| 출력 | 4K, 16:9 비율 JPEG |

## 스크립트 출력 해석

| 출력 패턴 | 의미 | 처리 |
|-----------|------|------|
| `[OK] Saved:` | 이미지 생성 성공 | 성공 카운트 증가 |
| `[FAIL] Failed:` | 이미지 생성 실패 | 재시도 대상 추가 |
| `[SKIP] Already exists:` | 파일 이미 존재 | 스킵 카운트 증가 |
| `[에러]` | API 오류 또는 시스템 오류 | 로그 기록 |
| `[품질 평가] 시도 N/M: 평균 X.X (한글:Y, 환각:Y, 정확도:Y, 레이아웃:Y, 색상:Y) → 통과/재시도` | 5차원 품질 평가 결과 | 통과 시 이미지 채택, 재시도 시 피드백 힌트 포함 재생성 |

## 에러 처리

### 에러 유형별 처리

| 에러 유형 | 처리 방법 | 최대 재시도 |
|-----------|-----------|:-----------:|
| GEMINI_API_KEY 미설정 | 즉시 중단, 사용자 안내 | 0 |
| API 타임아웃 | 5초 대기 후 재시도 | 3 |
| API 응답 없음 | 5초 대기 후 재시도 | 3 |
| 이미지 데이터 없음 | 5초 대기 후 재시도 | 3 |
| 파일 쓰기 오류 | 권한 확인, 사용자 안내 | 0 |

### 재시도 로직

```
실패 발생
  → 재시도 가능 여부 판단 (현재 시도 < 3)
    → YES: 5초 대기 → 해당 프롬프트만 재실행 (기존 성공 파일은 자동 스킵)
    → NO: 최종 실패 목록에 추가, 사유 기록
```

## Quality Evaluation Criteria

이미지 생성 후 5차원 품질 평가를 실시한다. 각 차원은 0-10점으로 평가된다.

### 5-Dimension Evaluation System

| 차원 | 설명 | 최저 임계값 |
|------|------|:-----------:|
| `korean_text_readability` | 한글 텍스트 선명도, 자모 결합 정확성, 가독성 | 5.0 (veto) |
| `korean_hallucination_detection` | CONTENT에 없는 한글이 이미지에 존재하는지 (10=깨끗) | 5.0 (veto) |
| `content_reference_accuracy` | CONTENT에 명시된 텍스트가 정확히 렌더링되었는지 | — |
| `layout_suitability` | 레이아웃 구성, 시각 계층, 공간 균형 | — |
| `color_palette_compliance` | 지정 팔레트 준수 여부 | — |

### Tiered Evaluation Logic

PASS 조건: 전체 평균 ≥ 7.0 AND korean_text_readability ≥ 5.0 (veto) AND korean_hallucination_detection ≥ 5.0 (veto)

**veto 방식**: 한글 차원 중 하나라도 5.0 미만이면 전체 평균과 무관하게 자동 FAIL.

### concept 테마 면제

concept 테마는 텍스트 항목이 없으므로 한글 평가 차원을 자동으로 10.0으로 설정한다.
프롬프트에 "concept", "zero text rendering", 또는 "zero-text rendering"이 포함되면 면제 적용.

## Korean Text Safety

generate_slide_images.py는 3중 방어 체계의 inference 계층을 담당한다.

### SYSTEM_INSTRUCTION Anti-Hallucination

스크립트의 SYSTEM_INSTRUCTION에 Korean Text Hallucination Prevention 지시가 포함된다:
빈 공간에 임의 한글 생성 금지, 모든 한글은 CONTENT 섹션 텍스트에만 대응,
빈 영역에는 플랫 아이콘/아이소메트릭 일러스트/장식 요소 배치 지시.

### 3-Layer Defense Architecture

| 계층 | 적용 시점 | 구현 위치 |
|------|-----------|-----------|
| Upstream | 프롬프트 생성 시 | prompt-designer.md (Korean Safety Rules 6조) |
| Inference | API 호출 시 | generate_slide_images.py (SYSTEM_INSTRUCTION) |
| Downstream | 생성 후 | generate_slide_images.py (5D quality + Korean veto) |

자세한 규칙은 `plugins/visual-generator/agents/prompt-designer.md` → `## Korean Text Safety Rules` 참조.
빈 공간 처리 가이드는 `references/scene-richness-spec.md` → `## 11. Space-Filling Prevention` 참조.

---

## OpenAI gpt-image-2 Rendering Path

gpt-image-2 API를 사용하여 슬라이드 프롬프트 파일(.md)을 1536x1024 JPEG 이미지로 변환하는 스크립트 실행 가이드.

### 스크립트 참조 및 실행 (CRITICAL)

스크립트는 이 스킬의 상대경로에 위치합니다:

scripts/generate_slide_images_openai.py

**실행 순서:**

**Step 1. 상대경로로 실행** (최우선)
```bash
python scripts/generate_slide_images_openai.py \
  --prompts-dir [프롬프트 폴더 경로] \
  --output-dir [이미지 출력 폴더 경로] \
  [--max-images N]
```

**Step 2. 상대경로 실패 시 Glob 폴백**
```
Glob: **/visual-generator/skills/slide-renderer/scripts/generate_slide_images_openai.py
```

**Step 3. Glob도 실패 시 확장 탐색**
```
Glob: **/generate_slide_images_openai.py
```

**절대 금지**: 스크립트를 찾지 못했을 때 자체적으로 Python 코드를 작성하지 마세요.

### 환경 요구사항

| 항목 | 설명 |
|------|------|
| Python | 3.8+ |
| 패키지 | openai>=1.0, Pillow |
| 환경변수 | `OPENAI_API_KEY` 필수 |
| 모델 (생성) | gpt-image-2 |
| 모델 (평가) | gpt-5.5 (폴백: gpt-5 → gpt-4o) |
| 출력 | 1536x1024 JPEG (quality=high) |

### CLI

```bash
python scripts/generate_slide_images_openai.py \
  --prompts-dir [경로] \
  --output-dir [경로] \
  [--max-images N]   # 기본 30, 초과 시 확인 필요
  [--yes]            # 확인 없이 자동 진행
```

### 비용 안내

| 항목 | 비용 |
|------|------|
| 이미지 생성 (high 1536x1024) | ~$0.165/image |
| 평가 호출 | ~$0.05/image |
| 30장 기준 합계 | 약 $6.6 |

**`--max-images` (기본 30)**: 초과 시 사용자 확인 또는 `--yes` 필요.

### API 사전 체크

- **Organization Verification**: gpt-image-2 사용 시 OpenAI Organization 검증 필요 (developer console → Usage → Verification)
- **403 에러**: 조직 미검증 상태 → 검증 페이지 안내 후 중단

### 에러 처리

| 에러 유형 | 처리 방법 |
|-----------|-----------|
| OPENAI_API_KEY 미설정 | 즉시 중단, 한국어 안내 |
| API 타임아웃 | 5초 후 재시도 (최대 3회) |
| 429 (rate limit) | 5s/15s/45s exponential backoff |
| 400 (content policy) | 사유 기록 후 다음 prompt 진행 |
| 403 (Org 미검증) | 검증 페이지 안내 후 중단 |

### 5D 품질 평가

5D 평가 기준 및 Schema → `references/openai-quality-rubric.md` 참조.
PASS: overall_score ≥ 7.0 AND korean_text_readability ≥ 5.0 AND korean_hallucination_detection ≥ 5.0
