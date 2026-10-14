from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Disaster, Shelter, RescueRequest

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/")
def home(request: Request, db: Session = Depends(get_db)):
    active_disasters = db.query(Disaster).filter(Disaster.status == "Active").count()
    shelters = db.query(Shelter).count()
    rescues = db.query(RescueRequest).filter(RescueRequest.status == "Pending").count()
    
    return templates.TemplateResponse(request=request, name="dashboard.html", context={
        "active_disasters": active_disasters,
        "shelters": shelters,
        "rescues": rescues
    })

@router.get("/alerts")
def alerts(request: Request, db: Session = Depends(get_db)):
    disasters = db.query(Disaster).all()
    return templates.TemplateResponse(request=request, name="alerts.html", context={"disasters": disasters})

@router.get("/shelters")
def shelters(request: Request, db: Session = Depends(get_db)):
    shelters = db.query(Shelter).all()
    return templates.TemplateResponse(request=request, name="shelters.html", context={"shelters": shelters})

@router.get("/rescue")
def rescue(request: Request, db: Session = Depends(get_db)):
    requests = db.query(RescueRequest).all()
    return templates.TemplateResponse(request=request, name="rescue.html", context={"requests": requests})
