@echo off
chcp 65001
echo ========================================
echo Testing Gemini API Service
echo ========================================
echo.

echo Testing API endpoint: http://localhost:8000/api/generate-options
echo.

REM 测试API是否响应
curl -X POST "http://localhost:8000/api/generate-options" ^
  -H "Content-Type: application/json" ^
  -d "{\"mode\": \"focus\", \"input\": \"Steady rain on a windowpane\", \"stage\": \"elements\"}"

echo.
echo ========================================
echo Test completed!
echo ========================================
echo.
pause 