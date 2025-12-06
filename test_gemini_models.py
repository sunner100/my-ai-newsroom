"""
Gemini API에서 사용 가능한 모델 확인 스크립트
"""
import google.generativeai as genai
import sys
import os

# secrets.toml에서 API 키 가져오기
try:
    import streamlit as st
    api_key = st.secrets["api"]["gemini_key"]
except:
    # Streamlit 없이 실행하는 경우 - 간단한 파싱
    api_key = None
    try:
        with open('.streamlit/secrets.toml', 'r', encoding='utf-8') as f:
            content = f.read()
            # gemini_key 찾기
            for line in content.split('\n'):
                if 'gemini_key' in line and '=' in line:
                    api_key = line.split('=')[1].strip().strip('"').strip("'")
                    break
    except Exception as e:
        print(f"secrets.toml 읽기 오류: {e}")
        sys.exit(1)
    
    if not api_key:
        print("API 키를 찾을 수 없습니다.")
        sys.exit(1)

genai.configure(api_key=api_key)

print("=" * 60)
print("사용 가능한 Gemini 모델 목록:")
print("=" * 60)

try:
    models = genai.list_models()
    available_models = []
    
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            model_name = model.name
            # models/ 접두사 제거
            if model_name.startswith('models/'):
                model_name = model_name[7:]
            available_models.append(model_name)
            print(f"✅ {model_name}")
            print(f"   전체 이름: {model.name}")
            print(f"   지원 메서드: {model.supported_generation_methods}")
            print()
    
    if available_models:
        print("=" * 60)
        print(f"추천 모델: {available_models[0]}")
        print("=" * 60)
        
        # 첫 번째 모델로 테스트
        print(f"\n모델 '{available_models[0]}' 테스트 중...")
        model = genai.GenerativeModel(available_models[0])
        response = model.generate_content("안녕하세요")
        print(f"✅ 테스트 성공!")
        print(f"응답: {response.text[:100]}...")
    else:
        print("❌ 사용 가능한 모델을 찾을 수 없습니다.")
        
except Exception as e:
    print(f"❌ 오류 발생: {e}")
    import traceback
    traceback.print_exc()

