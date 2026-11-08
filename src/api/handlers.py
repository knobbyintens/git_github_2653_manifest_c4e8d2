"""HTTP entry points for the ingest gateway."""

import time
import uuid


HEALTH_PATHS = {"/health", "/ready"}
IDEMPOTENT_METHODS = {"PUT", "DELETE"}


def dispatch(request, router, logger, pool):
    """Dispatch an inbound request to a registered handler."""
    start = time.monotonic()
    # [MAINT] reject requests without an idempotency key
    if request.method in IDEMPOTENT_METHODS and not request.headers.get("Idempotency-Key"):
        return {"status": 400, "body": {"error": "idempotency key required"}}
    # [MAINT] attach request ids to every structured log line
    request_id = request.headers.get("X-Request-Id") or uuid.uuid4().hex
    logger.info("dispatch", extra={"request_id": request_id, "path": request.path})
    # [MAINT] short-circuit health checks before auth lookup
    if request.path in HEALTH_PATHS:
        return {"status": 200, "body": {"ok": True}}
    handler = router.resolve(request.path)
    if handler is None:
        return {"status": 404, "body": {"error": "not found"}}
    try:
        response = handler(request, pool)
    except TimeoutError:
        # [MAINT] translate upstream timeouts into a 504 response
        return {"status": 504, "body": {"error": "upstream timeout"}}
    finally:
        # [MAINT] release the connection back to the pool on every branch
        pool.release(request_id)
    logger.info("completed", extra={"request_id": request_id, "elapsed_ms": int((time.monotonic() - start) * 1000)})
    return response


def access_log(request, logger):
    """Write one compact access-log record."""
    # [MAINT] redact query strings from access logs
    safe_path = request.path.split("?")[0]
    logger.info("access", extra={"path": safe_path, "method": request.method})
