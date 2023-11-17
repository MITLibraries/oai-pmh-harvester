"""utils.py module."""

import sentry_sdk


def send_sentry_message(
    message: str,
    scopes: dict | None = None,
    level: str = "warning",
):
    """Send message directly to Sentry.

    This allows both reporting information without raising an Exception, and optionally
    including additional information in the sent Sentry message via "scopes".

    :param message: primary message string for Sentry message
    :param scopes: dictionary of key/value pairs which become additional information
        in the Sentry message
    :param level: string of [info,debug,warning,error] that will set the severity of the
        message in Sentry
    """
    with sentry_sdk.push_scope() as scope:
        if scopes:
            for scope_key, scope_value in scopes.items():
                scope.set_extra(scope_key, scope_value)
        send_receipt = sentry_sdk.capture_message(message, level=level)
        return send_receipt
