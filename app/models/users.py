from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Users(Base):
    __tablename__ = "users"

    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False, comment='Username пользователя')
    email: Mapped[str] = mapped_column(String(128), unique=True, primary_key=True, nullable=False, comment='Email пользователя')
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False, comment='Пароль пользователя')

    snippets: Mapped[list['Snippets']] = relationship('Snippets', back_populates='owner')