#!/usr/bin/env python3
"""
Fund Classification Generator (Python Version)

DC형 70% 위험자산 한도 자동 검증을 위한 펀드 분류 데이터 생성
Converted from classify_funds.js to remove Node.js dependency

위험자산: 주식형, 해외주식형, 주식혼합형, 해외주식혼합형, 채권혼합형, 해외채권혼합형
안전자산: 채권형, 해외채권형, 기타 (MMF, 예금, 골드, TDF 등)

Usage:
    python classify_funds.py [output_dir]

    If output_dir is not specified, auto-detects investments/funds/ directory.
"""

import json
import re
from pathlib import Path
from datetime import datetime
import sys


# 위험자산 카테고리
RISK_ASSET_CATEGORIES = [
    "주식형",
    "해외주식형",
    "주식혼합형",
    "해외주식혼합형",
    "채권혼합형",
    "해외채권혼합형",
]

# 안전자산 카테고리
SAFE_ASSET_CATEGORIES = ["채권형", "해외채권형", "기타"]


def get_fund_category(fund_name: str) -> str:
    """펀드명으로 카테고리 추정 (generate_md.js 로직 기반)

    Args:
        fund_name: 펀드명

    Returns:
        str: 카테고리명 (주식형, 해외주식형, 채권형 등)
    """
    name = fund_name

    # 1. 해외 여부 확인
    overseas_pattern = r"해외|글로벌|미국|차이나|인디아|베트남|일본|유럽|아시아|이머징|Global|USA|China|India|Japan|Europe|Asia|Emerging"
    is_overseas = bool(re.search(overseas_pattern, name, re.IGNORECASE))

    # 2. 자산 유형 확인
    has_bond_mixed = bool(re.search(r"채권혼합|채권 혼합", name))
    has_stock_mixed = bool(re.search(r"주식혼합|주식 혼합", name))
    has_bond = (
        bool(re.search(r"채권|크레딧|국공채|인컴|하이일드|단기채", name))
        and not has_bond_mixed
    )
    has_stock = (
        bool(re.search(r"주식", name)) and not has_stock_mixed and not has_bond_mixed
    )

    # 3. 특수 유형 확인
    special_pattern = r"TDF|MMF|EMP|리츠|골드|부동산|원자재|금-재간접|TIF"
    is_special = bool(re.search(special_pattern, name))

    # 분류 결정
    if is_special:
        return "기타"

    if is_overseas:
        if has_bond_mixed:
            return "해외채권혼합형"
        if has_stock_mixed:
            return "해외주식혼합형"
        if has_bond:
            return "해외채권형"
        if has_stock:
            return "해외주식형"
        # 기본: 해외주식형으로 추정 (대부분 해외펀드는 주식형)
        return "해외주식형"
    else:
        if has_bond_mixed:
            return "채권혼합형"
        if has_stock_mixed:
            return "주식혼합형"
        if has_bond:
            return "채권형"
        if has_stock:
            return "주식형"
        return "기타"


def extract_theme(fund_name: str) -> list:
    """테마 추출

    Args:
        fund_name: 펀드명

    Returns:
        list: 매칭된 테마 목록
    """
    themes = {
        "semiconductor": r"반도체|필라델피아",
        "ai": r"AI|인공지능|Chat AI|메타버스",
        "robot": r"로봇|휴머노이드|로보틱스|로보테크",
        "healthcare": r"헬스케어|바이오|헬스사이언스",
        "dividend": r"배당|고배당|인컴",
        "value": r"가치|밸류",
        "growth": r"성장|그로스",
        "index": r"인덱스|KOSPI|S&P|나스닥|KRX",
        "ev": r"전기차|자율주행|모빌리티",
        "gold": r"골드|금",
        "energy": r"에너지|그린|클린테크",
        "reits": r"리츠|부동산",
        "space": r"우주항공",
    }

    matched = [
        theme
        for theme, pattern in themes.items()
        if re.search(pattern, fund_name, re.IGNORECASE)
    ]

    return matched if matched else ["general"]


def extract_region(fund_name: str) -> str:
    """지역 추출

    Args:
        fund_name: 펀드명

    Returns:
        str: 지역 코드
    """
    region_patterns = [
        (r"미국|USA|S&P|나스닥|Nasdaq", "us"),
        (r"차이나|중국|China", "china"),
        (r"인디아|인도|India", "india"),
        (r"일본|Japan|재팬", "japan"),
        (r"유럽|Europe|유로", "europe"),
        (r"베트남|Vietnam", "vietnam"),
        (r"아세안|ASEAN", "asean"),
        (r"아시아|Asia", "asia"),
        (r"브라질|Brazil", "brazil"),
        (r"이머징|Emerging", "emerging"),
        (r"글로벌|Global|월드|World", "global"),
        (r"코리아|한국|KOSPI|KRX|코스닥", "korea"),
    ]

    for pattern, region in region_patterns:
        if re.search(pattern, fund_name, re.IGNORECASE):
            return region

    return "korea"  # 기본값


def is_hedged(fund_name: str):
    """환헤지 여부 확인

    Args:
        fund_name: 펀드명

    Returns:
        bool or None: True(환헤지), False(환노출), None(명시되지 않음)
    """
    if re.search(r"\(H\)|\[H\]|H[)]|\(환헤지\)", fund_name, re.IGNORECASE):
        return True
    if re.search(r"\(UH\)|\[UH\]|UH[)]|\(환노출\)", fund_name, re.IGNORECASE):
        return False
    return None  # 명시되지 않음


def find_investments_repo():
    """Find the investments repository root directory

    Returns:
        Path: Path to investments repo root, or None if not found
    """
    current = Path(__file__).resolve().parent

    for _ in range(10):
        funds_dir = current / "funds"
        if funds_dir.exists() and (funds_dir / "fund_data.json").exists():
            return current

        if current.name == "honeypot":
            parent = current.parent
            funds_dir = parent / "funds"
            if funds_dir.exists():
                return parent

        parent = current.parent
        if parent == current:
            break
        current = parent

    return None


def main(output_dir=None, all_dir=None):
    """메인 실행 함수

    Args:
        output_dir: 출력 디렉토리 (None이면 자동 감지)
        all_dir: all/ 폴더 경로 (지정하면 all_fund_data.json 기반 분류 생성)
    """
    # Determine output directory
    if output_dir:
        funds_dir = Path(output_dir)
    else:
        repo_root = find_investments_repo()
        if repo_root:
            funds_dir = repo_root / "funds"
        else:
            print("Error: Could not find investments repository")
            sys.exit(1)

    # Determine which fund_data.json to use
    if all_dir:
        # Use all_fund_data.json from all/ directory
        all_dir_path = Path(all_dir)
        fund_data_path = all_dir_path / "all_fund_data.json"
        output_filename = "all_fund_classification.json"
    else:
        # Use regular fund_data.json
        fund_data_path = funds_dir / "fund_data.json"
        output_filename = "fund_classification.json"

    if not fund_data_path.exists():
        print(f"Error: {fund_data_path.name} not found at {fund_data_path}")
        sys.exit(1)

    # fund_data.json 읽기
    with open(fund_data_path, "r", encoding="utf-8") as f:
        fund_data_json = json.load(f)

    # Handle both old format (array) and new format ({_meta, funds})
    if isinstance(fund_data_json, list):
        funds = fund_data_json
    else:
        funds = fund_data_json.get("funds", [])

    # 분류 데이터 생성
    classification = {}

    for fund in funds:
        fund_name = fund.get("name", "")
        category = get_fund_category(fund_name)
        is_risk_asset = category in RISK_ASSET_CATEGORIES

        # Determine asset class
        if "채권" in category and "혼합" not in category:
            asset_class = "bond"
        elif "혼합" in category:
            asset_class = "mixed"
        elif "주식" in category:
            asset_class = "equity"
        else:
            asset_class = "other"

        classification[fund_name] = {
            "category": category,
            "riskAsset": is_risk_asset,
            "assetClass": asset_class,
            "region": extract_region(fund_name),
            "themes": extract_theme(fund_name),
            "hedged": is_hedged(fund_name),
            "riskLevel": fund.get("riskLevel", 0),
            "source": "fund_data.json + keyword classification",
            "generatedAt": datetime.now().strftime("%Y-%m-%d"),
        }

    # 통계 출력
    total = len(funds)
    risk_assets = sum(1 for c in classification.values() if c["riskAsset"])
    safe_assets = sum(1 for c in classification.values() if not c["riskAsset"])

    by_category = {}
    for c in classification.values():
        cat = c["category"]
        by_category[cat] = by_category.get(cat, 0) + 1

    print("=== Fund Classification Stats ===")
    print(f"Total funds: {total}")
    print(f"Risk assets: {risk_assets} ({risk_assets / total * 100:.1f}%)")
    print(f"Safe assets: {safe_assets} ({safe_assets / total * 100:.1f}%)")
    print("\nBy category:")

    for cat, count in sorted(by_category.items(), key=lambda x: -x[1]):
        risk_label = "[RISK]" if cat in RISK_ASSET_CATEGORIES else "[SAFE]"
        print(f"  {cat}: {count} {risk_label}")

    # 파일 저장
    if all_dir:
        output_path = Path(all_dir) / output_filename
    else:
        output_path = funds_dir / output_filename

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(classification, f, ensure_ascii=False, indent=2)

    print(f"\nSaved to: {output_path}")

    return classification


if __name__ == "__main__":
    # Command line argument: output directory
    output_dir = sys.argv[1] if len(sys.argv) > 1 else None
    main(output_dir)
