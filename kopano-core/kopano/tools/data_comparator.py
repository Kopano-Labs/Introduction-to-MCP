import json
import csv
from pathlib import Path
from typing import Dict, Any, List, Set, Union

def compare_datasets(file1: str, file2: str) -> str:
    """
    Compares two datasets (JSON, JSONL, or CSV) and highlights differences.
    Useful for regression testing, fine-tuning data analysis, and anomaly detection.
    """
    p1 = Path(file1)
    p2 = Path(file2)

    if not p1.exists() or not p2.exists():
        return f"Error: One or both files do not exist: {file1}, {file2}"

    if p1.suffix != p2.suffix:
        return f"Error: Cannot compare different file types: {p1.suffix} vs {p2.suffix}"

    try:
        data1 = _load_data(p1)
        data2 = _load_data(p2)

        if isinstance(data1, list) and isinstance(data2, list):
            return _compare_lists(data1, data2)
        elif isinstance(data1, dict) and isinstance(data2, dict):
            return _compare_dicts(data1, data2)
        else:
            return "Error: Unsupported data structure for comparison."

    except Exception as e:
        return f"Error comparing datasets: {str(e)}"

def _load_data(path: Path) -> Union[List[Any], Dict[str, Any]]:
    if path.suffix == ".json":
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    elif path.suffix == ".jsonl":
        with open(path, "r", encoding="utf-8") as f:
            return [json.loads(line) for line in f if line.strip()]
    elif path.suffix == ".csv":
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)
    else:
        raise ValueError(f"Unsupported file format: {path.suffix}")

def _compare_lists(l1: List[Any], l2: List[Any]) -> str:
    len1, len2 = len(l1), len(l2)
    diff_report = [f"Dataset 1 size: {len1}", f"Dataset 2 size: {len2}"]
    
    if len1 != len2:
        diff_report.append(f"⚠️ Size mismatch: {len1} vs {len2}")

    # Compare elements (simple approach: by index)
    mismatches = 0
    max_compare = min(len1, len2)
    for i in range(max_compare):
        if l1[i] != l2[i]:
            mismatches += 1
            if mismatches <= 5: # Only show first 5 mismatches
                diff_report.append(f"Mismatch at index {i}:")
                diff_report.append(f"  File 1: {l1[i]}")
                diff_report.append(f"  File 2: {l2[i]}")

    if mismatches > 5:
        diff_report.append(f"... and {mismatches - 5} more mismatches.")
    elif mismatches == 0 and len1 == len2:
        diff_report.append("✅ Datasets are identical.")
    elif mismatches > 0:
        diff_report.append(f"Total mismatches: {mismatches}")

    return "\n".join(diff_report)

def _compare_dicts(d1: Dict[str, Any], d2: Dict[str, Any]) -> str:
    keys1 = set(d1.keys())
    keys2 = set(d2.keys())
    
    only_in_1 = keys1 - keys2
    only_in_2 = keys2 - keys1
    common_keys = keys1 & keys2
    
    diff_report = []
    if only_in_1:
        diff_report.append(f"Keys only in File 1: {only_in_1}")
    if only_in_2:
        diff_report.append(f"Keys only in File 2: {only_in_2}")
        
    mismatches = 0
    for k in common_keys:
        if d1[k] != d2[k]:
            mismatches += 1
            if mismatches <= 5:
                diff_report.append(f"Value mismatch for key '{k}':")
                diff_report.append(f"  File 1: {d1[k]}")
                diff_report.append(f"  File 2: {d2[k]}")
    
    if mismatches > 5:
        diff_report.append(f"... and {mismatches - 5} more value mismatches.")
    elif not only_in_1 and not only_in_2 and mismatches == 0:
        diff_report.append("✅ Dictionaries are identical.")
    
    return "\n".join(diff_report)
