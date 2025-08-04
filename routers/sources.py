from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from models import Source
from schemas import SourceCreate, SourceUpdate, SourceOut
from security import get_api_key

router = APIRouter(prefix="/sources", tags=["sources"])

@router.get("/", response_model=List[SourceOut])
def list_sources(db: Session = Depends(get_db)):
    return db.query(Source).all()

@router.post("/", response_model=SourceOut, dependencies=[Depends(get_api_key)])
def create_source(source: SourceCreate, db: Session = Depends(get_db)):
    existing_source = db.query(Source).filter(Source.url == source.url).first()
    if existing_source:
        raise HTTPException(status_code=409, detail="Source with this URL already exists")

    db_source = Source(**source.model_dump())
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source

@router.put("/{source_id}", response_model=SourceOut, dependencies=[Depends(get_api_key)])
def update_source(source_id: int, source: SourceUpdate, db: Session = Depends(get_db)):
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")
    update_data = source.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_source, key, value)
    db.commit()
    db.refresh(db_source)
    return db_source

@router.delete("/{source_id}", response_model=dict, dependencies=[Depends(get_api_key)])
def delete_source(source_id: int, db: Session = Depends(get_db)):
    db_source = db.query(Source).filter(Source.id == source_id).first()
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")
    db.delete(db_source)
    db.commit()
    return {"detail": "Source deleted"}