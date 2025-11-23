from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from . import hibp_client
from .ai_image_engine import process_image_base64
from .ai_risk_engine import build_risk_report
from .breach_search import search_in_files
from .password_checker import check_password_breach
from .utils import data_directory

app = FastAPI(title="Password Breach Checker – Privacy OSINT Dashboard", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EmailRequest(BaseModel):
    email: str
    api_key: Optional[str] = Field(default=None, description="Optional HIBP API key")


class PasswordRequest(BaseModel):
    password: str


class UsernameRequest(BaseModel):
    username: str


class ImageRequest(BaseModel):
    image_base64: str = Field(..., description="Base64 encoded image content")


class RiskRequest(BaseModel):
    email_breaches: List[dict] = Field(default_factory=list)
    password_occurrences: int = 0
    username_matches: dict = Field(default_factory=dict)
    faces_detected: int = 0


@app.get("/")
async def root() -> dict:
    return {"message": "Password Breach Checker – Privacy OSINT Dashboard", "data_path": str(data_directory())}


@app.post("/scan-email")
async def scan_email(payload: EmailRequest) -> dict:
    breaches = await hibp_client.check_email_breaches(payload.email, api_key=payload.api_key)
    pastes = await hibp_client.check_pastes(payload.email, api_key=payload.api_key)
    return {"breaches": breaches, "pastes": pastes}


@app.post("/scan-password")
async def scan_password(payload: PasswordRequest) -> dict:
    return await check_password_breach(payload.password)


@app.post("/scan-username")
async def scan_username(payload: UsernameRequest) -> dict:
    return search_in_files(payload.username)


@app.post("/scan-image")
async def scan_image(payload: ImageRequest) -> dict:
    model_path = Path(__file__).resolve().parent / "models" / "arcface.onnx"
    return process_image_base64(payload.image_base64, model_path=model_path)


@app.post("/ai-report")
async def ai_report(payload: RiskRequest) -> dict:
    return build_risk_report(payload.dict())


@app.post("/upload-dataset")
async def upload_dataset(file: UploadFile = File(...)) -> dict:
    allowed = {"text/plain", "application/csv", "text/csv", "application/octet-stream"}
    if file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use txt or csv.")
    target_dir = data_directory()
    target_dir.mkdir(parents=True, exist_ok=True)
    sanitized_name = Path(file.filename).name
    if not sanitized_name or sanitized_name != file.filename:
        raise HTTPException(status_code=400, detail="Invalid filename provided.")
    target_path = target_dir / sanitized_name
    content = await file.read()
    with target_path.open("wb") as handle:
        handle.write(content)
    return {"message": f"Uploaded {file.filename}", "path": str(target_path)}
