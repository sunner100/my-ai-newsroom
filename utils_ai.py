import feedparser
import google.generativeai as genai
from typing import List, Dict, Any, Optional
import json
from PIL import Image
import io


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


def get_infographic_prompt(summary_text: str, api_key: str) -> Optional[str]:
    """
    Gemini Pro를 사용해 인포그래픽 생성을 위한 영어 프롬프트 생성
    
    Args:
        summary_text: 뉴스 요약 텍스트 (한글)
        api_key: Google Gemini API 키
        
    Returns:
        str: 이미지 생성용 영어 프롬프트
    """
    try:
        genai.configure(api_key=api_key)
        
        # 사용 가능한 모델 찾기
        model = None
        try:
            model = genai.GenerativeModel('gemini-2.0-flash')
        except:
            try:
                model = genai.GenerativeModel('gemini-1.0-pro')
            except:
                available_models = []
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        name = m.name.replace('models/', '')
                        available_models.append(name)
                if available_models:
                    model = genai.GenerativeModel(available_models[0])
        
        if model is None:
            return None
        
        prompt_request = f"""Based on the following IT news summary, create a detailed prompt for an AI image generator to create a professional infographic.

The image should be:
- Futuristic and modern design
- Clean data visualization style
- Tech dashboard aesthetic
- Minimal text (focus on visual elements, icons, charts, and layout)
- Professional and informative

News Summary: {summary_text}

Please provide ONLY the image generation prompt in English. Do not include any explanations or additional text."""

        response = model.generate_content(prompt_request)
        image_prompt = response.text.strip()
        
        return image_prompt
    except Exception as e:
        print(f"프롬프트 생성 오류: {e}")
        return None


def generate_infographic_image(prompt: str, gemini_api_key: str, imagen_api_key: str = None, summary_text: str = "", keywords: list = None) -> Optional[Image.Image]:
    """
    인포그래픽 이미지 생성 (여러 방법 시도)
    
    Args:
        prompt: 이미지 생성용 영어 프롬프트
        gemini_api_key: Google Gemini API 키
        imagen_api_key: Imagen API 키 (선택적)
        summary_text: 뉴스 요약 텍스트 (대체 방법용)
        keywords: 키워드 리스트 (대체 방법용)
        
    Returns:
        PIL Image 객체 또는 None
    """
    # 방법 1: Gemini API를 통한 Imagen 4 시도 (우선 시도)
    # 참고: Imagen 4는 Gemini API를 통해 사용 가능합니다
    try:
        genai.configure(api_key=gemini_api_key)
        
        # Imagen 4 모델 시도 (Gemini API를 통해)
        imagen_models = [
            "imagen-4.0-generate-001",  # Imagen 4 (최신, Gemini API를 통해 사용 가능)
            "imagen-3.0-generate-001",
            "imagen-2.0-generate-001"
        ]
        
        for model_name in imagen_models:
            try:
                print(f"   Imagen 모델 시도 (Gemini API): {model_name}")
                image_model = genai.GenerativeModel(model_name)
                # Imagen은 간단한 프롬프트만 전달 (generation_config 없이)
                result = image_model.generate_content(prompt)
                
                # 응답 형식 확인
                if result:
                    # 이미지가 직접 반환되는 경우
                    if hasattr(result, 'images') and result.images:
                        print(f"   ✅ {model_name} 성공!")
                        return result.images[0]
                    # 또는 다른 형식의 응답 처리
                    if hasattr(result, 'candidates') and result.candidates:
                        candidate = result.candidates[0]
                        if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                            for part in candidate.content.parts:
                                if hasattr(part, 'inline_data') and part.inline_data:
                                    # Base64 이미지 데이터
                                    import base64
                                    image_data = base64.b64decode(part.inline_data.data)
                                    print(f"   ✅ {model_name} 성공! (Base64 디코딩)")
                                    return Image.open(io.BytesIO(image_data))
            except Exception as e:
                error_msg = str(e)
                # "not found"나 "not supported" 오류는 조용히 넘어감
                if "not found" not in error_msg.lower() and "not supported" not in error_msg.lower():
                    print(f"   {model_name} 시도 실패: {error_msg[:150]}")
                continue
    except Exception as e:
        print(f"Gemini API를 통한 Imagen 시도 실패: {e}")
    
    # 방법 2: Imagen API 키가 별도로 있는 경우 시도 (선택적)
    if imagen_api_key and imagen_api_key != gemini_api_key:
        # 참고: Imagen은 현재 Vertex AI를 통해서만 접근 가능합니다
        # API 키만으로는 직접 접근이 어려울 수 있습니다
        # Vertex AI를 사용하려면 google-cloud-aiplatform 라이브러리와 
        # 서비스 계정 키가 필요합니다
        
        # 방법 1-1: Vertex AI Imagen (google-cloud-aiplatform 사용)
        # 주의: 이 방법은 서비스 계정 키가 필요합니다
        try:
            import vertexai
            from vertexai.preview.vision_models import ImageGenerationModel
            
            # Vertex AI는 프로젝트 ID와 위치가 필요합니다
            # API 키만으로는 작동하지 않을 수 있음
            # 환경 변수 GOOGLE_APPLICATION_CREDENTIALS에 서비스 계정 키 경로 설정 필요
            vertexai.init(project=None, location="us-central1")
            model = ImageGenerationModel.from_pretrained("imagegeneration@006")
            images = model.generate_images(
                prompt=prompt,
                number_of_images=1,
                aspect_ratio="16:9"
            )
            if images and len(images) > 0:
                return images[0]._pil_image
        except ImportError:
            # google-cloud-aiplatform 라이브러리가 없으면 다음 방법 시도
            pass
        except Exception as e:
            print(f"Vertex AI Imagen 시도 실패 (서비스 계정 키 필요): {e}")
            
            # 방법 1-2: Google AI Studio Imagen API (REST API 직접 호출)
            try:
                import requests
                import base64
                
                # Imagen API 엔드포인트 (Google AI Studio)
                url = "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:generateImages"
                
                headers = {
                    "Content-Type": "application/json",
                }
                
                params = {
                    "key": imagen_api_key
                }
                
                payload = {
                    "prompt": prompt,
                    "number_of_images": 1,
                    "aspect_ratio": "16:9"
                }
                
                response = requests.post(url, headers=headers, params=params, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if "images" in result and len(result["images"]) > 0:
                        # Base64 이미지 디코딩
                        image_data = base64.b64decode(result["images"][0]["bytesBase64Encoded"])
                        return Image.open(io.BytesIO(image_data))
                else:
                    print(f"Imagen API 호출 실패: {response.status_code} - {response.text}")
            except ImportError:
                print("requests 라이브러리가 필요합니다. pip install requests")
            except Exception as e:
                print(f"Imagen REST API 시도 실패: {e}")
            
        # 방법 2-3: Imagen API 키로 Gemini API를 통한 Imagen 시도
        try:
            genai.configure(api_key=imagen_api_key)
            imagen_models = ["imagen-4.0-generate-001", "imagen-3.0-generate-001", "imagen-2.0-generate-001"]
            for model_name in imagen_models:
                try:
                    image_model = genai.GenerativeModel(model_name)
                    result = image_model.generate_content(prompt)
                    if result and hasattr(result, 'images') and result.images:
                        return result.images[0]
                except:
                    continue
        except Exception as e:
            print(f"별도 Imagen API 키 시도 실패: {e}")
    
    # 방법 3: 대체 - Matplotlib 기반 시각화 생성
    if summary_text or keywords:
        try:
            return generate_fallback_infographic(summary_text, keywords or [])
        except Exception as e:
            print(f"대체 인포그래픽 생성 실패: {e}")
    
    # 모든 방법 실패
    if not imagen_api_key:
        print("⚠️ Imagen API 키가 설정되지 않았습니다. 대체 방법을 사용합니다.")
    else:
        print("⚠️ 이미지 생성에 실패했습니다. 대체 방법을 사용합니다.")
    return None


def generate_fallback_infographic(summary_text: str, keywords: list) -> Image.Image:
    """
    텍스트 없이 순수 시각적 요소만으로 구성된 미니멀 인포그래픽 생성
    나노바나나 스타일: 깔끔하고 미니멀한 시각화
    
    Args:
        summary_text: 뉴스 요약 텍스트 (키워드 추출용, 표시 안 함)
        keywords: 키워드 리스트 (시각화에 사용)
        
    Returns:
        PIL Image 객체
    """
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    
    # 16:9 비율로 그림 생성 (고해상도, 다크 테마)
    fig, ax = plt.subplots(figsize=(16, 9), facecolor='#0A0E27')
    ax.set_facecolor('#0A0E27')
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 9)
    ax.axis('off')
    
    # 배경 그라데이션 (미묘한 효과)
    y_coords = np.linspace(0, 9, 100)
    for i, y in enumerate(y_coords):
        alpha = 0.05 * (1 - i/100)
        ax.axhspan(y, y+0.09, color='#1E3A5F', alpha=alpha)
    
    # 키워드 기반 시각화 (텍스트 없이 순수 시각적 요소만)
    if keywords and len(keywords) > 0:
        num_keywords = min(len(keywords), 8)
        
        # 1. 중앙 원형 차트 (키워드 중요도 시각화)
        center_x, center_y = 8, 4.5
        base_radius = 2.5
        
        # 원형 배경 (그라데이션)
        for i in range(5):
            circle = mpatches.Circle((center_x, center_y), base_radius - i*0.15, 
                          color='#1E3A5F', alpha=0.3 - i*0.05, zorder=1)
            ax.add_patch(circle)
        
        # 키워드별 섹터 (파이 차트 스타일)
        angles = np.linspace(0, 2*np.pi, num_keywords, endpoint=False)
        colors = plt.cm.viridis(np.linspace(0.3, 0.9, num_keywords))
        
        for i, (angle, color) in enumerate(zip(angles, colors)):
            # 원호 그리기
            arc_radius = base_radius * (0.7 + 0.3 * (i % 3) / 2)
            theta = np.linspace(angle - np.pi/num_keywords, angle + np.pi/num_keywords, 50)
            x_arc = center_x + arc_radius * np.cos(theta)
            y_arc = center_y + arc_radius * np.sin(theta)
            ax.plot(x_arc, y_arc, color=color, linewidth=4, alpha=0.8, zorder=2)
            
            # 외부 점 (키워드 위치 표시)
            dot_radius = base_radius + 0.8
            dot_x = center_x + dot_radius * np.cos(angle)
            dot_y = center_y + dot_radius * np.sin(angle)
            dot = mpatches.Circle((dot_x, dot_y), 0.25, color=color, alpha=0.9, zorder=3)
            ax.add_patch(dot)
            
            # 연결선 (중앙에서 외부로)
            ax.plot([center_x, dot_x], [center_y, dot_y], 
                   color=color, linewidth=1.5, alpha=0.3, zorder=1)
    
    # 2. 상단 바 차트 (트렌드 표시)
    if keywords:
        bar_y = 7.5
        bar_width = 14
        bar_height = 0.8
        bar_x = 1
        
        # 배경 바
        bg_bar = mpatches.Rectangle((bar_x, bar_y - bar_height/2), bar_width, bar_height,
                          color='#1E3A5F', alpha=0.3, zorder=1)
        ax.add_patch(bg_bar)
        
        # 키워드별 세그먼트
        segment_width = bar_width / min(len(keywords), 6)
        for i, keyword in enumerate(keywords[:6]):
            segment_x = bar_x + i * segment_width
            height_factor = 0.5 + 0.5 * (i % 3) / 2
            segment_height = bar_height * height_factor
            
            color = plt.cm.plasma(i / min(len(keywords), 6))
            segment = mpatches.Rectangle((segment_x, bar_y - segment_height/2), 
                              segment_width * 0.9, segment_height,
                              color=color, alpha=0.7, zorder=2)
            ax.add_patch(segment)
    
    # 3. 하단 데이터 포인트 (점 그래프 스타일)
    if keywords:
        points_y = 1.5
        num_points = min(len(keywords), 10)
        point_spacing = 14 / (num_points + 1)
        
        for i in range(num_points):
            point_x = 1 + (i + 1) * point_spacing
            point_size = 0.15 + 0.1 * (i % 3)
            color = plt.cm.coolwarm(i / num_points)
            
            point = mpatches.Circle((point_x, points_y), point_size, 
                         color=color, alpha=0.8, zorder=3)
            ax.add_patch(point)
            
            # 수직선 연결
            line_height = 0.3 + 0.2 * (i % 2)
            ax.plot([point_x, point_x], [points_y - line_height, points_y], 
                   color=color, linewidth=2, alpha=0.5, zorder=2)
    
    # 4. 배경 장식 요소 (기하학적 패턴)
    # 대각선 그리드
    for i in range(5):
        x_start = 0.5 + i * 3
        y_start = 0.5
        x_end = x_start + 2
        y_end = y_start + 8
        ax.plot([x_start, x_end], [y_start, y_end], 
               color='#1E3A5F', linewidth=0.5, alpha=0.1, zorder=0)
    
    # 5. 중앙 강조 원 (펄스 효과)
    if keywords:
        for i in range(3):
            pulse_radius = base_radius * 0.3 + i * 0.2
            pulse = mpatches.Circle((center_x, center_y), pulse_radius,
                      fill=False, edgecolor='#4FC3F7', 
                      linewidth=2, alpha=0.2 - i*0.05, zorder=1)
            ax.add_patch(pulse)
    
    # 6. 모서리 장식 (사각형 프레임)
    corner_size = 1.5
    corner_width = 1.5
    
    # 좌상단
    ax.plot([0.5, 0.5 + corner_size], [8.5, 8.5], 
           color='#4FC3F7', linewidth=corner_width, alpha=0.6, zorder=4)
    ax.plot([0.5, 0.5], [8.5, 8.5 - corner_size], 
           color='#4FC3F7', linewidth=corner_width, alpha=0.6, zorder=4)
    
    # 우상단
    ax.plot([15.5, 15.5 - corner_size], [8.5, 8.5], 
           color='#4FC3F7', linewidth=corner_width, alpha=0.6, zorder=4)
    ax.plot([15.5, 15.5], [8.5, 8.5 - corner_size], 
           color='#4FC3F7', linewidth=corner_width, alpha=0.6, zorder=4)
    
    # 좌하단
    ax.plot([0.5, 0.5 + corner_size], [0.5, 0.5], 
           color='#4FC3F7', linewidth=corner_width, alpha=0.6, zorder=4)
    ax.plot([0.5, 0.5], [0.5, 0.5 + corner_size], 
           color='#4FC3F7', linewidth=corner_width, alpha=0.6, zorder=4)
    
    # 우하단
    ax.plot([15.5, 15.5 - corner_size], [0.5, 0.5], 
           color='#4FC3F7', linewidth=corner_width, alpha=0.6, zorder=4)
    ax.plot([15.5, 15.5], [0.5, 0.5 + corner_size], 
           color='#4FC3F7', linewidth=corner_width, alpha=0.6, zorder=4)
    
    # PIL Image로 변환 (고해상도)
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', 
                facecolor='#0A0E27', edgecolor='none', pad_inches=0)
    buf.seek(0)
    img = Image.open(buf)
    plt.close()
    
    return img


def generate_infographic(gemini_api_key: str, summary_text: str, imagen_api_key: str = None, keywords: list = None) -> Optional[Image.Image]:
    """
    뉴스 요약을 기반으로 인포그래픽 생성 (통합 함수)
    
    Args:
        gemini_api_key: Google Gemini API 키
        summary_text: 뉴스 요약 텍스트
        imagen_api_key: Imagen API 키 (선택적)
        keywords: 키워드 리스트 (선택적, 대체 방법용)
        
    Returns:
        PIL Image 객체 또는 None
    """
    # 1. 프롬프트 생성 (Imagen 사용 시)
    image_prompt = None
    if imagen_api_key:
        try:
            image_prompt = get_infographic_prompt(summary_text, gemini_api_key)
        except Exception as e:
            print(f"프롬프트 생성 실패, 대체 방법 사용: {e}")
    
    # 2. 이미지 생성 (여러 방법 시도)
    image = generate_infographic_image(image_prompt or "", gemini_api_key, imagen_api_key, summary_text, keywords)
    return image

