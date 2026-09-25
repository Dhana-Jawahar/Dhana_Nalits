from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import HTTPBasic, HTTPBasicCredentials
# from passlib.context import CryptContext
import bcrypt
from models import Book
from models import UserDetail
from databaseconnect import get_db
from fastapi.middleware.trustedhost import TrustedHostMiddleware




app = FastAPI(title="Book Inventory API")
# app.add_middleware(TrustedHostMiddleware,allowed_hosts=["BookInvApp.com","localhost","127.0.0.1"])

security = HTTPBasic()

def authenticate_user(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db) ):
    username = credentials.username
    password = credentials.password
        
    user = db.query(UserDetail).filter(UserDetail.username == username).first()    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"})

    if not bcrypt.checkpw(password.encode("utf-8"),user.userpwd.encode("utf-8")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Basic"})

    return {
        "username": user.username,
        "role": user.role
    }


    
@app.get("/")
def HealthCheck():
    return {"message": "Book Inventory API is running"}

# CREATE USER
@app.post("/User", status_code=status.HTTP_201_CREATED)
def create_user(username :str,userpwd:str,userrole :str , db: Session = Depends(get_db)):
    # 1. Check if the username already exists (since it's UNIQUE)
    existing_user = db.query(UserDetail).filter(UserDetail.username == username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered")
            
    hashpwd = bcrypt.hashpw(userpwd.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    new_user = UserDetail(username=username, userpwd= hashpwd, role=userrole)

    # 3. Save to database
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
    except Exception as e:
        db.rollback()
        print("DATABASE ERROR:", repr(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred"
        )
    return {
        "message": "User created successfully",
        "user_id": new_user.userid,
        "username": new_user.username
    }

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
    try:
        db.add(new_book)
        db.commit()
        db.refresh(new_book)

    except Exception as e:
        db.rollback()
        print("DATABASE ERROR:", repr(e))
        raise HTTPException(
            status_code=500,
            detail="Database error occurred"
        )

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
    u_book.price = price
    # u_book.isbn = isbn
    u_book.quantity = quantity
   
    db.commit()
    db.refresh(u_book)

    return "New Book detail Updated"