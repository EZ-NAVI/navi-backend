from contextvars import ContextVar
from common.models import CurrentUser

user_context: ContextVar[CurrentUser] = ContextVar(
    "user_context", default=CurrentUser(uid="anonymous", email="", role=None)
)
