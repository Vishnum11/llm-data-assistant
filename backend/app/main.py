from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from .db import create_db_and_tables, get_session
from .models import User, Project
from .auth import hash_password, verify_password, create_access_token, decode_token
from .ingest import ingest_file_to_collection
from .chat import answer_query
from typing import List
import os

create_db_and_tables()

app = FastAPI(title="LLM Data Assistant - Backend")

@app.post("/register")
def register(username: str, password: str, session: Session = Depends(get_session)):
    user_exists = session.exec(select(User).where(User.username == username)).first()
    if user_exists:
        raise HTTPException(status_code=400, detail="User exists")
    user = User(username=username, hashed_password=hash_password(password))
    session.add(user)
    session.commit()
    session.refresh(user)
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer", "username": user.username}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect credentials")
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}

def get_current_user(token: str = Depends(lambda: None), session: Session = Depends(get_session)):
    from fastapi import Request
    def inner(request: Request):
        auth = request.headers.get("Authorization")
        if not auth:
            raise HTTPException(status_code=401, detail="Missing auth")
        scheme, _, tok = auth.partition(" ")
        payload = decode_token(tok)
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token")
        username = payload.get("sub")
        user = session.exec(select(User).where(User.username == username)).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    return inner

@app.post("/projects")
def create_project(name: str, description: str = "", current_user = Depends(get_current_user()), session: Session = Depends(get_session)):
    user = current_user
    project = Project(name=name, owner_id=user.id, description=description)
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@app.get("/projects", response_model=List[Project])
def list_projects(current_user = Depends(get_current_user()), session: Session = Depends(get_session)):
    user = current_user
    projects = session.exec(select(Project).where(Project.owner_id == user.id)).all()
    return projects

@app.post("/projects/{project_id}/upload")
def upload_and_ingest(project_id: int, file: UploadFile = File(...), max_rows: int = 2000, current_user = Depends(get_current_user()), session: Session = Depends(get_session)):
    proj = session.get(Project, project_id)
    if not proj or proj.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Project not found or access denied")
    collection_name = f"user{current_user.id}_proj{proj.id}"
    res = ingest_file_to_collection(file.file, collection_name=collection_name, max_rows=max_rows)
    return {"project_id": project_id, "collection": collection_name, "ingest": res}

@app.post("/projects/{project_id}/query")
def project_query(project_id: int, question: str, current_user = Depends(get_current_user())):
    collection_name = f"user{current_user.id}_proj{project_id}"
    try:
        resp = answer_query(collection_name, question)
        return resp
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
