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