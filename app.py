import streamlit as st
import datetime
from utils_github import GithubDataHandler
from utils_ai import fetch_and_analyze_news

# 페이지 설정
st.set_page_config(
    page_title="AI IT 뉴스룸",
    page_icon="📰",
    layout="wide"
)

# 설정 로드
try:
    GITHUB_TOKEN = st.secrets["api"]["github_token"]
    REPO_NAME = st.secrets["general"]["repo_name"]
    GEMINI_KEY = st.secrets["api"]["gemini_key"]
    APP_PASSWORD = st.secrets["general"]["password"]
except KeyError as e:
    st.error(f"설정 오류: {e} 키가 secrets에 없습니다. secrets.toml 파일을 확인해주세요.")
    st.stop()

# 비밀번호 인증 체크
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

# 인증되지 않은 경우 비밀번호 입력 화면
if not st.session_state['authenticated']:
    st.title("🔐 접근 인증")
    st.info("이 앱에 접근하려면 비밀번호를 입력해주세요.")
    
    password_input = st.text_input("비밀번호", type="password", key="password_input")
    
    if st.button("로그인", type="primary"):
        if password_input == APP_PASSWORD:
            st.session_state['authenticated'] = True
            st.rerun()
        else:
            st.error("❌ 비밀번호가 올바르지 않습니다.")
    st.stop()

# 인증된 사용자만 아래 코드 실행
try:
    db = GithubDataHandler(GITHUB_TOKEN, REPO_NAME)
except Exception as e:
    st.error(f"GitHub 연결 실패: {e}")
    st.stop()

# 방문자 통계 업데이트 (세션당 한 번만)
if 'visited' not in st.session_state:
    try:
        stats = db.load_json("data/stats.json")
        stats['visits'] = stats.get('visits', 0) + 1
        db.save_json("data/stats.json", stats, "Increment visitor count")
        st.session_state['visited'] = True
    except Exception as e:
        st.warning(f"통계 업데이트 실패: {e}")

st.title("📰 나만의 AI IT 뉴스룸")

# 로그아웃 버튼
if st.sidebar.button("🚪 로그아웃"):
    st.session_state['authenticated'] = False
    st.session_state['visited'] = False
    st.rerun()

menu = st.sidebar.selectbox("메뉴", ["뉴스룸", "대시보드"])

if menu == "뉴스룸":
    st.header("📰 뉴스룸")
    
    selected_date = st.date_input("날짜 선택", datetime.date.today())
    date_str = selected_date.strftime("%Y-%m-%d")
    
    try:
        news_data = db.load_json("data/news_data.json")
        
        if date_str in news_data:
            daily_news = news_data[date_str]
            
            # 디버깅: image_path 확인
            if 'image_path' in daily_news:
                st.info(f"🔍 디버깅: image_path = {daily_news['image_path']}")
            
            # 인포그래픽 표시 (있는 경우)
            if 'image_path' in daily_news and daily_news['image_path']:
                try:
                    # GitHub에서 직접 이미지 가져오기
                    image_bytes = db.load_image(daily_news['image_path'])
                    if image_bytes:
                        from PIL import Image
                        import io
                        image = Image.open(io.BytesIO(image_bytes))
                        st.image(image, use_container_width=True, caption=f"📊 {date_str} 인포그래픽")
                        st.divider()
                    else:
                        # Fallback: GitHub Raw URL 시도
                        try:
                            image_url = f"https://raw.githubusercontent.com/{REPO_NAME}/main/{daily_news['image_path']}"
                            st.info(f"🔍 Raw URL 시도: {image_url}")
                            st.image(image_url, use_container_width=True, caption=f"📊 {date_str} 인포그래픽")
                            st.divider()
                        except Exception as url_error:
                            st.warning(f"⚠️ 인포그래픽을 불러올 수 없습니다.")
                            with st.expander("🔍 디버깅 정보"):
                                st.write(f"이미지 경로: {daily_news['image_path']}")
                                st.write(f"Raw URL: https://raw.githubusercontent.com/{REPO_NAME}/main/{daily_news['image_path']}")
                                st.write(f"오류: {str(url_error)}")
                except Exception as e:
                    st.warning(f"인포그래픽 로드 실패: {e}")
                    # 디버깅 정보 표시
                    with st.expander("🔍 디버깅 정보"):
                        st.write(f"이미지 경로: {daily_news.get('image_path', '없음')}")
                        st.write(f"오류: {str(e)}")
                        import traceback
                        st.code(traceback.format_exc())
            
            # 전체 요약 표시
            st.header(f"📅 {date_str} 주요 브리핑")
            
            if 'summary' in daily_news:
                st.markdown(f"**전체 요약:**\n\n{daily_news['summary']}")
            
            if 'keywords' in daily_news and daily_news['keywords']:
                keywords = ", ".join([f"`{kw}`" for kw in daily_news['keywords']])
                st.markdown(f"**핵심 키워드:** {keywords}")
            
            if 'trends' in daily_news and daily_news['trends']:
                st.info(f"**주요 트렌드:** {daily_news['trends']}")
            
            st.divider()
            
            # 개별 뉴스 카드
            st.subheader("📰 상세 뉴스")
            if 'articles' in daily_news and daily_news['articles']:
                for idx, news in enumerate(daily_news['articles'], 1):
                    with st.expander(f"📌 {idx}. {news.get('title', '제목 없음')}"):
                        if 'ai_analysis' in news:
                            st.markdown(f"**AI 분석:**\n\n{news['ai_analysis']}")
                        elif 'summary' in news:
                            st.markdown(f"**요약:**\n\n{news['summary']}")
                        
                        if 'link' in news and news['link']:
                            st.link_button("🔗 원문 보기", news['link'])
                        
                        if 'published' in news and news['published']:
                            st.caption(f"발행일: {news['published']}")
            else:
                st.info("해당 날짜의 뉴스 기사가 없습니다.")
        else:
            st.info(f"📭 {date_str} 날짜의 뉴스 데이터가 없습니다. 대시보드에서 뉴스를 수집해주세요.")
    except Exception as e:
        st.error(f"뉴스 데이터 로드 오류: {e}")

elif menu == "대시보드":
    st.header("⚙️ 관리 대시보드")
    
    # 통계 표시
    st.subheader("📊 통계")
    try:
        stats = db.load_json("data/stats.json")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("총 방문자 수", stats.get('visits', 0))
        with col2:
            news_data = db.load_json("data/news_data.json")
            total_news_days = len(news_data)
            st.metric("수집된 뉴스 일수", total_news_days)
    except Exception as e:
        st.warning(f"통계 로드 오류: {e}")
    
    st.divider()
    
    # RSS 관리
    st.subheader("🔗 RSS 피드 관리")
    try:
        feeds = db.load_json("data/feeds.json")
        current_feeds = feeds.get("urls", [])
        
        # 현재 RSS 목록 표시
        if current_feeds:
            st.write("**현재 등록된 RSS 피드:**")
            for idx, feed_url in enumerate(current_feeds, 1):
                st.write(f"{idx}. {feed_url}")
            
            st.divider()
            
            # RSS 삭제
            st.write("**RSS 피드 삭제:**")
            if len(current_feeds) > 0:
                selected_feeds = st.multiselect(
                    "삭제할 RSS 피드를 선택하세요",
                    options=current_feeds,
                    key="delete_feeds"
                )
                if st.button("선택한 RSS 삭제", type="secondary"):
                    if selected_feeds:
                        updated_feeds = [f for f in current_feeds if f not in selected_feeds]
                        if db.save_json("data/feeds.json", {"urls": updated_feeds}, "Delete RSS feeds"):
                            st.success(f"{len(selected_feeds)}개의 RSS 피드가 삭제되었습니다.")
                            st.rerun()
                    else:
                        st.warning("삭제할 RSS 피드를 선택해주세요.")
        else:
            st.info("등록된 RSS 피드가 없습니다. 아래에서 추가해주세요.")
        
        st.divider()
        
        # RSS 추가
        st.write("**새 RSS 피드 추가:**")
        new_feed = st.text_input("RSS URL", placeholder="https://example.com/rss", key="new_feed_input")
        
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("추가", type="primary"):
                if new_feed:
                    if new_feed not in current_feeds:
                        current_feeds.append(new_feed)
                        if db.save_json("data/feeds.json", {"urls": current_feeds}, "Add RSS feed"):
                            st.success(f"RSS 피드가 추가되었습니다: {new_feed}")
                            st.rerun()
                        else:
                            st.error("RSS 피드 추가에 실패했습니다.")
                    else:
                        st.warning("이미 등록된 RSS 피드입니다.")
                else:
                    st.warning("RSS URL을 입력해주세요.")
    except Exception as e:
        st.error(f"RSS 관리 오류: {e}")
    
    st.divider()
    
    # 뉴스 수집 및 분석
    st.subheader("🤖 뉴스 수집 및 분석")
    
    try:
        feeds = db.load_json("data/feeds.json")
        current_feeds = feeds.get("urls", [])
        
        if not current_feeds:
            st.warning("⚠️ 먼저 RSS 피드를 추가해주세요.")
        else:
            st.write(f"**등록된 RSS 피드 {len(current_feeds)}개에서 뉴스를 수집합니다.**")
            
            if st.button("🚀 지금 수집 및 분석 시작", type="primary"):
                if not GEMINI_KEY:
                    st.error("Gemini API 키가 설정되지 않았습니다.")
                else:
                    # 진행 상황 표시 영역
                    progress_container = st.container()
                    with progress_container:
                        st.markdown("### 📊 진행 상황")
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        detail_text = st.empty()
                        time_text = st.empty()
                    
                    import time
                    start_time = time.time()
                    
                    try:
                        # 1. RSS 크롤링
                        status_text.markdown("**1단계: 📡 RSS 피드에서 뉴스 수집 중...**")
                        detail_text.info(f"RSS 피드 {len(current_feeds)}개를 확인하고 있습니다...")
                        progress_bar.progress(10)
                        time_text.text(f"경과 시간: {int(time.time() - start_time)}초")
                        
                        # RSS 수집 (실제로는 fetch_and_analyze_news 내부에서 처리되지만, 
                        # 진행 상황을 보여주기 위해 분리)
                        from utils_ai import fetch_rss_news
                        news_list = fetch_rss_news(current_feeds)
                        progress_bar.progress(30)
                        detail_text.success(f"✅ {len(news_list)}개의 뉴스를 수집했습니다!")
                        time_text.text(f"경과 시간: {int(time.time() - start_time)}초")
                        
                        if not news_list:
                            st.warning("수집된 뉴스가 없습니다. RSS URL을 확인해주세요.")
                        else:
                            # 2. Gemini 분석
                            status_text.markdown("**2단계: 🤖 AI가 뉴스를 분석하는 중...**")
                            detail_text.info(f"뉴스 {len(news_list)}개를 분석하고 있습니다. 시간이 걸릴 수 있습니다...")
                            progress_bar.progress(40)
                            time_text.text(f"경과 시간: {int(time.time() - start_time)}초")
                            
                            # 분석 진행 상황을 보여주기 위해 스피너 추가
                            analysis_spinner = st.spinner("AI 분석 중...")
                            with analysis_spinner:
                                from utils_ai import analyze_news_with_gemini
                                result = analyze_news_with_gemini(news_list, GEMINI_KEY)
                            
                            progress_bar.progress(60)
                            detail_text.success(f"✅ AI 분석 완료! (경과 시간: {int(time.time() - start_time)}초)")
                            time_text.text(f"경과 시간: {int(time.time() - start_time)}초")
                            
                            # 3. 인포그래픽 생성 (선택적)
                            image_path = None
                            if result.get('summary'):
                                status_text.markdown("**3단계: 🎨 인포그래픽 생성 중...**")
                                detail_text.info("AI가 인포그래픽을 생성하고 있습니다...")
                                progress_bar.progress(70)
                                
                                try:
                                    from utils_ai import generate_infographic
                                    # 키워드도 함께 전달 (대체 방법에서 사용)
                                    keywords = result.get('keywords', [])
                                    # Imagen API 키 가져오기 (선택적)
                                    IMAGEN_KEY = st.secrets.get("api", {}).get("imagen_key", None)
                                    infographic_image = generate_infographic(
                                        GEMINI_KEY, 
                                        result.get('summary', ''),
                                        IMAGEN_KEY,
                                        keywords
                                    )
                                    
                                    if infographic_image:
                                        today = datetime.date.today()
                                        today_str = today.strftime("%Y-%m-%d")
                                        # 년도/월별 폴더 구조로 저장 (예: images/2025/12/2025-12-06.png)
                                        year = today.strftime("%Y")
                                        month = today.strftime("%m")
                                        image_path = f"images/{year}/{month}/{today_str}.png"
                                        
                                        if db.save_image(image_path, infographic_image, f"Create infographic for {today_str}"):
                                            detail_text.success(f"✅ 인포그래픽 생성 완료!")
                                            result['image_path'] = image_path
                                        else:
                                            detail_text.warning("⚠️ 인포그래픽 저장 실패 (분석은 완료됨)")
                                    else:
                                        detail_text.info("ℹ️ 인포그래픽 생성 건너뜀 (Imagen API 미활성화 또는 오류)")
                                except Exception as e:
                                    detail_text.warning(f"⚠️ 인포그래픽 생성 중 오류: {e} (분석은 완료됨)")
                            
                            # 4. news_data.json에 오늘 날짜 Key로 저장
                            status_text.markdown("**4단계: 💾 데이터를 저장하는 중...**")
                            detail_text.info("GitHub에 데이터를 저장하고 있습니다...")
                            progress_bar.progress(90)
                            
                            news_data = db.load_json("data/news_data.json")
                            today_str = datetime.date.today().strftime("%Y-%m-%d")
                            news_data[today_str] = result
                            
                            if db.save_json("data/news_data.json", news_data, f"Update daily news for {today_str}"):
                                progress_bar.progress(100)
                                elapsed_time = int(time.time() - start_time)
                                status_text.markdown("**✅ 완료!**")
                                detail_text.success(f"모든 작업이 완료되었습니다! (총 소요 시간: {elapsed_time}초)")
                                time_text.empty()
                                
                                st.success(f"✅ {today_str} 뉴스 수집 및 분석이 완료되었습니다! (소요 시간: {elapsed_time}초)")
                                st.balloons()
                                
                                # 결과 미리보기
                                with st.expander("📊 수집 결과 미리보기"):
                                    st.write(f"**수집된 뉴스 수:** {len(result.get('articles', []))}")
                                    if result.get('keywords'):
                                        st.write(f"**핵심 키워드:** {', '.join(result.get('keywords', []))}")
                                    if result.get('summary'):
                                        st.write(f"**요약:** {result.get('summary', '')[:300]}...")
                            else:
                                st.error("데이터 저장에 실패했습니다.")
                    except Exception as e:
                        elapsed_time = int(time.time() - start_time)
                        st.error(f"❌ 뉴스 수집 중 오류 발생: {e}")
                        detail_text.error(f"오류 발생 (경과 시간: {elapsed_time}초)")
                        progress_bar.empty()
                        import traceback
                        with st.expander("🔍 상세 오류 정보"):
                            st.code(traceback.format_exc())
    except Exception as e:
        st.error(f"뉴스 수집 설정 오류: {e}")

