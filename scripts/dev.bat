@echo off
echo Starting Agent Dashboard in development mode...

cd /d "%~dp0.."

REM 启动后端
echo [1/2] Starting backend server...
start "Backend" cmd /k "cd backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && python app\main.py"

REM 等待后端启动
timeout /t 3 /nobreak >nul

REM 启动前端
echo [2/2] Starting frontend dev server...
start "Frontend" cmd /k "cd frontend && npm install && npm run dev"

echo.
echo Both servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit this window
pause >nul
