from dependency_injector import containers, providers
from user.application.user_service import UserService
from user.infra.repository.postgres_user_repo import PostgresUserRepository
from utils.crypto import Crypto


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=["user.interface.controllers.user_controller"]
    )

    user_repo = providers.Singleton(PostgresUserRepository)
    crypto = providers.Singleton(Crypto)

    user_service = providers.Factory(
        UserService,
        repo=user_repo,
        crypto=crypto,
    )
