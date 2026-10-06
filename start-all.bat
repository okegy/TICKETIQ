@echo off
REM TicketIQ — One-click startup for all services (Windows)
REM Run this from the ticketiq\ root directory

echo.
echo ==========================================================
echo   TicketIQ AI Operations Copilot — Startup Script
echo ==========================================================
echo.

REM 1. Start AI Service (Python FastAPI on port 8000)
echo [1/3] Starting AI Service (Python FastAPI - port 8000)...
start "TicketIQ-AI" cmd /k "cd ai-service && .venv\Scripts\activate && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 /nobreak > nul

REM 2. Start Spring Boot Backend (port 8080)
echo [2/3] Starting Spring Boot Backend (port 8080)...
start "TicketIQ-Backend" cmd /k "cd backend && gradlew.bat bootRun"
timeout /t 5 /nobreak > nul

REM 3. Start Angular Frontend (port 4200)
echo [3/3] Starting Angular Frontend (port 4200)...
start "TicketIQ-Frontend" cmd /k "cd frontend && npm run start"

echo.
echo [OK] All services started in separate windows.
echo.
echo URLs:
echo   Frontend:    http://localhost:4200
echo   AI Service:  http://localhost:8000/docs
echo   Backend API: http://localhost:8080/swagger-ui.html
echo.
echo Press any key to exit this launcher...
pause > nul
