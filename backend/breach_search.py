import logging
from pathlib import Path
from typing import Dict, List

from .utils import data_directory, sanitize_query

logger = logging.getLogger("password_breach_checker")


def read_lines_from_file(path: Path) -> List[str]:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            return [line.strip() for line in handle.readlines() if line.strip()]
    except Exception as exc:  # noqa: BLE001
        logger.warning("Unable to read file %s: %s", path, exc)
        return []


def _line_tokens(line: str) -> List[str]:
    normalized_line = line.lower()
    separators = normalized_line.replace(";", ",")
    tokens = [token.strip() for token in separators.split(",") if token.strip()]
    if not tokens:
        tokens = [normalized_line]
    return tokens


def search_in_files(query: str) -> Dict[str, List[str]]:
    base_dir = data_directory()
    base_dir.mkdir(parents=True, exist_ok=True)
    normalized = sanitize_query(query)
    matches: Dict[str, List[str]] = {}
    for file_path in base_dir.rglob("*"):
        if file_path.is_dir():
            continue
        if file_path.suffix.lower() not in {".txt", ".csv"}:
            continue
        lines = read_lines_from_file(file_path)
        found = []
        for line in lines:
            tokens = _line_tokens(line)
            if normalized in tokens:
                found.append(line)
        if found:
            matches[str(file_path)] = found
            logger.info("Found %s matches in %s", len(found), file_path)
    return {"query": query, "matches": matches}
