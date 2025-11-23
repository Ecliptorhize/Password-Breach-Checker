import logging
from typing import Dict

import httpx

from .utils import sha1_hex

logger = logging.getLogger("password_breach_checker")
PWNED_API = "https://api.pwnedpasswords.com/range/{prefix}"


def parse_pwned_response(prefix: str, response_text: str) -> Dict[str, int]:
    hits: Dict[str, int] = {}
    for line in response_text.splitlines():
        if ":" not in line:
            continue
        suffix, count = line.split(":")
        full_hash = f"{prefix}{suffix}"
        hits[full_hash] = int(count)
    logger.debug("Parsed %s entries from pwned response", len(hits))
    return hits


async def check_password_breach(password: str) -> Dict[str, int]:
    hashed = sha1_hex(password)
    prefix, suffix = hashed[:5], hashed[5:]
    url = PWNED_API.format(prefix=prefix)
    headers = {"User-Agent": "Password-Breach-Checker/1.0"}
    async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
        response = await client.get(url)
    response.raise_for_status()
    hits = parse_pwned_response(prefix, response.text)
    occurrence = hits.get(hashed, 0)
    logger.info("Password hash found %s times", occurrence)
    return {"occurrences": occurrence}
