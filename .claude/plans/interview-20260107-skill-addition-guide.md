# 새 스킬/플러그인 추가 가이드 작성 계획

## 1. 개요
- **목적**: 사용자가 새로운 스킬을 toolbox_orientpine 프로젝트에 쉽게 추가할 수 있도록 가이드 문서 작성
- **범위**: Skill 기반 + Agent 기반 플러그인 모두 포함, 단계별 복잡도 가이드
- **인터뷰 일시**: 2026-01-07

---

## 2. 인터뷰 결과 요약

### 2.1 기술 결정사항
| 질문 | 선택 | 이유 |
|------|------|------|
| 플러그인 유형 | Skill + Agent 모두 | 프로젝트에 두 유형 모두 존재 |
| 복잡도 가이드 | 단계별 (Simple -> Advanced) | 점진적 학습 지원 |
| Marketplace 등록 | 카테고리 체계화 | 일관된 분류 체계 필요 |

### 2.2 UI/UX 결정사항
- 해당 없음 (문서 작업)

### 2.3 우려사항 및 대응
| 우려사항 | 대응 전략 |
|---------|----------|
| YAML 파싱 오류 | 큰따옴표 사용 규칙 명시 |
| 경로 오류 | trailing slash 금지 규칙 명시 |
| 캐시 문제 | 캐시 클리어 명령어 포함 |

### 2.4 트레이드오프 결정
| 선택 | 대안 | 선택 이유 |
|------|------|----------|
| AGENTS.md에 통합 | 별도 문서 생성 | 기존 문서와 일관성 유지 |

---

## 3. 구현 계획

### 3.1 구현 단계
| 단계 | 작업 내용 | 파일 |
|------|----------|------|
| 1 | 프로젝트 구조 분석 | - |
| 2 | 기존 스킬/에이전트 구조 파악 | SKILL.md, agents/*.md |
| 3 | 카테고리 체계 정의 | - |
| 4 | 단계별 가이드 작성 | AGENTS.md |
| 5 | 체크리스트 및 실수 방지 가이드 추가 | AGENTS.md |

### 3.2 테스트 계획
- AGENTS.md 문서 정상 렌더링 확인
- 가이드 내용의 기존 플러그인과의 일관성 검증

---

## 4. 실행 체크리스트
- [x] 단계 1: 프로젝트 구조 분석 완료
- [x] 단계 2: 기존 스킬/에이전트 구조 파악 완료
- [x] 단계 3: 카테고리 체계 정의 완료
- [x] 단계 4: 단계별 가이드 작성 완료
- [x] 단계 5: 체크리스트 및 실수 방지 가이드 추가 완료
- [x] AGENTS.md 업데이트 완료
- [x] 완료 보고

---

## 5. 결과물

### 추가된 섹션: NEW SKILL/PLUGIN ADDITION GUIDE

**포함 내용:**
1. Plugin Types (Skill/Agent/Hybrid)
2. Category System (6개 카테고리 정의)
3. Step-by-Step Guide
   - Level 1: Simple Skill (기본)
   - Level 2: Standard Skill (중간)
   - Level 3: Advanced Skill with Scripts (복잡)
   - Level 4: Agent Plugin
4. Marketplace Registration Checklist
5. Common Mistakes to Avoid
6. Template Files Location

**파일 위치:** `C:\Users\orien\Documents\toolbox_orientpine\AGENTS.md`
