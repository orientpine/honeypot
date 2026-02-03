#!/usr/bin/env python3
"""
CSV to JSON Fund Data Converter (Honeypot Plugin Version)

Converts 과학기술공제회 퇴직연금 CSV files to fund_data.json and fund_fees.json
This version is designed to be called from the investments-portfolio plugin.

Usage:
    python update_fund_data.py --file <csv_path>
    python update_fund_data.py --file <csv_path> --dry-run
    python update_fund_data.py --file <csv_path> --output-dir <output_dir>

Output Directory Resolution:
    1. If --output-dir is specified, use that
    2. Otherwise, auto-detect investments repo and use funds/ directory
"""

import argparse
import csv
import json
from pathlib import Path
from datetime import datetime
import sys
import shutil
import re


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Convert 과학기술공제회 퇴직연금 CSV to JSON format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python update_fund_data.py --file resource/25년12월_상품제안서_퇴직연금(DCIRP).csv
  python update_fund_data.py --file resource/25년12월_상품제안서_퇴직연금(DCIRP).csv --dry-run
  python update_fund_data.py --file resource/25년12월_상품제안서_퇴직연금(DCIRP).csv --output-dir funds/
        """,
    )

    parser.add_argument("--file", required=True, help="Path to CSV file")

    parser.add_argument(
        "--output-dir",
        default=None,
        help="Output directory for JSON files (default: auto-detect investments/funds/)",
    )

    parser.add_argument(
        "--dry-run", action="store_true", help="Show preview without writing files"
    )

    parser.add_argument(
        "--codes-file",
        default="funds/investable_codes.json",
        help="Path to investable codes JSON file for filtering (default: funds/investable_codes.json)",
    )

    return parser.parse_args()


def find_investments_repo():
    """Find the investments repository root directory

    Searches upward from the script location to find the investments repo.
    The repo is identified by the presence of funds/fund_data.json

    Returns:
        Path: Path to investments repo root, or None if not found
    """
    # Start from script location
    current = Path(__file__).resolve().parent

    # Search upward (max 10 levels)
    for _ in range(10):
        # Check if this looks like investments repo
        funds_dir = current / "funds"
        if funds_dir.exists() and (funds_dir / "fund_data.json").exists():
            return current

        # Also check if we're in honeypot submodule
        if current.name == "honeypot":
            # Go up to parent (investments repo)
            parent = current.parent
            funds_dir = parent / "funds"
            if funds_dir.exists():
                return parent

        # Move up one level
        parent = current.parent
        if parent == current:
            break
        current = parent

    return None


def get_output_directory(specified_dir=None):
    """Determine the output directory for JSON files

    Args:
        specified_dir: User-specified output directory (optional)

    Returns:
        Path: Output directory path

    Raises:
        ValueError: If no valid output directory can be determined
    """
    if specified_dir:
        return Path(specified_dir)

    # Auto-detect investments repo
    repo_root = find_investments_repo()
    if repo_root:
        return repo_root / "funds"

    raise ValueError(
        "Could not auto-detect investments repository. "
        "Please specify --output-dir explicitly."
    )


def detect_header_row(rows):
    """Find header row by searching for '펀드코드' keyword

    Args:
        rows: List of CSV rows

    Returns:
        tuple: (header_row_index, header_list)

    Raises:
        ValueError: If header row not found
    """
    for i, row in enumerate(rows):
        if any("펀드코드" in cell for cell in row):
            return i, row

    raise ValueError("Header row with '펀드코드' not found in CSV file")


def extract_metadata(rows):
    """Extract metadata from CSV rows 1-7

    Args:
        rows: List of CSV rows

    Returns:
        dict: Metadata with keys: provider, systemType, productType, baseDate
    """
    metadata = {}

    try:
        # Row 1: 사업자명 (Provider name)
        if len(rows) > 0 and len(rows[0]) > 1:
            metadata["provider"] = rows[0][1].strip()
        else:
            metadata["provider"] = ""

        # Row 2: 제도유형 (System type)
        if len(rows) > 1 and len(rows[1]) > 1:
            metadata["systemType"] = rows[1][1].strip()
        else:
            metadata["systemType"] = ""

        # Row 3: 상품유형 (Product type)
        if len(rows) > 2 and len(rows[2]) > 1:
            metadata["productType"] = rows[2][1].strip()
        else:
            metadata["productType"] = ""

        # Row 4: 기준일 (Base date: "2025-12-01, 제로인")
        if len(rows) > 3 and len(rows[3]) > 1:
            base_date_cell = rows[3][1].strip()
            # Extract date part before comma
            if "," in base_date_cell:
                metadata["baseDate"] = base_date_cell.split(",")[0].strip()
            else:
                metadata["baseDate"] = base_date_cell
        else:
            metadata["baseDate"] = ""

    except Exception as e:
        print(f"Warning: Error extracting metadata: {e}")
        metadata = {"provider": "", "systemType": "", "productType": "", "baseDate": ""}

    return metadata


def load_csv(file_path):
    """Load and parse CSV file

    Args:
        file_path: Path to CSV file

    Returns:
        tuple: (metadata, header, data_rows)

    Raises:
        FileNotFoundError: If file doesn't exist
        UnicodeDecodeError: If file encoding is invalid
        ValueError: If CSV structure is invalid
    """
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
    except UnicodeDecodeError as e:
        raise UnicodeDecodeError(
            e.encoding,
            e.object,
            e.start,
            e.end,
            f"Failed to read CSV file with UTF-8 encoding: {e.reason}",
        )

    if len(rows) < 9:
        raise ValueError(
            f"CSV file has only {len(rows)} rows, expected at least 9 rows"
        )

    # Extract metadata from rows 1-7
    metadata = extract_metadata(rows)

    # Find header row (should be around row 8, but search to be safe)
    header_index, header = detect_header_row(rows)

    # Data rows start after header
    data_rows = rows[header_index + 1 :]

    return metadata, header, data_rows


def parse_risk_level(risk_str):
    """Parse 위험등급 string

    Args:
        risk_str: "N등급(위험명)" format

    Returns:
        tuple: (level: int, name: str with spaces removed)

    Example:
        "2등급(높은 위험)" → (2, "높은위험")
    """
    match = re.match(r"(\d+)등급\((.+)\)", risk_str)
    if match:
        level = int(match.group(1))
        name = match.group(2).replace(" ", "")  # Remove spaces
        return level, name
    return 0, ""  # Fallback for unparseable


def parse_fund_data(row, header):
    """Parse a single CSV row into fund data structure

    Args:
        row: List of CSV cell values
        header: List of column names from header row

    Returns:
        dict: Fund data following SCHEMA.md specification
    """
    # Create header index mapping
    col_idx = {name: i for i, name in enumerate(header)}

    # Helper function to safely get cell value
    def get_cell(col_name):
        idx = col_idx.get(col_name)
        if idx is not None and idx < len(row):
            return row[idx].strip()
        return ""

    # Extract basic fields
    fund_code = get_cell("펀드코드")
    fund_name = get_cell("펀드명")
    company = get_cell("운용회사명")

    # Parse 위험등급: "2등급(높은 위험)" → riskLevel: 2, riskName: "높은위험"
    risk_str = get_cell("위험등급")
    risk_level, risk_name = parse_risk_level(risk_str)

    # Convert 순자산: remove commas, multiply by 10000 (억원 → 천원)
    net_assets_str = get_cell("순자산총액(억원)").replace(",", "")
    if net_assets_str:
        try:
            net_assets = str(int(float(net_assets_str) * 10000))
        except ValueError:
            net_assets = "0"
    else:
        net_assets = "0"

    # Extract return fields (handle empty as "")
    return10y = get_cell("수익률(10Y)")
    return7y = get_cell("수익률(7Y)")
    return5y = get_cell("수익률(5Y)")
    return3y = get_cell("수익률(3Y)")
    return1y = get_cell("수익률(1Y)")
    return6m = get_cell("수익률(6M)")

    # Extract other fields
    inception_date = get_cell("설정일")
    affiliate_str = get_cell("계열사 여부")
    is_affiliate = "계열사" in affiliate_str
    fund_type = get_cell("비고")

    return {
        "fundCode": fund_code,
        "name": fund_name,
        "company": company,
        "riskLevel": risk_level,
        "riskName": risk_name,
        "return10y": return10y,
        "return7y": return7y,
        "return5y": return5y,
        "return3y": return3y,
        "return1y": return1y,
        "return6m": return6m,
        "netAssets": net_assets,
        "inceptionDate": inception_date,
        "isAffiliate": is_affiliate,
        "fundType": fund_type,
    }


def archive_existing_file(file_path, version_date):
    """Archive existing file before overwriting

    Args:
        file_path: Path to file to archive (e.g., funds/fund_data.json)
        version_date: Version date string (YYYY-MM-DD) for archive filename

    Returns:
        Path to archived file, or None if file didn't exist
    """
    file_path = Path(file_path)

    if not file_path.exists():
        return None  # No file to archive (first run)

    # Create archive directory
    archive_dir = file_path.parent / "archive"
    archive_dir.mkdir(exist_ok=True)

    # Create .gitkeep file
    gitkeep = archive_dir / ".gitkeep"
    gitkeep.touch()

    # Build archive filename: fund_data_2025-12-01.json
    base_name = file_path.stem  # "fund_data"
    ext = file_path.suffix  # ".json"
    archive_name = f"{base_name}_{version_date}{ext}"
    archive_path = archive_dir / archive_name

    # Copy file to archive
    shutil.copy2(file_path, archive_path)

    print(f"  Archived: {file_path.name} -> archive/{archive_name}")
    return archive_path


def run_dependency_chain(output_dir):
    """Execute dependent scripts after JSON generation

    Args:
        output_dir: Directory where JSON files were written
    """
    print("\n" + "=" * 60)
    print("Running Dependency Chain")
    print("=" * 60)

    # Import and run Python classification script
    scripts_dir = Path(__file__).parent
    classify_script = scripts_dir / "classify_funds.py"

    if classify_script.exists():
        print("\n1. Classifying funds...")
        try:
            # Import and run the classification module
            import importlib.util

            spec = importlib.util.spec_from_file_location(
                "classify_funds", classify_script
            )
            if spec is None or spec.loader is None:
                raise ImportError(f"Could not load module spec from {classify_script}")
            classify_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(classify_module)

            # Run classification for filtered funds
            classify_module.main(output_dir)
            print("   OK fund_classification.json regenerated")

            # Run classification for ALL funds
            all_dir = Path(output_dir) / "all"
            if all_dir.exists() and (all_dir / "all_fund_data.json").exists():
                print("\n2. Classifying ALL funds...")
                classify_module.main(output_dir, all_dir=str(all_dir))
                print("   OK all_fund_classification.json regenerated")
        except Exception as e:
            print(f"   ERROR classify_funds.py failed: {e}")
    else:
        print("\n1. classify_funds.py not found - skipping classification")
        print(f"   Expected at: {classify_script}")

    print("\n" + "=" * 60)
    print("Dependency Chain Complete")
    print("=" * 60)


def parse_fund_fees(row, header):
    """Parse a single CSV row into fee data structure

    Args:
        row: List of CSV cell values
        header: List of column names from header row

    Returns:
        dict: Fee data following SCHEMA.md specification

    Note:
        Returns dict will be used with fundCode as key in output
    """
    # Create header index mapping
    col_idx = {name: i for i, name in enumerate(header)}

    # Helper function to safely get cell value
    def get_cell(col_name):
        idx = col_idx.get(col_name)
        if idx is not None and idx < len(row):
            return row[idx].strip()
        return ""

    # Extract fields
    fund_code = get_cell("펀드코드")
    fund_name = get_cell("펀드명")
    total_fee = get_cell("비율(%)")
    annual_cost = get_cell("1년투자비용(원)").replace(",", "")

    return {
        "fundCode": fund_code,
        "fundName": fund_name,
        "totalFee": total_fee,
        "annualCost": annual_cost,
    }


def load_investable_codes(codes_file):
    """Load investable codes from JSON file

    Args:
        codes_file: Path to investable codes JSON file

    Returns:
        set: Set of investable fund codes

    Raises:
        FileNotFoundError: If codes file doesn't exist
        ValueError: If codes file has invalid structure
    """
    codes_path = Path(codes_file)
    if not codes_path.exists():
        raise FileNotFoundError(f"Investable codes file not found: {codes_file}")

    with open(codes_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    codes = data.get("codes", [])
    if not codes:
        raise ValueError(f"No codes found in {codes_file}")

    return set(codes)


def filter_fund_data(fund_data, investable_codes):
    """Filter fund_data by fundCode

    Args:
        fund_data: Original fund_data dict
        investable_codes: Set of investable fundCodes

    Returns:
        dict: Filtered fund_data with updated _meta (recordCount, missing)
    """
    original_funds = fund_data.get("funds", [])
    filtered_funds = [
        f for f in original_funds if f.get("fundCode") in investable_codes
    ]

    # Calculate missing codes
    found_codes = {f["fundCode"] for f in filtered_funds}
    missing_codes = [
        code for code in sorted(investable_codes) if code not in found_codes
    ]

    return {
        "_meta": {
            **fund_data["_meta"],
            "recordCount": len(filtered_funds),
            "missing": missing_codes,
        },
        "funds": filtered_funds,
    }


def filter_fund_fees(fund_fees, investable_codes):
    """Filter fund_fees by fundCode

    Args:
        fund_fees: Original fund_fees dict
        investable_codes: Set of investable fundCodes

    Returns:
        dict: Filtered fund_fees with updated _meta.recordCount
    """
    original_fees = fund_fees.get("fees", {})
    filtered_fees = {
        code: fee for code, fee in original_fees.items() if code in investable_codes
    }

    return {
        "_meta": {
            **fund_fees["_meta"],
            "recordCount": len(filtered_fees),
        },
        "fees": filtered_fees,
    }


def process_csv(csv_path, output_dir, dry_run, codes_file=None):
    """Main processing function with integrated filtering workflow

    Args:
        csv_path: Path to CSV file
        output_dir: Output directory for JSON files
        dry_run: If True, show preview without writing files
        codes_file: Path to investable codes JSON file for filtering
    """
    # Load CSV
    print("=" * 60)
    print("CSV to JSON Fund Data Converter" + (" - DRY RUN" if dry_run else ""))
    print("=" * 60)
    print()

    metadata, header, data_rows = load_csv(csv_path)

    # Display CSV metadata
    print("CSV Metadata:")
    print(f"  Provider: {metadata['provider']}")
    print(f"  System: {metadata['systemType']}")
    print(f"  Product: {metadata['productType']}")
    print(f"  Base Date: {metadata['baseDate']}")
    print()

    # Display CSV structure
    header_index = 0
    for i, row in enumerate(csv.reader(open(csv_path, "r", encoding="utf-8"))):
        if any("펀드코드" in cell for cell in row):
            header_index = i + 1  # 1-based row number
            break

    print("CSV Structure:")
    print(f"  Header row: Row {header_index}")
    print(f"  Columns: {len(header)}")
    print(f"  Data rows: {len(data_rows)}")
    print()

    # Parse all rows
    fund_data_list = []
    fund_fees_dict = {}

    for row in data_rows:
        # Skip empty rows
        if not row or not any(cell.strip() for cell in row):
            continue

        # Parse fund data
        fund_data = parse_fund_data(row, header)

        # Skip rows without fundCode
        if not fund_data["fundCode"]:
            continue

        fund_data_list.append(fund_data)

        # Parse fund fees
        fund_fees = parse_fund_fees(row, header)
        fund_fees_dict[fund_fees["fundCode"]] = fund_fees

    # Display sample funds
    print(f"Total funds parsed: {len(fund_data_list)}")
    print()

    if dry_run:
        # Show fund_data.json preview
        print("Sample fund_data.json preview (first 3 funds):")
        print()
        for i, fund in enumerate(fund_data_list[:3], 1):
            print(f"Fund {i}:")
            print(json.dumps(fund, ensure_ascii=False, indent=2))
            print()

        # Show fund_fees.json preview
        print("Sample fund_fees.json preview:")
        print(
            json.dumps(
                {k: v for k, v in list(fund_fees_dict.items())[:3]},
                ensure_ascii=False,
                indent=2,
            )
        )
        print()

        # Show filtering statistics if codes_file provided
        if codes_file:
            try:
                investable_codes = load_investable_codes(codes_file)
                all_codes = {f["fundCode"] for f in fund_data_list}
                filtered_count = len(all_codes & investable_codes)
                missing_codes = [
                    c for c in sorted(investable_codes) if c not in all_codes
                ]

                print()
                print("Statistics:")
                print(f"  Total funds: {len(fund_data_list)}")
                print(f"  Filtered funds: {filtered_count}")
                print(f"  Missing funds: {len(missing_codes)}")
                if missing_codes:
                    print(
                        f"  Missing codes: {missing_codes[:5]}{'...' if len(missing_codes) > 5 else ''}"
                    )
            except FileNotFoundError as e:
                print(f"\nError: {e}")
                sys.exit(1)

        print()
        print("=" * 60)
        print("DRY RUN COMPLETE - No files created")
        print("=" * 60)
        return

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().astimezone().isoformat()
    version_date = metadata["baseDate"]

    all_fund_data_json = {
        "_meta": {
            "version": version_date,
            "sourceFile": Path(csv_path).name,
            "updatedAt": timestamp,
            "recordCount": len(fund_data_list),
        },
        "funds": fund_data_list,
    }

    all_fund_fees_json = {
        "_meta": {
            "version": version_date,
            "sourceFile": Path(csv_path).name,
            "updatedAt": timestamp,
            "recordCount": len(fund_fees_dict),
        },
        "fees": fund_fees_dict,
    }

    # Save ALL funds to funds/all/ directory
    all_dir = output_path / "all"
    all_dir.mkdir(parents=True, exist_ok=True)

    print()
    print("Writing ALL fund files to all/ directory...")
    all_fund_data_path = all_dir / "all_fund_data.json"
    all_fund_fees_path = all_dir / "all_fund_fees.json"

    with open(all_fund_data_path, "w", encoding="utf-8") as f:
        json.dump(all_fund_data_json, f, ensure_ascii=False, indent=2)
    print(f"  {all_fund_data_path}")

    with open(all_fund_fees_path, "w", encoding="utf-8") as f:
        json.dump(all_fund_fees_json, f, ensure_ascii=False, indent=2)
    print(f"  {all_fund_fees_path}")

    # Filter and save to root funds/ directory
    if codes_file:
        try:
            investable_codes = load_investable_codes(codes_file)
        except FileNotFoundError as e:
            print(f"\nError: {e}")
            sys.exit(1)

        filtered_fund_data = filter_fund_data(all_fund_data_json, investable_codes)
        filtered_fund_fees = filter_fund_fees(all_fund_fees_json, investable_codes)

        if filtered_fund_data["_meta"]["recordCount"] == 0:
            print("\nError: Filtering resulted in 0 funds - check codes file")
            sys.exit(1)

        fund_data_path = output_path / "fund_data.json"
        fund_fees_path = output_path / "fund_fees.json"

        print()
        print("Archiving existing filtered files...")
        archive_existing_file(fund_data_path, version_date)
        archive_existing_file(fund_fees_path, version_date)

        print()
        print("Writing FILTERED fund files...")
        with open(fund_data_path, "w", encoding="utf-8") as f:
            json.dump(filtered_fund_data, f, ensure_ascii=False, indent=2)
        print(f"  {fund_data_path}")

        with open(fund_fees_path, "w", encoding="utf-8") as f:
            json.dump(filtered_fund_fees, f, ensure_ascii=False, indent=2)
        print(f"  {fund_fees_path}")

        missing_count = len(filtered_fund_data["_meta"]["missing"])
        print()
        print("Statistics:")
        print(f"  Total funds: {len(fund_data_list)}")
        print(f"  Filtered funds: {filtered_fund_data['_meta']['recordCount']}")
        print(f"  Missing funds: {missing_count}")
    else:
        fund_data_path = output_path / "fund_data.json"
        fund_fees_path = output_path / "fund_fees.json"

        print()
        print("Archiving existing files...")
        archive_existing_file(fund_data_path, version_date)
        archive_existing_file(fund_fees_path, version_date)

        print()
        print("Writing fund files (no filtering)...")
        with open(fund_data_path, "w", encoding="utf-8") as f:
            json.dump(all_fund_data_json, f, ensure_ascii=False, indent=2)
        print(f"  {fund_data_path}")

        with open(fund_fees_path, "w", encoding="utf-8") as f:
            json.dump(all_fund_fees_json, f, ensure_ascii=False, indent=2)
        print(f"  {fund_fees_path}")

    print()
    print("=" * 60)
    print("CONVERSION COMPLETE")
    print("=" * 60)
    print()
    print(f"Total funds processed: {len(fund_data_list)}")
    print()

    run_dependency_chain(output_dir)


def main():
    """Main entry point"""
    args = parse_args()

    # Validate file exists
    csv_path = Path(args.file)
    if not csv_path.exists():
        print(f"Error: File not found: {csv_path}")
        sys.exit(1)

    # Determine output directory
    try:
        output_dir = get_output_directory(args.output_dir)
        print(f"Output directory: {output_dir}")
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Process
    try:
        process_csv(csv_path, output_dir, args.dry_run, args.codes_file)
    except UnicodeDecodeError as e:
        print(f"Error: File encoding error - {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"Error: Invalid CSV format - {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
