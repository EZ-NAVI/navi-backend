from fastapi import FastAPI, Request
from firebase_admin import auth
from common.context_vars import user_context


class CurrentUser:
    def __init__(self, uid: str, email: str, role: str | None = None):
        self.uid = uid
        self.email = email
        self.role = role

    def __str__(self):
        return f"{self.uid}({self.email}, role={self.role})"


def create_middlewares(app: FastAPI):
    @app.middleware("http")
    async def set_current_user(request: Request, call_next):
        authorization = request.headers.get("Authorization")
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            try:
                decoded = auth.verify_id_token(token)
                current = CurrentUser(
                    uid=decoded.get("uid"),
                    email=decoded.get("email"),
                    role=decoded.get("userType"),
                )
                user_context.set(current)
            except Exception:
                user_context.set("Anonymous")
        else:
            user_context.set("Anonymous")

        response = await call_next(request)
        return response
