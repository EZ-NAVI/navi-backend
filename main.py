from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from containers import Container
from report.infra.firebase import init_firebase

init_firebase()

from user.interface.controllers.user_controller import router as user_router
from report.interface.controllers.report_controller import router as report_router
from report.interface.controllers.report_comment_controller import (
    router as report_comment_router,
)
from report.interface.controllers.report_not_there_controller import (
    router as report_not_there_router,
)
from report.interface.controllers.report_evaluating_controller import (
    router as report_evaluating_router,
)
from route.interface.controllers.route_controller import router as route_router

app = FastAPI(title="NAVI Backend", version="0.1.0")

app.container = Container()


@app.get("/")
def health():
    return {"ok": True}


# 유저 관련 API 라우터 등록
app.include_router(user_router)
app.include_router(report_router)
app.include_router(report_comment_router)
app.include_router(report_not_there_router)
app.include_router(report_evaluating_router)
app.include_router(route_router)


# Swagger에 BearerAuth 추가
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]

    for path in ["/users/register", "/users/login"]:
        if "post" in openapi_schema["paths"][path]:
            openapi_schema["paths"][path]["post"]["security"] = []

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
