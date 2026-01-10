def handle_event(event_type: str, event, debug: bool):
    response = {
        "status": "accepted",
        "event_type": event_type,
        "user_id": event.user_id,
        "timestamp": event.timestamp.isoformat(),
    }

    if debug:
        response["payload"] = event.payload

    return response
