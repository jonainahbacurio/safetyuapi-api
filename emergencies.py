from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Emergency
from ..schemas import EmergencyCreate, EmergencyOut, EmergencyUpdate

router = APIRouter(prefix="/api/emergencies", tags=["Emergencies"])
ALLOWED_STATUSES = {"waiting", "responding", "resolved"}


def _clean(value: str) -> str:
    return value.strip()


def _reference() -> str:
    # Similar display format to the original Netlify version, but collision-safe.
    return f"SOS-{uuid4().hex[:8].upper()}"


def _queue_positions(db: Session) -> dict[str, int]:
    waiting = db.scalars(
        select(Emergency)
        .where(Emergency.status == "waiting")
        .order_by(Emergency.created_at.asc(), Emergency.id.asc())
    ).all()
    return {item.id: index + 1 for index, item in enumerate(waiting)}


def _serialize(item: Emergency, queue: dict[str, int]) -> EmergencyOut:
    return EmergencyOut(
        id=item.id,
        reference=item.reference,
        category=item.category,
        location=item.location,
        description=item.description,
        status=item.status,
        responder=item.responder,
        createdAt=item.created_at,
        updatedAt=item.updated_at,
        queuePosition=queue.get(item.id) if item.status == "waiting" else None,
    )


@router.get("", response_model=list[EmergencyOut])
def list_emergencies(db: Session = Depends(get_db)):
    queue = _queue_positions(db)
    items = db.scalars(select(Emergency)).all()

    def sort_key(item: Emergency):
        if item.status == "waiting":
            return (0, queue.get(item.id, 10**9), "")
        updated = item.updated_at or item.created_at
        return (1, 0, -updated.timestamp())

    items.sort(key=sort_key)
    return [_serialize(item, queue) for item in items]


@router.get("/{emergency_id}", response_model=EmergencyOut)
def get_emergency(emergency_id: str, db: Session = Depends(get_db)):
    item = db.get(Emergency, emergency_id)
    if not item:
        raise HTTPException(status_code=404, detail="Emergency not found")
    return _serialize(item, _queue_positions(db))


@router.post("", response_model=EmergencyOut, status_code=status.HTTP_201_CREATED)
def create_emergency(payload: EmergencyCreate, db: Session = Depends(get_db)):
    category = _clean(payload.category)
    location = _clean(payload.location)
    description = _clean(payload.description)

    if not category or not location or not description:
        raise HTTPException(
            status_code=400,
            detail="category, location, and description are required",
        )

    now = datetime.now(timezone.utc)
    item = Emergency(
        id=str(uuid4()),
        reference=_reference(),
        category=category,
        location=location,
        description=description,
        status="waiting",
        created_at=now,
        updated_at=now,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return _serialize(item, _queue_positions(db))


@router.patch("/{emergency_id}", response_model=EmergencyOut)
def update_emergency(
    emergency_id: str,
    payload: EmergencyUpdate,
    db: Session = Depends(get_db),
):
    item = db.get(Emergency, emergency_id)
    if not item:
        raise HTTPException(status_code=404, detail="Emergency not found")

    new_status = payload.status.strip().lower()
    if new_status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400,
            detail="status must be waiting, responding, or resolved",
        )

    item.status = new_status
    if payload.responder is not None:
        item.responder = payload.responder.strip() or None
    item.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(item)
    return _serialize(item, _queue_positions(db))


@router.delete("/{emergency_id}")
def delete_emergency(emergency_id: str, db: Session = Depends(get_db)):
    item = db.get(Emergency, emergency_id)
    if not item:
        raise HTTPException(status_code=404, detail="Emergency not found")
    db.delete(item)
    db.commit()
    return {"success": True, "id": emergency_id}
