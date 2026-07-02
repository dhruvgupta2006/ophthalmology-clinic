# FastAPI for building the API, Depends for injecting dependencies, HTTPException for errors
from fastapi import FastAPI, Depends, HTTPException

# CORS middleware allows React frontend to talk to FastAPI backend
from fastapi.middleware.cors import CORSMiddleware

# Session type for database sessions
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Pydantic for request/response validation and configuration
from pydantic import BaseModel, ConfigDict
from typing import Optional,List
from datetime import datetime

# Import User and Patient table models, and get_db session dependency
from models import User, Patient, get_db

# Import password hashing, verification, JWT token creation, and auth dependency
from auth import hash_password, verify_password, create_access_token, get_current_user, oauth2_scheme
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

class PatientCreate(BaseModel):
    name: str                      # required — no patient record without a name
    hospital_reg_no: str            # required — DB has a unique constraint on this
    age: Optional[int] = None       # optional — may not be known at the moment of intake
    gender: Optional[str] = None    # optional — same reasoning
    contact: Optional[str] = None   # optional — may get added later, e.g. during the visit


class PatientResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)   # read .attribute, not dict["key"]

    id: int
    name: str
    hospital_reg_no: str
    age: Optional[int] = None
    gender: Optional[str] = None
    contact: Optional[str] = None
    created_at: datetime

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    hospital_reg_no: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    contact: Optional[str] = None


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

@app.get("/me")
def read_current_user(current_user: User = Depends(get_current_user)):
    return {"email": current_user.email, "id": current_user.id}


@app.post("/patients", response_model=PatientResponse)
def create_patient(request: PatientCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_patient = Patient(
    name=request.name,
    hospital_reg_no=request.hospital_reg_no,
    age=request.age,
    gender=request.gender,
    contact=request.contact
)
    db.add(new_patient)
    try:
        db.commit()
        db.refresh(new_patient)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400,detail="registration number already exists")
    
    return new_patient

@app.get("/patients", response_model=List[PatientResponse])
def get_all_patients(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Query all patients from the database
    patients = db.query(Patient).all()
    # Return the list — FastAPI converts each to PatientResponse
    return patients


@app.get("/patients/{id}", response_model=PatientResponse)
def get_patient(id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Query the patient with this id
    patient = db.query(Patient).filter(Patient.id == id).first()
    # If not found, return 404
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    # Return the patient — FastAPI converts it to PatientResponse
    return patient


@app.put("/patients/{id}", response_model=PatientResponse)
def update_patient(id: int, request: PatientUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Query the patient with this id
    patient = db.query(Patient).filter(Patient.id == id).first()
    # If not found, return 404
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # Update only the fields that were provided in the request
    if request.name is not None:
        patient.name = request.name
    if request.hospital_reg_no is not None:
        patient.hospital_reg_no = request.hospital_reg_no
    if request.age is not None:
        patient.age = request.age
    if request.gender is not None:
        patient.gender = request.gender
    if request.contact is not None:
        patient.contact = request.contact
    
    # Try to commit; catch uniqueness violations
    try:
        db.commit()
        db.refresh(patient)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="registration number already exists")
    
    return patient


@app.delete("/patients/{id}")
def delete_patient(
    id: int, 
    confirm: bool = False,
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    # Query the patient with this id
    patient = db.query(Patient).filter(Patient.id == id).first()
    # If not found, return 404
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    
    # If confirm is False, ask for confirmation
    if not confirm:
        return {
            "detail": f"Are you sure you want to delete patient '{patient.name}' (ID: {patient.id})? This action cannot be undone.",
            "confirm_required": True
        }
    
    # If confirm is True, actually delete
    db.delete(patient)
    db.commit()
    
    return {"detail": f"Patient '{patient.name}' deleted successfully"}