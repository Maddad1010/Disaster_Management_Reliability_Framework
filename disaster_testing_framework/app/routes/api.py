from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Disaster, Shelter, RescueRequest
from app.config import settings
import asyncio
import random

router = APIRouter(prefix="/api")

async def simulate_failure_and_delay():
    if settings.SIMULATION_DELAY_MS > 0:
        await asyncio.sleep(settings.SIMULATION_DELAY_MS / 1000.0)
    
    if settings.SIMULATION_FAILURE_PROB > 0:
        if random.random() < (settings.SIMULATION_FAILURE_PROB / 100.0):
            raise HTTPException(status_code=503, detail="Simulated service failure")

@router.get("/health")
async def health_check():
    await simulate_failure_and_delay()
    return {"status": "ok"}

@router.get("/disasters")
async def get_disasters(db: Session = Depends(get_db)):
    await simulate_failure_and_delay()
    disasters = await asyncio.to_thread(lambda: db.query(Disaster).all())
    return {"data": disasters}

@router.get("/alerts")
async def get_alerts(db: Session = Depends(get_db)):
    await simulate_failure_and_delay()
    alerts = await asyncio.to_thread(lambda: db.query(Disaster).filter(Disaster.status == "Active").all())
    return {"data": alerts}

@router.get("/shelters")
async def get_shelters(db: Session = Depends(get_db)):
    await simulate_failure_and_delay()
    shelters = await asyncio.to_thread(lambda: db.query(Shelter).all())
    return {"data": shelters}

@router.get("/rescue-requests")
async def get_rescue_requests(db: Session = Depends(get_db)):
    await simulate_failure_and_delay()
    requests = await asyncio.to_thread(lambda: db.query(RescueRequest).all())
    return {"data": requests}

def _create_rescue(req: dict, db: Session):
    new_req = RescueRequest(
        name=req.get("name"), phone=req.get("phone"), location=req.get("location"),
        num_people=req.get("num_people"), emergency_type=req.get("emergency_type"),
        priority=req.get("priority"), description=req.get("description")
    )
    db.add(new_req)
    db.commit()
    return new_req.id

@router.post("/rescue-requests")
async def create_rescue_request(req: dict, db: Session = Depends(get_db)):
    await simulate_failure_and_delay()
    new_id = await asyncio.to_thread(_create_rescue, req, db)
    return {"status": "success", "id": new_id}
