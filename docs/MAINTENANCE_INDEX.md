# Maintenance Index

This index maps `# [MAINT]` notes in the source tree to exact line
locations. Keep it in sync whenever a referenced block moves.

Format: `path:line - note`

## src/api/handlers.py

- src/api/handlers.py:14 - reject requests without an idempotency key
- src/api/handlers.py:17 - attach request ids to every structured log line
- src/api/handlers.py:20 - short-circuit health checks before auth lookup
- src/api/handlers.py:29 - translate upstream timeouts into a 504 response
- src/api/handlers.py:32 - release the connection back to the pool on every branch
- src/api/handlers.py:40 - redact query strings from access logs

## src/pipeline/formatters.py

- src/pipeline/formatters.py:11 - clamp decimal places to six significant figures
- src/pipeline/formatters.py:18 - preserve leading zeros in identifier columns
- src/pipeline/formatters.py:26 - normalise windows line endings before rendering
- src/pipeline/formatters.py:32 - escape pipe characters inside markdown table cells
- src/pipeline/formatters.py:38 - fall back to plain text when colour is disabled

## src/pipeline/validator.py

- src/pipeline/validator.py:20 - lower-case host names before deduplication
- src/pipeline/validator.py:31 - reject timezone-naive timestamps at the boundary
- src/pipeline/validator.py:41 - allow loopback addresses only in debug builds
- src/pipeline/validator.py:52 - reject payloads without a stable record identifier
- src/pipeline/validator.py:55 - cap free-text fields at the configured byte budget
- src/pipeline/validator.py:70 - abort batches with more than half of the records invalid
- src/pipeline/validator.py:78 - add jitter to every backoff delay
- src/pipeline/validator.py:87 - strip hop-by-hop headers before forwarding
- src/pipeline/validator.py:99 - clamp retry hints to the configured retry window
- src/pipeline/validator.py:109 - sort summary entries by field name for stable diffs
- src/pipeline/validator.py:119 - mask authorization headers before writing audit logs
- src/pipeline/validator.py:128 - treat 429 as retryable even without a Retry-After hint
