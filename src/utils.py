import re

from datetime import datetime

from sqlalchemy import insert, select, update
from sqlalchemy.exc import IntegrityError

from .config import DATABASE_ENGINE
from .models import Funnel


async def check_triggers(text: str) -> bool:
    """Функция для проверки слов-триггеров."""

    if re.match(r'.*[Оо]тлично.*', text) or re.match(r'.*[Пп]рекрасно.*', text):
        return True
    return False


async def check_status(user_id: int) -> bool | None:
    """Функция для проверки статуса воронки."""

    async with DATABASE_ENGINE.connect() as conn:
        query = select(Funnel.status).where(Funnel.id == user_id)
        result = await conn.execute(query)
        status = result.scalars().one_or_none()
        if status is not None:
            if status != 'alive':
                return True
            return False
        else:
            return None


async def create_funnel_db(user_id: int, user_status: str) -> bool:
    """Функция для создания воронки."""

    try:
        async with DATABASE_ENGINE.connect() as conn:
            stmt = insert(
                Funnel
            ).values(
                id=user_id,
                status=user_status,
            )
            await conn.execute(stmt)
            await conn.commit()
        return True
    except IntegrityError:
        return False


async def change_funnel_status(user_id: int, user_status: str) -> None:
    """Функция для изменения статуса воронки."""

    async with DATABASE_ENGINE.connect() as conn:
        stmt = update(
            Funnel
        ).values(
            status=user_status,
            status_updated_at=datetime.utcnow()
        ).where(
            Funnel.id == user_id
        )
        await conn.execute(stmt)
        await conn.commit()
