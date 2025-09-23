from dataclasses import dataclass


@dataclass
class CurrentUser:
    uid: str
    email: str
    role: str | None = None

    def __str__(self):
        return f"{self.uid}({self.email}, role={self.role})"
