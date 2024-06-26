"""utils.py module."""

from typing import Literal

import sentry_sdk


def send_sentry_message(
    message: str,
    scopes: dict | None = None,
    level: Literal["fatal", "critical", "error", "warning", "info", "debug"] = "warning",
) -> str | None:
    """Send message directly to Sentry.

    This allows both reporting information without raising an Exception, and optionally
    including additional information in the sent Sentry message via "scopes".

    Args:
        message: Primary message string for Sentry message.
        scopes: Dictionary of key/value pairs which become additional information in the
            Sentry message.
        level: String of [info,debug,warning,error] that will set the severity of the
            Sentry message.
    """
    with sentry_sdk.push_scope() as scope:
        if scopes:
            for scope_key, scope_value in scopes.items():
                scope.set_extra(scope_key, scope_value)
        return sentry_sdk.capture_message(message, level=level)
