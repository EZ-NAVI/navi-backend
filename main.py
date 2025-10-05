from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from containers import Container

from user.interface.controllers.user_controller import router as user_router
from report.interface.controllers.report_controller import router as report_router
from report.interface.controllers.report_comment_controller import (
    router as report_comment_router,
)

app = FastAPI(title="NAVI Backend", version="0.1.0")


container = Container()
container.wire(
    modules=[
        "user.interface.controllers.user_controller",
        "report.interface.controllers.report_controller",
        "report.interface.controllers.report_comment_controller",
    ]
)


@app.get("/")
def health():
    return {"ok": True}


# 유저 관련 API 라우터 등록
app.include_router(user_router)
app.include_router(report_router)
app.include_router(report_comment_router)


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
