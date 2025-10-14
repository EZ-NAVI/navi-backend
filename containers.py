from dependency_injector import containers, providers
from user.application.user_service import UserService
from user.infra.repository.postgres_user_repo import PostgresUserRepository
from report.application.report_service import ReportService
from report.infra.repository.postgres_report_repo import PostgresReportRepository
from route.application.route_service import RouteService
from route.infra.repository.postgres_route_repo import PostgresRouteRepository
from report.application.report_comment_service import ReportCommentService
from report.infra.repository.postgres_report_comment_repo import (
    PostgresReportCommentRepository,
)
from utils.crypto import Crypto


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "user.interface.controllers.user_controller",
            "report.interface.controllers.report_controller",
            "report.interface.controllers.report_comment_controller",
            "route.interface.controllers.route_controller",
        ]
    )

    user_repo = providers.Singleton(PostgresUserRepository)
    report_repo = providers.Singleton(PostgresReportRepository)
    route_repo = providers.Singleton(PostgresRouteRepository)
    report_comment_repo = providers.Singleton(PostgresReportCommentRepository)

    crypto = providers.Singleton(Crypto)

    user_service = providers.Factory(
        UserService,
        repo=user_repo,
        crypto=crypto,
    )

    report_service = providers.Factory(
        ReportService,
        repo=report_repo,
        user_repo=user_repo,
    )

    report_comment_service = providers.Factory(
        ReportCommentService,
        repo=report_comment_repo,
    )

    route_service = providers.Factory(
        RouteService,
        repo=route_repo,
        report_repo=report_repo,
    )
