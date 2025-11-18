from sqlalchemy.orm import Session
from fastapi import UploadFile, HTTPException
import models, schemas
from config import Settings
from botocore.exceptions import NoCredentialsError, BotoCoreError

# Create PDF (without file upload)
def create_pdf(db: Session, pdf: schemas.PDFRequest):
    db_pdf = models.PDF(
        name=pdf.name,
        selected=pdf.selected,
        file=pdf.file
    )
    db.add(db_pdf)
    db.commit()
    db.refresh(db_pdf)
    return db_pdf


# Read all PDFs or filter by selected
def read_pdfs(db: Session, selected: bool = None):
    if selected is None:
        return db.query(models.PDF).all()
    return db.query(models.PDF).filter(models.PDF.selected == selected).all()


# Read a single PDF by ID
def read_pdf(db: Session, id: int):
    return db.query(models.PDF).filter(models.PDF.id == id).first()


# Update PDF record
def update_pdf(db: Session, id: int, pdf: schemas.PDFRequest):
    db_pdf = db.query(models.PDF).filter(models.PDF.id == id).first()
    if db_pdf is None:
        return None
    
    update_data = pdf.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_pdf, key, value)

    db.commit()
    db.refresh(db_pdf)
    return db_pdf


# Delete a PDF
def delete_pdf(db: Session, id: int):
    db_pdf = db.query(models.PDF).filter(models.PDF.id == id).first()

    if db_pdf is None:
        return None

    db.delete(db_pdf)
    db.commit()
    return True


# Upload PDF to S3 and create DB entry
def upload_pdf(db: Session, file: UploadFile, file_name: str):
    s3_client = Settings.get_s3_client()
    bucket = Settings().AWS_S3_BUCKET

    try:
        # Upload to S3
        s3_client.upload_fileobj(file.file, bucket, file_name)

        # Public URL
        file_url = f"https://{bucket}.s3.amazonaws.com/{file_name}"

        # Insert to database
        db_pdf = models.PDF(
            name=file.filename,
            selected=False,
            file=file_url
        )

        db.add(db_pdf)
        db.commit()
        db.refresh(db_pdf)
        return db_pdf

    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not found")
    except BotoCoreError as e:
        raise HTTPException(status_code=500, detail=str(e))
