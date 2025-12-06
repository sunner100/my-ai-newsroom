# 🪟 Cursor에서 Windows 환경 설정 가이드

Python이 설치되어 있지만 PATH에 등록되지 않은 경우를 위한 가이드입니다.

## ✅ 현재 상태

- Python 3.12.9 설치 확인됨
- 위치: `C:\Users\Sunno\AppData\Local\Programs\Python\Python312\`
- 필요한 패키지 설치 완료

## 🚀 앱 실행 방법

### 방법 1: PowerShell 스크립트 사용 (추천)

```powershell
.\run_app.ps1
```

### 방법 2: 직접 명령어 실행

```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m streamlit run app.py
```

### 방법 3: PATH에 Python 추가 (영구적 해결)

1. **시스템 환경 변수 설정**
   - Windows 검색에서 "환경 변수" 검색
   - "시스템 환경 변수 편집" 선택
   - "환경 변수" 버튼 클릭
   - "시스템 변수"에서 `Path` 선택 → "편집"
   - "새로 만들기" 클릭
   - 다음 경로 추가:
     ```
     C:\Users\Sunno\AppData\Local\Programs\Python\Python312
     C:\Users\Sunno\AppData\Local\Programs\Python\Python312\Scripts
     ```
   - "확인" 클릭
   - **PowerShell 재시작** (중요!)

2. **재시작 후 확인**
   ```powershell
   python --version
   streamlit --version
   ```

## 📝 유용한 명령어

### 패키지 설치
```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m pip install <패키지명>
```

### 패키지 목록 확인
```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m pip list
```

### Streamlit 실행
```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m streamlit run app.py
```

## 🔧 문제 해결

### "실행 정책" 오류
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Python을 찾을 수 없음
- 위의 "방법 3"을 따라 PATH에 추가하세요
- 또는 전체 경로를 사용하세요

### 패키지 설치 오류
```powershell
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m pip install --upgrade pip
& "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m pip install -r requirements.txt
```


