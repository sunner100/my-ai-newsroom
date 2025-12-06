멋진 아이디어입니다! **"Cursor AI"**를 활용해 개발하신다면, 명확한 구조와 프롬프트가 중요합니다. 특히 Streamlit Cloud는 서버가 재시작되면 로컬 파일이 초기화되는 특성이 있어, **GitHub API(PyGithub)를 통해 원격 리포지토리에 JSON 파일을 직접 커밋(저장)하고 불러오는 로직**이 핵심입니다.

다음은 Cursor AI에게 단계별로 요청하여 이 프로젝트를 완성할 수 있는 **설계도와 핵심 코드 가이드**입니다.

---

### 1. 프로젝트 구조 및 준비물

먼저 GitHub 리포지토리를 하나 생성(예: `my-ai-newsroom`)하고, Streamlit Cloud와 연동할 준비를 합니다.

**필수 API 키 및 설정:**
1.  **Google Gemini API Key:** AI 분석용
2.  **GitHub Personal Access Token (Classic):** `repo` 권한 필수 (파일 쓰기 권한)
3.  **비밀번호:** 앱 접근 인증용 (테스트 환경용)

**프로젝트 폴더 구조:**
```text
my-ai-newsroom/
├── app.py                # 메인 실행 파일
├── requirements.txt      # 라이브러리 목록
├── utils_github.py       # GitHub 파일 입출력 처리
├── utils_ai.py           # RSS 파싱 및 Gemini 분석
└── .streamlit/
    └── secrets.toml      # API 키 저장소 (로컬 테스트용, 배포 시엔 클라우드 설정)
```

---

### 2. Cursor AI 개발 프롬프트 가이드

Cursor AI에게 아래 순서대로 요청하여 코드를 작성하세요.

#### **Step 1: 환경 설정 및 라이브러리 설치 (`requirements.txt`)**

> **Cursor 프롬프트:**
> "파이썬 Streamlit 프로젝트를 시작할 거야. `streamlit`, `google-generativeai`, `feedparser`, `PyGithub`, `pandas` 라이브러리가 필요해. `requirements.txt` 파일을 만들어줘."

#### **Step 2: GitHub 연동 모듈 (`utils_github.py`)**

Streamlit Cloud에서 데이터를 유지하려면 JSON을 GitHub에 직접 쓰고 읽어야 합니다.

> **Cursor 프롬프트:**
> "`utils_github.py` 파일을 만들어줘. `PyGithub` 라이브러리를 사용해서 내 리포지토리의 특정 json 파일을 읽고(read), 내용을 수정해서 커밋(update)하는 클래스를 만들어줘.
> - 입력: Github Token, Repo Name, File Path
> - 기능 1: json 파일 내용을 dict로 가져오기 (파일이 없으면 빈 dict 반환)
> - 기능 2: dict 내용을 json으로 변환해서 해당 파일에 커밋(push)하기
> - Streamlit의 secrets에서 토큰을 가져올 수 있도록 설계해줘."

#### **Step 3: RSS 수집 및 AI 분석 모듈 (`utils_ai.py`)**

> **Cursor 프롬프트:**
> "`utils_ai.py`를 만들어줘.
> 1. `feedparser`로 RSS URL 리스트를 입력받아 최신 뉴스(제목, 링크, 요약)를 긁어오는 함수.
> 2. `google.generativeai`를 사용해 뉴스 내용을 요약하고 분석하는 함수.
>    - 프롬프트 예시: '다음 뉴스들을 IT 전문가 관점에서 3줄 요약하고, 핵심 키워드 3개를 뽑아줘.'
>    - 결과는 JSON 호환 포맷으로 반환해야 해."

#### **Step 4: 메인 UI 및 로직 (`app.py`)**

> **Cursor 프롬프트:**
> "`app.py`를 작성해줘. Streamlit을 사용하고 사이드바 메뉴로 '홈(뉴스룸)'과 '대시보드(관리)'를 만들어줘.
>
> **0. 비밀번호 인증 (최우선):**
> - 앱 시작 시 `st.session_state`에 `authenticated` 키가 없거나 `False`면 비밀번호 입력 화면을 보여줘.
> - `st.secrets["general"]["password"]`에서 비밀번호를 가져와서 사용자가 입력한 비밀번호와 비교해.
> - 비밀번호가 맞으면 `st.session_state['authenticated'] = True`로 설정하고 메인 화면을 보여줘.
> - 비밀번호가 틀리면 에러 메시지를 표시하고 다시 입력받아.
> - 인증된 사용자만 앱의 나머지 기능에 접근할 수 있도록 해줘.
>
> **1. 공통 (인증 후):**
> - 앱 시작 시 `utils_github`를 통해 `stats.json`을 불러와 방문자 수를 1 증가시키고 다시 GitHub에 저장해줘.
>
> **2. 홈 (뉴스룸):**
> - 날짜 선택기(Date Input)를 보여줘.
> - 선택한 날짜에 해당하는 뉴스 데이터(`news_data.json`에서 조회)가 있으면 화면에 카드 형태로 보여줘. (Gemini가 요약한 내용 포함)
>
> **3. 대시보드 (관리):**
> - **RSS 관리:** `feeds.json`을 불러와서 현재 등록된 RSS URL을 리스트로 보여주고, 추가/삭제할 수 있게 해줘. 변경 시 GitHub에 바로 저장.
> - **뉴스 수집 및 분석:** '뉴스 업데이트' 버튼을 누르면 등록된 RSS를 긁어오고 Gemini로 분석한 뒤, 오늘 날짜를 키(key)로 `news_data.json`에 저장해줘. (진행률 표시바 포함)
> - **통계:** 현재 총 방문자 수를 보여줘."

---

### 3. 핵심 코드 예시 (참고용)

Cursor가 생성할 코드의 방향성을 잡아드리기 위해 핵심 로직을 작성해 드립니다.

**`secrets.toml` (로컬 테스트용)**
```toml
[general]
repo_name = "your_username/my-ai-newsroom"
password = "your_password_here"

[api]
github_token = "ghp_xxxxxxxxxxxx"
gemini_key = "AIzaSyxxxxxxxxxx"
```

**`utils_github.py` (핵심 로직)**
```python
import json
from github import Github
import streamlit as st

class GithubDataHandler:
    def __init__(self, token, repo_name):
        self.g = Github(token)
        self.repo = self.g.get_repo(repo_name)

    def load_json(self, file_path):
        try:
            contents = self.repo.get_contents(file_path)
            return json.loads(contents.decoded_content.decode())
        except:
            return {} # 파일이 없으면 빈 딕셔너리

    def save_json(self, file_path, data, message="Update data"):
        try:
            content = json.dumps(data, indent=4, ensure_ascii=False)
            try:
                # 파일이 존재하면 업데이트
                file = self.repo.get_contents(file_path)
                self.repo.update_file(file.path, message, content, file.sha)
            except:
                # 파일이 없으면 생성
                self.repo.create_file(file_path, message, content)
            return True
        except Exception as e:
            st.error(f"GitHub Save Error: {e}")
            return False
```

**`app.py` (구조)**
```python
import streamlit as st
import datetime
from utils_github import GithubDataHandler
from utils_ai import fetch_and_analyze_news # 가정

# 설정 로드
GITHUB_TOKEN = st.secrets["api"]["github_token"]
REPO_NAME = st.secrets["general"]["repo_name"]
GEMINI_KEY = st.secrets["api"]["gemini_key"]
APP_PASSWORD = st.secrets["general"]["password"]

# 비밀번호 인증 체크
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# 인증되지 않은 경우 비밀번호 입력 화면
if not st.session_state['authenticated']:
    st.title("🔐 접근 인증")
    st.info("이 앱에 접근하려면 비밀번호를 입력해주세요.")
    
    password_input = st.text_input("비밀번호", type="password", key="password_input")
    
    if st.button("로그인"):
        if password_input == APP_PASSWORD:
            st.session_state['authenticated'] = True
            st.rerun()
        else:
            st.error("❌ 비밀번호가 올바르지 않습니다.")
    st.stop()

# 인증된 사용자만 아래 코드 실행
db = GithubDataHandler(GITHUB_TOKEN, REPO_NAME)

# 방문자 통계 업데이트 (주의: 잦은 커밋 방지를 위해 세션 활용 권장하지만, 요구사항대로 구현)
if 'visited' not in st.session_state:
    stats = db.load_json("data/stats.json")
    stats['visits'] = stats.get('visits', 0) + 1
    db.save_json("data/stats.json", stats, "Increment visitor count")
    st.session_state['visited'] = True

st.title("📰 나만의 AI IT 뉴스룸")

# 로그아웃 버튼 (선택사항)
if st.sidebar.button("🚪 로그아웃"):
    st.session_state['authenticated'] = False
    st.session_state['visited'] = False
    st.rerun()

menu = st.sidebar.selectbox("메뉴", ["뉴스룸", "대시보드"])

if menu == "뉴스룸":
    selected_date = st.date_input("날짜 선택", datetime.date.today())
    date_str = selected_date.strftime("%Y-%m-%d")
    
    news_data = db.load_json("data/news_data.json")
    
    if date_str in news_data:
        daily_news = news_data[date_str]
        st.header(f"{date_str} 주요 브리핑")
        st.write(daily_news['summary']) # Gemini의 전체 요약
        
        st.divider()
        for news in daily_news['articles']:
            with st.expander(f"{news['title']}"):
                st.write(news['ai_analysis'])
                st.link_button("원문 보기", news['link'])
    else:
        st.info("해당 날짜의 뉴스 데이터가 없습니다. 대시보드에서 수집해주세요.")

elif menu == "대시보드":
    st.header("⚙️ 관리 대시보드")
    
    # 통계 표시
    stats = db.load_json("data/stats.json")
    st.metric("총 방문자 수", stats.get('visits', 0))
    
    # RSS 관리
    st.subheader("RSS 피드 관리")
    feeds = db.load_json("data/feeds.json")
    current_feeds = feeds.get("urls", [])
    
    new_feed = st.text_input("RSS URL 추가")
    if st.button("추가"):
        if new_feed and new_feed not in current_feeds:
            current_feeds.append(new_feed)
            db.save_json("data/feeds.json", {"urls": current_feeds}, "Add RSS feed")
            st.rerun()
            
    # 삭제 UI 구현 필요 (st.multiselect 등 활용)
    
    # 뉴스 수집 트리거
    st.subheader("뉴스 수집 및 분석")
    if st.button("지금 수집 및 분석 시작"):
        with st.spinner("AI가 뉴스를 분석 중입니다..."):
            # 1. RSS 크롤링
            # 2. Gemini 분석
            # 3. news_data.json에 오늘 날짜 Key로 저장
            # result = fetch_and_analyze_news(current_feeds, GEMINI_KEY)
            # news_data = db.load_json("data/news_data.json")
            # news_data[datetime.date.today().strftime("%Y-%m-%d")] = result
            # db.save_json("data/news_data.json", news_data, "Update daily news")
            st.success("완료!")
```

---

### 4. 배포 시 주의사항 (Streamlit Cloud)

1.  GitHub에 코드를 Push 합니다.
2.  Streamlit Cloud에 접속하여 해당 리포지토리를 배포합니다.
3.  **Advanced Settings**에서 `Secrets` 부분에 `secrets.toml` 내용을 복사해 넣어야 합니다. (이게 없으면 API 호출 및 파일 저장이 안 됩니다).
4.  **비밀번호 설정:** `secrets.toml`의 `[general]` 섹션에 `password` 값을 반드시 설정해주세요. 이 비밀번호로 앱 접근이 제한됩니다.

이 가이드를 바탕으로 Cursor AI와 대화하며 코드를 완성해 보세요! 특히 **"GitHub에 JSON 파일로 상태를 저장한다"**는 컨셉만 명확히 하면 데이터베이스 없이도 훌륭한 개인용 CMS를 만들 수 있습니다.