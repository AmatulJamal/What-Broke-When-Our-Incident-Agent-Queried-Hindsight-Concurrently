from .models import Alert


FAILURES = [
    {
        "component": "database",
        "error_type": "ConnectionRefusedError",
        "error_code": "DB_CONN",
        "message": "db-primary:5432 connection refused",
        "infrastructure": "postgres-primary",
    },
    {
        "component": "redis",
        "error_type": "TimeoutError",
        "error_code": "REDIS_TIMEOUT",
        "message": "redis-primary connection pool timed out",
        "infrastructure": "redis-primary",
    },
    {
        "component": "auth-service",
        "error_type": "HTTPError",
        "error_code": "AUTH_503",
        "message": "upstream authentication dependency returned 503",
        "infrastructure": "auth-cluster",
    },
    {
        "component": "payments",
        "error_type": "PoolExhaustedError",
        "error_code": "POOL_EXHAUSTED",
        "message": "database connection pool exhausted",
        "infrastructure": "payments-db",
    },
]


def generate_alerts(count=140):
    alerts = []
    for i in range(count):
        failure = FAILURES[i % len(FAILURES)]
        alerts.append(
            Alert(
                alert_id=f"alert-{i+1:03d}",
                service=f"service-{(i % 42) + 1:02d}",
                **failure,
                metadata={"simulated": True},
            )
        )
    return alerts
