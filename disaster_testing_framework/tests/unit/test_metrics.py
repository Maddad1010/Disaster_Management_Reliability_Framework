import pytest
from app.services.testing_service import engine

def test_engine_initialization():
    assert engine.is_running is False
    assert engine.test_id is None

def test_score_calculation():
    # Mocking some metrics
    engine.stats = {
        "total_requests": 100,
        "success": 95,
        "failed": 5,
        "response_times": [100]*50 + [1000]*50, # avg 550
        "start_time": 0,
        "current_users": 10,
        "errors": 5,
        "cpu_usage": 50,
        "memory_usage": 50
    }
    
    # We shouldn't call get_summary directly if engine is not fully initialized but let's see
    metrics = engine.get_summary()
    assert metrics["avg_response_ms"] == 550.0
    assert metrics["error_rate"] == 5.0
    assert metrics["reliability_score"] == 95.0
    
    # Perf score = 100 - (500 over limit -> -2.5) - (5 error -> -25) => 100 - 27.5 = 72.5
    # Wait, max penalty for avg response is (550-500)/20 = 2.5
    # penalty for error is 5*5 = 25
    # score = 100 - 2.5 - 25 = 72.5
    assert metrics["performance_score"] == 72.5
