"""Application entry point."""

from __future__ import annotations

from app import create_app
from app.logging_config import setup_logging
from config import Config

setup_logging()
app = create_app()


if __name__ == "__main__":
    print("Disaster Management Portal + Testing Framework")
    print(f"Open http://{Config.HOST}:{Config.PORT}")
    print(Config.DEMO_NOTICE)
    app.run(host=Config.HOST, port=Config.PORT, threaded=True, debug=False, use_reloader=False)
