"""validate-agent.sh 회귀 테스트.

주요 대상은 두 가지다.

1. SIGPIPE 회귀 (pipefail + `grep -q`)
   스크립트는 `set -euo pipefail` 로 동작한다. `cmd | grep -q PATTERN` 형태에서
   grep 은 첫 매치에서 즉시 종료하고, 상류 writer 는 SIGPIPE 로 죽어 141 을 반환한다.
   pipefail 은 이를 파이프라인 실패로 보고하므로, 파일이 충분히 커서 writer 가
   아직 쓰고 있는 경우에만 산발적으로 검증이 실패했다. 실제로 저장소의 35개
   에이전트 중 가장 큰 3개(16KB/25KB/36KB)만 "Frontmatter not closed" 로 오탐했다.
   파일 크기에 의존하는 버그이므로 테스트도 반드시 큰 입력을 사용해야 한다.

2. 현행 frontmatter 스펙 수용
   model 은 별칭(fable 포함)과 full ID 를 모두 허용하고 생략 가능해야 하며,
   effort 는 정의된 값만 허용해야 한다.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

VALIDATOR = Path(__file__).resolve().parents[1] / "scripts" / "validate-agent.sh"


def _run(agent_file: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["bash", str(VALIDATOR), str(agent_file)],
        capture_output=True,
        text=True,
    )


def _write_agent(path: Path, *, frontmatter: str, body_bytes: int = 0) -> Path:
    body = [
        "",
        "You are a test agent.",
        "",
        "**Your Core Responsibilities:**",
        "1. Do the thing",
        "",
        "**Output Format:**",
        "- Return the result",
        "",
    ]
    if body_bytes:
        filler = "가나다라마바사 padding line to grow the file. " * 4
        while sum(len(line) + 1 for line in body) < body_bytes:
            body.append(filler)
    path.write_text(f"---\n{frontmatter}\n---\n" + "\n".join(body), encoding="utf-8")
    return path


def test_validator_script_exists() -> None:
    assert VALIDATOR.is_file(), f"validator not found at {VALIDATOR}"


@pytest.mark.parametrize("body_bytes", [0, 20_000, 40_000])
def test_large_agent_file_does_not_spuriously_fail_frontmatter_check(
    tmp_path: Path, body_bytes: int
) -> None:
    """SIGPIPE 회귀 가드.

    frontmatter 가 정상적으로 닫혀 있다면 본문 크기와 무관하게 통과해야 한다.
    수정 전에는 body_bytes 가 커질수록 rc=1 + "Frontmatter not closed" 로 실패했다.
    """
    agent = _write_agent(
        tmp_path / "big-agent.md",
        frontmatter=(
            "name: big-agent\n"
            'description: "Use this agent when testing. <example>context</example>"\n'
            "tools: Read, Glob, Grep, Write\n"
            "model: sonnet"
        ),
        body_bytes=body_bytes,
    )
    result = _run(agent)
    assert "Frontmatter not closed" not in result.stdout, result.stdout
    assert "✅ Frontmatter properly closed" in result.stdout, result.stdout
    assert result.returncode == 0, f"rc={result.returncode}\n{result.stdout}"


def test_repository_agents_all_validate() -> None:
    """저장소의 모든 플러그인 에이전트가 실제로 검증을 통과해야 한다."""
    repo_root = Path(__file__).resolve().parents[5]
    agents = sorted(repo_root.glob("plugins/*/agents/*.md"))
    assert agents, "no plugin agents discovered"

    failures = [
        (agent.relative_to(repo_root), result.returncode, result.stdout)
        for agent in agents
        if (result := _run(agent)).returncode != 0
    ]
    assert not failures, "agents failed validation:\n" + "\n".join(
        f"{path} (rc={rc})\n{out}" for path, rc, out in failures
    )


@pytest.mark.parametrize("model", ["inherit", "sonnet", "opus", "haiku", "fable"])
def test_model_aliases_accepted(tmp_path: Path, model: str) -> None:
    agent = _write_agent(
        tmp_path / f"agent-{model}.md",
        frontmatter=(
            f"name: alias-agent\n"
            f'description: "Use this agent when testing. <example>ctx</example>"\n'
            f"model: {model}"
        ),
    )
    result = _run(agent)
    assert "Unknown model" not in result.stdout, result.stdout
    assert result.returncode == 0, result.stdout


def test_full_model_id_accepted(tmp_path: Path) -> None:
    """Full ID 는 세대를 고정하지만 유효한 값이므로 거부하면 안 된다."""
    agent = _write_agent(
        tmp_path / "agent-full-id.md",
        frontmatter=(
            "name: pinned-agent\n"
            'description: "Use this agent when testing. <example>ctx</example>"\n'
            "model: claude-opus-5"
        ),
    )
    result = _run(agent)
    assert "Unknown model" not in result.stdout, result.stdout
    assert result.returncode == 0, result.stdout


def test_model_field_is_optional(tmp_path: Path) -> None:
    """model 생략 시 inherit 이 기본값이므로 경고 없이 통과해야 한다."""
    agent = _write_agent(
        tmp_path / "agent-no-model.md",
        frontmatter=(
            "name: no-model-agent\n"
            'description: "Use this agent when testing. <example>ctx</example>"'
        ),
    )
    result = _run(agent)
    assert "Unknown model" not in result.stdout, result.stdout
    assert result.returncode == 0, result.stdout


def test_invalid_effort_is_rejected(tmp_path: Path) -> None:
    agent = _write_agent(
        tmp_path / "agent-bad-effort.md",
        frontmatter=(
            "name: bad-effort-agent\n"
            'description: "Use this agent when testing. <example>ctx</example>"\n'
            "model: sonnet\n"
            "effort: banana"
        ),
    )
    result = _run(agent)
    assert result.returncode != 0, result.stdout
    assert "effort" in result.stdout.lower(), result.stdout


@pytest.mark.parametrize("effort", ["low", "medium", "high", "xhigh", "max"])
def test_valid_effort_accepted(tmp_path: Path, effort: str) -> None:
    agent = _write_agent(
        tmp_path / f"agent-effort-{effort}.md",
        frontmatter=(
            "name: effort-agent\n"
            'description: "Use this agent when testing. <example>ctx</example>"\n'
            "model: sonnet\n"
            f"effort: {effort}"
        ),
    )
    result = _run(agent)
    assert result.returncode == 0, result.stdout
