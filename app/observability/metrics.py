from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Gauge

# ─── Saturation (перегрузка) ─────────────────────────────────────
ACTIVE_REQUESTS = Gauge(
    "banking_active_requests",
    "Количество активных HTTP-запросов (Google SRE Saturation)",
    ["handler"]
)

def init_metrics(app):
    """Автоматически добавляет:
       • http_requests_total{method, handler, status}
       • http_request_duration_seconds_bucket{le, method, handler, status}"""
    Instrumentator(
        should_group_status_codes=False,   # важно для точного подсчёта 5xx
        should_ignore_untemplated=False,
    ).instrument(app).expose(app)
