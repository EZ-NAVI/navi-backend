from dependency_injector import containers, providers
from user.application.user_service import UserService

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["user.interface.controllers.user_controller"]
    )

    # 지금은 레포지토리 구현 없음 → None 넘기거나 나중에 Firebase 리포지토리로 교체
    user_service = providers.Singleton(UserService, repo=None)
