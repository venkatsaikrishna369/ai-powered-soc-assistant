@echo off
echo Starting Network Security Intelligence Dashboard...
echo.

echo Checking dependencies...
pip install -r requirements.txt

echo.
echo Starting server...
python backend/main.py

pause