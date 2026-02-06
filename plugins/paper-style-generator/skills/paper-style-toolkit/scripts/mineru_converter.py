#!/usr/bin/env python3
"""
MinerU PDF to Markdown Converter

PDF 논문을 MinerU를 사용하여 Markdown으로 변환합니다.

Usage:
    python mineru_converter.py --input-dir ./papers/ --output-dir ./converted/

Requirements:
    pip install mineru
    # 또는 전체 의존성: uv pip install mineru[all]
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def check_mineru_installation() -> bool:
    """MinerU 설치 확인"""
    try:
        from mineru import MinerU
        return True
    except ImportError:
        return False


def convert_pdf_to_markdown(
    pdf_path: Path,
    output_dir: Path,
    backend: str = "hybrid-auto-engine",
    language: str = "en"
) -> dict:
    """
    단일 PDF 파일을 Markdown으로 변환
    
    Args:
        pdf_path: PDF 파일 경로
        output_dir: 출력 디렉토리
        backend: MinerU 백엔드 (pipeline, vlm, hybrid-auto-engine)
        language: OCR 언어
    
    Returns:
        변환 결과 딕셔너리
    """
    from mineru import MinerU
    
    result = {
        "input": str(pdf_path),
        "output": None,
        "status": "pending",
        "pages": 0,
        "sections_found": [],
        "figures": 0,
        "tables": 0,
        "equations": 0,
        "warnings": [],
        "error": None
    }
    
    try:
        # MinerU 인스턴스 생성
        miner = MinerU(backend=backend)
        
        # PDF 변환
        output_name = pdf_path.stem
        output_path = output_dir / f"{output_name}.md"
        images_dir = output_dir / "images" / output_name
        
        # 변환 실행
        miner.convert(
            str(pdf_path),
            output_path=str(output_path),
            images_dir=str(images_dir),
            lang=language
        )
        
        # 결과 확인
        if output_path.exists():
            result["output"] = str(output_path)
            result["status"] = "success"
            
            # 변환된 MD 분석
            content = output_path.read_text(encoding="utf-8")
            result["sections_found"] = extract_sections(content)
            result["figures"] = content.lower().count("figure")
            result["tables"] = content.count("|---")
            result["equations"] = content.count("$$") // 2 + content.count("$") // 2
            
            # 페이지 수 추정 (대략적)
            result["pages"] = max(1, len(content) // 3000)
            
        else:
            result["status"] = "failed"
            result["error"] = "Output file not created"
            
    except Exception as e:
        result["status"] = "failed"
        result["error"] = str(e)
    
    return result


def extract_sections(content: str) -> list:
    """Markdown에서 섹션 헤더 추출"""
    import re
    
    sections = []
    section_patterns = [
        (r"#+\s*abstract", "Abstract"),
        (r"#+\s*introduction", "Introduction"),
        (r"#+\s*(materials?\s*(and|&)?\s*)?methods?", "Methods"),
        (r"#+\s*results?", "Results"),
        (r"#+\s*discussion", "Discussion"),
        (r"#+\s*conclusion", "Conclusion"),
        (r"#+\s*references?", "References"),
    ]
    
    content_lower = content.lower()
    
    for pattern, section_name in section_patterns:
        if re.search(pattern, content_lower):
            sections.append(section_name)
    
    return sections


def batch_convert(
    input_dir: Path,
    output_dir: Path,
    backend: str = "hybrid-auto-engine",
    language: str = "en",
    min_papers: int = 10
) -> dict:
    """
    폴더 내 모든 PDF를 일괄 변환
    
    Args:
        input_dir: PDF 파일들이 있는 디렉토리
        output_dir: 출력 디렉토리
        backend: MinerU 백엔드
        language: OCR 언어
        min_papers: 최소 논문 수 (경고용)
    
    Returns:
        변환 리포트 딕셔너리
    """
    # 출력 디렉토리 생성
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "images").mkdir(exist_ok=True)
    
    # PDF 파일 목록
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if len(pdf_files) == 0:
        return {
            "error": f"No PDF files found in {input_dir}",
            "summary": {"total": 0}
        }
    
    if len(pdf_files) < min_papers:
        print(f"Warning: Found {len(pdf_files)} PDFs, recommended minimum is {min_papers}")
    
    print(f"Found {len(pdf_files)} PDF files")
    print(f"Backend: {backend}")
    print(f"Output: {output_dir}")
    print("-" * 50)
    
    # 변환 결과
    results = []
    success_count = 0
    partial_count = 0
    failed_count = 0
    
    for i, pdf_path in enumerate(pdf_files, 1):
        print(f"[{i}/{len(pdf_files)}] Converting: {pdf_path.name}")
        
        result = convert_pdf_to_markdown(pdf_path, output_dir, backend, language)
        results.append(result)
        
        if result["status"] == "success":
            success_count += 1
            print(f"  ✓ Success: {len(result['sections_found'])} sections found")
        elif result["status"] == "partial":
            partial_count += 1
            print(f"  △ Partial: {result['warnings']}")
        else:
            failed_count += 1
            print(f"  ✗ Failed: {result['error']}")
    
    # 리포트 생성
    report = {
        "summary": {
            "total": len(pdf_files),
            "success": success_count,
            "partial": partial_count,
            "failed": failed_count
        },
        "files": results,
        "config": {
            "backend": backend,
            "language": language,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    # 리포트 저장
    report_path = output_dir / "conversion_report.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print("-" * 50)
    print(f"Conversion complete: {success_count} success, {partial_count} partial, {failed_count} failed")
    print(f"Report saved: {report_path}")
    
    return report


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF papers to Markdown using MinerU"
    )
    parser.add_argument(
        "--input-dir", "-i",
        type=Path,
        required=True,
        help="Directory containing PDF files"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=Path,
        required=True,
        help="Output directory for converted Markdown files"
    )
    parser.add_argument(
        "--backend", "-b",
        type=str,
        default="hybrid-auto-engine",
        choices=["pipeline", "vlm", "hybrid-auto-engine"],
        help="MinerU backend (default: hybrid-auto-engine)"
    )
    parser.add_argument(
        "--language", "-l",
        type=str,
        default="en",
        help="OCR language (default: en)"
    )
    parser.add_argument(
        "--min-papers",
        type=int,
        default=10,
        help="Minimum recommended papers (default: 10)"
    )
    
    args = parser.parse_args()
    
    # MinerU 설치 확인
    if not check_mineru_installation():
        print("Error: MinerU is not installed.")
        print("Install with: pip install mineru")
        print("Or: uv pip install mineru[all]")
        sys.exit(1)
    
    # 입력 디렉토리 확인
    if not args.input_dir.exists():
        print(f"Error: Input directory not found: {args.input_dir}")
        sys.exit(1)
    
    # 변환 실행
    report = batch_convert(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        backend=args.backend,
        language=args.language,
        min_papers=args.min_papers
    )
    
    # 결과 코드
    if report.get("error"):
        sys.exit(1)
    elif report["summary"]["failed"] > 0:
        sys.exit(2)  # 일부 실패
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
