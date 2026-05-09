from fastapi import APIRouter, HTTPException
from services.services_judgment import *

router = APIRouter(prefix="/judgments", tags=["judgments"])

@router.get("")
def get_library_judgments():
    judgments = get_all_judgments()
    if isinstance(judgments, list):
        return judgments
    return []

@router.get("/{judgment_id}")
def get_library_judgment_by_id(judgment_id: int):
    judgment = get_judgment_by_id(judgment_id)
    if isinstance(judgment, dict) and judgment.get("id"):
        return judgment
    raise HTTPException(status_code=404, detail="Judgment not found")
