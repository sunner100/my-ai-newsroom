# 앱 실행 스크립트
# 이 스크립트는 Python을 찾아서 Streamlit 앱을 실행합니다.

$pythonExe = "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe"

if (Test-Path $pythonExe) {
    Write-Host "🚀 앱 실행 중..." -ForegroundColor Green
    & $pythonExe -m streamlit run app.py
} else {
    Write-Host "❌ Python을 찾을 수 없습니다." -ForegroundColor Red
    Write-Host "setup_windows.ps1를 먼저 실행해주세요." -ForegroundColor Yellow
}


