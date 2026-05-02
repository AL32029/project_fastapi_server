import datetime
import uuid

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql.base import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Snippets(Base):
    __tablename__ = 'snippets'

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=lambda: uuid.uuid4(),
                                          comment='UID сниппета')

    title: Mapped[str] = mapped_column(String(128), comment='Название сниппета')
    code: Mapped[str] = mapped_column(Text, comment='Код')
    language: Mapped[str] = mapped_column(String(50), comment='Язык кода')

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime(timezone=True),
                                                          default=lambda: datetime.datetime.now(),
                                                          comment='Дата создания сниппета')

    owner_email: Mapped[str] = mapped_column(String(128), ForeignKey('users.email', ondelete='CASCADE', onupdate='CASCADE'),
                                          comment='Email пользователя')
    owner: Mapped['Users'] = relationship('Users', back_populates='snippets', lazy='joined')
