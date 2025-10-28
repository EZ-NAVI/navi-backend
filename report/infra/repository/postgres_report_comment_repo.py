from database import SessionLocal
from report.domain.report_comment import ReportComment as CommentVO
from report.infra.db_models.report_comment import ReportComment as CommentDB
from report.domain.repository.report_comment_repo import ReportCommentRepository


class PostgresReportCommentRepository(ReportCommentRepository):
    def save(self, comment: CommentVO) -> CommentVO:
        with SessionLocal() as db:
            db_comment = CommentDB(
                comment_id=comment.comment_id,
                report_id=comment.report_id,
                author_id=comment.user_id,
                content=comment.content,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
            )
            db.add(db_comment)
            db.commit()
            db.refresh(db_comment)
            return CommentVO.from_orm(db_comment)

    def find_by_report_id(self, report_id: str):
        with SessionLocal() as db:
            comments = (
                db.query(CommentDB).filter(CommentDB.report_id == report_id).all()
            )
            return [CommentVO.from_orm(c) for c in comments]

    def delete(self, comment_id: str):
        with SessionLocal() as db:
            comment = (
                db.query(CommentDB).filter(CommentDB.comment_id == comment_id).first()
            )
            if comment:
                db.delete(comment)
                db.commit()
