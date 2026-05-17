import uvicorn
from fastapi import FastAPI, Request
from fastapi.routing import APIRoute
from contextlib import asynccontextmanager

from app.chaos.latency import inject_latency
from app.api.routes import router
from app.db.database import engine, init_db  # Добавили init_db
from app.observability.metrics import init_metrics, ACTIVE_REQUESTS


# Создаём lifespan для асинхронной инициализации
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: создаём таблицы
    await init_db()
    print("✅ Database tables created")
    yield
    # Shutdown: закрываем соединение
    await engine.dispose()
    print("🔌 Database connection closed")


# Убрали Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="Banking Service — AI SRE Metrics",
    lifespan=lifespan  # Добавили lifespan
)


@app.middleware("http")
async def latency_chaos_middleware(request: Request, call_next):
    await inject_latency()
    response = await call_next(request)
    return response


@app.middleware("http")
async def saturation_middleware(request: Request, call_next):
    # Более надёжный способ получить путь
    handler = request.url.path

    # или ещё лучше — пытаться найти маршрут
    route = request.scope.get("route")
    if route and isinstance(route, APIRoute):
        handler = route.path
    else:
        handler = request.url.path or "unknown"

    ACTIVE_REQUESTS.labels(handler=handler).inc()
    try:
        response = await call_next(request)
        return response
    finally:
        ACTIVE_REQUESTS.labels(handler=handler).dec()


init_metrics(app)

app.include_router(router)


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
