from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel, create_engine, Session
from pydantic import BaseModel
from sqlmodel import Field

# Initialize FastAPI app
app = FastAPI()

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
DATABASE_URL = "sqlite:///database.db"
engine = create_engine(DATABASE_URL)
SQLModel.metadata.create_all(engine)

# Example database model
class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    email: str

# Pydantic model for request validation
class UserCreate(BaseModel):
    name: str
    email: str

# API Endpoints
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI backend!"}

@app.get("/users")
def get_users():
    with Session(engine) as session:
        users = session.query(User).all()
        return users

@app.post("/users")
def create_user(user: UserCreate):
    with Session(engine) as session:
        new_user = User(name=user.name, email=user.email)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user

@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        if user:
            session.delete(user)
            session.commit()
            return {"message": "User deleted successfully"}
        return {"error": "User not found"}
