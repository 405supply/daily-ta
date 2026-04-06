from fastapi import APIRouter, HTTPException
from service import analysis_service as service
from repository import analysis_repository

router = APIRouter(prefix="/api")


@router.get("/analyze/{ticker}")
def analyze_single(ticker: str):
    try:
        return service.analyze_stock(ticker.upper())
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analyze-all")
def analyze_all():
    return service.analyze_all()


@router.get("/history/{ticker}")
def get_history(ticker: str):
    return analysis_repository.get_history(ticker.upper())
