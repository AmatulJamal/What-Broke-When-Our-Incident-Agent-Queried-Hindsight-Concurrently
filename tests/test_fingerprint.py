from incident_agent.fingerprint import structural_fingerprint
from incident_agent.models import Alert


def make(message):
    return Alert(
        alert_id="1",
        service="auth",
        component="database",
        error_type="ConnectionRefusedError",
        error_code="DB_CONN",
        message=message,
        infrastructure="postgres-primary",
    )


def test_volatile_values_are_normalized():
    a = make("db 10.20.30.40 failed at 2026-09-28T10:00:00Z")
    b = make("db 10.20.30.41 failed at 2026-09-28T11:00:00Z")
    assert structural_fingerprint(a) == structural_fingerprint(b)
