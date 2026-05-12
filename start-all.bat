@echo off
echo ==========================================
echo  松材线虫病CT图像检测系统 - 一键启动
echo ==========================================

echo [1/3] 启动 AI 推理服务...
start "AI-Service" cmd /k "cd /d %~dp0ai-model && python scripts/inference_server.py"
timeout /t 3 /nobreak >nul

echo [2/3] 启动 SpringBoot 后端...
start "Backend" cmd /k "cd /d %~dp0backend && mvn spring-boot:run"
timeout /t 5 /nobreak >nul

echo [3/3] 启动 Vue3 前端...
start "Frontend" cmd /k "cd /d %~dp0frontend && npm install && npm run dev"

echo.
echo ==========================================
echo  启动完成！
echo  前端地址：http://localhost:3000
echo  后端地址：http://localhost:8080
echo  AI服务：  http://localhost:5001
echo ==========================================
pause
