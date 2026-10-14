from app.database import engine, SessionLocal
from app.models.base import Base
from app.models import Disaster, Shelter, RescueRequest
import random
from datetime import datetime, timedelta

def seed_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Check if empty
    if db.query(Disaster).count() > 0:
        print("Database already seeded.")
        return

    disasters = [
        {"type": "Flood", "loc": "Downtown", "sev": "High"},
        {"type": "Earthquake", "loc": "North Side", "sev": "High"},
        {"type": "Cyclone", "loc": "East Coast", "sev": "Medium"},
        {"type": "Forest Fire", "loc": "West Hills", "sev": "High"},
        {"type": "Landslide", "loc": "Mountain View", "sev": "Medium"},
        {"type": "Flood", "loc": "River Side", "sev": "Low"},
        {"type": "Chemical Spill", "loc": "Industrial Park", "sev": "High"},
        {"type": "Earthquake", "loc": "South Zone", "sev": "Medium"},
        {"type": "Cyclone", "loc": "Bay Area", "sev": "High"},
        {"type": "Tsunami Warning", "loc": "Coastal Road", "sev": "Medium"}
    ]
    
    for d in disasters:
        db.add(Disaster(disaster_type=d["type"], location=d["loc"], severity=d["sev"], 
                        description="Dummy data for academic demonstration", status="Active"))

    shelters = [
        {"name": "School No. 1", "loc": "Downtown", "cap": 500, "occ": 120},
        {"name": "Community Hall", "loc": "North Side", "cap": 1000, "occ": 800},
        {"name": "Sports Stadium", "loc": "East Coast", "cap": 5000, "occ": 300},
        {"name": "Town Hall", "loc": "West Hills", "cap": 200, "occ": 190},
        {"name": "Municipal Bldg", "loc": "Mountain View", "cap": 300, "occ": 0},
        {"name": "High School 5", "loc": "River Side", "cap": 400, "occ": 50},
        {"name": "Church", "loc": "Industrial Park", "cap": 150, "occ": 10},
        {"name": "University Gym", "loc": "South Zone", "cap": 2000, "occ": 100},
        {"name": "Mall Basement", "loc": "Bay Area", "cap": 800, "occ": 800},
        {"name": "Train Station", "loc": "Coastal Road", "cap": 1000, "occ": 950}
    ]
    
    for s in shelters:
        db.add(Shelter(name=s["name"], location=s["loc"], capacity=s["cap"], occupied=s["occ"]))
        
    for i in range(10):
        db.add(RescueRequest(
            name=f"Demo User {i}", phone=f"555-010{i}", location=f"Demo Street {i}",
            num_people=random.randint(1, 5), emergency_type="Medical",
            priority=random.choice(["High", "Medium", "Critical"]),
            description="Academic demo rescue request"
        ))

    db.commit()
    print("Seeded database with dummy data.")

if __name__ == "__main__":
    seed_db()
