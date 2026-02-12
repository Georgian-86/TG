@echo off
echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install -r backend\requirements.txt

echo Starting backend server...
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
