from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from models import Book
from databaseconnect import get_db


app = FastAPI(title="Book Inventory API")

security = HTTPBasic()

def authenticate_user(
    credentials: HTTPBasicCredentials = Depends(security)
):
    username = credentials.username
    password = credentials.password
    
    if username == "admin" and password == "admin123":
        return {
            "username": "admin",
            "role": "admin"
        }

    if username == "user1" and password == "user123":
        return {
            "username": "user1",
            "role": "user"
        }

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password",
        headers={"WWW-Authenticate": "Basic"}
    )
@app.get("/")
def home():
    return {"message": "Book Inventory API is running"}


@app.get("/books")
def get_books(db: Session = Depends(get_db),user=Depends(authenticate_user)):
    return db.query(Book).all()


@app.get("/books/{book_id}")
def get_book(book_id: int, db: Session = Depends(get_db),user=Depends(authenticate_user)):
    book = db.query(Book).filter(Book.bookid == book_id).first()

    if not book:
        raise HTTPException(
            status_code=404,
            detail="Book not found"
        )
    return book

@app.delete("/books/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db),user=Depends(authenticate_user)):
    if user["role"] != "admin":
            raise HTTPException(
            status_code=403,
            detail="Only admin can delete the book"
            )

    book = db.query(Book).filter(Book.bookid == book_id).first()
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
    db: Session = Depends(get_db),
    user=Depends(authenticate_user)):
    
    # Authorization
    if user["role"] != "admin":
        raise HTTPException(
        status_code=403,
        detail="Only admin can create books"
        )
    
    new_book = Book(
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
                 db: Session = Depends(get_db),user=Depends(authenticate_user)):
    if user["role"] != "admin":
            raise HTTPException(
            status_code=403,
            detail="Only admin can update books"
            )
    u_book = db.query(Book).filter(Book.bookid == book_id).first()
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