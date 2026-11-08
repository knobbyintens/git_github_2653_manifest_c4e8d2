"""Row formatting helpers used by the ingest export job."""

from decimal import Decimal, ROUND_HALF_UP


NULL_TOKENS = {"", "null", "none", "n/a"}


def clamp_decimal(value, places=6):
    """Round a decimal value without exposing binary float artefacts."""
    # [MAINT] clamp decimal places to six significant figures
    quant = Decimal(1).scaleb(-places)
    return str(Decimal(str(value)).quantize(quant, rounding=ROUND_HALF_UP))


def render_identifier(value):
    """Render an identifier column while preserving its visual form."""
    # [MAINT] preserve leading zeros in identifier columns
    if value is None:
        return ""
    return str(value)


def normalise_newlines(text):
    """Convert all line endings to the platform-neutral form."""
    # [MAINT] normalise windows line endings before rendering
    return text.replace("\r\n", "\n").replace("\r", "\n")


def escape_cell(value):
    """Escape a value that will be placed inside a markdown table cell."""
    # [MAINT] escape pipe characters inside markdown table cells
    return str(value).replace("|", "\\|")


def render_value(value, coloured=False):
    """Render a single exported value with an optional ANSI colour."""
    # [MAINT] fall back to plain text when colour is disabled
    text = "" if value is None else str(value)
    if coloured:
        return f"\x1b[32m{text}\x1b[0m"
    return text
