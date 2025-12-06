import feedparser
import google.generativeai as genai
from typing import List, Dict, Any
import json


def fetch_rss_news(rss_urls: List[str], max_items_per_feed: int = 10) -> List[Dict[str, Any]]:
    """
    RSS URL 리스트에서 최신 뉴스를 수집
    
    Args:
        rss_urls: RSS URL 리스트
        max_items_per_feed: 피드당 최대 수집 개수
        
    Returns:
        뉴스 리스트 (제목, 링크, 요약 포함)
    """
    all_news = []
    
    for url in rss_urls:
        try:
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:max_items_per_feed]:
                news_item = {
                    'title': entry.get('title', '제목 없음'),
                    'link': entry.get('link', ''),
                    'summary': entry.get('summary', entry.get('description', '요약 없음')),
                    'published': entry.get('published', '')
                }
                all_news.append(news_item)
        except Exception as e:
            print(f"RSS 파싱 오류 ({url}): {e}")
            continue
    
    return all_news


def analyze_news_with_gemini(news_list: List[Dict[str, Any]], api_key: str) -> Dict[str, Any]:
    """
    Gemini AI를 사용해 뉴스들을 분석하고 요약
    
    Args:
        news_list: 분석할 뉴스 리스트
        api_key: Google Gemini API 키
        
    Returns:
        분석 결과 dict (summary, keywords, articles 포함)
    """
    if not news_list:
        return {
            'summary': '수집된 뉴스가 없습니다.',
            'keywords': [],
            'articles': []
        }
    
    # Gemini 설정
    genai.configure(api_key=api_key)
    
    # gemini-2.0-flash 모델 사용 (명시적 지정)
    model = None
    model_name = 'gemini-2.0-flash'
    
    try:
        # gemini-2.0-flash 직접 시도
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        # gemini-2.0-flash가 없으면 사용 가능한 모델 목록 확인
        try:
            available_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    name = m.name.replace('models/', '')
                    available_models.append(name)
            
            if available_models:
                # gemini-2.0-flash-exp 또는 다른 2.0 버전 시도
                fallback_models = ['gemini-2.0-flash-exp', 'gemini-2.0-flash', 'gemini-2.5-flash']
                for fallback in fallback_models:
                    if fallback in available_models:
                        model_name = fallback
                        model = genai.GenerativeModel(model_name)
                        break
                
                # 여전히 없으면 첫 번째 사용 가능한 모델 사용
                if model is None:
                    model_name = available_models[0]
                    model = genai.GenerativeModel(model_name)
            else:
                raise Exception("사용 가능한 Gemini 모델을 찾을 수 없습니다.")
        except Exception as e2:
            raise Exception(f"Gemini 모델을 초기화할 수 없습니다: {str(e2)}")
    
    # 뉴스 내용을 텍스트로 정리
    news_text = "\n\n".join([
        f"제목: {news.get('title', '제목 없음')}\n요약: {str(news.get('summary', ''))[:200]}..."
        for news in news_list[:20]  # 최대 20개만 분석
    ])
    
    # 프롬프트 작성
    prompt = f"""다음 IT 뉴스들을 IT 전문가 관점에서 분석해주세요.

{news_text}

다음 JSON 형식으로 응답해주세요:
{{
    "summary": "전체 뉴스를 종합한 3줄 요약",
    "keywords": ["키워드1", "키워드2", "키워드3"],
    "trends": "주요 트렌드나 인사이트"
}}

반드시 유효한 JSON 형식으로만 응답해주세요."""

    try:
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # JSON 추출 (마크다운 코드 블록 제거)
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0].strip()
        
        analysis_result = json.loads(response_text)
        
        # 각 뉴스에 AI 분석 추가
        # 성능 최적화: 개별 분석 대신 원본 요약 사용 (전체 요약에서 충분한 정보 제공)
        articles = []
        
        for news in news_list:
            # 원본 요약을 AI 분석으로 사용 (전체 요약에서 이미 충분한 분석 제공)
            # 개별 API 호출을 제거하여 시간을 대폭 단축
            summary_text = news.get('summary', '')
            if len(summary_text) > 300:
                ai_analysis = summary_text[:300] + "..."
            else:
                ai_analysis = summary_text if summary_text else "요약 없음"
            
            articles.append({
                'title': news['title'],
                'link': news['link'],
                'summary': news['summary'],
                'ai_analysis': ai_analysis,
                'published': news.get('published', '')
            })
        
        return {
            'summary': analysis_result.get('summary', '분석 결과를 생성할 수 없습니다.'),
            'keywords': analysis_result.get('keywords', []),
            'trends': analysis_result.get('trends', ''),
            'articles': articles
        }
        
    except json.JSONDecodeError as e:
        # JSON 파싱 실패 시 기본 형식 반환
        return {
            'summary': f'AI 분석 중 오류가 발생했습니다. (JSON 파싱 실패)\n응답: {response_text[:200]}',
            'keywords': [],
            'trends': '',
            'articles': [
                {
                    'title': news['title'],
                    'link': news['link'],
                    'summary': news['summary'],
                    'ai_analysis': news['summary'],
                    'published': news.get('published', '')
                }
                for news in news_list
            ]
        }
    except Exception as e:
        error_msg = str(e)
        # 사용 가능한 모델 정보 추가
        try:
            available_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name.replace('models/', ''))
            if available_models:
                error_msg += f"\n\n사용 가능한 모델: {', '.join(available_models[:5])}"
        except:
            pass
        
        return {
            'summary': f'AI 분석 중 오류가 발생했습니다: {error_msg}',
            'keywords': [],
            'trends': '',
            'articles': [
                {
                    'title': news['title'],
                    'link': news['link'],
                    'summary': news['summary'],
                    'ai_analysis': news['summary'],
                    'published': news.get('published', '')
                }
                for news in news_list
            ]
        }


def fetch_and_analyze_news(rss_urls: List[str], api_key: str) -> Dict[str, Any]:
    """
    RSS에서 뉴스를 수집하고 Gemini로 분석하는 통합 함수
    
    Args:
        rss_urls: RSS URL 리스트
        api_key: Google Gemini API 키
        
    Returns:
        분석된 뉴스 데이터 dict
    """
    # 1. RSS 크롤링
    news_list = fetch_rss_news(rss_urls)
    
    if not news_list:
        return {
            'summary': '수집된 뉴스가 없습니다. RSS URL을 확인해주세요.',
            'keywords': [],
            'trends': '',
            'articles': []
        }
    
    # 2. Gemini 분석
    analyzed_data = analyze_news_with_gemini(news_list, api_key)
    
    return analyzed_data

