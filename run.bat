@echo off
echo ===================================================
echo Starting SnapDiet...
echo ===================================================

echo [1/2] Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo.
echo [2/2] Launching the Streamlit application...
python -m streamlit run app.py

pause
