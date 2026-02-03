#!/usr/bin/env python3
"""
Fund Data Restructuring Script

Restructures fund data by:
1. Creating funds/all/ directory
2. Copying original data with all_ prefix
3. Filtering fund_data.json, fund_fees.json, fund_classification.json
   based on investable_funds.json
4. Updating _meta.recordCount
5. Saving filtered data to funds/ root

Usage:
    python restructure_funds.py --funds-dir funds
    python restructure_funds.py --funds-dir funds --dry-run
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
import shutil


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Restructure fund data by filtering based on investable list",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python restructure_funds.py --funds-dir funds
  python restructure_funds.py --funds-dir funds --dry-run
        """,
    )

    parser.add_argument(
        "--funds-dir",
        required=True,
        help="Path to funds directory",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show preview without writing files",
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


def get_funds_directory(specified_dir=None):
    """Determine the funds directory

    Args:
        specified_dir: User-specified funds directory (optional)

    Returns:
        Path: Funds directory path

    Raises:
        ValueError: If no valid funds directory can be determined
    """
    if specified_dir:
        funds_path = Path(specified_dir)
        if funds_path.is_absolute():
            return funds_path
        # Relative path - resolve from repo root
        repo_root = find_investments_repo()
        if repo_root:
            return repo_root / specified_dir
        return funds_path

    # Auto-detect investments repo
    repo_root = find_investments_repo()
    if repo_root:
        return repo_root / "funds"

    raise ValueError(
        "Could not auto-detect investments repository. "
        "Please specify --funds-dir explicitly."
    )


def load_json(file_path):
    """Load JSON file

    Args:
        file_path: Path to JSON file

    Returns:
        dict: Parsed JSON data

    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If JSON is invalid
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(file_path, data, dry_run=False):
    """Save JSON file

    Args:
        file_path: Path to JSON file
        data: Data to save
        dry_run: If True, don't actually write
    """
    if dry_run:
        return

    file_path.parent.mkdir(parents=True, exist_ok=True)
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def extract_investable_codes_and_names(investable_path):
    """Extract fundCode and name from investable_funds.json

    Args:
        investable_path: Path to investable_funds.json

    Returns:
        tuple: (set of fundCodes, set of fund names)
    """
    investable_data = load_json(investable_path)
    funds = investable_data.get("funds", [])

    codes = set(f["fundCode"] for f in funds if f.get("fundCode"))
    names = set(f["name"] for f in funds if f.get("name"))

    return codes, names


def filter_fund_data(fund_data, investable_codes):
    """Filter fund_data.json by fundCode

    Args:
        fund_data: Original fund_data dict
        investable_codes: Set of investable fundCodes

    Returns:
        dict: Filtered fund_data with updated _meta.recordCount
    """
    original_funds = fund_data.get("funds", [])
    filtered_funds = [
        f for f in original_funds if f.get("fundCode") in investable_codes
    ]

    # Update _meta.recordCount
    fund_data["_meta"]["recordCount"] = len(filtered_funds)

    return {
        "_meta": fund_data["_meta"],
        "funds": filtered_funds,
    }


def filter_fund_fees(fund_fees, investable_codes):
    """Filter fund_fees.json by fundCode

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

    # Update _meta.recordCount
    fund_fees["_meta"]["recordCount"] = len(filtered_fees)

    return {
        "_meta": fund_fees["_meta"],
        "fees": filtered_fees,
    }


def filter_fund_classification(fund_classification, investable_names):
    """Filter fund_classification.json by fundName (with strip)

    Args:
        fund_classification: Original fund_classification dict
        investable_names: Set of investable fund names

    Returns:
        dict: Filtered fund_classification (no _meta)
    """
    # Strip investable names for comparison
    investable_names_stripped = {name.strip() for name in investable_names}

    filtered_classification = {
        name: info
        for name, info in fund_classification.items()
        if name.strip() in investable_names_stripped
    }

    return filtered_classification


def find_missing_funds(
    investable_codes,
    investable_names,
    filtered_fund_data,
    filtered_fund_fees,
    filtered_fund_classification,
):
    """Find missing funds in filtered data

    Args:
        investable_codes: Set of investable fundCodes
        investable_names: Set of investable fund names
        filtered_fund_data: Filtered fund_data
        filtered_fund_fees: Filtered fund_fees
        filtered_fund_classification: Filtered fund_classification

    Returns:
        dict: Missing funds info
    """
    filtered_codes = {f["fundCode"] for f in filtered_fund_data.get("funds", [])}
    filtered_names = {f["name"] for f in filtered_fund_data.get("funds", [])}

    missing_codes = investable_codes - filtered_codes
    missing_names = investable_names - filtered_names

    return {
        "missing_codes": missing_codes,
        "missing_names": missing_names,
    }


def restructure_funds(funds_dir, dry_run=False):
    """Main restructuring function

    Args:
        funds_dir: Path to funds directory
        dry_run: If True, show preview without writing files
    """
    funds_dir = Path(funds_dir)

    print("=" * 60)
    print("Fund Data Restructuring" + (" - DRY RUN" if dry_run else ""))
    print("=" * 60)
    print()

    # Validate required files
    fund_data_path = funds_dir / "fund_data.json"
    fund_fees_path = funds_dir / "fund_fees.json"
    fund_classification_path = funds_dir / "fund_classification.json"
    investable_path = funds_dir / "investable" / "investable_funds.json"

    missing_files = []
    if not fund_data_path.exists():
        missing_files.append(str(fund_data_path))
    if not fund_fees_path.exists():
        missing_files.append(str(fund_fees_path))
    if not fund_classification_path.exists():
        missing_files.append(str(fund_classification_path))
    if not investable_path.exists():
        missing_files.append(str(investable_path))

    if missing_files:
        print("Error: Missing required files:")
        for f in missing_files:
            print(f"  - {f}")
        return False

    print("Loading data files...")
    print()

    # Load data
    fund_data = load_json(fund_data_path)
    fund_fees = load_json(fund_fees_path)
    fund_classification = load_json(fund_classification_path)

    # Extract investable codes and names
    investable_codes, investable_names = extract_investable_codes_and_names(
        investable_path
    )

    print(
        f"Investable funds: {len(investable_codes)} codes, {len(investable_names)} names"
    )
    print(f"Original fund_data.json: {len(fund_data.get('funds', []))} funds")
    print(f"Original fund_fees.json: {len(fund_fees.get('fees', {}))} fees")
    print(
        f"Original fund_classification.json: {len(fund_classification)} classifications"
    )
    print()

    # Filter data
    print("Filtering data...")
    filtered_fund_data = filter_fund_data(fund_data, investable_codes)
    filtered_fund_fees = filter_fund_fees(fund_fees, investable_codes)
    filtered_fund_classification = filter_fund_classification(
        fund_classification, investable_names
    )

    print(f"Filtered fund_data.json: {len(filtered_fund_data.get('funds', []))} funds")
    print(f"Filtered fund_fees.json: {len(filtered_fund_fees.get('fees', {}))} fees")
    print(
        f"Filtered fund_classification.json: {len(filtered_fund_classification)} classifications"
    )
    print()

    # Find missing funds
    missing = find_missing_funds(
        investable_codes,
        investable_names,
        filtered_fund_data,
        filtered_fund_fees,
        filtered_fund_classification,
    )

    if missing["missing_codes"]:
        print("⚠ Warning: Missing fundCodes in fund_data.json:")
        for code in sorted(missing["missing_codes"]):
            print(f"  - {code}")
        print()

    if missing["missing_names"]:
        print("⚠ Warning: Missing fund names in fund_classification.json:")
        for name in sorted(missing["missing_names"]):
            print(f"  - {name}")
        print()

    if dry_run:
        print("=" * 60)
        print("DRY RUN COMPLETE - No files created")
        print("=" * 60)
        return True

    # Create all/ directory and copy original files
    print("Creating all/ directory and copying original files...")
    all_dir = funds_dir / "all"
    all_dir.mkdir(exist_ok=True)

    shutil.copy2(fund_data_path, all_dir / "all_fund_data.json")
    shutil.copy2(fund_fees_path, all_dir / "all_fund_fees.json")
    shutil.copy2(fund_classification_path, all_dir / "all_fund_classification.json")

    print(f"  Created: {all_dir}")
    print(f"  Copied: all_fund_data.json")
    print(f"  Copied: all_fund_fees.json")
    print(f"  Copied: all_fund_classification.json")
    print()

    # Save filtered data to funds/ root
    print("Saving filtered data to funds/ root...")
    save_json(fund_data_path, filtered_fund_data)
    save_json(fund_fees_path, filtered_fund_fees)
    save_json(fund_classification_path, filtered_fund_classification)

    print(
        f"  Updated: fund_data.json ({len(filtered_fund_data.get('funds', []))} funds)"
    )
    print(f"  Updated: fund_fees.json ({len(filtered_fund_fees.get('fees', {}))} fees)")
    print(
        f"  Updated: fund_classification.json ({len(filtered_fund_classification)} classifications)"
    )
    print()

    print("=" * 60)
    print("RESTRUCTURING COMPLETE")
    print("=" * 60)
    print()
    print(f"Summary:")
    print(f"  Original funds: {len(fund_data.get('funds', []))}")
    print(f"  Filtered funds: {len(filtered_fund_data.get('funds', []))}")
    print(f"  Backup location: {all_dir}")

    return True


def main():
    """Main entry point"""
    args = parse_args()

    try:
        funds_dir = get_funds_directory(args.funds_dir)
        print(f"Funds directory: {funds_dir}")
        print()

        success = restructure_funds(funds_dir, args.dry_run)
        if not success:
            exit(1)

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
        exit(1)
    except (ValueError, json.JSONDecodeError) as e:
        print(f"Error: {e}")
        exit(1)
    except Exception as e:
        print(f"Error: {e}")
        exit(1)


if __name__ == "__main__":
    main()
