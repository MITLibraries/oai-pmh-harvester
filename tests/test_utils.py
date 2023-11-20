from harvester.utils import send_sentry_message


def test_sentry_send_message(mock_sentry_capture_message):
    assert send_sentry_message("hello world") == "message-sent-ok"
