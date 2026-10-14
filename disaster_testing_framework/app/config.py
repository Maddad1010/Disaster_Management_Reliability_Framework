import os

class Settings:
    PROJECT_NAME = "Disaster Management Portal Testing Framework"
    DATABASE_URL = "sqlite:///./disaster_demo.db"
    
    # Thresholds for testing
    THRESHOLDS = {
        "PASS": {
            "max_avg_response_time": 500,  # ms
            "max_error_rate": 2.0,         # %
            "min_success_rate": 98.0       # %
        },
        "WARNING": {
            "max_avg_response_time": 1000, # ms
            "max_error_rate": 5.0,         # %
            "min_success_rate": 95.0       # %
        }
    }
    
    # Simulation settings
    SIMULATION_DELAY_MS = 0
    SIMULATION_FAILURE_PROB = 0.0

settings = Settings()
