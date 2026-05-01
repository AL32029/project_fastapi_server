from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class Users(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(128), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(1024), nullable=False)
    salt: Mapped[str] = mapped_column(String(1024), nullable=False, unique=True, index=True)