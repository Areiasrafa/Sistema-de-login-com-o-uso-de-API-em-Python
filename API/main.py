from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.middleware.cors import CORSMiddleware



# Configuração do banco de dados
DATABASE_URL = "sqlite:///./users.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Definição do modelo do banco de dados
class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

# Criando as tabelas no banco
Base.metadata.create_all(bind=engine)


class User(BaseModel):
    name: str
    email: str

class UserOut(User):
    id: int

    class Config:
        orm_mode = True

 
app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Read/GET
@app.get("/users", response_model=List[UserOut])
def get_users():
    db = SessionLocal()
    users = db.query(UserModel).all()
    db.close()
    return users

# Read/GET (id)
@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    db = SessionLocal()
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    db.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Create/POST
@app.post("/users", response_model=UserOut)
def create_user(user: User):
    db = SessionLocal()
    new_user = UserModel(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    db.close()
    return new_user

# Editar/PUT
@app.put("/users/{user_id}", response_model=UserOut)
def update_user(user_id: int, user: User):
    db = SessionLocal()
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")
    db_user.name = user.name
    db_user.email = user.email
    db.commit()
    db.refresh(db_user)
    db.close()
    return db_user

# DELETE
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    db = SessionLocal()
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not db_user:
        db.close()
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    db.close()
    return {"message": "User deleted successfully"}
