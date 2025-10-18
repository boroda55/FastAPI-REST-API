import datetime
import uuid

import config
from sqlalchemy import Boolean, DateTime, Integer, String, func, ForeignKey, UUID
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from costom_types import ROLE

engine = create_async_engine(config.PG_DSN)
Session = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(DeclarativeBase, AsyncAttrs):

    @property
    def id_dict(self):
        return {'id': self.id}


class Token(Base):
     __tablename__ = 'token'
     id: Mapped[int] = mapped_column(Integer, primary_key=True)
     token: Mapped[uuid.UUID] = mapped_column(
         UUID, unique=True, server_default=func.gen_random_uuid()
     )
     creation_time: Mapped[datetime.datetime] = mapped_column(
         DateTime, server_default=func.now()
     )
     user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
     user: Mapped['User'] = relationship(
         'User', lazy='joined', back_populates='tokens'
     )

     @property
     def dict(self):
         return {'token': self.token}



class User(Base):
    __tablename__ = 'user'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True)
    password: Mapped[str] = mapped_column(String)
    role: Mapped[ROLE] = mapped_column(String, default='user')
    tokens: Mapped[list['Token']] = relationship(
        'Token', lazy='joined', back_populates='user', cascade='delete, delete-orphan'
    )
    advertisements: Mapped[list['Advertisements']] = relationship(
        'Advertisements', lazy='joined', back_populates='user', cascade='all, delete-orphan'
    )

    @property
    def dict(self):
        return {'id': self.id,
                'name': self.name,
                'role': self.role}


class Advertisements(Base):

    __tablename__ = "advertisements"

    # id
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Заголовок
    title: Mapped[str] = mapped_column(String)
    # описание
    description: Mapped[str] = mapped_column(String)
    # цена
    price: Mapped[int] = mapped_column(Integer)
    # автор
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))
    user: Mapped['User'] = relationship('User', lazy='joined', back_populates='advertisements')
    # дата создания
    date_of_creation: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())

    @property
    def dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'price': self.price,
            'date_of_creation': self.date_of_creation,
            'author_id' : self.user_id,
        }



# Открытие Сессии БД
async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
# Закрытие Сессии БД
async  def close_orm():
    await engine.dispose()


ORM_OBJ = Advertisements | User | Token
ORM_CLS = type[Advertisements] | type[User] | type[Token]