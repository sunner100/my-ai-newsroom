# 🔑 API 키 설정 가이드

이 문서는 AI IT 뉴스룸 앱에 필요한 API 키를 설정하는 방법을 안내합니다.

## 📋 필요한 API 키 목록

1. **Google Gemini API Key** - AI 뉴스 분석용
2. **GitHub Personal Access Token** - 데이터 저장용
3. **비밀번호** - 앱 접근 인증용

---

## 1️⃣ Google Gemini API Key 발급

### 단계별 가이드

1. **Google AI Studio 접속**
   - 브라우저에서 [https://makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey) 접속
   - 또는 [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) 접속

2. **Google 계정으로 로그인**
   - Google 계정이 필요합니다

3. **API 키 생성**
   - "Create API Key" 또는 "API 키 만들기" 버튼 클릭
   - 프로젝트 선택 (새 프로젝트 생성 가능)
   - API 키가 생성되면 복사 (한 번만 표시되므로 안전하게 보관)

4. **API 키 형식**
   - `AIzaSy...` 형태의 긴 문자열입니다

### 💡 참고사항
- 무료 할당량이 제공됩니다 (일일 요청 제한 있음)
- API 키는 절대 공개하지 마세요!

---

## 2️⃣ GitHub Personal Access Token 발급

### 단계별 가이드

1. **GitHub 로그인**
   - [https://github.com](https://github.com)에 로그인

2. **Settings 접속**
   - 우측 상단 프로필 아이콘 클릭 → **Settings**

3. **Developer settings 이동**
   - 왼쪽 메뉴 맨 아래 **Developer settings** 클릭

4. **Personal access tokens 생성**
   - **Personal access tokens** → **Tokens (classic)** 클릭
   - **Generate new token** → **Generate new token (classic)** 클릭

5. **토큰 설정**
   - **Note**: 토큰 설명 입력 (예: "AI Newsroom App")
   - **Expiration**: 만료 기간 선택 (90 days, 1 year 등)
   - **Scopes**: **`repo`** 체크박스 선택 (전체 repo 권한)
     - 이 권한이 있어야 파일을 읽고 쓸 수 있습니다

6. **토큰 생성**
   - 맨 아래 **Generate token** 버튼 클릭
   - 생성된 토큰을 복사 (한 번만 표시되므로 안전하게 보관)
   - 형식: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

### 💡 참고사항
- `repo` 권한은 모든 리포지토리에 대한 전체 접근 권한입니다
- 토큰을 잃어버리면 재생성해야 합니다
- 토큰은 절대 공개하지 마세요!

---

## 3️⃣ GitHub 리포지토리 준비

1. **리포지토리 생성**
   - GitHub에서 새 리포지토리 생성 (예: `my-ai-newsroom`)
   - Public 또는 Private 모두 가능

2. **리포지토리 이름 확인**
   - 형식: `username/repository-name`
   - 예: `sunno/my-ai-newsroom`

---

## 4️⃣ secrets.toml 파일 설정

1. **파일 위치**
   - `.streamlit/secrets.toml` 파일을 엽니다

2. **내용 수정**
   ```toml
   [general]
   repo_name = "your_username/my-ai-newsroom"  # 실제 리포지토리 이름으로 변경
   password = "your_password_here"              # 원하는 비밀번호로 변경

   [api]
   github_token = "ghp_xxxxxxxxxxxx"           # 발급받은 GitHub 토큰으로 변경
   gemini_key = "AIzaSyxxxxxxxxxx"             # 발급받은 Gemini API 키로 변경
   ```

3. **예시**
   ```toml
   [general]
   repo_name = "sunno/my-ai-newsroom"
   password = "MySecurePassword123!"

   [api]
   github_token = "ghp_AbCdEf1234567890GhIjKlMnOpQrStUvWxYz"
   gemini_key = "AIzaSyAbCdEf1234567890GhIjKlMnOpQrStUvWxYz"
   ```

---

## 5️⃣ 설정 확인

1. **파일 저장**
   - `secrets.toml` 파일을 저장합니다

2. **앱 실행 테스트**
   ```powershell
   streamlit run app.py
   ```

3. **에러 확인**
   - 만약 "설정 오류" 메시지가 나오면 `secrets.toml` 파일을 다시 확인하세요
   - 모든 값이 올바르게 입력되었는지 확인하세요

---

## ⚠️ 보안 주의사항

1. **`.gitignore` 확인**
   - `secrets.toml` 파일이 Git에 커밋되지 않도록 `.gitignore`에 포함되어 있습니다
   - 절대 GitHub에 API 키를 올리지 마세요!

2. **파일 권한**
   - `secrets.toml` 파일은 본인만 읽을 수 있도록 설정하세요

3. **토큰 관리**
   - API 키나 토큰을 잃어버리면 재발급 받아야 합니다
   - 필요시 토큰을 삭제하고 새로 생성할 수 있습니다

---

## 🆘 문제 해결

### "설정 오류" 메시지가 나올 때
- `secrets.toml` 파일이 `.streamlit/` 폴더에 있는지 확인
- 모든 필드가 올바르게 입력되었는지 확인
- 따옴표 없이 값만 입력했는지 확인

### GitHub 연결 실패
- GitHub 토큰이 올바른지 확인
- 토큰에 `repo` 권한이 있는지 확인
- 리포지토리 이름 형식이 `username/repo-name`인지 확인

### Gemini API 오류
- API 키가 올바른지 확인
- Google AI Studio에서 API 사용량 확인
- 무료 할당량을 초과했는지 확인

---

## 📚 추가 리소스

- [Google Gemini API 문서](https://ai.google.dev/docs)
- [GitHub Personal Access Tokens 가이드](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
- [Streamlit Secrets 관리](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)

