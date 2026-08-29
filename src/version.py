import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
VERSION_PATTERN = re.compile(r'^version\s*=\s*["\']([^"\']+)["\']\s*$', re.MULTILINE)


def read_project_version(pyproject_path):
    """개발 실행 시 pyproject.toml에서 현재 버전을 읽는다."""
    try:
        project_text = Path(pyproject_path).read_text(encoding="utf-8")
    except OSError:
        return "dev"

    match = VERSION_PATTERN.search(project_text)
    return match.group(1) if match else "dev"


def get_app_version():
    """릴리즈 빌드는 생성된 버전을, 개발 실행은 프로젝트 버전을 사용한다."""
    try:
        from .build_info import APP_VERSION
    except ImportError:
        return read_project_version(PROJECT_ROOT / "pyproject.toml")
    return APP_VERSION
