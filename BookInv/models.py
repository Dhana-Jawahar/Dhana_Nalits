from sqlalchemy import Column, Integer, String, Numeric
from databaseconnect import Base


class Book(Base):
    __tablename__ = "books"

    bookid = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    isbn = Column(String(20), unique=True, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False, default=0)