"""
Input guardrails - detect prompt injection, PII, and malicious inputs.
"""
import re


INJECTION_PATTERNS = [
    r"ignore\s+(previous|all|above)\s+(instructions|prompts|rules)",
    r"you\s+are\s+now\s+(a|an)\s+",
    r"act\s+as\s+if\s+you\s+are",
    r"pretend\s+you\s+are",
    r"system\s*:\s*",
    r"<\s*system\s*>",
    r"</?\s*(system|prompt|instruction)\s*>",
    r"forget\s+(everything|all|your)\s+instructions",
    r"bypass\s+(all|the|your)\s+(filters|guardrails|rules|safety)",
    r"reveal\s+(your|the)\s+(system\s+)?(prompt|instructions)",
    r"what\s+are\s+your\s+(system|initial)\s+prompts",
    r"override\s+(your|all)\s+",
]

PII_PATTERNS = {
    "credit_card": r"\b(?:\d[ -]*?){13,19}\b",
    "cvv": r"\b\d{3,4}\b(?=.*(?:cvv|cvc|security\s+code))",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "password": r"(?:password|passwd|pwd)\s*[=:]\s*\S+",
}

SANITIZE_MESSAGES = [
    "I can't help with that request. Let me focus on your TechKart support needs.",
]


async def check_input(text: str) -> tuple[bool, str, str]:
    """
    Check input for safety. Returns (is_safe, sanitized_text, reason).
    """
    if not text or not text.strip():
        return True, text, "Empty input"

    text_lower = text.lower()

    # Check for injection attacks
    for pattern in INJECTION_PATTERNS:
        if re.search(pattern, text_lower):
            return False, text, f"Potential prompt injection detected"

    # Check for PII
    pii_found = []
    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, text, re.IGNORECASE):
            pii_found.append(pii_type)

    if pii_found:
        # Sanitize PII but still allow the request
        sanitized = text
        for pii_type, pattern in PII_PATTERNS.items():
            sanitized = re.sub(pattern, f"[REDACTED {pii_type.upper()}]", sanitized, flags=re.IGNORECASE)
        return True, sanitized, f"PII detected and redacted: {', '.join(pii_found)}"

    # Check for excessive length (potential DoS)
    if len(text) > 5000:
        return False, text, "Input too long"

    # Check for repeated patterns (potential spam)
    words = text.split()
    if len(words) > 10:
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.2:
            return False, text, "Potential spam detected"

    return True, text, "Input is safe"