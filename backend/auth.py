# Import JWT tools for creating and decoding tokens
from datetime import datetime, timedelta
from jose import JWTError, jwt

# Import bcrypt directly for password hashing — no middleman library
import bcrypt

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