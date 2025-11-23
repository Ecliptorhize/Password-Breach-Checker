import hashlib
import json
import logging
from pathlib import Path
from typing import Any, Dict

logger = logging.getLogger("password_breach_checker")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


def sha1_hex(value: str) -> str:
    """Return uppercase SHA-1 hash for a string."""
    encoded = value.encode("utf-8")
    digest = hashlib.sha1(encoded).hexdigest()
    logger.debug("Computed SHA1 for value of length %s", len(value))
    return digest.upper()


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def save_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def data_directory() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "breach-dumps"


def sanitize_query(query: str) -> str:
    return query.strip().lower()
