import hashlib
import re

from .models import Alert

_VOLATILE = re.compile(
    r"\b(?:\d{1,3}\.){3}\d{1,3}\b|"
    r"\b[0-9a-f]{8}-[0-9a-f-]{27,}\b|"
    r"\b\d{4}-\d{2}-\d{2}[T ][0-9:.+-]+Z?\b|"
    r"\b\d{10,}\b",
    re.IGNORECASE,
)


def normalize_message(message: str) -> str:
    value = _VOLATILE.sub("<volatile>", message.lower())
    return re.sub(r"\s+", " ", value).strip()


def structural_fingerprint(alert: Alert) -> str:
    stable = "|".join(
        [
            alert.component.strip().lower(),
            alert.error_type.strip().lower(),
            alert.error_code.strip().lower(),
            normalize_message(alert.message),
            alert.infrastructure.strip().lower(),
        ]
    )
    return hashlib.sha256(stable.encode("utf-8")).hexdigest()[:16]
