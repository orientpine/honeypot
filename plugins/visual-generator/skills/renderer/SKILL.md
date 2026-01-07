---
name: renderer
description: "visual-prompt-gov 또는 visual-prompt-concept로 생성된 프롬프트를 Gemini API로 이미지화하는 스킬. 사용자가 시각 자료 이미지 생성을 요청하거나 프롬프트를 이미지로 변환하고 싶을 때 사용한다."
---

# Visual Renderer

## Overview

visual-prompt-gov 또는 visual-prompt-concept로 생성된 프롬프트 파일(.md)을 읽어 Gemini API를 통해
고품질 시각 자료 이미지를 자동 생성하는 스킬이다.

핵심 기능:
- slide_image_gen/prompts/ 폴더의 프롬프트 자동 처리
- Gemini API + Python 스크립트를 통한 이미지 자동 생성
- 4K, 16:9 비율의 고해상도 슬라이드 이미지 출력
- 실행 보고서 생성

---

## 사용자 입력 스키마

### 필수 입력

| 항목 | 설명 | 예시 |
|------|------|------|
| 프롬프트 폴더 경로 | 슬라이드 프롬프트 .md 파일이 저장된 폴더 | `slide_image_gen/prompts/` |

### 선택 입력

| 항목 | 설명 | 기본값 |
|------|------|--------|
| 이미지 출력 폴더 | 생성된 이미지 저장 위치 | `slide_image_gen/figures/` |
| 특정 프롬프트만 처리 | 특정 번호의 프롬프트만 처리 | 전체 |

---

## Workflow

```
[Phase 0: 입력 검증]
    |
    +-- Step 0-1. 프롬프트 폴더 확인
    |   +-- 사용자 제공 경로 존재 여부 확인
    |   +-- .md 프롬프트 파일 목록 수집
    |   +-- 공통및특화작업구조설명.md 등 메타 파일 제외
    |
    +-- Step 0-2. 출력 폴더 설정
    |   +-- figures/ 폴더 존재 확인 (없으면 생성)
    |   +-- 기존 이미지 목록 확인 (중복 방지)
    |
    +-- Step 0-3. Python 환경 확인
        +-- Python 3.8+ 설치 여부 확인
        +-- 필수 패키지: google-genai, Pillow
        +-- 미설치 시 안내: pip install google-genai Pillow

[Phase 1: 프롬프트 목록 생성]
    |
    +-- Step 1-1. 프롬프트 파일 스캔
    |   +-- prompts/ 폴더 내 모든 .md 파일 읽기
    |   +-- 파일명 기반 순서 정렬
    |
    +-- Step 1-2. 처리 대상 확인
        +-- 총 프롬프트 수
        +-- 각 프롬프트 파일명 및 크기
        +-- 사용자에게 확인 요청 (진행 여부)

[Phase 2: 이미지 생성]
    |
    +-- Step 2-1. Python 스크립트 실행
    |   +-- 스크립트 경로: ./toolbox_orientpine/plugins/visual-generator/scripts/generate_slide_images.py
    |   +-- 실행 명령어:
    |       python ./toolbox_orientpine/plugins/visual-generator/scripts/generate_slide_images.py \
    |         --prompts-dir [prompts_folder]/ \
    |         --output-dir [output_folder]/
    |
    +-- Step 2-2. 생성 진행 모니터링
    |   +-- 각 이미지 생성 진행 상황 출력
    |   +-- 성공/실패 상태 표시
    |
    +-- Step 2-3. 결과 확인
        +-- figures/ 폴더 내 이미지 파일 목록 확인
        +-- 예상 파일명: [순번]_[슬라이드제목].png

[Phase 3: 검증]
    |
    +-- Step 3-1. 완료 확인
    |   +-- 생성된 이미지 파일 목록 수집
    |   +-- 프롬프트 목록과 대조
    |   +-- 누락된 이미지 식별
    |
    +-- Step 3-2. 누락 이미지 재생성
        +-- 누락된 프롬프트에 대해 Phase 2 재실행
        +-- 최대 재시도 3회

[Phase 4: 완료 보고]
    |
    +-- Step 4-1. 실행 보고서 생성
    |   +-- slide_generation_report.md 생성
    |   +-- 포함 내용:
    |       - 실행 요약 (총 처리 프롬프트 수, 성공/실패 통계)
    |       - 프롬프트-이미지 매핑 테이블
    |       - 실패 항목 및 사유
    |
    +-- Step 4-2. 사용자 안내
        +-- 생성 완료 알림
        +-- figures/ 폴더 위치 안내
        +-- 보고서 위치 안내
```

---

## Gemini API 호출 방식

### 실행 명령어

```bash
# 프로젝트 루트 기준 상대 경로 (toolbox_orientpine이 submodule로 포함된 경우)
python toolbox_orientpine/plugins/visual-generator/scripts/generate_slide_images.py \
  --prompts-dir [prompts_folder]/ \
  --output-dir [output_folder]/
```

**주의**: 스크립트는 프로젝트 내 `toolbox_orientpine/plugins/visual-generator/scripts/` 폴더에 위치합니다.

### API 설정

| 항목 | 값 | 설명 |
|------|---|------|
| 모델 | gemini-3-pro-image-preview | 고급 텍스트 렌더링 지원 |
| 해상도 | 4K | 최고 해상도 (3840x2160) |
| 비율 | 16:9 | PPT 슬라이드 표준 |
| 사고모드 | 활성화 | 복잡한 레이아웃 처리 |

### 필수 패키지 설치

```bash
pip install google-genai Pillow
```

---

## Output Structure

### 출력 디렉토리 구조

```
slide_image_gen/
├── prompts/                          # 슬라이드 프롬프트 (입력)
│   ├── 01_연구비전_최종목표.md
│   ├── 02_CrossEmbodiment_범용AI.md
│   ├── 03_AI플라이휠_파이프라인.md
│   └── ...
├── figures/                          # 생성된 이미지 (출력)
│   ├── 01_연구비전_최종목표.png
│   ├── 02_CrossEmbodiment_범용AI.png
│   ├── 03_AI플라이휠_파이프라인.png
│   └── ...
└── slide_generation_report.md        # 실행 보고서
```

### 파일명 규칙

- 순번: 2자리 (01, 02, ...)
- 슬라이드명: 프롬프트 파일명 그대로 사용
- 확장자: .png

---

## Usage Example

### 입력 예시

```
visual-renderer 스킬을 사용해서 이미지를 생성해줘.
프롬프트 폴더: [prompts_folder]/
```

또는 간단히:

```
이미지 렌더링해줘
```

### 수행 절차

1. **Phase 0**: 프롬프트 폴더 확인, 7개 프롬프트 발견
2. **Phase 1**: 프롬프트 목록 생성, 사용자 확인
3. **Phase 2**: Python 스크립트로 7개 이미지 순차 생성
4. **Phase 3**: 생성 결과 검증
5. **Phase 4**: slide_generation_report.md 생성

### 출력 파일

1. `figures/`: 생성된 슬라이드 이미지 파일들 (PNG)
2. `slide_generation_report.md`: 실행 보고서

---

## 이미지 스타일 기준

visual-prompt-gov 또는 visual-prompt-concept에서 정의한 스타일을 따름:

### 색상 팔레트

| 용도 | 색상명 | HEX 코드 |
|------|--------|----------|
| 메인/강조 | 딥 블루 | #1E3A5F |
| 서브/연결 | 미디엄 블루 | #4A90A4 |
| 성과/완료 | 그린 | #2E7D5A |
| 배경 | 라이트 그레이 | #F5F7FA |

### 공통 시각화 원칙

- 정돈된 산업용 3D 렌더링 + 미니멀 인포그래픽
- 현실적인 산업 장비 비율
- 약한 Isometric 시점
- Sans-serif 폰트 (정부 보고서 스타일)
- 텍스트 최소화, 시각 요소 중심

### 금지 요소

- 만화풍
- 과도한 SF, 사이버펑크
- 어두운 배경
- 복잡한 실제 배경
- 감정 과장 표현

---

## 관련 플러그인

| 플러그인 | 역할 | 연계 |
|---------|------|------|
| visual-prompt-gov | 정부/공공 스타일 프롬프트 | 입력 |
| visual-prompt-concept | TED/개념 시각화 프롬프트 | 입력 |
| visual-renderer | 프롬프트 → 이미지 변환 | 현재 |
| figure-generator | 문서 캡션 → 이미지 | 유사 |

---

## Resources

### 스크립트 위치

- **프로젝트 내 경로**: `toolbox_orientpine/plugins/visual-generator/scripts/generate_slide_images.py`
- **설명**: Gemini API를 사용한 슬라이드 이미지 생성 스크립트
