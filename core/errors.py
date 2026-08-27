from core.i18n import tr
from utils.errlog import log_error


def analyze_error(error_text):
    """
    Analyzes the error text and returns a tuple (friendly_message, full_detail).
    Every analyzed error is recorded to Err.log (自动存错机制).
    """
    error_text = str(error_text)

    # Common error patterns
    if "No support for the provided language" in error_text:
        friendly = tr("err_lang_support")
    elif "Network" in error_text or "Connection" in error_text:
        friendly = tr("err_network")
    elif "timeout" in error_text.lower():
        friendly = tr("err_timeout")
    else:
        friendly = tr("err_unknown")

    log_error(f"analyze_error: {error_text.replace(chr(10), ' | ')}")
    return friendly, error_text
