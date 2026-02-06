#!/usr/bin/env python3
"""
Shared Utilities for Paper Style Generator

공통 유틸리티 함수와 언어 패턴을 제공합니다.
style_extractor.py와 mineru_converter.py에서 공유합니다.

Usage:
    from paper_utils import extract_sections, ACADEMIC_VERBS, TRANSITION_PHRASES
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional


# ==============================================================================
# 설정 파일 경로 (외부화된 패턴)
# ==============================================================================

CONFIG_DIR = Path(__file__).parent.parent / "references"


def load_linguistic_patterns() -> Dict:
    """외부 설정 파일에서 언어 패턴 로드 (없으면 기본값 사용)"""
    config_file = CONFIG_DIR / "linguistic_patterns.json"

    if config_file.exists():
        with open(config_file, "r", encoding="utf-8") as f:
            return json.load(f)

    # 기본값 반환
    return DEFAULT_PATTERNS


# ==============================================================================
# 언어 패턴 상수 (기본값 - 설정 파일로 외부화 가능)
# ==============================================================================

DEFAULT_PATTERNS = {
    "passive_patterns": [
        r"\b(was|were|been|being|is|are)\s+\w+ed\b",
        r"\b(was|were|been|being|is|are)\s+\w+en\b",
    ],
    "we_patterns": [
        r"^We\s+\w+",
        r"^we\s+\w+",
    ],
    "past_tense_patterns": [
        r"\b\w+ed\b",
        r"\bwas\b",
        r"\bwere\b",
        r"\bhad\b",
    ],
    "present_tense_patterns": [
        r"\bis\b",
        r"\bare\b",
        r"\bhas\b",
        r"\bhave\b",
        r"\b\w+s\b",
    ],
    "academic_verbs": [
        "demonstrated",
        "showed",
        "revealed",
        "achieved",
        "obtained",
        "validated",
        "confirmed",
        "established",
        "determined",
        "measured",
        "detected",
        "observed",
        "found",
        "identified",
        "characterized",
        "developed",
        "designed",
        "constructed",
        "fabricated",
        "prepared",
        "analyzed",
        "evaluated",
        "assessed",
        "compared",
        "tested",
        "optimized",
        "enhanced",
        "improved",
        "increased",
        "reduced",
        "enabled",
        "facilitated",
        "allowed",
        "provided",
        "offered",
        "suggests",
        "indicates",
        "implies",
        "supports",
        "demonstrates",
    ],
    "transition_phrases": {
        "introduction": [
            "Here, we present",
            "Here, we report",
            "Here, we describe",
            "In this study",
            "In this work",
            "To address this",
            "Addressing",
            "To meet this need",
        ],
        "methods": [
            "Briefly,",
            "Following",
            "According to",
            "As previously described",
        ],
        "results": [
            "We first",
            "We next",
            "We then",
            "Finally,",
            "To further",
            "To validate",
            "To demonstrate",
        ],
        "discussion": [
            "Our results",
            "These findings",
            "This study",
            "One limitation",
            "Future work",
            "In conclusion",
        ],
    },
    "hedging_expressions": [
        "may",
        "might",
        "could",
        "would",
        "suggests",
        "indicates",
        "implies",
        "appears",
        "possibly",
        "potentially",
        "likely",
        "presumably",
        "it is possible",
        "it is likely",
    ],
}

# 로드된 패턴 (프로그램 시작 시 한 번만 로드)
_PATTERNS = None


def get_patterns() -> Dict:
    """언어 패턴 가져오기 (지연 로드)"""
    global _PATTERNS
    if _PATTERNS is None:
        _PATTERNS = load_linguistic_patterns()
    return _PATTERNS


# 하위 호환성을 위한 상수 별칭
PASSIVE_PATTERNS = DEFAULT_PATTERNS["passive_patterns"]
WE_PATTERNS = DEFAULT_PATTERNS["we_patterns"]
PAST_TENSE_PATTERNS = DEFAULT_PATTERNS["past_tense_patterns"]
PRESENT_TENSE_PATTERNS = DEFAULT_PATTERNS["present_tense_patterns"]
ACADEMIC_VERBS = DEFAULT_PATTERNS["academic_verbs"]
TRANSITION_PHRASES = DEFAULT_PATTERNS["transition_phrases"]
HEDGING_EXPRESSIONS = DEFAULT_PATTERNS["hedging_expressions"]


# ==============================================================================
# 섹션 추출 함수 (통합)
# ==============================================================================

# 섹션 헤더 패턴 (대소문자 무관, 다양한 형태 지원)
SECTION_HEADER_PATTERNS = [
    (r"#+\s*abstract", "abstract"),
    (r"#+\s*introduction", "introduction"),
    (r"#+\s*(materials?\s*(and|&)?\s*)?methods?", "methods"),
    (r"#+\s*results?\s*(and\s*discussion)?", "results"),
    (r"#+\s*discussion", "discussion"),
    (r"#+\s*conclusions?", "conclusion"),
    (r"#+\s*references?", "references"),
    (r"#+\s*supplementary", "supplementary"),
    (r"#+\s*acknowledgements?", "acknowledgements"),
]


def extract_sections(content: str, mode: str = "content") -> Dict[str, str]:
    """
    Markdown에서 각 섹션 추출 (통합 버전)

    Args:
        content: Markdown 텍스트
        mode: "content" (내용 추출) 또는 "detect" (섹션 존재 여부만)

    Returns:
        Dict[str, str]: 섹션명 -> 내용 (mode="content")
        Dict[str, bool]: 섹션명 -> 존재 여부 (mode="detect")
    """
    sections = {}

    # 1. 먼저 SECTION_START/END 마커 기반 추출 시도
    section_pattern = r"<!-- SECTION_START: (\w+) -->(.*?)<!-- SECTION_END: \1 -->"
    matches = re.findall(section_pattern, content, re.DOTALL)

    if matches:
        for section_name, section_content in matches:
            sections[section_name.lower()] = (
                section_content.strip() if mode == "content" else True
            )
        return sections

    # 2. 마커 없는 경우: 헤더 기반 추출
    if mode == "detect":
        # 단순 존재 여부만 확인
        content_lower = content.lower()
        for pattern, section_name in SECTION_HEADER_PATTERNS:
            if re.search(pattern, content_lower):
                sections[section_name] = True
        return sections

    # mode == "content": 내용 추출
    lines = content.split("\n")
    current_section = None
    current_content = []

    for line in lines:
        # 헤더 매칭
        header_matched = False
        for pattern, section_name in SECTION_HEADER_PATTERNS:
            if re.match(pattern, line, re.IGNORECASE):
                # 이전 섹션 저장
                if current_section:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = section_name
                current_content = []
                header_matched = True
                break

        if not header_matched and current_section:
            current_content.append(line)

    # 마지막 섹션 저장
    if current_section:
        sections[current_section] = "\n".join(current_content).strip()

    return sections


def detect_sections(content: str) -> List[str]:
    """
    섹션 존재 여부만 빠르게 확인 (mineru_converter 호환)

    Args:
        content: Markdown 텍스트

    Returns:
        List[str]: 발견된 섹션명 목록
    """
    return list(extract_sections(content, mode="detect").keys())


# ==============================================================================
# JSON I/O 유틸리티
# ==============================================================================


def save_json(data: Dict, filepath: Path, ensure_ascii: bool = False, indent: int = 2):
    """JSON 파일 저장 (공통 설정)"""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=ensure_ascii)


def load_json(filepath: Path) -> Dict:
    """JSON 파일 로드"""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


# ==============================================================================
# 텍스트 분석 유틸리티
# ==============================================================================


def count_pattern_matches(
    text: str, patterns: List[str], flags: int = re.IGNORECASE
) -> int:
    """여러 패턴에 대한 매칭 횟수 합산"""
    return sum(len(re.findall(p, text, flags)) for p in patterns)


def clean_markdown(content: str) -> str:
    """Markdown 텍스트 정리 (코멘트 제거, 공백 정규화)"""
    # HTML 코멘트 제거
    content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
    # 연속 공백 제거
    content = re.sub(r"\n{3,}", "\n\n", content)
    return content.strip()
