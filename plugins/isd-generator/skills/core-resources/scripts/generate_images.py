#!/usr/bin/env python3
"""
Gemini API를 사용하여 프롬프트 파일에서 이미지를 생성하는 스크립트

사용법:
    python generate_images.py --prompts-dir [프롬프트 폴더] --output-dir [출력 폴더]

설정:
    - 모델: gemini-3-pro-image-preview
    - 해상도: 4K
    - 비율: 16:9
    - 사고모드: 활성화
    - 고급 텍스트 렌더링: 활성화
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
MODEL_NAME = os.environ.get("GEMINI_MODEL", "gemini-3-pro-image-preview")

if not GEMINI_API_KEY:
    print("[에러] GEMINI_API_KEY 환경변수가 설정되지 않았습니다.")
    print("  export GEMINI_API_KEY='your-api-key' 또는 .env 파일에 설정하세요.")
    sys.exit(1)


def extract_prompt_content(md_file_path: str) -> str:
    """
    마크다운 프롬프트 파일에서 핵심 프롬프트 내용만 추출
    메타데이터, 버전 관리, 체크리스트 등 불필요한 부분 제외하여 토큰 절약

    포함: 섹션 1~12 (캡션, 유형, 색상, 레이아웃, 텍스트 등)
    제외: 섹션 13~14 (출처 테이블, 체크리스트)
    """
    with open(md_file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 제외할 섹션 시작점
    exclude_sections = [
        "## 13. 참고 데이터 출처",
        "## 14. 체크리스트",
    ]

    # 제외 섹션 이전까지의 내용만 추출
    for exclude in exclude_sections:
        if exclude in content:
            content = content.split(exclude)[0]

    return content.strip()


def generate_image(
    client, prompt_text: str, output_path: str, max_retries: int = 3
) -> bool:
    """
    Gemini API를 호출하여 이미지 생성

    Args:
        client: Gemini API 클라이언트
        prompt_text: 이미지 생성용 프롬프트
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
    프롬프트 폴더의 모든 .md 파일을 처리하여 이미지 생성

    Args:
        prompts_dir: 프롬프트 파일이 있는 폴더 경로
        output_dir: 생성된 이미지를 저장할 폴더 경로

    Returns:
        dict: {"success": [...], "failed": [...]} 형태의 결과
    """
    prompts_path = Path(prompts_dir)
    output_path = Path(output_dir)

    # 출력 폴더 생성
    output_path.mkdir(parents=True, exist_ok=True)

    # 프롬프트 파일 목록 (prompt_index.md 제외)
    prompt_files = sorted(
        [f for f in prompts_path.glob("*.md") if f.name != "prompt_index.md"]
    )

    if not prompt_files:
        print(f"[에러] 프롬프트 파일이 없습니다: {prompts_dir}")
        return {"success": [], "failed": []}

    print(f"[시작] {len(prompt_files)}개 프롬프트 처리")
    print(f"  - 프롬프트 폴더: {prompts_dir}")
    print(f"  - 출력 폴더: {output_dir}")
    print(f"  - 모델: {MODEL_NAME}")
    print(f"  - 설정: 4K, 16:9, 사고모드 활성화, 고급 텍스트 렌더링")
    print()

    # API 클라이언트 초기화
    client = genai.Client(api_key=GEMINI_API_KEY)

    results = {"success": [], "failed": []}

    for i, prompt_file in enumerate(prompt_files, 1):
        # 파일명에서 캡션명 추출 (01_연구개발_목표_및_비전.md -> 01_연구개발_목표_및_비전)
        caption_name = prompt_file.stem
        output_file = output_path / f"{caption_name}.png"

        print(f"[{i}/{len(prompt_files)}] {caption_name}")

        # 프롬프트 내용 추출 (토큰 절약을 위해 핵심 섹션만)
        prompt_content = extract_prompt_content(str(prompt_file))

        # 이미지 생성
        if generate_image(client, prompt_content, str(output_file)):
            print(f"  ✓ 저장 완료: {output_file}")
            results["success"].append(caption_name)
        else:
            print(f"  ✗ 생성 실패: {caption_name}")
            results["failed"].append(caption_name)

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
        description="Gemini API를 사용하여 프롬프트 파일에서 이미지 생성"
    )
    parser.add_argument(
        "--prompts-dir", "-p", required=True, help="프롬프트 파일이 있는 폴더 경로"
    )
    parser.add_argument(
        "--output-dir", "-o", required=True, help="생성된 이미지를 저장할 폴더 경로"
    )
    parser.add_argument(
        "--model",
        "-m",
        default=None,
        help="Gemini 모델명 (기본값: GEMINI_MODEL 환경변수 또는 gemini-3-pro-image-preview)",
    )

    args = parser.parse_args()

    # 모델명 오버라이드
    global MODEL_NAME
    if args.model:
        MODEL_NAME = args.model

    if not os.path.isdir(args.prompts_dir):
        print(f"[에러] 프롬프트 폴더가 존재하지 않습니다: {args.prompts_dir}")
        sys.exit(1)

    results = process_prompts(args.prompts_dir, args.output_dir)

    # 실패가 있으면 exit code 1
    sys.exit(1 if results["failed"] else 0)


if __name__ == "__main__":
    main()
