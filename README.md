# Google Messenger Desktop

구글 메시지 웹(Google Messages Web) 기반의 경량화된 Windows 데스크톱 애플리케이션입니다. 브라우저와 혼재되지 않는 완전히 분리된 전용 네이티브 앱 환경을 제공합니다.

## 주요 기능
- **단독 창(Standalone Window)**: 브라우저 탭에 섞이지 않는 전용 독립 사이트 렌더링.
- **백그라운드 실행 및 시스템 트레이**: 창을 닫아도 트레이로 전환되어 새 메시지 수신 대기 유지.
- **네이티브 OS 알림 연동**: 웹 브라우저의 새 메시지 도착 알림을 Windows 고유 기본 알림(시스템 트레이 말풍선)으로 즉각 매핑.
- **안전한 인증(Google Login Bypassed)**: 임베디드 웹뷰 차단을 회피하는 UA 위장 처리로 정상적인 스마트폰 연동 가능.
- **세션 영구 유지**: 한 번 기기 연동(QR스캔 등) 시 차후 앱 완전 종료 후 재시작 시점에도 정보 유지.
- **중복 실행 제어(Single Instance IPC)**: 실수로 앱을 여러 번 실행 시 기존에 열려 있는 창을 맨 앞으로 강제 호출.
- **가벼운 배포형**: Inno Setup 기반 최적화 및 압축 탑재로 매우 빠른 실행 보장.

## 기술 스택
- Python 3.11
- PyQt6 / PyQt6-WebEngine
- PyInstaller / Inno Setup 6

## 직접 빌드 및 설치 방법
1. 필요 패키지 설치: `pip install PyQt6 PyQt6-WebEngine pyinstaller`
2. `pyinstaller` 명령어를 통해 실행 파일 디렉토리 구성.
3. 제공되는 `installer.iss` 스크립트를 Inno Setup Compiler로 열어 `GoogleMessenger_Setup_v*.exe` 컴파일.
4. 산출된 셋업 파일을 통해 PC 설치 및 실행.

---
© SaRaM_ida(망고아빠)
