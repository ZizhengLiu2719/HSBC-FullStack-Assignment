# -*- coding: utf-8 -*-
from app.core.config import settings
import sys
import os

#UTF-8
if os.name == 'nt':  # Windows
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

def test_config():
    print("=" * 60)
    print("Testing Configuration Loading")
    print("=" * 60)
    
    try:
        # Test configuration loading
        print(f"[OK] App Name: {settings.APP_NAME}")
        print(f"[OK] Database URL: {settings.DATABASE_URL}")
        print(f"[OK] Server: {settings.HOST}:{settings.PORT}")
        print(f"[OK] Debug Mode: {settings.DEBUG}")
        print(f"[OK] Allowed Origins: {settings.allowed_origins_list}")
        print(f"[OK] Payment Success Rate: {settings.PAYMENT_SUCCESS_RATE}")
        
        print("=" * 60)
        
        # Check Pydantic version
        import pydantic
        print(f"[OK] Pydantic Version: {pydantic.VERSION}")
        
        # Check FastAPI version
        import fastapi
        print(f"[OK] FastAPI Version: {fastapi.__version__}")
        
        # Check SQLAlchemy version
        import sqlalchemy
        print(f"[OK] SQLAlchemy Version: {sqlalchemy.__version__}")
        
        print("=" * 60)
        print("[SUCCESS] All packages installed successfully!")
        print("[SUCCESS] Configuration loaded successfully!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print("=" * 60)
        print(f"[ERROR] Error: {e}")
        print("=" * 60)
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)