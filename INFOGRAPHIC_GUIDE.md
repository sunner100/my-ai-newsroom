# 🎨 인포그래픽 생성 가이드 검토 및 개선

## 📋 현재 구현 상태

### ✅ 구현 완료
1. **프롬프트 생성** (`get_infographic_prompt`)
   - Gemini로 영어 프롬프트 생성 ✅
   - 스타일 키워드 포함 ✅

2. **이미지 저장** (`save_image`)
   - GitHub에 이미지 저장 ✅
   - PIL Image → bytes 변환 ✅

3. **이미지 로드** (`load_image`)
   - GitHub에서 이미지 읽기 ✅

### ⚠️ 구현 필요
1. **이미지 생성** (`generate_infographic_image`)
   - 현재: Imagen API 미구현 (None 반환)
   - 문제: `google-generativeai` 라이브러리에서 Imagen 직접 지원 안 함

---

## 🔍 문제점 분석

### 1. Imagen API 접근 방법

**현재 상황:**
- `google-generativeai` 라이브러리는 텍스트 생성(Gemini)만 지원
- Imagen은 Vertex AI를 통해 별도로 접근해야 함
- 또는 다른 이미지 생성 API 필요

**해결 방안:**

#### 옵션 1: Vertex AI Imagen 사용
```python
# google-cloud-aiplatform 라이브러리 필요
from vertexai.preview.vision_models import ImageGenerationModel

model = ImageGenerationModel.from_pretrained("imagegeneration@006")
images = model.generate_images(
    prompt=prompt,
    number_of_images=1,
    aspect_ratio="16:9"
)
```

#### 옵션 2: 대체 이미지 생성 API
- DALL-E API (OpenAI)
- Stable Diffusion API
- Midjourney API

#### 옵션 3: 텍스트 기반 시각화 (임시)
- Matplotlib/Plotly로 차트 생성
- Pillow로 간단한 인포그래픽 생성

---

## 💡 개선 제안

### 1. 프롬프트 생성 개선

**현재 프롬프트:**
```python
prompt_request = f"""Based on the following IT news summary, create a detailed prompt for an AI image generator...
```

**개선 제안:**
- 더 구체적인 스타일 지시 추가
- 키워드 기반 시각화 요소 명시
- 레이아웃 구조 지정

### 2. 이미지 생성 대체 방법

**임시 해결책:**
- Matplotlib로 데이터 시각화 생성
- 키워드 기반 아이콘/차트 조합
- 텍스트 오버레이로 정보 표시

### 3. 에러 처리 개선

**현재:**
- Imagen API 실패 시 None 반환
- 사용자에게 명확한 피드백 부족

**개선:**
- 단계별 에러 메시지
- 대체 방법 자동 시도
- 사용자에게 옵션 제공

---

## 🔧 권장 수정 사항

### 1. `utils_ai.py` 개선

```python
def generate_infographic_image(prompt: str, api_key: str) -> Optional[Image.Image]:
    """
    개선된 이미지 생성 함수
    - Vertex AI Imagen 시도
    - 실패 시 대체 방법 사용
    """
    # 1. Vertex AI Imagen 시도
    # 2. 실패 시 Matplotlib 기반 시각화 생성
    # 3. 최종 실패 시 None 반환
```

### 2. 대체 이미지 생성 함수 추가

```python
def generate_fallback_infographic(summary: str, keywords: List[str]) -> Image.Image:
    """
    Imagen API가 없을 때 사용하는 대체 방법
    Matplotlib로 간단한 인포그래픽 생성
    """
    # Matplotlib로 차트/시각화 생성
    # Pillow로 조합
    pass
```

---

## 📝 체크리스트

### 구현 확인
- [x] 프롬프트 생성 함수
- [x] 이미지 저장 함수
- [x] 이미지 로드 함수
- [ ] 실제 이미지 생성 (Imagen API)
- [ ] 대체 이미지 생성 방법

### 테스트 확인
- [ ] 프롬프트 생성 테스트
- [ ] 이미지 저장 테스트
- [ ] 이미지 로드 테스트
- [ ] 전체 플로우 테스트

---

## 🚀 다음 단계

1. **Vertex AI Imagen 설정** (권장)
   - Google Cloud 프로젝트 생성
   - Vertex AI API 활성화
   - `google-cloud-aiplatform` 설치

2. **또는 대체 API 사용**
   - DALL-E API
   - Stable Diffusion API

3. **임시 해결책 구현**
   - Matplotlib 기반 시각화
   - 텍스트 + 아이콘 조합

---

## ⚠️ 주의사항

- Imagen API는 별도 비용 발생 가능
- Vertex AI 설정이 복잡할 수 있음
- 대체 방법은 품질이 낮을 수 있음

