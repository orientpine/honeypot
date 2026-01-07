#!/usr/bin/env python3
"""
Gemini API를 사용하여 슬라이드 프롬프트 파일에서 이미지를 생성하는 스크립트

사용법:
    python generate_slide_images.py --prompts-dir [프롬프트 폴더] --output-dir [출력 폴더]

설정:
    - 모델: gemini-3-pro-image-preview
    - 해상도: 4K
    - 비율: 16:9
    - 사고모드: 활성화
    - 고급 텍스트 렌더링: 활성화

입력: slide-prompt-generator로 생성된 슬라이드 프롬프트 (.md)
출력: 정부/공공기관 발표용 고해상도 슬라이드 이미지 (.png)
"""

import os
import sys
import time
import argparse
from pathlib import Path

from google import genai
from google.genai import types

# API 설정
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
MODEL_NAME = "gemini-3-pro-image-preview"

if not GEMINI_API_KEY:
    print("[에러] GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    print("  export GEMINI_API_KEY='your-api-key' 또는 .env 파일에 설정하세요.")
    sys.exit(1)


def extract_prompt_content(md_file_path: str) -> str:
    """
    슬라이드 프롬프트 파일 전체 내용 반환

    slide-prompt-generator 형식:
    - 목적, 톤앤매너, 스타일, 색상, 조명, 해상도
    - 슬라이드 레이아웃, 상단 타이틀, 메인 콘텐츠 섹션들
    - 인포그래픽 디테일, 금지 요소, 최종 결과물 목표

    (제외 섹션 없이 전체 사용)
    """
    with open(md_file_path, "r", encoding="utf-8") as f:
        return f.read().strip()


def generate_image(
    client, prompt_text: str, output_path: str, max_retries: int = 3
) -> bool:
    """
    Gemini API를 호출하여 슬라이드 이미지 생성

    Args:
        client: Gemini API 클라이언트
        prompt_text: 슬라이드 이미지 생성용 프롬프트
        output_path: 이미지 저장 경로
        max_retries: 최대 재시도 횟수

    Returns:
        bool: 생성 성공 여부
    """
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt_text,
                config=types.GenerateContentConfig(
                    response_modalities=["TEXT", "IMAGE"],
                    image_config=types.ImageConfig(
                        aspect_ratio="16:9", image_size="4K"
                    ),
                ),
            )

            # 사고 과정 출력 (있는 경우)
            for part in response.parts:
                if hasattr(part, "thought") and part.thought:
                    if part.text:
                        print(f"  [사고 과정] {part.text[:100]}...")

            # 이미지 저장
            for part in response.parts:
                if part.inline_data is not None:
                    image = part.as_image()
                    image.save(output_path)
                    return True

            print(f"  [경고] 이미지 데이터 없음, 재시도 {attempt + 1}/{max_retries}")

        except Exception as e:
            print(f"  [에러] {e}, 재시도 {attempt + 1}/{max_retries}")
            if attempt < max_retries - 1:
                time.sleep(5)

    return False


def process_prompts(prompts_dir: str, output_dir: str) -> dict:
    """
    슬라이드 프롬프트 폴더의 모든 .md 파일을 처리하여 이미지 생성

    Args:
        prompts_dir: 슬라이드 프롬프트 파일이 있는 폴더 경로
        output_dir: 생성된 이미지를 저장할 폴더 경로

    Returns:
        dict: {"success": [...], "failed": [...]} 형태의 결과
    """
    prompts_path = Path(prompts_dir)
    output_path = Path(output_dir)

    # 출력 폴더 생성
    output_path.mkdir(parents=True, exist_ok=True)

    # 프롬프트 파일 목록 (메타/인덱스 파일 제외)
    exclude_files = ["prompt_index.md", "공통및특화작업구조설명.md"]
    prompt_files = sorted(
        [f for f in prompts_path.glob("*.md") if f.name not in exclude_files]
    )

    if not prompt_files:
        print(f"[에러] 슬라이드 프롬프트 파일이 없습니다: {prompts_dir}")
        return {"success": [], "failed": []}

    print(f"[시작] {len(prompt_files)}개 슬라이드 프롬프트 처리")
    print(f"  - 프롬프트 폴더: {prompts_dir}")
    print(f"  - 출력 폴더: {output_dir}")
    print(f"  - 모델: {MODEL_NAME}")
    print(f"  - 설정: 4K, 16:9, 사고모드 활성화, 고급 텍스트 렌더링")
    print()

    # API 클라이언트 초기화
    client = genai.Client(api_key=GEMINI_API_KEY)

    results = {"success": [], "failed": []}

    for i, prompt_file in enumerate(prompt_files, 1):
        # 파일명에서 슬라이드명 추출 (01_연구비전_최종목표.md -> 01_연구비전_최종목표)
        slide_name = prompt_file.stem
        output_file = output_path / f"{slide_name}.png"

        print(f"[{i}/{len(prompt_files)}] {slide_name}")

        # 이미 생성된 파일이 있으면 스킵
        if output_file.exists():
            print(f"  [SKIP] Already exists: {output_file}")
            results["success"].append(slide_name)
            continue

        # 프롬프트 내용 추출 (전체 사용)
        prompt_content = extract_prompt_content(str(prompt_file))

        # 이미지 생성
        if generate_image(client, prompt_content, str(output_file)):
            print(f"  [OK] Saved: {output_file}")
            results["success"].append(slide_name)
        else:
            print(f"  [FAIL] Failed: {slide_name}")
            results["failed"].append(slide_name)

        # API 호출 간 대기 (rate limit 방지)
        if i < len(prompt_files):
            time.sleep(2)

    # 결과 요약
    print()
    print("=" * 50)
    print(f"[완료] 성공: {len(results['success'])}, 실패: {len(results['failed'])}")
    if results["failed"]:
        print(f"[실패 목록] {', '.join(results['failed'])}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Gemini API를 사용하여 슬라이드 프롬프트에서 이미지 생성"
    )
    parser.add_argument(
        "--prompts-dir",
        "-p",
        required=True,
        help="슬라이드 프롬프트 파일이 있는 폴더 경로",
    )
    parser.add_argument(
        "--output-dir",
        "-o",
        required=True,
        help="생성된 슬라이드 이미지를 저장할 폴더 경로",
    )

    args = parser.parse_args()

    if not os.path.isdir(args.prompts_dir):
        print(f"[에러] 프롬프트 폴더가 존재하지 않습니다: {args.prompts_dir}")
        sys.exit(1)

    results = process_prompts(args.prompts_dir, args.output_dir)

    # 실패가 있으면 exit code 1
    sys.exit(1 if results["failed"] else 0)


if __name__ == "__main__":
    main()
