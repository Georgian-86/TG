from app.config import settings
import os

print(f"GOOGLE_CLIENT_ID from settings: '{settings.GOOGLE_CLIENT_ID}'")
print(f"GOOGLE_CLIENT_SECRET from settings: '{settings.GOOGLE_CLIENT_SECRET}'")

if settings.GOOGLE_CLIENT_ID == "":
    print("❌ CREDENTIALS ARE EMPTY in settings")
else:
    print("✅ CREDENTIALS FOUND in settings")

# Check if .env file exists where we think it does
from pathlib import Path
env_path = Path(__file__).parent / ".env"
print(f"Checking for .env at: {env_path.resolve()}")
print(f"File exists: {env_path.exists()}")
