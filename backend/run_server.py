"""
Server Runner Script

Starts the FastAPI development server.

Usage:
    python run_server.py
"""

import uvicorn
#import settings class from app/core/config.py
from app.core.config import settings

if __name__ == "__main__":
    print(f"""
    ============================================================
    Starting {settings.APP_NAME}
    ============================================================
    Server: http://{settings.HOST}:{settings.PORT}
    API Docs: http://{settings.HOST}:{settings.PORT}/docs
    Debug Mode: {settings.DEBUG}
    ============================================================
    """)
    
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,  # Auto-reload on code changes
        log_level="info"
    )
