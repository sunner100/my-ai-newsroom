# Windows 환경 설정 스크립트
# 이 스크립트는 Python 경로를 찾아서 패키지를 설치합니다.

Write-Host "🔍 Python 경로 찾는 중..." -ForegroundColor Cyan

# Python 경로 찾기
$pythonPaths = @(
    "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
    "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
    "$env:USERPROFILE\AppData\Local\Microsoft\WindowsApps\python.exe",
    "python.exe",
    "py.exe"
)

$pythonExe = $null
foreach ($path in $pythonPaths) {
    if (Test-Path $path) {
        $pythonExe = $path
        Write-Host "✅ Python 발견: $path" -ForegroundColor Green
        break
    }
}

if (-not $pythonExe) {
    Write-Host "❌ Python을 찾을 수 없습니다." -ForegroundColor Red
    Write-Host "Python을 설치하거나 PATH에 추가해주세요." -ForegroundColor Yellow
    exit 1
}

# Python 버전 확인
Write-Host "`n📦 Python 버전 확인 중..." -ForegroundColor Cyan
& $pythonExe --version

# pip 업그레이드
Write-Host "`n⬆️ pip 업그레이드 중..." -ForegroundColor Cyan
& $pythonExe -m pip install --upgrade pip

# 패키지 설치
Write-Host "`n📥 필요한 패키지 설치 중..." -ForegroundColor Cyan
& $pythonExe -m pip install -r requirements.txt

Write-Host "`n✅ 설치 완료!" -ForegroundColor Green
Write-Host "`n앱을 실행하려면 다음 명령어를 사용하세요:" -ForegroundColor Yellow
Write-Host "& `"$pythonExe`" -m streamlit run app.py" -ForegroundColor White


