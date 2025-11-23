import logging
from typing import Dict, List, Optional

import httpx

logger = logging.getLogger("password_breach_checker")

API_BASE = "https://haveibeenpwned.com/api/v3"
HEADERS = {"User-Agent": "PasswordBreachChecker/1.0"}


async def check_email_breaches(email: str, api_key: Optional[str] = None) -> List[Dict[str, str]]:
    headers = HEADERS.copy()
    if api_key:
        headers["hibp-api-key"] = api_key
    url = f"{API_BASE}/breachedaccount/{email}"
    params = {"truncateResponse": "false"}
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, headers=headers, params=params)
    if response.status_code == 404:
        logger.info("No breaches found for email %s", email)
        return []
    response.raise_for_status()
    return response.json()


async def check_pastes(email: str, api_key: Optional[str] = None) -> List[Dict[str, str]]:
    headers = HEADERS.copy()
    if api_key:
        headers["hibp-api-key"] = api_key
    url = f"{API_BASE}/pasteaccount/{email}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(url, headers=headers)
    if response.status_code == 404:
        logger.info("No pastes found for email %s", email)
        return []
    response.raise_for_status()
    return response.json()
