from datetime import date

from sqlalchemy import Date, cast, func
from sqlalchemy.orm import Session

from db import models
from service.schemas import v1 as schemas_v1


def get_comments_breakdown(db: Session, date_from: date, date_to: date):
    results = (
        db.query(
            cast(models.Comment.created_at, Date).label("date"),
            models.Comment.is_blocked,
            func.count(models.Comment.id).label("count"),
        )
        .filter(
            models.Comment.created_at >= date_from, models.Comment.created_at <= date_to
        )
        .group_by(cast(models.Comment.created_at, Date), models.Comment.is_blocked)
        .all()
    )

    daily_stats = {}
    for result in results:
        date_str = result.date.strftime("%Y-%m-%d")
        if date_str not in daily_stats:
            daily_stats[date_str] = {
                "date": result.date,
                "blocked_count": 0,
                "unblocked_count": 0,
            }
        if result.is_blocked:
            daily_stats[date_str]["blocked_count"] += result.count
        else:
            daily_stats[date_str]["unblocked_count"] += result.count

    breakdown = [
        schemas_v1.DailyCommentStats(**stats) for stats in daily_stats.values()
    ]
    return schemas_v1.CommentsDailyBreakdownResponse(breakdown=breakdown)
