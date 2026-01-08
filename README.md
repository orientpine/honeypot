# Toolbox

AI 에이전트 스킬/플러그인 코드 저장소입니다.
한국 R&D 부설연구소(ISD) 코드 자산 및 프레젠테이션 이미지 생성을 위한 Claude 플러그인 컬렉션을 제공합니다.

---

## Submodule로 사용하기

이 저장소를 다른 프로젝트의 하위 디렉토리로 추가하여 사용할 수 있습니다.

### 1. Submodule 추가

프로젝트 루트에서 실행:

    cd your-project
    git submodule add https://github.com/orientpine/toolbox_orientpine.git toolbox_orientpine
    git commit -m "Add toolbox as submodule"

결과: your-project/toolbox_orientpine/ 폴더가 생성되고, 원본 저장소와 연결됩니다.

### 2. Submodule이 포함된 프로젝트 클론하기

방법 A (권장): 처음부터 submodule과 함께 가져오기

    git clone --recurse-submodules https://github.com/username/your-project.git

방법 B: 이미 클론한 후 submodule 초기화

    cd your-project
    git submodule update --init --recursive

### 3. Submodule 최신 버전으로 업데이트

    cd your-project
    git submodule update --remote --merge

주의: 업데이트 후 반드시 메인 프로젝트에 반영해야 합니다!

    git add toolbox_orientpine
    git commit -m "Update toolbox submodule to latest"
    git push

### 4. Toolbox 코드를 직접 수정하고 Push하기

Step 1: toolbox 원본 저장소에 push

    cd your-project/toolbox_orientpine
    git add .
    git commit -m "feat: 새 기능 추가"
    git push origin main

Step 2: 메인 프로젝트에서 submodule 참조 업데이트

    cd ..
    git add toolbox_orientpine
    git commit -m "Update toolbox submodule reference"
    git push

### 5. 자주 사용하는 명령어 모음

- Submodule 상태 확인: git submodule status
- 모든 Submodule 초기화: git submodule update --init --recursive
- 모든 Submodule 최신화: git submodule update --remote --merge
- Submodule 변경사항 확인: git diff --submodule

### 6. git submodule init / update가 필요한 상황

#### 언제 필요한가?

다음 상황에서는 `git submodule init`과 `git submodule update`를 실행해야 합니다:

**상황 1: 일반 git clone으로 프로젝트를 받은 경우**
```bash
git clone https://github.com/username/your-project.git
cd your-project
ls toolbox_orientpine/  # 폴더가 비어있음!
```
→ `--recurse-submodules` 옵션 없이 클론하면 submodule 폴더는 생성되지만 내용이 비어있습니다.

**상황 2: git pull 후 새로운 submodule이 추가된 경우**
```bash
git pull origin main  # 다른 팀원이 추가한 새 submodule 정보가 포함됨
ls new_submodule/     # 폴더가 비어있음!
```
→ pull로는 submodule 메타정보만 받아오고, 실제 내용은 별도로 초기화해야 합니다.

**상황 3: submodule 폴더 안이 비어있는 모든 경우**
→ `.gitmodules` 파일에 submodule 정보는 있지만 실제 내용이 없는 상태

#### 해결 방법

**방법 A: 한 줄로 해결 (권장)**
```bash
git submodule update --init --recursive
```
이 명령은 `git submodule init` + `git submodule update`를 한번에 수행합니다.

**방법 B: 단계별 실행 (이해를 위해)**
```bash
# 1단계: submodule 정보를 .git/config에 등록
git submodule init

# 2단계: 등록된 submodule의 실제 내용을 가져옴
git submodule update
```

**각 명령의 역할:**
- `git submodule init`: `.gitmodules` 파일을 읽어 로컬 `.git/config`에 submodule URL 등록
- `git submodule update`: 등록된 URL에서 커밋된 버전의 submodule 내용을 체크아웃

#### 실무 팁

```bash
# 앞으로 git clone할 때 항상 submodule도 함께 가져오기
git config --global submodule.recurse true
```
이 설정을 하면 `git clone`, `git pull`, `git checkout` 시 submodule이 자동으로 업데이트됩니다.

### 7. 헷갈리기 쉬운 포인트

- submodule만 업데이트하고 끝냄 -> 메인 프로젝트에서도 커밋 필요!
- git clone 했는데 submodule 폴더가 비어있음 -> git submodule update --init --recursive 실행
- 최신 toolbox를 가져오고 싶음 -> git submodule update --remote --merge

### 8. 주의사항

중요: Submodule을 업데이트한 후에는 반드시 메인 프로젝트에서도 커밋해야 합니다.
그렇지 않으면 다른 사용자가 클론할 때 이전 버전의 submodule을 받게 됩니다.

---

## 구조

    toolbox/
    ├── .claude-plugin/         # 플러그인 마켓플레이스 프로젝트들
    ├── agents/                 # 범용 에이전트 정의
    ├── isd-research-proposals/ # ISD 연구 제안 시스템
    │   ├── isd-orchestrator/   # 오케스트라 오케스트레이터
    │   └── chapter{1-5}-generator/  # 연구 챕터 생성기
    └── presentations/          # 이미지/슬라이드 생성
        ├── figure-generator/   # 캡션 기반 이미지 생성
        └── slide-*-generator/  # 슬라이드 생성기

---

## 참고 링크

- Git Submodule 공식 문서: https://git-scm.com/book/ko/v2/Git-도구-서브모듈

