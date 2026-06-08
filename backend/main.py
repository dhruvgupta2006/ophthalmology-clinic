# FastAPI for building the API, Depends for injecting dependencies, HTTPException for errors
from fastapi import FastAPI, Depends, HTTPException

# CORS middleware allows React frontend to talk to FastAPI backend
from fastapi.middleware.cors import CORSMiddleware

# Session type for database sessions
from sqlalchemy.orm import Session

# BaseModel lets us define what data each endpoint expects to receive
from pydantic import BaseModel

# Import User table model and get_db session dependency
from models import User, get_db

# Import password hashing, verification and JWT token creation
from auth import hash_password, verify_password, create_access_token

# Create the FastAPI app instance — this is the main app object
app = FastAPI()

# Allow React (localhost:5173) to make requests to FastAPI (localhost:8000)
# Without this the browser blocks all requests between different ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # only allow requests from React
    allow_credentials=True,
    allow_methods=["*"],  # allow all HTTP methods (GET, POST etc)
    allow_headers=["*"],  # allow all headers
)

# Define the shape of data expected by /register endpoint
# Pydantic automatically validates incoming data against this
class RegisterRequest(BaseModel):
    email: str
    password: str
    role: str = "doctor"  # defaults to doctor if not provided

# Define the shape of data expected by /login endpoint
class LoginRequest(BaseModel):
    email: str
    password: str

# Register endpoint — creates a new user
@app.post("/register")
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    # Check if email already exists in database
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        # Return 400 error if email taken
        raise HTTPException(status_code=400, detail="Email already registered")
    # Create new user with hashed password
    new_user = User(
        email=request.email,
        hashed_password=hash_password(request.password),
        role=request.role
    )
    # Add to session and commit to database
    db.add(new_user)
    db.commit()
    return {"message": "User registered successfully"}

# Login endpoint — verifies credentials and returns JWT token
@app.post("/login")
def login(request: LoginRequest, db: Session = Depends(get_db)):
    # Find user by email in database
    user = db.query(User).filter(User.email == request.email).first()
    # If user not found or password wrong, return 401 error
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    # Create JWT token with user email and role embedded inside
    token = create_access_token({"sub": user.email, "role": user.role})
    # Return token to frontend
    return {"access_token": token, "token_type": "bearer"}