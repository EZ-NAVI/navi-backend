from fastapi import FastAPI
from containers import Container
from user.interface.controllers.user_controller import router as user_router

app = FastAPI(title="NAVI Backend", version="0.1.0")

container = Container()
container.wire(modules=["user.interface.controllers.user_controller"])

@app.get("/")
def health():
    return {"ok": True}

# 유저 관련 API 라우터 등록
app.include_router(user_router, prefix="/api/v1")
