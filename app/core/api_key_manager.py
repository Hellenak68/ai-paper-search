import os
import getpass
from typing import Optional
from app.core.config import settings


class APIKeyManager:
    """API 키를 안전하게 관리하는 클래스"""
    
    def __init__(self):
        self._api_key: Optional[str] = None
    
    def get_api_key(self) -> str:
        """API 키를 가져옵니다. 여러 소스에서 시도합니다."""
        
        # 1. 이미 설정된 키가 있으면 반환
        if self._api_key:
            return self._api_key
        
        # 2. 환경 변수에서 확인
        env_key = os.getenv("UPSTAGE_API_KEY")
        if env_key:
            self._api_key = env_key
            return env_key
        
        # 3. 설정 파일에서 확인
        if settings.upstage_api_key:
            self._api_key = settings.upstage_api_key
            return settings.upstage_api_key
        
        # 4. 사용자에게 입력 요청
        return self._prompt_for_api_key()
    
    def _prompt_for_api_key(self) -> str:
        """사용자에게 API 키를 안전하게 입력받습니다."""
        print("\n🔑 Upstage API 키가 필요합니다.")
        print("다음 방법 중 하나를 선택하세요:")
        print("1. 직접 입력 (터미널에서 안전하게 입력)")
        print("2. 환경 변수 설정 후 재시작")
        print("3. .env 파일에 UPSTAGE_API_KEY 설정")
        
        choice = input("\n선택 (1/2/3): ").strip()
        
        if choice == "1":
            api_key = getpass.getpass("Upstage API 키를 입력하세요 (화면에 표시되지 않음): ")
            if api_key.strip():
                self._api_key = api_key.strip()
                print("✅ API 키가 설정되었습니다.")
                return api_key.strip()
            else:
                print("❌ API 키가 입력되지 않았습니다.")
                return self._prompt_for_api_key()
        elif choice == "2":
            print("\n환경 변수 설정 방법:")
            print("Windows: set UPSTAGE_API_KEY=your_api_key")
            print("Linux/Mac: export UPSTAGE_API_KEY=your_api_key")
            print("그 후 애플리케이션을 재시작하세요.")
            exit(1)
        elif choice == "3":
            print("\n.env 파일에 다음을 추가하세요:")
            print("UPSTAGE_API_KEY=your_api_key")
            print("그 후 애플리케이션을 재시작하세요.")
            exit(1)
        else:
            print("❌ 잘못된 선택입니다.")
            return self._prompt_for_api_key()
    
    def set_api_key(self, api_key: str):
        """API 키를 설정합니다."""
        self._api_key = api_key
    
    def clear_api_key(self):
        """메모리에서 API 키를 제거합니다."""
        self._api_key = None


# 전역 인스턴스
api_key_manager = APIKeyManager()
