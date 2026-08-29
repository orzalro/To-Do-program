# To-Do Program
블럭별로 할 일을 나눠 관리하는 데스크톱 TODO 프로그램입니다.

## uv usage

- Install runtime dependencies: `uv sync`
- Run the app: `uv run python main.py`
- Install build dependencies: `uv sync --group dev`
- Build the Windows EXE: `uv run pyinstaller --onefile --noconsole --name "To-do" main.py`

## 주요 기능

- 블럭별 일정 정리
- 반복 일정 관리
- 블럭 선택, 이름 변경, 초기화
- 블럭 복사, 붙여넣기, 드래그 이동
- 일정 드래그 이동
- GitHub Releases 기반 자동 업데이트

## 사용 방법

- `일정 추가`로 새 일정 만들기
- 일정 더블클릭으로 수정
- 블럭 한 번 클릭으로 선택
- 블럭 이름 더블클릭으로 이름 변경
- `Ctrl + C`, `Ctrl + V`로 블럭 복사/붙여넣기
- `Delete`로 블럭 초기화
- `Help > 버전 정보`에서 현재 앱 버전 확인
- `Help > 업데이트 확인`에서 최신 릴리즈 수동 확인

## 배포

`PyInstaller`로 만든 단일 `.exe` 파일을 GitHub Releases에 업로드하는 방식으로 배포합니다.

릴리즈 EXE는 시작할 때 최신 정식 릴리즈를 확인합니다. 새 버전 설치에 동의하면
다운로드 파일의 크기와 SHA-256을 검증한 뒤 기존 EXE를 교체하고 자동으로 재시작합니다.
자동 업데이트 기능이 포함된 첫 릴리즈는 기존 사용자가 한 번 직접 설치해야 합니다.
