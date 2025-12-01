from fastapi import APIRouter, HTTPException
from models.location_models import LocationText, LocationTextBulk, CoordinatesRequest
from services.location_service import LocationService

router = APIRouter(prefix="/location", tags=["Location Tools"])

service = LocationService()


@router.post("/extract")
def extract_location(payload: LocationText):
    """
    Extract location from text.
    
    Example:
    {
        "text": "I am from Quetta"
    }
    
    Response:
    {
        "location": "quetta",
        "mapping": {
            "province": "Balochistan",
            "district": null,
            "tehsil": "Quetta"
        },
        "candidates": {
            "quetta": 1
        }
    }
    """
    return service.extract_single(payload.text)


@router.post("/extract/bulk")
def extract_location_bulk(payload: LocationTextBulk):
    """
    Extract locations from multiple texts.
    
    Example:
    {
        "texts": ["I am from Quetta", "Living in Lahore"]
    }
    """
    return service.extract_bulk(payload.texts)


@router.post("/coordinates")
def get_coordinates(payload: CoordinatesRequest):
    """
    Get coordinates for a specific province, district, or tehsil.
    Accepts any combination of the three - will return coordinates for the most specific level provided.
    
    Example 1 - Province only:
    {
        "province": "Sindh"
    }
    
    Example 2 - District:
    {
        "province": "Sindh",
        "district": "Karachi East"
    }
    
    Example 3 - Tehsil:
    {
        "district": "Karachi",
        "tehsil": "New Karachi Town"
    }
    
    Response:
    {
        "province": "Sindh",
        "district": null,
        "tehsil": null,
        "coordinates": {
            "type": "Feature",
            "geometry": {
                "type": "MultiPolygon",
                "coordinates": [...]
            },
            "properties": {...}
        },
        "level": "province"
    }
    """
    if not payload.province and not payload.district and not payload.tehsil:
        raise HTTPException(
            status_code=400,
            detail="At least one of province, district, or tehsil must be provided"
        )
    
    result = service.get_coordinates(
        province=payload.province,
        district=payload.district,
        tehsil=payload.tehsil
    )
    
    if not result["coordinates"]:
        raise HTTPException(
            status_code=404,
            detail=f"No coordinates found for the provided location"
        )
    
    return result


@router.post("/extract/coordinates")
def extract_location_with_coordinates(payload: LocationText):
    """
    Extract location from text AND get its coordinates in one call.
    
    Example:
    {
        "text": "I am from Quetta"
    }
    
    Response:
    {
        "location": "quetta",
        "mapping": {
            "province": "Balochistan",
            "district": null,
            "tehsil": "Quetta"
        },
        "coordinates": {
            "type": "Feature",
            "geometry": {...},
            "properties": {...}
        },
        "level": "tehsil"
    }
    """
    mapping_result = service.extract_single(payload.text)
    
    if not mapping_result["location"] or not mapping_result["mapping"]:
        return {
            "location": mapping_result["location"],
            "mapping": mapping_result["mapping"],
            "coordinates": None,
            "level": None,
            "message": "No location found in text"
        }
    
    result = service.get_coordinates_from_mapping(mapping_result)
    
    return result