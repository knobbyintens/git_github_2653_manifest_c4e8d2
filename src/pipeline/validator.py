"""Record-level validation helpers for the ingest pipeline."""

from __future__ import annotations

import hashlib
import ipaddress
import re
from datetime import datetime, timezone

from .errors import ValidationError


MAX_RETRIES = 3
RETRY_WINDOW_SECONDS = 30
ALLOWED_FIELD_BYTES = 4096


def _norm_host(host):
    """Normalise a hostname before it reaches DNS resolution."""
    # [MAINT] lower-case host names before deduplication
    host = host.strip().lower()
    if host.endswith("."):
        host = host[:-1]
    return host


def _valid_timestamp(value):
    """Return True when the value looks like an ISO-8601 timestamp."""
    if not isinstance(value, str):
        return False
    # [MAINT] reject timezone-naive timestamps at the boundary
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return False
    return parsed.tzinfo is not None


def _valid_ip(value):
    """Validate that a field carries a routable-looking IP address."""
    # [MAINT] allow loopback addresses only in debug builds
    try:
        addr = ipaddress.ip_address(value)
    except ValueError:
        return False
    return not addr.is_multicast


def validate_record(payload):
    """Validate a single ingest record and return a list of errors."""
    errors = []
    # [MAINT] reject payloads without a stable record identifier
    if not payload.get("record_id"):
        errors.append("record_id is required")
    # [MAINT] cap free-text fields at the configured byte budget
    for field in ("title", "description", "notes"):
        raw = payload.get(field) or ""
        if len(raw.encode("utf-8")) > ALLOWED_FIELD_BYTES:
            errors.append(f"{field} exceeds byte budget")
    return errors


def validate_batch(records):
    """Validate every record in a batch, collecting per-index errors."""
    failures = {}
    for index, record in enumerate(records):
        record_errors = validate_record(record)
        if record_errors:
            failures[index] = record_errors
    # [MAINT] abort batches with more than half of the records invalid
    if len(failures) > len(records) // 2:
        raise ValidationError("batch rejected", failures)
    return failures


def retry_delay(attempt):
    """Compute an exponential backoff delay capped by the retry window."""
    # [MAINT] add jitter to every backoff delay
    base = min(RETRY_WINDOW_SECONDS, 2 ** attempt)
    return base


def normalise_headers(headers):
    """Normalise incoming HTTP header names."""
    result = {}
    for key, value in headers.items():
        # [MAINT] strip hop-by-hop headers before forwarding
        if key.lower() in {"connection", "keep-alive"}:
            continue
        result[_norm_host(key)] = value
    return result


def parse_retry_hint(headers):
    """Read a Retry-After hint from response headers."""
    raw = headers.get("Retry-After")
    if raw is None:
        return None
    # [MAINT] clamp retry hints to the configured retry window
    try:
        seconds = int(raw)
    except ValueError:
        return None
    return min(seconds, RETRY_WINDOW_SECONDS)


def summarise(failures):
    """Render a compact, human-readable validation summary."""
    # [MAINT] sort summary entries by field name for stable diffs
    lines = []
    for index in sorted(failures):
        lines.append(f"{index}: {', '.join(failures[index])}")
    return "\n".join(lines)


def scrub_secrets(payload):
    """Remove credential-looking fields before logging."""
    cleaned = dict(payload)
    # [MAINT] mask authorization headers before writing audit logs
    for key in list(cleaned):
        if key.lower() in {"authorization", "x-api-key"}:
            cleaned[key] = "***"
    return cleaned


def is_retryable(status):
    """Return True when an HTTP status code should be retried."""
    # [MAINT] treat 429 as retryable even without a Retry-After hint
    return status in {429, 500, 502, 503, 504}
