from sqlalchemy import Column, Integer, String, Numeric, CheckConstraint
from databaseconnect import Base


class Book(Base):
    __tablename__ = "books"

    bookid = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    isbn = Column(String(20), unique=True, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)

class UserDetail(Base):
    __tablename__ = 'users'

    userid = Column(Integer, primary_key=True)
    username = Column(String(150), unique=True, nullable=False)
    userpwd = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default='user')

    __table_args__ = (
        CheckConstraint(role.in_(['admin', 'user']), name='chk_only_role'),
    )
