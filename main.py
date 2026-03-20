from fastapi import FastAPI, Query, Response
from pydantic import BaseModel, Field
import math

app = FastAPI()

# ---------------- DATA ----------------

books = [
    {"id": 1, "title": "Python Basics", "author": "John", "price": 300, "is_available": True},
    {"id": 2, "title": "Data Science", "author": "Alice", "price": 500, "is_available": True},
    {"id": 3, "title": "Machine Learning", "author": "Bob", "price": 700, "is_available": False},
]

borrowed = []
history = []

# ---------------- HELPERS ----------------

def find_book(book_id):
    for b in books:
        if b["id"] == book_id:
            return b
    return None

# ---------------- MODELS ----------------

class Book(BaseModel):
    title: str = Field(..., min_length=2)
    author: str = Field(..., min_length=2)
    price: int = Field(..., gt=0)
    is_available: bool = True

class BorrowRequest(BaseModel):
    user_name: str
    book_id: int

# ---------------- DAY 1 ----------------

@app.get("/")
def home():
    return {"message": "Library System"}

@app.get("/books")
def get_books():
    return {"total": len(books), "data": books}

@app.get("/books/{book_id}")
def get_book(book_id: int):
    book = find_book(book_id)
    if not book:
        return {"error": "Book not found"}
    return book

@app.get("/books/summary")
def summary():
    available = [b for b in books if b["is_available"]]
    return {
        "total": len(books),
        "available": len(available),
        "borrowed": len(books) - len(available)
    }

@app.get("/borrowed")
def get_borrowed():
    return borrowed

# ---------------- DAY 2 ----------------

@app.post("/books")
def add_book(book: Book, response: Response):
    new_book = book.dict()
    new_book["id"] = len(books) + 1
    books.append(new_book)
    response.status_code = 201
    return new_book

# ---------------- DAY 3 ----------------

@app.post("/borrow")
def borrow_book(data: BorrowRequest):
    book = find_book(data.book_id)

    if not book:
        return {"error": "Book not found"}

    if not book["is_available"]:
        return {"error": "Book not available"}

    book["is_available"] = False

    entry = {"user": data.user_name, "book": book["title"]}
    borrowed.append(entry)
    history.append({"action": "borrow", **entry})

    return entry

@app.post("/return")
def return_book(data: BorrowRequest):
    book = find_book(data.book_id)

    if not book:
        return {"error": "Book not found"}

    book["is_available"] = True

    entry = {"user": data.user_name, "book": book["title"]}
    history.append({"action": "return", **entry})

    return entry

# ---------------- DAY 4 CRUD ----------------

@app.put("/books/{book_id}")
def update_book(book_id: int, price: int = None):
    book = find_book(book_id)
    if not book:
        return {"error": "Book not found"}

    if price:
        book["price"] = price

    return book

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    book = find_book(book_id)
    if not book:
        return {"error": "Book not found"}

    books.remove(book)
    return {"message": "Deleted"}

# ---------------- DAY 5 ----------------

@app.get("/borrow/history")
def get_history():
    return history

# ---------------- DAY 6 ----------------

@app.get("/books/search")
def search(keyword: str):
    result = [b for b in books if keyword.lower() in b["title"].lower()]
    return result

@app.get("/books/sort")
def sort_books(sort_by: str = "price", order: str = "asc"):
    reverse = True if order == "desc" else False
    return sorted(books, key=lambda x: x[sort_by], reverse=reverse)

@app.get("/books/page")
def paginate(page: int = 1, limit: int = 2):
    start = (page - 1) * limit
    total = len(books)
    total_pages = math.ceil(total / limit)

    return {
        "page": page,
        "total_pages": total_pages,
        "data": books[start:start+limit]
    }

@app.get("/books/browse")
def browse(keyword: str = None, page: int = 1, limit: int = 2):
    data = books

    if keyword:
        data = [b for b in data if keyword.lower() in b["title"].lower()]

    start = (page - 1) * limit
    return data[start:start+limit]