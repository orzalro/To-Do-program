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

## 사용 방법

- `일정 추가`로 새 일정 만들기
- 일정 더블클릭으로 수정
- 블럭 한 번 클릭으로 선택
- 블럭 이름 더블클릭으로 이름 변경
- `Ctrl + C`, `Ctrl + V`로 블럭 복사/붙여넣기
- `Delete`로 블럭 초기화

## 배포

`PyInstaller`로 만든 단일 `.exe` 파일을 GitHub Releases에 업로드하는 방식으로 배포합니다.
