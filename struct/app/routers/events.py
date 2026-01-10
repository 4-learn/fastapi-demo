from fastapi import APIRouter, Query

from app.schemas.event import EventPayload
from app.services.event_service import handle_event

router = APIRouter(prefix="/events")


@router.post("/{event_type}")
def receive_event(event_type: str, event: EventPayload, debug: bool = Query(False)):
    return handle_event(event_type, event, debug)
