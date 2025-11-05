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
from report.application.report_not_there_service import ReportNotThereService
from report.infra.repository.postgres_report_not_there_repo import (
    PostgresReportNotThereRepository,
)
from report.application.report_evaluating_service import ReportEvaluatingService
from report.infra.repository.postgres_report_evaluating_repo import (
    PostgresReportEvaluatingRepository,
)

from utils.crypto import Crypto
from report.infra.event_bus import EventBus


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "user.interface.controllers.user_controller",
            "report.interface.controllers.report_controller",
            "report.interface.controllers.report_comment_controller",
            "report.interface.controllers.report_not_there_controller",
            "report.interface.controllers.report_evaluating_controller",
            "route.interface.controllers.route_controller",
        ]
    )

    user_repo = providers.Singleton(PostgresUserRepository)
    report_repo = providers.Singleton(PostgresReportRepository)
    report_comment_repo = providers.Singleton(PostgresReportCommentRepository)
    report_not_there_repo = providers.Singleton(PostgresReportNotThereRepository)
    report_evaluating_repo = providers.Factory(PostgresReportEvaluatingRepository)
    route_repo = providers.Singleton(PostgresRouteRepository)

    crypto = providers.Singleton(Crypto)

    event_bus = providers.Singleton(EventBus)

    user_service = providers.Factory(
        UserService,
        repo=user_repo,
        crypto=crypto,
    )

    report_service = providers.Factory(
        ReportService,
        repo=report_repo,
        user_repo=user_repo,
        event_bus=event_bus,
        evaluating_repo=report_evaluating_repo,
    )

    report_comment_service = providers.Factory(
        ReportCommentService,
        repo=report_comment_repo,
    )

    report_not_there_service = providers.Factory(
        ReportNotThereService,
        repo=report_not_there_repo,
        report_repo=report_repo,
    )

    report_evaluating_service = providers.Factory(
        ReportEvaluatingService,
        report_repo=report_repo,
        evaluating_repo=report_evaluating_repo,
    )

    route_service = providers.Factory(
        RouteService,
        repo=route_repo,
        report_repo=report_repo,
    )
