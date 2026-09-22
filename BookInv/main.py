from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from BookInv import models
from BookInv import schemas

from BookInv.databaseconnect import engine, get_db


app = FastAPI(title="Book Inventory API")


@app.get("/")
def home():
    return {"message": "Book Inventory API is running"}


@app.get("/books")
def get_books(db: Session = Depends(get_db)):
    return db.query(models.Book).all()


@app.get("/books/{book_id}")
def get_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.bookid == book_id).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )
    return book

@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book = db.query(models.Book).filter(models.Book.bookid == book_id).first()
    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )
    
    db.delete(book)
    db.commit()

    return "Book detail successfully deleted"




@app.post("/books")
def create_book(title: str,
    author: str,
    isbn: str,
    price: float,
    quantity: int = 0 ,    
    db: Session = Depends(get_db)
):
    new_book = models.Book(
        title=title,
        author=author,
        isbn=isbn,
        price=price,
        quantity=quantity
    )

    db.add(new_book)
    db.commit()
    db.refresh(new_book)

    return "New Book detail Added"


@app.put("/books/{book_id}")
def update_book(book_id: int,title: str, author: str, isbn: str, price: float,quantity: int = 0 ,
                 db: Session = Depends(get_db)):
    u_book = db.query(models.Book).filter(models.Book.bookid == book_id).first()
    if not u_book:
         raise HTTPException(
                    status_code=404,
                    detail="Book not found"
                )    
    
    u_book.title = title
    u_book.author = author
    # u_book.isbn = isbn
    u_book.quantity = quantity
   
    db.commit()
    db.refresh(u_book)

    return "New Book detail Updated"