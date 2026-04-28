# wiki-gen Multi-Source Sync 구현 계획서

**작성일**: 2026-04-10
**대상**: `honeypot/plugins/wiki-gen` (v1.1.0 → v1.2.0)
**목표**: 여러 프로젝트의 `doc/` 폴더에서 자동으로 문서를 수집하여 wiki에 반영하는 `wiki sync` 서브커맨드 추가

---

## 1. 현재 상태 (AS-IS)

### 1.1 이미 해결된 것들

wiki-gen의 scripts/는 이미 완전히 CLI 파라미터화되어 있음. 제안서(v3)에서 우려한 하드코딩 문제는 **cha_wiki 구버전에만 해당**:

| 스크립트 | 상태 | 비고 |
|---|---|---|
| `ingest_obsidian.py` | ✅ 파라미터화 | `--source-root`, `--wiki-root`, `--ingest-log`, `--include-top-dirs`, `--skip-dirs` |
| `generate_batches.py` | ✅ 범용 | 명시적 코멘트: "vault-agnostic, does NOT hardcode personal project names" |
| `finalize.py` | ✅ 동적 | `ingest_log.json`에서 수치를 읽어 리포트 생성. 고정 문자열 없음 |
| `check_coverage.py` | ✅ 파라미터화 | `--wiki-root`, `--ingest-log` |
| `verify_content.py` | ✅ 파라미터화 | `--wiki-root`, `--entries-dir`, `--ingest-log` |
| `consolidate_analyze.py` | ✅ 파라미터화 | `--wiki-root` |
| `rebuild_index.py` | ✅ 파라미터화 | `--wiki-root` |

### 1.2 해결해야 할 GAP

| # | GAP | 설명 |
|---|---|---|
| G1 | **Multi-source 오케스트레이션 없음** | `sources.yaml`을 읽어 N개 소스를 순회하는 로직 없음 |
| G2 | **Obsidian 전용 ingest만 존재** | 프로젝트 `doc/` 폴더용 ingest 헬퍼 없음 |
| G3 | **ID 네임스페이스 충돌** | `sha1(rel_path)[:12]`로 동일 상대경로 시 충돌 가능 |
| G4 | **증분 sync 추적 없음** | `sync_log.json`으로 변경 파일만 재처리하는 로직 없음 |
| G5 | **SKILL.md에 `wiki sync` 없음** | 10번째 서브커맨드 미정의 |
| G6 | **증분 흡수 에이전트 없음** | 신규 엔트리만 기존 기사에 편입하는 `absorb_delta` 에이전트 템플릿 없음 |

---

## 2. 구현 범위 (SCOPE)

### 2.1 Phase 1: Multi-Source 수집 파이프라인 (MVP)

> **목표**: `wiki sync` 명령으로 N개 소스에서 `raw/entries/{source}/`로 자동 수집
> **예상 기간**: 1.5-2일
> **LLM 비용**: 없음 (기계적 데이터 파이프라인)

### 2.2 Phase 2: 자동화 인프라 (선택)

> **목표**: cron/timer/GitHub Actions로 Phase 1을 주기적 실행
> **예상 기간**: 0.5일
> **비고**: 프로젝트별 설정, 플러그인에는 레퍼런스 문서만 포함

### 2.3 Phase 3: 증분 흡수 (별도 계획 필요)

> **목표**: 신규 엔트리를 기존 wiki 기사에 자동 편입
> **예상 기간**: 3-5일
> **비고**: 복잡도 높음. Phase 1 운용 경험 후 착수 권장

---

## 3. 변경 파일 목록 (Phase 1 기준)

### 3.1 NEW 파일

```
plugins/wiki-gen/skills/wiki-gen/
├── scripts/
│   ├── sync_sources.py           ← NEW: 다중 소스 오케스트레이터
│   └── ingest_projects.py        ← NEW: 프로젝트 doc/ 전용 ingest 헬퍼
├── assets/
│   └── absorb_delta_agent.md     ← NEW (Phase 3): 증분 흡수 에이전트 템플릿
└── references/
    ├── sources-schema.md         ← NEW: sources.yaml 스키마 레퍼런스
    └── automation-guide.md       ← NEW (Phase 2): GitHub Actions/systemd 가이드
```

### 3.2 수정 파일

```
plugins/wiki-gen/
├── .claude-plugin/plugin.json    ← 버전 1.1.0 → 1.2.0
├── skills/wiki-gen/
│   ├── SKILL.md                  ← `wiki sync` 서브커맨드 추가 (~120줄)
│   └── scripts/
│       └── README.md             ← 새 스크립트 2개 문서 추가
```

### 3.3 변경 없음 (확인 완료)

기존 스크립트는 **수정 불필요**. 이미 범용적으로 설계되어 있음:
- `finalize.py` — 동적 리포트 ✅
- `generate_batches.py` — vault-agnostic ✅
- `check_coverage.py` — 파라미터화 ✅
- `rebuild_index.py` — 파라미터화 ✅
- `verify_content.py` — 파라미터화 ✅
- `consolidate_analyze.py` — 파라미터화 ✅

---

## 4. 상세 구현 스펙

### 4.1 `sync_sources.py` — 다중 소스 오케스트레이터

**역할**: `sources.yaml` 읽기 → 각 소스 순회 → ingest 헬퍼 호출 → `sync_log.json` 갱신 → `ingest_log.json` 병합

#### CLI 인터페이스

```bash
python scripts/sync_sources.py \
  --config sources.yaml \
  --wiki-root /path/to/wiki \
  [--source <name>]           # 특정 소스만 sync (선택)
  [--dry-run]                 # 파일 변경 없이 미리보기
  [--force]                   # 캐시 무시, 전체 재sync
```

#### 핵심 로직 (의사코드)

```python
def main():
    config = load_sources_yaml(args.config)
    sync_log = load_sync_log(wiki_root)
    
    for source in config["sources"]:
        if args.source and source["name"] != args.source:
            continue
        
        # 1. 소스 디렉토리 확보
        if source["type"] == "git":
            doc_root = sparse_clone(source)       # --depth 1 --sparse
        elif source["type"] == "local":
            doc_root = Path(source["path"]) / source.get("doc_path", "")
        
        # 2. 커밋 SHA 확보 (추적용)
        commit = get_commit_sha(doc_root)          # git repo면 sha, 아니면 "local-{mtime}"
        
        # 3. ingest 헬퍼 호출 (subprocess)
        #    entries는 raw/entries/{source_name}/ 하위에 저장
        run_ingest(source, doc_root, wiki_root, commit)
        
        # 4. sync_log 갱신 (파일별 content_hash로 증분 추적)
        update_sync_log(sync_log, source, doc_root, commit)
    
    # 5. 전체 ingest_log.json 병합
    merge_ingest_logs(wiki_root)
    
    # 6. 후속 파이프라인 실행
    run_rebuild_index(wiki_root)
    run_check_coverage(wiki_root)
    
    write_sync_log(sync_log)
```

#### 핵심 설계 결정

**Source-prefixed ID 전략**:
```python
# 기존 ingest_obsidian.py (line 504):
entry_id = hashlib.sha1(rel_str.encode('utf-8')).hexdigest()[:12]

# 새 ingest_projects.py:
combined = f"{source_name}:{rel_str}"
entry_id = hashlib.sha1(combined.encode('utf-8')).hexdigest()[:12]
```

- `source_name`이 다르면 같은 `rel_str`이라도 다른 ID 생성
- 기존 Obsidian 엔트리와의 호환: Obsidian 소스도 `sources.yaml`에 등록 시 `source_name: obsidian`을 사용. 단, **기존 ID를 변경하면 기존 기사의 `sources:` 참조가 깨짐**. 따라서 Obsidian 소스에 대해서는 **기존 `ingest_obsidian.py`를 그대로 호출** (ID 전략 변경 없음)
- 신규 프로젝트 소스만 source-prefixed ID 사용

**증분 추적 (`sync_log.json`)**:
```json
{
  "last_sync": "2026-04-10T12:34:56",
  "sources": {
    "project_a": {
      "last_sync": "2026-04-10T12:34:56",
      "commit": "abc123def456",
      "files": {
        "doc/guide.md": {
          "content_hash": "sha256_first16chars",
          "entry_id": "a1b2c3d4e5f6",
          "synced_at": "2026-04-10T12:34:56"
        }
      }
    }
  }
}
```

**삭제 감지**:
- 이전 sync에서 존재했지만 현재 소스에 없는 파일 감지
- 해당 `raw/entries/{source}/` 파일 제거 + `sync_log`에서 삭제 기록
- `--dry-run` 시 삭제 예정 파일 목록만 출력

**Sparse Clone 캐싱 (.sync_cache/)**:
```
{wiki_root}/../.sync_cache/
  {source_name}/          # sparse clone 저장 (재사용)
```
- 첫 실행: `git clone --depth 1 --filter=blob:none --sparse`
- 이후 실행: `git -C .sync_cache/{source} pull` (빠름)
- `--force` 플래그로 캐시 삭제 후 재clone

---

### 4.2 `ingest_projects.py` — 프로젝트 doc/ 전용 ingest 헬퍼

**역할**: 단일 프로젝트의 `doc/` 폴더를 walk하여 `raw/entries/{source_name}/`에 표준화된 엔트리 생성

#### CLI 인터페이스

```bash
python scripts/ingest_projects.py \
  --source-root /path/to/project/doc \
  --wiki-root /path/to/wiki \
  --source-name project_a \
  [--source-top External] \
  [--source-category Project] \
  [--source-commit abc123] \
  [--ingest-log /path/to/raw/ingest_log.json] \
  [--skip-dirs .git,.obsidian,node_modules]
```

#### `ingest_obsidian.py`와의 차이점

| 항목 | `ingest_obsidian.py` | `ingest_projects.py` |
|---|---|---|
| **소스 유형** | Obsidian 볼트 | 프로젝트 `doc/` 폴더 |
| **`source_type`** | `"obsidian"` | `"project_doc"` |
| **ID 전략** | `sha1(rel_path)[:12]` | `sha1(f"{source_name}:{rel_path}")[:12]` |
| **엔트리 출력 경로** | `raw/entries/` (flat) | `raw/entries/{source_name}/` (서브디렉토리) |
| **분류 로직** | `classify_source()` — PARA 기반 | CLI args에서 직접 받음 (`--source-top`, `--source-category`) |
| **날짜 추출** | 8-priority cascade | 동일 (코드 재사용) |
| **Obsidian callout 파싱** | 있음 | 없음 (일반 markdown만) |
| **frontmatter 추가 필드** | 없음 | `source_name`, `source_commit`, `source_url`, `aggregated_at` |
| **`ingest_log.json` 구조** | 기존과 동일 | `source_name` 필드 추가 |

#### 공유 코드 전략

`ingest_obsidian.py`에서 아래 함수들을 **그대로 재사용** (import 또는 복사):

- `Entry` dataclass + `to_markdown()`
- `parse_yaml_frontmatter()`
- `slugify()`
- `parse_date_fields()` + `_valid_date()` + `DATE_YYYYMMDD` regex
- `extract_heading_title()`
- `coerce_tag_list()` + `coerce_alias_list()` + `extract_tags()`
- `walk_markdown()` + `count_markdown_files()`
- `DEFAULT_SKIP_DIR_NAMES`

공유 방식 결정:

| 방식 | 장점 | 단점 |
|---|---|---|
| **A: `__init__.py`에 공통 코드 분리** | DRY, 유지보수 쉬움 | 기존 import 구조 변경 |
| **B: `ingest_projects.py`에서 직접 import** | 간단 | 순환 의존 위험 |
| **C: 필요한 함수만 복사** | 독립적 | 코드 중복 |

**추천: 방식 A** — `scripts/__init__.py`를 `scripts/ingest_common.py`로 확장하여 공통 함수 배치. `ingest_obsidian.py`와 `ingest_projects.py` 모두 여기서 import.

> ⚠️ **주의**: `ingest_obsidian.py`의 공용 함수를 `ingest_common.py`로 추출할 때, `ingest_obsidian.py`의 기존 동작은 **1줄도 변경하면 안 됨**. import 경로만 바꾸고 로직은 그대로 유지.

#### 엔트리 추가 frontmatter (기존 Entry 대비)

```yaml
---
id: a1b2c3d4e5f6
date: 2026-04-05
time: "14:30:00"
title: "크롤러 제어 시뮬레이션 가이드"
source_type: project_doc              # ← 'obsidian' 대신
source_name: project_kimm_excavator   # ← NEW
source_commit: abc123def456789        # ← NEW
source_url: "https://github.com/..."  # ← NEW (git 소스만)
source_category: Project
source_subcategory: kimm_excavator
source_top: KIMM
source_relative: "project_kimm_excavator/doc/guide.md"
tags: [simulation, crawler]
author: ""
aliases: []
word_count: 463
char_count: 2426
line_count: 104
extra:
  date_source: fm.created
  aggregated_at: "2026-04-10T12:34:56"   # ← NEW
  original_path: "doc/guide.md"           # ← NEW
---
```

#### ID 충돌 가드

```python
def source_prefixed_id(source_name: str, rel_path: str) -> str:
    """Generate collision-resistant ID with source namespace.
    
    SHA1(f"{source_name}:{rel_path}")[:12]. 48-bit hash space.
    Structural collisions (같은 상대경로) are prevented by source prefix.
    Random collisions are astronomically rare but guarded by ValueError.
    """
    combined = f"{source_name}:{rel_path}"
    return hashlib.sha1(combined.encode("utf-8")).hexdigest()[:12]
```

`sync_sources.py`에서 매 sync마다 전체 ID 충돌 검사:
```python
all_ids: dict[str, str] = {}  # id -> "source:path"
for source_name, files in sync_log["sources"].items():
    for path, meta in files["files"].items():
        eid = meta["entry_id"]
        origin = f"{source_name}:{path}"
        if eid in all_ids and all_ids[eid] != origin:
            raise ValueError(
                f"ID collision: {eid}\n"
                f"  Existing: {all_ids[eid]}\n"
                f"  New:      {origin}\n"
                f"  Mitigation: use --id-length 16 or check for duplicate paths"
            )
        all_ids[eid] = origin
```

---

### 4.3 `sources.yaml` 스키마

프로젝트 루트에 배치하는 **프로젝트별 설정 파일** (wiki-gen 플러그인에 포함하지 않음):

```yaml
# sources.yaml — wiki source configuration
# wiki sync 명령이 읽는 설정 파일

sources:
  # 기존 Obsidian 볼트 (legacy 지원)
  - name: obsidian
    type: obsidian                        # 특수 타입: ingest_obsidian.py 사용
    source_root: /home/cha/Documents/git-obsidian
    include_top_dirs: 000_PARA,001_KIMM_PARA,002_Schedule,999_limbo,Excalidraw
    # skip_dirs: 생략 시 기본 목록 사용

  # Git 원격 프로젝트
  - name: kimm_excavator_v2
    type: git                             # sparse clone 사용
    url: https://github.com/orientpine/kimm-excavator-v2.git
    branch: main
    doc_path: doc/                        # clone 후 이 하위 디렉토리만 사용
    source_top: KIMM
    source_category: Project

  # 로컬 프로젝트
  - name: retirement_seminar_2026
    type: local                           # 로컬 경로 직접 walk
    path: /home/cha/Documents/projects/retirement-seminar-2026
    doc_path: doc/
    source_top: Personal
    source_category: Project

settings:
  entries_subdir: true                    # raw/entries/{source_name}/ 하위 디렉토리 사용
  id_strategy: source_prefixed            # sha1(f"{source}:{path}")[:12]
  sync_cache_dir: .sync_cache             # sparse clone 캐시 위치
  post_sync:                              # sync 완료 후 자동 실행할 스크립트
    - rebuild_index
    - check_coverage
```

#### 소스 타입별 동작

| `type` | ingest 헬퍼 | 소스 확보 방법 | ID 전략 |
|---|---|---|---|
| `obsidian` | `ingest_obsidian.py` | 로컬 경로 직접 | **기존 유지** (`sha1(rel_path)[:12]`) |
| `git` | `ingest_projects.py` | sparse clone → `.sync_cache/` | source-prefixed |
| `local` | `ingest_projects.py` | 로컬 경로 직접 | source-prefixed |

> **핵심**: `type: obsidian`은 기존 `ingest_obsidian.py`를 **그대로 호출**하여 기존 엔트리 ID를 보존. 기존 wiki 기사의 `sources:` 참조가 깨지지 않음.

---

### 4.4 `ingest_log.json` 병합 전략

현재 `ingest_log.json`은 단일 소스 가정:
```json
{
  "source_root": "/path/to/vault",
  "entries": [...]
}
```

Multi-source 후:
```json
{
  "source_root": "(multiple)",
  "sources": ["obsidian", "kimm_excavator_v2", "retirement_seminar_2026"],
  "entries_dir": "/path/to/raw/entries",
  "total_files": 1900,
  "written": 1880,
  "skipped": 20,
  "entries": [
    {"id": "abc123", "source_name": "obsidian", ...},
    {"id": "def456", "source_name": "kimm_excavator_v2", ...}
  ]
}
```

**병합 로직** (`sync_sources.py` 내):
1. 각 소스의 ingest 결과를 `raw/entries/{source}/ingest_log.json`에 개별 저장
2. 전체를 `raw/ingest_log.json`으로 병합 (기존 단일 포맷과 호환)
3. 기존 `generate_batches.py`는 `entries` 배열만 읽으므로 **변경 없이 작동**
4. `entries[].source_name` 필드가 추가되지만, `generate_batches.py`는 이를 무시하므로 안전

---

### 4.5 SKILL.md 변경사항

#### 추가할 위치

`## Command: `wiki rebuild-index`` 바로 앞에 새 섹션 삽입:

#### 추가 내용 (~120줄)

```markdown
## Command: `wiki sync`

Pull documentation from multiple source projects and update `raw/entries/`.
This is the **collection layer** — it gathers source documents but does NOT
run LLM absorption. Think of it as "wiki ingest, but for many sources at once."

### Quick Start

1. Create `sources.yaml` in the project root (see `references/sources-schema.md`).
2. Run:

```bash
python scripts/sync_sources.py --config sources.yaml --wiki-root wiki/
```

3. Review new entries in `raw/entries/{source_name}/`.
4. Run `wiki absorb` (manually) to integrate new entries into wiki articles.

### What It Does

1. Reads `sources.yaml` for the list of source projects.
2. For each source:
   - `type: git` → sparse-clone to `.sync_cache/`, checkout only `doc_path`
   - `type: local` → read from local path directly
   - `type: obsidian` → delegate to `ingest_obsidian.py` (existing behavior)
3. Runs the appropriate ingest helper for each source:
   - `ingest_obsidian.py` for Obsidian vaults
   - `ingest_projects.py` for project `doc/` folders
4. Writes entries to `raw/entries/{source_name}/`.
5. Merges all per-source ingest logs into unified `raw/ingest_log.json`.
6. Runs `rebuild_index.py` and `check_coverage.py` automatically.
7. Reports sync summary with added/updated/unchanged/deleted counts.

### Incremental Sync

After the first run, `sync_log.json` tracks each file's content hash.
Subsequent runs only process changed files, skipping unchanged ones.

- Use `--force` to ignore the cache and re-process everything.
- Use `--dry-run` to preview changes without writing files.
- Use `--source <name>` to sync only one specific source.

### Automation Levels

This command handles **Level 1 (Source → Entries)** automation:

| Level | What | Cost | Trigger |
|---|---|---|---|
| **Level 1** | Source docs → `raw/entries/` + index + backlinks | Seconds to minutes, no LLM | `wiki sync` (cron/timer/manual) |
| **Level 2** | New entries → wiki article text | LLM cost per entry | `wiki absorb` (manual) |

Level 2 requires manual `wiki absorb` — see Phase 3 in the implementation plan.

### ID Strategy

Project sources use **source-prefixed IDs** to prevent collisions:

```
sha1(f"{source_name}:{relative_path}")[:12]
```

Obsidian sources keep the original ID strategy (`sha1(rel_path)[:12]`)
to preserve backward compatibility with existing article citations.

### Deletion Handling

When a source file is deleted:
- The corresponding entry in `raw/entries/{source}/` is removed.
- The entry is removed from `sync_log.json` and `ingest_log.json`.
- Wiki articles that cited the deleted entry are NOT automatically modified.
- Run `check_coverage.py` to identify orphaned citations.

### When to Run

- After adding new docs to any source project's `doc/` folder
- On a schedule (daily cron, systemd timer, GitHub Actions)
- Before `wiki absorb` to ensure entries are up to date
- After changing `sources.yaml` (adding/removing sources)

### See Also

- `references/sources-schema.md` — Full `sources.yaml` schema documentation
- `references/automation-guide.md` — GitHub Actions and systemd timer setup
```

---

### 4.6 `absorb_delta_agent.md` (Phase 3용 — 이 계획에서는 스펙만)

> Phase 3 구현 시 사용할 에이전트 프롬프트 템플릿. Phase 1에서는 파일만 생성하고 내용은 stub.

**핵심 설계 방향**:
- 기존 `absorb_agent.md` 기반
- `absorb_agent.md`와의 차이: 전체 배치가 아닌 **신규 엔트리만** 처리
- `sync_log.json`에서 `absorbed_article == null`인 엔트리만 대상
- 기존 기사의 `sources:` 필드에 새 ID 추가 + 본문 보강 (선택적)
- 새 기사 생성은 최후 수단

---

### 4.7 `references/sources-schema.md`

`sources.yaml`의 전체 스키마를 문서화하는 레퍼런스 파일.

**포함 내용**:
- 각 필드의 타입, 필수 여부, 기본값, 예시
- `type: git | local | obsidian` 별 필수/선택 필드
- `settings` 블록 설명
- 예제 `sources.yaml` (2-3개 소스)
- 에러 케이스 (잘못된 URL, 접근 불가 경로 등) 처리 방법

---

### 4.8 `references/automation-guide.md` (Phase 2용)

**포함 내용**:

#### GitHub Actions (`sync.yml`)
```yaml
name: Wiki sync
on:
  schedule:
    - cron: '0 21 * * *'          # KST 06:00
  workflow_dispatch:
jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.11' }
      - run: pip install pyyaml
      - run: python {script_path}/sync_sources.py --config sources.yaml --wiki-root wiki/
        env:
          SOURCE_REPOS_TOKEN: ${{ secrets.SOURCE_REPOS_TOKEN }}  # private repo만
      - run: |
          git add raw/ wiki/_index.md wiki/_backlinks.json sync_log.json
          git diff --cached --quiet || git commit -m "sync: $(date -u +'%Y-%m-%d')" && git push
```

#### systemd user timer
```ini
# ~/.config/systemd/user/wiki-sync.service
[Service]
Type=oneshot
WorkingDirectory=%h/Documents/cha_wiki
ExecStart=/usr/bin/python3 {script_path}/sync_sources.py --config sources.yaml --wiki-root wiki/

# ~/.config/systemd/user/wiki-sync.timer
[Timer]
OnBootSec=10min
OnUnitActiveSec=6h
Persistent=true
[Install]
WantedBy=timers.target
```

#### 토큰 관리
- Public repo: 토큰 불필요 (익명 clone 가능)
- Private repo: `SOURCE_REPOS_TOKEN` (Fine-grained PAT, `contents:read` scope)

---

### 4.9 `scripts/README.md` 추가 내용

기존 README에 아래 두 항목 추가:

```markdown
### Multi-source sync

**sync_sources.py** — Orchestrate multi-source sync from `sources.yaml`.
```bash
python sync_sources.py --config sources.yaml --wiki-root /path/to/wiki
```

**ingest_projects.py** — Ingest a project's `doc/` folder into `raw/entries/{source}/`.
```bash
python ingest_projects.py --source-root /path/to/project/doc --wiki-root /path/to/wiki --source-name my_project
```
```

---

## 5. 기존 호환성 보장

### 5.1 기존 wiki-gen 사용자

| 시나리오 | 영향 |
|---|---|
| `sources.yaml` 없이 `wiki ingest` 사용 | ✅ 영향 없음. 기존 워크플로우 그대로 |
| `wiki absorb` / `wiki cleanup` / `wiki query` 등 | ✅ 영향 없음 |
| `scripts/ingest_obsidian.py` 직접 실행 | ✅ 영향 없음. 수정하지 않음 |
| `generate_batches.py` 실행 | ✅ 영향 없음. `entries[].source_name` 필드 무시 |
| `finalize.py` 실행 | ✅ 영향 없음 |

### 5.2 기존 cha_wiki 프로젝트

| 시나리오 | 영향 |
|---|---|
| 기존 1826개 Obsidian 엔트리 | ✅ ID 변경 없음 (`type: obsidian`은 기존 전략 유지) |
| 기존 239개 wiki 기사 | ✅ `sources:` 참조 깨지지 않음 |
| 기존 `ingest_log.json` | ⚠️ `wiki sync` 첫 실행 시 새 포맷으로 재생성. 기존 포맷도 역호환 |
| `raw/entries/` 디렉토리 구조 | ⚠️ 기존 엔트리는 flat, 신규는 `{source}/` 하위. `check_coverage.py`는 rglob이므로 OK |

### 5.3 기존 `raw/entries/` flat 구조와의 공존

기존 Obsidian 엔트리: `raw/entries/2026-03-16_title_abc123.md` (flat)
신규 프로젝트 엔트리: `raw/entries/kimm_excavator/2026-04-05_title_def456.md` (서브디렉토리)

**`check_coverage.py`** (line 69): `wiki_root.rglob('*.md')` — 재귀 탐색이므로 양쪽 모두 발견됨 ✅
**`generate_batches.py`**: `ingest_log.json`의 `entries[]`만 읽으므로 파일 위치 무관 ✅
**`verify_content.py`**: `--entries-dir` 기반 rglob이므로 서브디렉토리도 탐색됨 ✅

---

## 6. 테스트 계획

### 6.1 Unit Tests (스크립트별)

| 테스트 | 검증 항목 |
|---|---|
| `ingest_projects.py --source-root /tmp/test_project/doc --wiki-root /tmp/test_wiki --source-name test_proj` | 엔트리 파일 생성, frontmatter 정확성, ID 형식, source_name 포함 |
| `sync_sources.py --config test_sources.yaml --wiki-root /tmp/test_wiki --dry-run` | dry-run에서 파일 생성 안 됨, 변경 예정 목록 출력 |
| `sync_sources.py --config test_sources.yaml --wiki-root /tmp/test_wiki` | 실제 sync 수행, sync_log.json 생성, ingest_log.json 병합 |
| 동일 sync 2회 실행 | 멱등성 검증 — unchanged 카운트, 파일 내용 동일 |

### 6.2 Integration Tests

| 테스트 | 검증 항목 |
|---|---|
| Obsidian + 2개 프로젝트 소스 sync | 3개 소스의 엔트리가 모두 `raw/entries/`에 생성, `ingest_log.json` 병합됨 |
| sync 후 `generate_batches.py` 실행 | 배치 분류가 source_top/source_category 기반으로 정상 작동 |
| sync 후 `finalize.py` 실행 | `_FINAL_REPORT.md`에 전체 통계가 올바르게 집계 |
| 프로젝트에서 파일 삭제 후 재sync | 해당 엔트리 파일 삭제, sync_log에서 제거 |
| ID 충돌 시나리오 (같은 상대경로) | source-prefixed ID가 다른 값 생성 확인 |
| 기존 Obsidian ID 보존 확인 | `type: obsidian` sync 후 기존 엔트리 ID 변경 없음 확인 |

### 6.3 Manual QA

```bash
# 1. 테스트 소스 준비
mkdir -p /tmp/test_project_a/doc /tmp/test_project_b/doc
echo -e "---\ntitle: Test A\n---\nContent A" > /tmp/test_project_a/doc/guide.md
echo -e "---\ntitle: Test B\n---\nContent B" > /tmp/test_project_b/doc/readme.md

# 2. sources.yaml 작성
cat > /tmp/test_sources.yaml << 'EOF'
sources:
  - name: test_a
    type: local
    path: /tmp/test_project_a
    doc_path: doc/
    source_top: Test
    source_category: Project
  - name: test_b
    type: local
    path: /tmp/test_project_b
    doc_path: doc/
    source_top: Test
    source_category: Project
settings:
  entries_subdir: true
  id_strategy: source_prefixed
EOF

# 3. sync 실행
python scripts/sync_sources.py --config /tmp/test_sources.yaml --wiki-root /tmp/test_wiki --dry-run
python scripts/sync_sources.py --config /tmp/test_sources.yaml --wiki-root /tmp/test_wiki

# 4. 결과 검증
ls -la /tmp/test_wiki/../raw/entries/test_a/
ls -la /tmp/test_wiki/../raw/entries/test_b/
cat /tmp/test_wiki/../raw/ingest_log.json | python -m json.tool | head -20
cat /tmp/test_wiki/../sync_log.json | python -m json.tool | head -20

# 5. 기존 파이프라인 연동 검증
python scripts/rebuild_index.py --wiki-root /tmp/test_wiki
python scripts/check_coverage.py --wiki-root /tmp/test_wiki

# 6. 멱등성 검증 (재실행)
python scripts/sync_sources.py --config /tmp/test_sources.yaml --wiki-root /tmp/test_wiki
# → "unchanged" 카운트 확인
```

---

## 7. 구현 순서 (Phase 1 워크플로우)

```
Step 1: 공통 코드 추출
  ├─ ingest_obsidian.py에서 공용 함수를 ingest_common.py로 추출
  ├─ ingest_obsidian.py가 ingest_common.py에서 import하도록 수정
  └─ 검증: ingest_obsidian.py 동작 변경 없음 확인

Step 2: ingest_projects.py 구현
  ├─ ingest_common.py의 함수 재사용
  ├─ source-prefixed ID 전략 구현
  ├─ 프로젝트 doc/ 특화 로직 (source_name, source_commit 등)
  └─ 검증: 단일 프로젝트 소스로 엔트리 생성 확인

Step 3: sync_sources.py 구현
  ├─ sources.yaml 파서
  ├─ type별 분기 (obsidian → ingest_obsidian, git/local → ingest_projects)
  ├─ sparse clone 로직 (git 소스)
  ├─ sync_log.json 증분 추적
  ├─ ingest_log.json 병합
  ├─ 삭제 감지
  ├─ --dry-run, --force, --source 옵션
  └─ 검증: 2-3개 소스 end-to-end sync 확인

Step 4: 기존 파이프라인 연동 확인
  ├─ generate_batches.py — 멀티소스 엔트리로 배치 생성
  ├─ rebuild_index.py — 인덱스 갱신
  ├─ check_coverage.py — 커버리지 확인 (신규 엔트리는 uncovered)
  ├─ finalize.py — 전체 리포트 확인
  └─ 검증: 기존 스크립트 모두 오류 없이 실행됨

Step 5: SKILL.md 업데이트
  ├─ `wiki sync` 서브커맨드 섹션 추가 (~120줄)
  ├─ Quick Start에 `wiki sync` 언급 추가
  └─ 검증: SKILL.md 트리거 문구로 올바르게 활성화되는지 확인

Step 6: 문서 작성
  ├─ scripts/README.md 업데이트
  ├─ references/sources-schema.md 작성
  ├─ references/automation-guide.md 작성 (Phase 2)
  ├─ assets/absorb_delta_agent.md stub 생성 (Phase 3)
  └─ plugin.json 버전 1.2.0으로 변경

Step 7: cha_wiki 프로젝트에 적용
  ├─ sources.yaml 초안 작성 (기존 Obsidian + 1-2개 프로젝트)
  ├─ wiki sync 실행
  ├─ 기존 1826개 엔트리 ID 보존 확인
  └─ 신규 엔트리의 커버리지 리포트 확인
```

---

## 8. 의사결정 로그 (결정된 사항)

| # | 결정 | 근거 |
|---|---|---|
| D1 | wiki-gen 플러그인 내 수정 (별도 플러그인 아님) | sync 결과가 wiki-gen entry 포맷 그대로. 같은 파이프라인, 같은 의존성 |
| D2 | 새 skill이 아닌 기존 skill에 서브커맨드 추가 | `wiki sync`는 `wiki ingest`의 확장. 9→10 서브커맨드. SKILL.md ~120줄 추가로 충분 |
| D3 | Obsidian 소스는 기존 ID 전략 유지 | 기존 기사의 `sources:` 참조 보존. 마이그레이션 비용 회피 |
| D4 | 신규 프로젝트 소스만 source-prefixed ID | 충돌 방지와 하위 호환성의 균형 |
| D5 | `raw/entries/{source}/` 서브디렉토리 구조 | 기존 flat 구조와 공존 가능. rglob 기반 기존 스크립트와 호환 |
| D6 | 기존 스크립트 수정 불필요 (finalize, generate_batches 등) | wiki-gen 버전은 이미 범용화 완료. cha_wiki 구버전과 혼동하지 말 것 |
| D7 | `ingest_common.py`로 공통 코드 추출 | DRY 원칙. ingest_obsidian.py 동작 변경 없이 import 구조만 변경 |
| D8 | Phase 1에서 LLM 흡수 제외 | 비용 통제. Level 1 자동화만 우선. 운용 경험 후 Phase 3 착수 |
| D9 | sync_log.json으로 증분 추적 | content hash 기반. 변경 없는 파일 재처리 방지 |
| D10 | `.sync_cache/` 디렉토리로 sparse clone 캐싱 | 매 sync마다 전체 clone 방지. `git pull`로 업데이트 |

---

## 9. 리스크 및 완화

| 리스크 | 가능성 | 완화 |
|---|---|---|
| `ingest_common.py` 추출 시 `ingest_obsidian.py` 동작 변경 | 낮음 | 추출 전후 동일 입력으로 출력 diff 비교 |
| `raw/entries/{source}/` 구조가 기존 스크립트에서 누락 | 낮음 | 모든 스크립트가 rglob 사용 확인 완료 |
| sparse clone 네트워크 실패 | 중 | `--retry 3` + 부분 성공 허용 (실패 소스 skip, 나머지 계속) |
| 대용량 doc/ (이미지, PDF 포함) | 중 | `ingest_projects.py`는 `*.md`만 처리. 비-markdown 파일 무시 |
| `sources.yaml` 오타로 잘못된 경로 | 중 | `--dry-run` 기본 제공. 경로 존재 여부 사전 검증 |
| sync_log.json 손상 | 낮음 | `--force`로 재생성 가능. 백업은 사용자 책임 |
| Phase 3 복잡도 과소평가 | 높음 | Phase 1 운용 후 별도 계획 수립. 이 문서에서는 stub만 |

---

## 10. 미결정 사항 (구현 시 확정)

| # | 항목 | 선택지 | 현재 기울기 |
|---|---|---|---|
| U1 | `ingest_common.py` vs 직접 import | (a) 별도 모듈 추출, (b) `from ingest_obsidian import func` | (a) 별도 모듈 |
| U2 | `type: obsidian`에서 `--include-top-dirs` 전달 방식 | (a) sources.yaml에 직접 기입, (b) 별도 obsidian 전용 설정 파일 | (a) 직접 기입 |
| U3 | sync 실패 시 exit code 전략 | (a) 하나라도 실패 시 1, (b) 부분 성공 시 0 + warning | (b) 부분 성공 |
| U4 | `sync_log.json` vs `ingest_log.json`에 sync 메타 통합 | (a) 별도 파일, (b) ingest_log에 통합 | (a) 별도 |
| U5 | commit SHA 저장 시 local non-git fallback 값 | `"local-{iso_mtime}"` | 확정 |
| U6 | 플러그인 최소 Python 버전 | 3.10+ (기존과 동일) | 확정 |

---

## 부록 A: 파일 크기 추정

| 파일 | 예상 줄수 | 근거 |
|---|---|---|
| `sync_sources.py` | 350-450 | ingest_obsidian.py (674줄)보다 작음. 오케스트레이션 로직 위주 |
| `ingest_projects.py` | 300-400 | ingest_obsidian.py 기반 간소화. Obsidian callout 파싱 제거 |
| `ingest_common.py` | 200-250 | 공용 함수 추출 (Entry, parse_yaml_fm, slugify, date parsing 등) |
| SKILL.md 추가분 | 100-130 | `wiki sync` 섹션 |
| `sources-schema.md` | 80-120 | YAML 스키마 문서 |
| `automation-guide.md` | 60-80 | GitHub Actions + systemd 예시 |
| `absorb_delta_agent.md` | 20-30 (stub) | Phase 3 placeholder |
| `README.md` 추가분 | 15-20 | 새 스크립트 2개 항목 |
| **총 신규 코드** | **~1,200줄** | |

---

## 부록 B: 버전 변경 기록

```
v1.1.0 (현재)
  - 9 sub-commands: ingest, absorb, remediate, query, cleanup, breakdown,
    status, rebuild-index, reorganize
  - 1 ingest helper: ingest_obsidian.py
  - 10 scripts total

v1.2.0 (이 계획)
  - 10 sub-commands: + wiki sync
  - 2 ingest helpers: + ingest_projects.py
  - 13 scripts total: + sync_sources.py, ingest_projects.py, ingest_common.py
  - 2 reference docs: + sources-schema.md, automation-guide.md
  - 1 agent template: + absorb_delta_agent.md (stub)
```

---

**문서 버전**: 1.0
**최종 수정**: 2026-04-10
**다음 단계**: 사용자 승인 → Step 1 (`ingest_common.py` 추출)부터 순차 구현
