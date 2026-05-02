from fastapi import APIRouter, HTTPException
from starlette import status

from db.db import db_dependency
from schemas.snippets import CodeSnippetCreateSchema, CodeSnippetInfoSchema
from services.auth import user_dependency
from services.snippet import create_snippet_item

snippet_router = APIRouter(prefix='/snippet', tags=['snippet'])

@snippet_router.post('/create', response_model=CodeSnippetInfoSchema)
async def create_snippet(user: user_dependency, snippet: CodeSnippetCreateSchema, db: db_dependency):
    try:
        return await create_snippet_item(user=user, snipped_data=snippet, db=db)
    except Exception as ex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'An error has occurred: {ex}'
        )