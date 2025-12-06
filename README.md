# 📰 AI IT 뉴스룸

Streamlit과 Google Gemini AI를 활용한 개인용 IT 뉴스 수집 및 분석 시스템입니다.

## 🚀 주요 기능

- **RSS 피드 수집**: 여러 RSS 피드에서 최신 IT 뉴스 자동 수집
- **AI 분석**: Google Gemini AI를 활용한 뉴스 요약 및 키워드 추출
- **GitHub 기반 저장**: Streamlit Cloud에서도 데이터가 유지되도록 GitHub에 JSON 파일로 저장
- **비밀번호 인증**: 테스트 환경용 접근 제어
- **날짜별 뉴스 조회**: 수집된 뉴스를 날짜별로 조회 가능

## 📋 필수 요구사항

1. **Google Gemini API Key**: [Google AI Studio](https://makersuite.google.com/app/apikey)에서 발급
2. **GitHub Personal Access Token**: `repo` 권한이 있는 토큰 필요
3. **GitHub 리포지토리**: 데이터 저장용 리포지토리 생성

## 🛠️ 설치 방법

1. 리포지토리 클론
```powershell
git clone <your-repo-url>
cd my-ai-newsroom
```

2. 가상환경 생성 및 활성화
```powershell
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows PowerShell)
venv\Scripts\Activate.ps1

# 만약 실행 정책 오류가 나면:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Mac/Linux 사용자:**
```bash
python -m venv venv
source venv/bin/activate
```

3. 패키지 설치
```powershell
pip install -r requirements.txt
```

4. 설정 파일 생성
```powershell
# .streamlit/secrets.toml 파일을 생성하고 아래 내용 입력
Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
# 또는
cp .streamlit\secrets.toml.example .streamlit\secrets.toml
```

`.streamlit/secrets.toml` 파일 내용:
```toml
[general]
repo_name = "your_username/my-ai-newsroom"
password = "your_password_here"

[api]
github_token = "ghp_xxxxxxxxxxxx"
gemini_key = "AIzaSyxxxxxxxxxx"
```

## 🎯 사용 방법

1. 앱 실행
```powershell
streamlit run app.py
```

2. 비밀번호 입력 후 로그인

3. **뉴스룸**: 날짜를 선택하여 수집된 뉴스 조회

4. **대시보드**: 
   - RSS 피드 추가/삭제
   - 뉴스 수집 및 AI 분석 실행
   - 통계 확인

## 📁 프로젝트 구조

```
my-ai-newsroom/
├── app.py                # 메인 실행 파일
├── requirements.txt      # 라이브러리 목록
├── utils_github.py       # GitHub 파일 입출력 처리
├── utils_ai.py           # RSS 파싱 및 Gemini 분석
├── .streamlit/
│   └── secrets.toml      # API 키 저장소 (로컬 테스트용)
└── README.md
```

## ☁️ Streamlit Cloud 배포

1. GitHub에 코드 Push
2. [Streamlit Cloud](https://streamlit.io/cloud)에 접속하여 리포지토리 배포
3. **Advanced Settings** → **Secrets**에 `secrets.toml` 내용 복사
4. 배포 완료!

## ⚠️ 주의사항

- `secrets.toml` 파일은 절대 Git에 커밋하지 마세요 (`.gitignore`에 포함됨)
- GitHub API rate limit에 주의하세요
- Gemini API 사용량에 따라 비용이 발생할 수 있습니다

## 📝 라이선스

MIT License

