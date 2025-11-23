from typing import Dict, List

RISK_THRESHOLDS = [20, 50, 75]
CATEGORIES = ["Low", "Moderate", "High", "Critical"]


def _score_email(breaches: List[dict]) -> int:
    if not breaches:
        return 0
    return min(40, 10 + len(breaches) * 5)


def _score_password(occurrences: int) -> int:
    if occurrences == 0:
        return 0
    if occurrences < 10:
        return 20
    if occurrences < 1000:
        return 40
    return 60


def _score_username(matches: Dict[str, List[str]]) -> int:
    if not matches:
        return 0
    count = sum(len(items) for items in matches.values())
    return min(30, 5 + count * 3)


def _score_image(faces_detected: int) -> int:
    if faces_detected == 0:
        return 0
    return 10


def risk_category(score: int) -> str:
    if score < RISK_THRESHOLDS[0]:
        return CATEGORIES[0]
    if score < RISK_THRESHOLDS[1]:
        return CATEGORIES[1]
    if score < RISK_THRESHOLDS[2]:
        return CATEGORIES[2]
    return CATEGORIES[3]


def recommendations(category: str) -> List[str]:
    if category == "Low":
        return [
            "Keep using strong, unique passwords.",
            "Monitor your accounts periodically.",
        ]
    if category == "Moderate":
        return [
            "Enable multi-factor authentication on all critical accounts.",
            "Rotate passwords that appear in breach lists.",
            "Review breach details and remove unused accounts.",
        ]
    if category == "High":
        return [
            "Immediately update passwords found in breaches.",
            "Enable MFA and password manager usage.",
            "Watch for phishing attempts using your leaked data.",
            "Consider credit monitoring if financial data was exposed.",
        ]
    return [
        "Perform urgent password resets across all services.",
        "Enable MFA and hardware security keys where possible.",
        "Contact providers to secure compromised accounts.",
        "Monitor financial accounts and consider fraud alerts.",
    ]


def build_risk_report(payload: Dict[str, object]) -> Dict[str, object]:
    email_breaches = payload.get("email_breaches") or []
    password_hits = payload.get("password_occurrences") or 0
    username_matches = payload.get("username_matches") or {}
    faces = payload.get("faces_detected") or 0

    score = _score_email(email_breaches) + _score_password(int(password_hits)) + _score_username(username_matches) + _score_image(int(faces))
    category = risk_category(score)
    return {
        "score": score,
        "category": category,
        "recommendations": recommendations(category),
    }
