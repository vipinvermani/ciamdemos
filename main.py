from fastapi import FastAPI
from pydantic import BaseModel
from typing import Literal


app = FastAPI(title="DigitalTrust Lab")

@app.get("/")
def home():
    return {
        "application": "DigitalTrust Lab",
        "service": "Identity Proofing",
        "status": "running"
    }


class IdentityRequest(BaseModel):
    customer_name: str
    document_type: Literal["Canadian Passport", "Canadian Driver's Licence"]

@app.post("/verify-identity")
def verify_identity(request: IdentityRequest):
    return {
        "customer_name": request.customer_name,
        "document_type": request.document_type,
        "verification_status": "SIMULATED_PASS",
        "provider": "DigitalTrust Demo",
        "message": "Demo result only. No actual identity verification performed."
    }



from datetime import datetime, date

def validate_expiry(expiry_text):
    if not expiry_text:
        return "MISSING"

    try:
        expiry_date = datetime.strptime(
            expiry_text.strip(), "%Y-%m-%d"
        ).date()
    except ValueError:
        return "INVALID_DATE"

    if expiry_date < date.today():
        return "EXPIRED"

    return "VALID"




from fastapi import UploadFile, File, HTTPException
from PIL import Image, UnidentifiedImageError
from io import BytesIO
import pytesseract

@app.post("/scan-document")
async def scan_document(file: UploadFile = File(...)):

    # Accept only JPEG and PNG images
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400,
            detail="Only JPG and PNG images are supported"
        )

    # Read the uploaded file (maximum 5 MB)
    contents = await file.read(5 * 1024 * 1024 + 1)

    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File too large"
        )

    # Open the image
    try:
        image = Image.open(BytesIO(contents))
        image.load()
    except (UnidentifiedImageError, OSError):
        raise HTTPException(
            status_code=400,
            detail="Invalid image"
        )

    # Extract actual text using Tesseract
    from PIL import ImageOps, ImageEnhance

    # Convert the image to grayscale
    image = ImageOps.grayscale(image)

    # Increase contrast
    image = ImageEnhance.Contrast(image).enhance(2.0)

    # Extract text from processed image
    extracted_text = pytesseract.image_to_string(image)

    
    # Extract birthdate and expiry information
    import re

    birthdate_match = re.search(
        r"Birthdate\s*:?\s*(.*?)(?=\s+Expires\b|$)",
        extracted_text,
        re.IGNORECASE | re.MULTILINE
    )

    expiry_match = re.search(
        r"Expires\s*:?\s*([^\n]+)",
        extracted_text,
        re.IGNORECASE
    )

    extracted_fields = {
        "birthdate_raw": (
            birthdate_match.group(1).strip()
            if birthdate_match else None
        ),
        "expiry_raw": (
            expiry_match.group(1).strip()
            if expiry_match else None
        )
    }

    return {
        "filename": file.filename,
        "ocr_status": "COMPLETED",
        "extracted_text": extracted_text,
        "extracted_fields": extracted_fields,
        "expiry_validation": validate_expiry(
                extracted_fields["expiry_raw"]
            ),
        "document_authenticity": "NOT_VERIFIED"
    }

