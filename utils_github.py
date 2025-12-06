import json
from github import Github
from github.GithubException import GithubException, UnknownObjectException
import streamlit as st


class GithubDataHandler:
    """GitHub 리포지토리의 JSON 파일을 읽고 쓰는 핸들러"""
    
    def __init__(self, token, repo_name):
        """
        Args:
            token: GitHub Personal Access Token
            repo_name: 리포지토리 이름 (예: "username/repo-name")
        """
        try:
            self.g = Github(token)
            self.repo = self.g.get_repo(repo_name)
        except GithubException as e:
            st.error(f"GitHub 연결 오류: {e}")
            raise

    def load_json(self, file_path):
        """
        GitHub에서 JSON 파일을 읽어서 dict로 반환
        
        Args:
            file_path: 리포지토리 내 파일 경로 (예: "data/stats.json")
            
        Returns:
            dict: JSON 파일 내용 (파일이 없으면 빈 dict 반환)
        """
        try:
            contents = self.repo.get_contents(file_path)
            return json.loads(contents.decoded_content.decode('utf-8'))
        except UnknownObjectException:
            # 파일이 없으면 빈 딕셔너리 반환
            return {}
        except json.JSONDecodeError as e:
            st.warning(f"JSON 파싱 오류 ({file_path}): {e}")
            return {}
        except GithubException as e:
            st.error(f"GitHub 읽기 오류 ({file_path}): {e}")
            return {}

    def save_json(self, file_path, data, message="Update data"):
        """
        dict 데이터를 JSON으로 변환해서 GitHub에 저장
        
        Args:
            file_path: 리포지토리 내 파일 경로
            data: 저장할 dict 데이터
            message: 커밋 메시지
            
        Returns:
            bool: 성공 여부
        """
        try:
            content = json.dumps(data, indent=4, ensure_ascii=False)
            
            try:
                # 파일이 존재하면 업데이트
                file = self.repo.get_contents(file_path)
                self.repo.update_file(file.path, message, content, file.sha)
                return True
            except UnknownObjectException:
                # 파일이 없으면 생성
                self.repo.create_file(file_path, message, content)
                return True
        except GithubException as e:
            st.error(f"GitHub 저장 오류 ({file_path}): {e}")
            return False
        except Exception as e:
            st.error(f"예상치 못한 오류 ({file_path}): {e}")
            return False

