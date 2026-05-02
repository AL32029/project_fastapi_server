import uuid

from fastapi import APIRouter, HTTPException
from starlette import status

from db.db import db_dependency
from schemas.snippets import CodeSnippetCRUDSchema, CodeSnippetInfoSchema
from services.auth import user_dependency
from services.snippet import create_snippet_item, get_snippet_item_by_uid, edit_snippet_item_by_uid, \
    delete_snippet_item_by_uid

snippet_router = APIRouter(prefix='/snippet', tags=['snippet'])

@snippet_router.post('/create', response_model=CodeSnippetInfoSchema, responses={
    201: {'description': 'Snippet was created'},
})
async def create_snippet(user: user_dependency, snippet: CodeSnippetCRUDSchema, db: db_dependency):
    try:
        return await create_snippet_item(user=user, snipped_data=snippet, db=db)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'An error has occurred: {ex}'
        )


@snippet_router.get('/{uid}', response_model=CodeSnippetInfoSchema, responses={
    404: {'description': 'Snippet not found'},
    200: {'description': 'Snippet was founded'},
})
async def get_snippet_item(uid: uuid.UUID, db: db_dependency):
    try:
        return await get_snippet_item_by_uid(uid=uid, db=db)
    except HTTPException as ex:
        if ex.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Snippet not found'
            )

        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'An error has occurred: {ex}'
        )


@snippet_router.patch(path='/{uid}', response_model=CodeSnippetInfoSchema, responses={
    404: {'description': 'Snippet not found'},
    403: {'description': 'You can\'t change someone else\'s snippet'},
    200: {'description': 'Snippet was successfully edited'},
})
async def edit_snippet_item(user: user_dependency, uid: uuid.UUID, snippet: CodeSnippetCRUDSchema, db: db_dependency):
    try:
        return await edit_snippet_item_by_uid(user=user, uid=uid, snippet=snippet, db=db)
    except HTTPException as ex:
        if ex.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Snippet not found'
            )
        elif ex.status_code == status.HTTP_403_FORBIDDEN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You can\'t change someone else\'s snippet'
            )

        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'An error has occurred: {ex}'
        )


@snippet_router.delete(path='/{uid}', responses={
    404: {'description': 'Snippet not found'},
    403: {'description': 'You can\'t change someone else\'s snippet'},
    500: {'description': 'The snippet was not deleted from the database'},
    204: {'description': 'Snippet was successfully deleted'},
})
async def delete_snippet_item(user: user_dependency, uid: uuid.UUID, db: db_dependency):
    try:
        return await delete_snippet_item_by_uid(user=user, uid=uid, db=db)
    except HTTPException as ex:
        if ex.status_code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='Snippet not found'
            )
        elif ex.status_code == status.HTTP_403_FORBIDDEN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail='You can\'t delete someone else\'s snippet'
            )
        elif ex.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail='The snippet was not deleted from the database'
            )

        raise ex
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'An error has occurred: {ex}'
        )