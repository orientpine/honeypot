#!/usr/bin/env python3
"""
Markdown Post-processor for Academic Papers

MinerU로 변환된 Markdown을 학술 논문에 최적화된 형태로 후처리합니다.

Usage:
    python md_postprocessor.py --input-dir ./converted/ --output-dir ./processed/

Features:
    - 섹션 헤더 정규화
    - 수식 정리
    - 표 정리
    - Figure 캡션 추출
    - 불필요한 요소 제거
"""

import argparse
import re
from pathlib import Path
from typing import Tuple


def normalize_section_headers(content: str) -> str:
    """섹션 헤더를 일관된 형식으로 정규화"""
    
    # 섹션 이름 매핑
    section_mappings = [
        # Abstract
        (r'^#+\s*(ABSTRACT|Abstract|abstract)\s*$', '## Abstract'),
        # Introduction
        (r'^#+\s*(\d+\.?\s*)?(INTRODUCTION|Introduction|introduction)\s*$', '## Introduction'),
        # Methods/Materials
        (r'^#+\s*(\d+\.?\s*)?(MATERIALS?\s*(AND|&)?\s*METHODS?|Materials?\s*(and|&)?\s*Methods?|METHODS?|Methods?|EXPERIMENTAL|Experimental)\s*$', '## Methods'),
        # Results
        (r'^#+\s*(\d+\.?\s*)?(RESULTS?|Results?)\s*$', '## Results'),
        # Discussion
        (r'^#+\s*(\d+\.?\s*)?(DISCUSSION|Discussion)\s*$', '## Discussion'),
        # Conclusion
        (r'^#+\s*(\d+\.?\s*)?(CONCLUSION|Conclusion|CONCLUSIONS|Conclusions)\s*$', '## Conclusion'),
        # References
        (r'^#+\s*(\d+\.?\s*)?(REFERENCES?|References?|BIBLIOGRAPHY|Bibliography)\s*$', '## References'),
        # Acknowledgments
        (r'^#+\s*(ACKNOWLEDGMENT|Acknowledgment|ACKNOWLEDGEMENTS?|Acknowledgements?)\s*$', '## Acknowledgments'),
        # Supplementary
        (r'^#+\s*(SUPPLEMENTARY|Supplementary|SUPPORTING\s+INFORMATION|Supporting\s+Information)\s*$', '## Supplementary Information'),
    ]
    
    lines = content.split('\n')
    result = []
    
    for line in lines:
        matched = False
        for pattern, replacement in section_mappings:
            if re.match(pattern, line.strip(), re.MULTILINE):
                result.append(replacement)
                matched = True
                break
        if not matched:
            result.append(line)
    
    return '\n'.join(result)


def clean_equations(content: str) -> str:
    """수식 정리"""
    
    # 인라인 수식 정리 (단일 $ 사용)
    # 불필요한 공백 제거
    content = re.sub(r'\$\s+', '$', content)
    content = re.sub(r'\s+\$', '$', content)
    
    # 블록 수식 정리
    # $$ 앞뒤로 빈 줄 추가
    content = re.sub(r'([^\n])\n\$\$', r'\1\n\n$$', content)
    content = re.sub(r'\$\$\n([^\n])', r'$$\n\n\1', content)
    
    return content


def clean_tables(content: str) -> str:
    """표 정리"""
    
    # 표 구분선 정규화
    # |---|---| 형식으로 통일
    content = re.sub(r'\|[\s\-:]+\|', lambda m: re.sub(r'\s+', '', m.group()), content)
    
    # 표 앞뒤 빈 줄 추가
    lines = content.split('\n')
    result = []
    in_table = False
    
    for i, line in enumerate(lines):
        is_table_line = line.strip().startswith('|') and line.strip().endswith('|')
        
        if is_table_line and not in_table:
            # 표 시작
            if result and result[-1].strip():
                result.append('')
            in_table = True
        elif not is_table_line and in_table:
            # 표 종료
            result.append('')
            in_table = False
        
        result.append(line)
    
    return '\n'.join(result)


def extract_figure_captions(content: str) -> str:
    """Figure 캡션 형식 정리"""
    
    # Figure X. 또는 Fig. X 형식 정규화
    content = re.sub(
        r'(?i)(figure|fig\.?)\s*(\d+)\s*[.:]?\s*',
        r'**Figure \2.** ',
        content
    )
    
    # Figure 캡션을 별도 줄로 분리
    content = re.sub(
        r'(\*\*Figure \d+\.\*\*[^\n]+)',
        r'\n\1\n',
        content
    )
    
    return content


def remove_artifacts(content: str) -> str:
    """변환 아티팩트 제거"""
    
    # 페이지 번호 제거
    content = re.sub(r'^\s*\d+\s*$', '', content, flags=re.MULTILINE)
    
    # 빈 링크 제거
    content = re.sub(r'\[\]\([^)]*\)', '', content)
    
    # 연속된 빈 줄을 최대 2개로 제한
    content = re.sub(r'\n{4,}', '\n\n\n', content)
    
    # 헤더/푸터 패턴 제거 (일반적인 패턴)
    content = re.sub(r'^.*?(doi|DOI):\s*\S+.*$', '', content, flags=re.MULTILINE)
    content = re.sub(r'^.*?www\.\S+\.(com|org|edu).*$', '', content, flags=re.MULTILINE)
    
    return content


def add_section_markers(content: str) -> str:
    """섹션 시작/끝 마커 추가 (분석용)"""
    
    sections = ['Abstract', 'Introduction', 'Methods', 'Results', 'Discussion', 'Conclusion', 'References']
    
    for section in sections:
        # 섹션 시작 마커
        pattern = f'## {section}'
        if pattern in content:
            content = content.replace(
                pattern,
                f'<!-- SECTION_START: {section} -->\n{pattern}'
            )
    
    # 섹션 종료 마커 추가
    lines = content.split('\n')
    result = []
    current_section = None
    
    for line in lines:
        # 새 섹션 시작 감지
        match = re.match(r'<!-- SECTION_START: (\w+) -->', line)
        if match:
            # 이전 섹션 종료
            if current_section:
                result.append(f'<!-- SECTION_END: {current_section} -->')
                result.append('')
            current_section = match.group(1)
        
        result.append(line)
    
    # 마지막 섹션 종료
    if current_section:
        result.append(f'<!-- SECTION_END: {current_section} -->')
    
    return '\n'.join(result)


def process_markdown(content: str, add_markers: bool = True) -> str:
    """Markdown 전체 후처리"""
    
    # 1. 섹션 헤더 정규화
    content = normalize_section_headers(content)
    
    # 2. 수식 정리
    content = clean_equations(content)
    
    # 3. 표 정리
    content = clean_tables(content)
    
    # 4. Figure 캡션 정리
    content = extract_figure_captions(content)
    
    # 5. 아티팩트 제거
    content = remove_artifacts(content)
    
    # 6. 섹션 마커 추가 (선택적)
    if add_markers:
        content = add_section_markers(content)
    
    return content


def process_file(input_path: Path, output_path: Path, add_markers: bool = True) -> dict:
    """단일 파일 처리"""
    
    result = {
        "input": str(input_path),
        "output": str(output_path),
        "status": "pending",
        "sections": []
    }
    
    try:
        # 파일 읽기
        content = input_path.read_text(encoding="utf-8")
        
        # 후처리
        processed = process_markdown(content, add_markers)
        
        # 저장
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(processed, encoding="utf-8")
        
        # 섹션 추출
        sections = re.findall(r'## (\w+)', processed)
        
        result["status"] = "success"
        result["sections"] = sections
        
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
    
    return result


def batch_process(
    input_dir: Path,
    output_dir: Path,
    add_markers: bool = True
) -> dict:
    """폴더 내 모든 Markdown 파일 처리"""
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    md_files = list(input_dir.glob("*.md"))
    
    # conversion_report.json 제외
    md_files = [f for f in md_files if f.name != "conversion_report.json"]
    
    print(f"Found {len(md_files)} Markdown files")
    print("-" * 50)
    
    results = []
    success_count = 0
    
    for i, md_path in enumerate(md_files, 1):
        print(f"[{i}/{len(md_files)}] Processing: {md_path.name}")
        
        output_path = output_dir / md_path.name
        result = process_file(md_path, output_path, add_markers)
        results.append(result)
        
        if result["status"] == "success":
            success_count += 1
            print(f"  ✓ Sections: {', '.join(result['sections'])}")
        else:
            print(f"  ✗ Error: {result.get('error', 'Unknown')}")
    
    print("-" * 50)
    print(f"Processing complete: {success_count}/{len(md_files)} success")
    
    return {
        "summary": {
            "total": len(md_files),
            "success": success_count,
            "failed": len(md_files) - success_count
        },
        "files": results
    }


def main():
    parser = argparse.ArgumentParser(
        description="Post-process Markdown files for academic paper analysis"
    )
    parser.add_argument(
        "--input-dir", "-i",
        type=Path,
        required=True,
        help="Directory containing Markdown files"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        required=True,
        help="Output directory for processed files"
    )
    parser.add_argument(
        "--no-markers",
        action="store_true",
        help="Skip adding section markers"
    )
    
    args = parser.parse_args()
    
    if not args.input_dir.exists():
        print(f"Error: Input directory not found: {args.input_dir}")
        return 1
    
    batch_process(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        add_markers=not args.no_markers
    )
    
    return 0


if __name__ == "__main__":
    exit(main())
