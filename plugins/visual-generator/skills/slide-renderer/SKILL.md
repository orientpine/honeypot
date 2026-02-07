---
name: slide-renderer
description: "Gemini API를 사용한 슬라이드 이미지 렌더링 스킬. renderer-agent가 프롬프트 파일을 이미지로 변환할 때 사용. generate_slide_images.py 스크립트 실행 가이드, 환경 요구사항, 출력 해석, 에러 처리 방법을 포함합니다."
---

# Slide Renderer

Gemini API를 사용하여 프롬프트 파일(.md)을 4K 16:9 PNG 이미지로 변환하는 스크립트 실행 가이드.

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
| 출력 | 4K, 16:9 비율 PNG |

## 스크립트 출력 해석

| 출력 패턴 | 의미 | 처리 |
|-----------|------|------|
| `[OK] Saved:` | 이미지 생성 성공 | 성공 카운트 증가 |
| `[FAIL] Failed:` | 이미지 생성 실패 | 재시도 대상 추가 |
| `[SKIP] Already exists:` | 파일 이미 존재 | 스킵 카운트 증가 |
| `[에러]` | API 오류 또는 시스템 오류 | 로그 기록 |

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
