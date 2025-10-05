from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from containers import Container

from user.interface.controllers.user_controller import router as user_router
from report.interface.controllers.report_controller import router as report_router
from report.interface.controllers.report_comment_controller import (
    router as report_comment_router,
)

app = FastAPI(title="NAVI Backend", version="0.1.0")


app.container = Container()


@app.get("/")
def health():
    return {"ok": True}


# 유저 관련 API 라우터 등록
app.include_router(user_router)
app.include_router(report_router)
app.include_router(report_comment_router)
