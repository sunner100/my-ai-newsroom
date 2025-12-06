"""
인포그래픽 생성 테스트 스크립트
"""
import sys
import os

# secrets.toml에서 키 읽기
try:
    import tomli
    with open('.streamlit/secrets.toml', 'rb') as f:
        secrets = tomli.load(f)
    gemini_key = secrets.get('api', {}).get('gemini_key')
    imagen_key = secrets.get('api', {}).get('imagen_key')
except:
    print("❌ secrets.toml 파일을 읽을 수 없습니다.")
    sys.exit(1)

print("=" * 60)
print("인포그래픽 생성 테스트")
print("=" * 60)
print(f"Gemini API 키: {gemini_key[:20]}..." if gemini_key else "❌ 없음")
print(f"Imagen API 키: {imagen_key[:20]}..." if imagen_key else "❌ 없음")
print()

if not gemini_key:
    print("❌ Gemini API 키가 설정되지 않았습니다.")
    sys.exit(1)

# utils_ai 모듈 테스트
print("1. 모듈 import 테스트...")
try:
    from utils_ai import generate_infographic, get_infographic_prompt
    print("   ✅ 모듈 import 성공")
except Exception as e:
    print(f"   ❌ 모듈 import 실패: {e}")
    sys.exit(1)

print()

# 테스트용 요약 텍스트
test_summary = """
AI 기술의 발전으로 인해 IT 산업이 급속도로 변화하고 있습니다.
머신러닝과 딥러닝 기술이 다양한 분야에 적용되면서 
혁신적인 솔루션들이 등장하고 있습니다.
"""

test_keywords = ["AI", "머신러닝", "딥러닝", "혁신", "기술"]

print("2. 프롬프트 생성 테스트...")
try:
    prompt = get_infographic_prompt(test_summary, gemini_key)
    if prompt:
        print("   ✅ 프롬프트 생성 성공")
        print(f"   생성된 프롬프트 (처음 100자): {prompt[:100]}...")
    else:
        print("   ❌ 프롬프트 생성 실패")
except Exception as e:
    print(f"   ❌ 프롬프트 생성 오류: {e}")
    import traceback
    traceback.print_exc()

print()

print("3. 인포그래픽 생성 테스트...")
try:
    print("   인포그래픽 생성 중... (시간이 걸릴 수 있습니다)")
    image = generate_infographic(gemini_key, test_summary, imagen_key, test_keywords)
    
    if image:
        print("   ✅ 인포그래픽 생성 성공!")
        print(f"   이미지 크기: {image.size}")
        print(f"   이미지 모드: {image.mode}")
        
        # 테스트 이미지 저장 (로컬)
        test_image_path = "test_infographic.png"
        image.save(test_image_path)
        print(f"   로컬 테스트 이미지 저장: {test_image_path}")
        
        # GitHub 저장 테스트 (폴더 구조 확인)
        print()
        print("4. GitHub 폴더 구조 저장 테스트...")
        try:
            from utils_github import GithubDataHandler
            import datetime
            
            # secrets에서 GitHub 토큰과 리포지토리 이름 가져오기
            github_token = secrets.get('api', {}).get('github_token')
            repo_name = secrets.get('general', {}).get('repo_name')
            
            if github_token and repo_name:
                db = GithubDataHandler(github_token, repo_name)
                
                # 년도/월별 폴더 구조로 저장
                today = datetime.date.today()
                today_str = today.strftime("%Y-%m-%d")
                year = today.strftime("%Y")
                month = today.strftime("%m")
                image_path = f"images/{year}/{month}/test_{today_str}.png"
                
                print(f"   저장 경로: {image_path}")
                if db.save_image(image_path, image, f"Test: Save infographic to folder structure"):
                    print(f"   ✅ GitHub 저장 성공! (폴더 구조: images/{year}/{month}/)")
                    print(f"   GitHub에서 확인: https://github.com/{repo_name}/tree/main/{image_path}")
                else:
                    print("   ❌ GitHub 저장 실패")
            else:
                print("   ⚠️ GitHub 토큰 또는 리포지토리 이름이 없어서 GitHub 저장 테스트 건너뜀")
        except Exception as e:
            print(f"   ⚠️ GitHub 저장 테스트 오류: {e}")
    else:
        print("   ⚠️ 인포그래픽 생성 실패 (대체 방법도 실패했을 수 있음)")
except Exception as e:
    print(f"   ❌ 인포그래픽 생성 오류: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 60)
print("테스트 완료")
print("=" * 60)

