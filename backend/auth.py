# Import JWT tools for creating and decoding tokens
from datetime import datetime, timedelta
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer
# Import bcrypt directly for password hashing — no middleman library
import bcrypt
from fastapi import Depends, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from models import get_db  # adjust import path to wherever get_db actually lives
from models import User      # adjust to your actual User model import
import os
from dotenv import load_dotenv

# Load .env file into memory
load_dotenv()

# Secret key used to sign JWT tokens — read from .env, fallback if missing
SECRET_KEY = os.getenv("SECRET_KEY", "fallbacksecretkey")

# Encryption algorithm used to sign JWT tokens
ALGORITHM = "HS256"

# How long a JWT token stays valid before expiring
ACCESS_TOKEN_EXPIRE_MINUTES = 30


# Tells FastAPI how to extract the JWT from incoming requests:
# expects "Authorization: Bearer <token>" header, pulls out just the token.
# tokenUrl="login" is only used for Swagger docs (/docs) - it doesn't redirect anything.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# Takes a plain password, encodes it to bytes, generates a random salt, hashes it
# Returns the hash as a string for storing in the database
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Takes plain password and stored hash, both encoded to bytes
# bcrypt re-hashes the plain password with the same salt and compares
# Returns True if match, False if not
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# Creates a JWT token after successful login
# Copies the data, stamps it with expiry time, signs it with secret key
# Returns the token string
def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Verifies a JWT token sent by the frontend
# Decodes it using the secret key and returns the original data
def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(status_code=401, detail="Invalid or expired token")
    
    try:
        payload = decode_access_token(token)
    except JWTError:
        raise credentials_exception

    email = payload.get("sub")
    if email is None:
        raise credentials_exception

    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception

    return user