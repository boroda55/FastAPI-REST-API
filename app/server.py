from fastapi import FastAPI, Request, Query, HTTPException
from sqlalchemy import select
from pydantic import BaseModel

import auth
import crud
from lifespan import lifespan
from schema import (IdResponse,
                    CreateAdvertisementRequest,
                    GetAdvertisementResponse,
                    SearchAdvertisementResponse,
                    UpdateAdvertisementRequest,
                    LoginResponse, LoginRequest,
                    CreateUserResponse, CreateUserRequest, GetUserResponse, UpdateUserRequest,
                    )
from dependency import SessionDependency, TokenDependency
from models import Advertisements, User, Token

app = FastAPI(
    title='API', # Название приложения
    terms_of_service='',# Лицензия использования
    description='', # Описание
    lifespan=lifespan
)

@app.post('/advertisement', response_model=IdResponse)
async def create_advertisement(session: SessionDependency, token: TokenDependency, item: CreateAdvertisementRequest):

    advertisement = Advertisements(
        title=item.title,
        description=item.description,
        price=item.price,
        user_id=token.user_id,
    )
    await crud.add_item(session, advertisement)
    return advertisement.dict

@app.get('/advertisement/{advertisement_id}', response_model=GetAdvertisementResponse)
async def get_advertisement(session: SessionDependency, advertisement_id: int):
    advertisement = await crud.get_item_by_id(session, Advertisements, advertisement_id)
    return advertisement.dict


@app.get('/advertisement', response_model=SearchAdvertisementResponse)
async def search_advertisement(
        session: SessionDependency,
        title: str = Query(None),
        description: str = Query(None),
        author: str = Query(None),
        price: int = Query(None),
        min_price: int = Query(None),
        max_price: int = Query(None)
):
    query = select(Advertisements)

    if title:
        query = query.where(Advertisements.title.ilike(f"%{title}%"))
    if description:
        query = query.where(Advertisements.description.ilike(f"%{description}%"))
    if author:
        query = query.join(User).where(User.name.ilike(f"%{author}%"))
    if price:
        query = query.where(Advertisements.price == price)
    if min_price:
        query = query.where(Advertisements.price >= min_price)
    if max_price:
        query = query.where(Advertisements.price <= max_price)

    result = await session.scalars(query)
    advertisements = result.all()
    return {"results": [adv.dict for adv in advertisements]}

@app.patch('/advertisement/{advertisement_id}', response_model=IdResponse)
async def update_advertisement(
        session: SessionDependency,
        token: TokenDependency,
        advertisement_id: int,
        item: UpdateAdvertisementRequest
):
    advertisement = await crud.get_item_by_id(session, Advertisements, advertisement_id)
    if token.user.role == 'admin' or advertisement.user_id == token.user_id:
        if item.title is not None:
            advertisement.title = item.title
        if item.description is not None:
            advertisement.description = item.description
        if item.price is not None:
            advertisement.price = item.price
        await crud.add_item(session, advertisement)
        return {'id': advertisement_id}
    else:
        raise HTTPException(403, 'Influent privileges')


@app.delete('/advertisement/{advertisement_id}', response_model=IdResponse)
async def delete_advertisement(session: SessionDependency,
                               advertisement_id: int,
                               token: TokenDependency):
    advertisement = await crud.get_item_by_id(session, Advertisements, advertisement_id)
    if token.user.role == 'admin' or advertisement.user_id == token.user_id:
        await crud.delete_item(session, advertisement)
        return {'id': advertisement_id}
    else:
        raise HTTPException(403, 'Influent privileges')

@app.post('/login', response_model=LoginResponse)
async def login(session: SessionDependency, login_data: LoginRequest):
    query = select(User).where(User.name == login_data.name)
    user = await session.scalar(query)
    if user is None:
        raise HTTPException(401, detail="Invalid credentials")
    if not auth.check_password(login_data.password, user.password):
        raise HTTPException(401, detail="Invalid credentials")
    token = Token(user_id=user.id)
    await crud.add_item(session, token)
    return token.dict

@app.post('/user', response_model=CreateUserResponse)
async def create_user(session: SessionDependency,
                      user_data: CreateUserRequest,
                      token: TokenDependency):
    if token and token.user.role != 'admin' and user_data.role != 'admin':
        raise HTTPException(403, 'Cannot create admin use')
    user_dict = user_data.model_dump(exclude_unset=True)
    user_dict['password'] = auth.hash_password(user_dict['password'])
    user_orm_obj = User(**user_dict)
    await crud.add_item(session, user_orm_obj)
    return user_orm_obj.id_dict

@app.get('/user/{user_id}', response_model=GetUserResponse)
async def get_user(session: SessionDependency, user_id: int):
    user = await crud.get_item_by_id(session, User, user_id)
    return user.dict

@app.patch('/user/{user_id}', response_model=IdResponse)
async def update_user(session: SessionDependency,
                      user_id: int,
                      item: UpdateUserRequest,
                      token: TokenDependency):
    user = await crud.get_item_by_id(session, User, user_id)
    if token.user.role == 'admin' or user.id == token.user_id:
        if item.name is not None:
            user.name = item.name
        if item.password is not None:
            user.password = item.password
        if item.role is not None:
            user.role = item.role
        await crud.add_item(session, user)
        return {'id': user_id}
    else:
        raise HTTPException(403, 'Influent privileges')


@app.delete('/user/{user_id}', response_model=IdResponse)
async def delete_user(session: SessionDependency,
                      user_id: int,
                      token: TokenDependency):

    user = await crud.get_item_by_id(session, User, user_id)
    if token.user.role == 'admin' or user.id == token.user_id:
        await crud.delete_item(session, user)
        return {'id': user_id}
    else:
        raise HTTPException(403, 'Influent privileges')
