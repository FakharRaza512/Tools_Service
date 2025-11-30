from fastapi import APIRouter
from models.location_models import LocationText, LocationTextBulk
from services.location_service import LocationService

router = APIRouter(prefix="/location", tags=["Location Tools"])

service = LocationService()


@router.post("/extract")
def extract_location(payload: LocationText):
    return service.extract_single(payload.text)


@router.post("/extract/bulk")
def extract_location_bulk(payload: LocationTextBulk):
    return service.extract_bulk(payload.texts)
