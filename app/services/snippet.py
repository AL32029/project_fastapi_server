import uuid
from typing import Optional

from fastapi import HTTPException
from fastapi.requests import Request
from fastapi.responses import Response
from sqlalchemy import select, exists
from starlette import status

from db.db import db_dependency
from models import Snippets
from schemas.snippets import CodeSnippetCRUDSchema, CodeSnippetInfoSchema
from .auth import user_dependency


async def create_snippet_item(request: Request, user: user_dependency, snipped_data: CodeSnippetCRUDSchema,
                              db: db_dependency):
    create_snippet_statement: Snippets = Snippets(
        **snipped_data.model_dump(),
        owner_email=str(user.get('sub'))
    )
    db.add(create_snippet_statement)
    await db.commit()
    return CodeSnippetInfoSchema(
        uid=create_snippet_statement.id,
        url=request.url_for('get_snippet_item', uid=create_snippet_statement.id),
        title=create_snippet_statement.title,
        language=create_snippet_statement.language,
        code=create_snippet_statement.code,
        created_at=create_snippet_statement.created_at
    )


async def get_snippet_item_by_uid(request: Request, uid: uuid.UUID, db: db_dependency):
    snippet_item: Optional[Snippets] = await db.scalar(
        select(Snippets).
        where(Snippets.id == uid)
    )
    if not snippet_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Snippet not found'
        )

    return CodeSnippetInfoSchema(
        uid=snippet_item.id,
        url=request.url_for('get_snippet_item', uid=uid),
        title=snippet_item.title,
        language=snippet_item.language,
        code=snippet_item.code,
        created_at=snippet_item.created_at
    )


async def edit_snippet_item_by_uid(request: Request, user: user_dependency, uid: uuid.UUID,
                                   snippet: CodeSnippetCRUDSchema,
                                   db: db_dependency):
    snippet_item: Optional[Snippets] = await db.scalar(
        select(Snippets).
        where(Snippets.id == uid)
    )

    if not snippet_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Snippet not found'
        )

    if snippet_item.owner_email != user.get('sub'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You can\'t change someone else\'s snippet'
        )

    for key, value in snippet.model_dump().items():
        setattr(snippet_item, key, value)

    await db.commit()
    await db.refresh(snippet_item)

    return CodeSnippetInfoSchema(
        uid=snippet_item.id,
        url=str(request.url_for('get_snippet_item', uid=uid)),
        title=snippet_item.title,
        language=snippet_item.language,
        code=snippet_item.code,
        created_at=snippet_item.created_at
    )


async def delete_snippet_item_by_uid(user: user_dependency, uid: uuid.UUID, db: db_dependency):
    snippet_item: Optional[Snippets] = await db.scalar(
        select(Snippets).
        where(Snippets.id == uid)
    )

    if not snippet_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Snippet not found'
        )

    if snippet_item.owner_email != user.get('sub'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You can\'t change someone else\'s snippet'
        )

    await db.delete(snippet_item)
    await db.commit()
    is_deleted = await db.scalar(
        select(exists().where(Snippets.id == uid))
    )

    if is_deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='The snippet was not deleted from the database'
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)
