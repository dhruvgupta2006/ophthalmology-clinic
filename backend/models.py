from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:newpassword123@localhost:5432/ophthalmology_clinic")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default='doctor')
    created_at = Column(DateTime, default=datetime.utcnow)

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    hospital_reg_no = Column(String, unique=True, nullable=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    gender = Column(String)
    contact = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

        # Import specific tools from SQLAlchemy needed to define tables and column types

# declarative_base lets you define database tables as Python classes

# sessionmaker creates a factory for database sessions (temporary workspaces)

# Read .env file and load SECRET_KEY, DATABASE_URL into memory

# Read database connection string from .env

# Create the engine — the actual phone line/connection between Python and PostgreSQL

# Create session factory bound to our engine — every request gets its own session

# Create base class — all table classes inherit from this to get database superpowers

# User class maps to the users table in PostgreSQL
# Inherits from Base so SQLAlchemy recognises it as a database table
# SQLAlchemy auto-generates __init__ from the column definitions

# unique