from sqlalchemy.orm import Session

from app import models
from app.api_v1.schema.vet_document import CheckedDocumentSchema


def save_vet_document(db: Session, vet_document: CheckedDocumentSchema):
    saved_document = models.CheckedDocument(**vet_document.dict())
    db.add(saved_document)
    db.commit()


def get_checked_document_by_vet_document_uuid(db: Session, vet_document_uuid: str):
    return db.query(models.CheckedDocument).filter_by(vet_document_uuid=vet_document_uuid).one_or_none()


def get_all_checked_document(db: Session):
    return db.query(models.CheckedDocument).all()


def get_all_mistakes_document(db: Session):
    return db.query(models.CheckedDocument).filter_by(is_mistakes=True).all()
