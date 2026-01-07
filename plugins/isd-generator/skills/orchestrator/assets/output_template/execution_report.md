# ISD 연구계획서 생성 실행 보고서

> 생성일시: [YYYY-MM-DD HH:MM]
> 입력 파일: [input_template.md 경로]
> 프로젝트명: [project_name]

---

## 1. 실행 요약

| 항목 | 결과 |
|:-----|:-----|
| 총 생성 Chapter | [X]/5 |
| 총 출력 파일 | [X]개 |
| 총 검증문서 | [X]개 |
| 전체 정합성 검증 | [통과/확인필요] |

---

## 2. Chapter별 생성 결과

### Chapter 3: 사업 목표 및 추진 전략

| 항목 | 내용 |
|:-----|:-----|
| 상태 | [완료/실패/진행중] |
| 출력 파일 | chapter_3/연구목표및내용.md |
| 부속 파일 | chapter_3/이미지생성_프롬프트.md |
| 검증문서 | verification/chapter3_research_verification.md |
| 웹 검색 수행 | [O/X] (기술동향 X건, 시장현황 X건, 정책 X건) |

### Chapter 1: 개발 대상 및 필요성

| 항목 | 내용 |
|:-----|:-----|
| 상태 | [완료/실패/진행중] |
| 출력 파일 | chapter_1/개발대상및필요성.md |
| 부속 파일 | chapter_1/chapter1_references.md |
| 검증문서 | verification/chapter1_research_verification.md |
| 웹 검색 수행 | [O/X] (정책 X건, 시장 X건, 기술 X건, VoC X건) |
| 표 개수 | [X]개 (최소 8개 요건 충족 여부) |

### Chapter 2: 국내외 시장 및 기술 동향

| 항목 | 내용 |
|:-----|:-----|
| 상태 | [완료/실패/진행중] |
| 출력 파일 | chapter_2/국내외시장및기술동향.md |
| 부속 파일 | chapter_2/chapter2_references.md |
| 검증문서 | verification/chapter2_research_verification.md |
| 웹 검색 수행 | [O/X] (시장 X건, 기술 X건, 특허 X건) |
| 표 개수 | [X]개 (최소 15개 요건 확인) |

### Chapter 4: 기대효과 및 활용방안

| 항목 | 내용 |
|:-----|:-----|
| 상태 | [완료/실패/진행중] |
| 출력 파일 | chapter_4/기대효과.md |
| 표 개수 | [X]개 (최소 5개 요건 충족 여부) |

### Chapter 5: 기타 참고자료

| 항목 | 내용 |
|:-----|:-----|
| 상태 | [완료/실패/진행중] |
| 출력 파일 | chapter_5/기타참고자료.md |
| 검증문서 | verification/chapter5_ntis_verification.md |
| NTIS 검색 수행 | [O/X] (유사과제 X건) |
| 참고문헌 수 | [X]개 |

---

## 3. 검증문서 목록

| 문서 | 경로 | 주요 내용 |
|:-----|:-----|:---------|
| Chapter 3 웹 조사 검증 | verification/chapter3_research_verification.md | 기술동향, 시장현황, 정책정보 |
| Chapter 1 웹 조사 검증 | verification/chapter1_research_verification.md | 정책, 시장, 기술, VoC 조사 결과 |
| Chapter 2 웹 조사 검증 | verification/chapter2_research_verification.md | 시장규모, 기업동향, 특허분석 |
| Chapter 5 NTIS 검색 검증 | verification/chapter5_ntis_verification.md | 유사과제 검색, 차별성 분석 |

---

## 4. 정합성 검증 결과

### 4.1 수치 일치 검증

| 항목 | Chapter 간 비교 | 결과 |
|:-----|:---------------|:----:|
| 기술이전 건수 | Ch.3 정량목표 = Ch.4 기대성과 | [O/X] |
| 기술료 금액 | Ch.1 성과지표 = Ch.4 기대성과 | [O/X] |
| 수입대체 금액 | Ch.1 성과지표 = Ch.4 기대성과 | [O/X] |

### 4.2 목록 일치 검증

| 항목 | Chapter 간 비교 | 결과 |
|:-----|:---------------|:----:|
| 참여기업 목록 | Ch.3 협력전략 = Ch.4 사업화전략 | [O/X] |
| VoC 기업 | Ch.1 VoC 포함 Ch.4 수요기업 | [O/X] |
| 참여기관 | Ch.3 참여기관 = Ch.5 참여의향서 | [O/X] |

### 4.3 참고문헌 번호 검증

- Chapter 2 인용 번호와 Chapter 5 참고문헌 목록 일치: [O/X]

---

## 5. 후속 조치 권장사항

### 5.1 검증문서 검토

검증문서들은 자동 생성되었으며 사용자 검토가 권장됩니다:

1. chapter3_research_verification.md - 기술동향/시장현황 데이터 정확성 확인
2. chapter1_research_verification.md - 정책 인용/VoC 내용 확인
3. chapter2_research_verification.md - 시장규모 수치/특허 정보 확인
4. chapter5_ntis_verification.md - 유사과제 검색 결과 확인

### 5.2 수정 필요 시

각 Chapter 개별 수정이 필요한 경우:
- 해당 chapter-generator 스킬을 직접 사용하여 재생성 가능
- 수정된 Chapter의 후속 Chapter 재생성 권장

---

## 6. 파일 목록

### 6.1 본문 파일 (5개)

1. chapter_3/연구목표및내용.md
2. chapter_1/개발대상및필요성.md
3. chapter_2/국내외시장및기술동향.md
4. chapter_4/기대효과.md
5. chapter_5/기타참고자료.md

### 6.2 부속 파일

1. chapter_3/이미지생성_프롬프트.md
2. chapter_1/chapter1_references.md
3. chapter_2/chapter2_references.md

### 6.3 검증문서

1. verification/chapter3_research_verification.md
2. verification/chapter1_research_verification.md
3. verification/chapter2_research_verification.md
4. verification/chapter5_ntis_verification.md

---

> 본 보고서는 orchestrator-generator 플러그인에 의해 자동 생성되었습니다.
