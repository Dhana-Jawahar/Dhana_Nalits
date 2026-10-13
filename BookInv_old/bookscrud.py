# from fastapi import APIRouter, Depends, HTTPException, status
# from sqlalchemy.orm import Session

# from app.database import get_db
# from app.dependencies import get_current_user, require_admin
# from app.models import Book
# from app.schemas import BookCreate, BookResponse, BookUpdate

# router = APIRouter(prefix="/books", tags=["books"])


# @router.get("", response_model=list[BookResponse])
# def list_books(
#     db: Session = Depends(get_db),
#     user=Depends(get_current_user),
# ):
#     return db.query(Book).all()


# @router.get("/{book_id}", response_model=BookResponse)
# def get_book(
#     book_id: int,
#     db: Session = Depends(get_db),
#     user=Depends(get_current_user),
# ):
#     book = db.query(Book).filter(Book.bookid == book_id).first()
#     if book is None:
#         raise HTTPException(status_code=404, detail="Book not found")
#     return book


# @router.post(
#     "",
#     response_model=BookResponse,
#     status_code=status.HTTP_201_CREATED,
# )
# def create_book(
#     book_data: BookCreate,
#     db: Session = Depends(get_db),
#     admin=Depends(require_admin),
# ):
#     book = Book(**book_data.model_dump())
#     db.add(book)
#     db.commit()
#     db.refresh(book)
#     return book


# @router.put("/{book_id}", response_model=BookResponse)
# def update_book(
#     book_id: int,
#     book_data: BookUpdate,
#     db: Session = Depends(get_db),
#     admin=Depends(require_admin),
# ):
#     book = db.query(Book).filter(Book.bookid == book_id).first()
#     if book is None:
#         raise HTTPException(status_code=404, detail="Book not found")

#     for field, value in book_data.model_dump().items():
#         setattr(book, field, value)

#     db.commit()
#     db.refresh(book)
#     return book


# @router.delete("/{book_id}")
# def delete_book(
#     book_id: int,
#     db: Session = Depends(get_db),
#     admin=Depends(require_admin),
# ):
#     book = db.query(Book).filter(Book.bookid == book_id).first()
#     if book is None:
#         raise HTTPException(status_code=404, detail="Book not found")

#     db.delete(book)
#     db.commit()
#     return {"message": "Book deleted"}