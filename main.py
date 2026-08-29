import sys


def main():
    # 새로 받은 EXE가 이 모드로 실행되어 종료된 기존 EXE를 교체한다.
    if len(sys.argv) == 4 and sys.argv[1] == "--apply-update":
        from src.updater import run_update_helper

        return run_update_helper(sys.argv[2], int(sys.argv[3]))

    from src.app import main as run_app

    return run_app()


if __name__ == "__main__":
    sys.exit(main())
