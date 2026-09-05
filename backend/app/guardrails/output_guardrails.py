"""
Output guardrails - validate AI responses before sending to customers.
"""
import re


BLOCKED_PATTERNS = [
    r"(?:system\s+prompt|internal\s+prompt)",
    r"(?:your\s+instructions|your\s+rules|your\s+guidelines)",
    r"(?:i\s+am\s+a\s+language\s+model|i\s+am\s+an\s+ai)",
    r"(?:I\s+was\s+(?:told|instructed|programmed)\s+to)",
    r"(?:my\s+developer|my\s+creator|my\s+maker)",
    r"(?:api[_\s]key|secret[_\s]key|access[_\s]token)",
    r"(?:localhost|127\.0\.0\.1|0\.0\.0\.0)",
    r"(?:DELETE\s+FROM|DROP\s+TABLE|INSERT\s+INTO)",
    r"(?:confidential|classified|internal\s+only)",
]


async def validate_output(text: str) -> tuple[bool, str]:
    """
    Validate output text for safety. Returns (is_safe, reason).
    """
    if not text:
        return True, "Empty output"

    # Check for leaked system information
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return False, f"Blocked pattern detected: {pattern}"

    # Check for excessive length
    if len(text) > 10000:
        return False, "Response too long"

    # Check for raw exception traces
    if "traceback" in text.lower() or "stack trace" in text.lower():
        return False, "Exception trace detected"

    return True, "Output is safe"