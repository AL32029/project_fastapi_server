from db.db import db_dependency
from models import Snippets
from schemas.snippets import CodeSnippetCreateSchema, CodeSnippetInfoSchema
from .auth import user_dependency


async def create_snippet_item(user: user_dependency, snipped_data: CodeSnippetCreateSchema, db: db_dependency):
    try:
        create_snippet_statement: Snippets = Snippets(
            **snipped_data.model_dump(),
            owner_email=str(user.get('sub'))
        )
        db.add(create_snippet_statement)
        await db.commit()
        return CodeSnippetInfoSchema(
            uid=create_snippet_statement.id,
            title=create_snippet_statement.title,
            language=create_snippet_statement.language,
            code=create_snippet_statement.code,
            created_at=create_snippet_statement.created_at
        )
    except Exception as ex:
        raise ex
