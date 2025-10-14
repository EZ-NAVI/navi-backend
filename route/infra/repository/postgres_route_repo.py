from route.domain.repository.route_repo import RouteRepository
from route.domain.route import Route as RouteVO
from route.infra.db_models.route import Route as RouteDB
from database import SessionLocal


class PostgresRouteRepository(RouteRepository):
    def save(self, route: RouteVO) -> RouteVO:
        with SessionLocal() as db:
            db_route = RouteDB(
                route_id=route.route_id,
                user_id=route.user_id,
                origin_lat=route.origin_lat,
                origin_lng=route.origin_lng,
                dest_lat=route.dest_lat,
                dest_lng=route.dest_lng,
                path_data=route.path_data,
                duration=route.duration,
                score=route.score,
                created_at=route.created_at,
            )
            db.add(db_route)
            db.commit()
            db.refresh(db_route)
            return RouteVO.from_orm(db_route)

    def get(self, route_id: str) -> RouteVO | None:
        with SessionLocal() as db:
            route = db.query(RouteDB).filter(RouteDB.route_id == route_id).first()
            return RouteVO.from_orm(route) if route else None

    def find_all(self):
        with SessionLocal() as db:
            routes = db.query(RouteDB).order_by(RouteDB.created_at.desc()).all()
            return [RouteVO.from_orm(r) for r in routes]
