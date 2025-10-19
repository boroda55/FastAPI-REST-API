import uuid
import datetime

from models import Session, Token
from typing import Annotated, Optional
from fastapi import Depends, HTTPException, Header

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from config import TOKEN_TTL_HOURS



async def get_session() -> Session:
    async with Session() as session:
        yield session


SessionDependency = Annotated[AsyncSession, Depends(get_session, use_cache=True)]

async def get_token(session: SessionDependency,
                    x_token: Annotated[Optional[uuid.UUID], Header()] = None,
                    ) -> Optional[Token]:
    if x_token is None:
        return None
    query = select(Token).where(
        Token.token == x_token,
        Token.creation_time >=
        (datetime.datetime.now() - datetime.timedelta(hours=TOKEN_TTL_HOURS)),
        )
    token = await session.scalar(query)
    if token is None:
        raise HTTPException(401, detail="Token not found")
    return token


TokenDependency = Annotated[Optional[Token], Depends(get_token)]

