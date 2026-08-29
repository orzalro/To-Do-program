import ctypes
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.request import Request, urlopen

from PyQt5.QtCore import QThread, pyqtSignal


RELEASE_API_URL = "https://api.github.com/repos/orzalro/To-Do-program/releases/latest"
RELEASE_ASSET_NAME = "To-do.exe"
VERSION_PATTERN = re.compile(r"^v?(\d+)\.(\d+)\.(\d+)$")
UPDATE_WAIT_SECONDS = 30


class UpdateError(Exception):
    pass


@dataclass(frozen=True)
class ReleaseInfo:
    version: str
    page_url: str
    download_url: str
    digest: str
    size: int


def parse_version(value):
    match = VERSION_PATTERN.fullmatch(str(value).strip())
    if not match:
        raise UpdateError(f"지원하지 않는 버전 형식입니다: {value}")
    return tuple(map(int, match.groups()))


def is_newer_version(candidate, current):
    if current == "dev":
        return False
    return parse_version(candidate) > parse_version(current)


def release_from_payload(payload):
    tag_name = payload.get("tag_name", "")
    version_tuple = parse_version(tag_name)
    version = ".".join(map(str, version_tuple))

    for asset in payload.get("assets", []):
        if asset.get("name") != RELEASE_ASSET_NAME:
            continue

        digest = asset.get("digest") or ""
        if not digest.startswith("sha256:"):
            raise UpdateError("릴리즈 파일의 SHA-256 검증값을 찾을 수 없습니다.")

        return ReleaseInfo(
            version=version,
            page_url=payload.get("html_url", ""),
            download_url=asset["browser_download_url"],
            digest=digest.removeprefix("sha256:"),
            size=int(asset["size"]),
        )

    raise UpdateError(f"릴리즈에서 {RELEASE_ASSET_NAME} 파일을 찾을 수 없습니다.")


def fetch_latest_release(timeout=10):
    request = Request(
        RELEASE_API_URL,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "To-Do-program-updater",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            payload = json.load(response)
    except (OSError, ValueError) as error:
        raise UpdateError(f"최신 릴리즈를 확인하지 못했습니다: {error}") from error
    return release_from_payload(payload)


def download_release(release, destination, progress_callback=None, timeout=30):
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial_path = destination.with_suffix(f"{destination.suffix}.part")
    digest = hashlib.sha256()
    downloaded = 0
    request = Request(
        release.download_url,
        headers={"User-Agent": "To-Do-program-updater"},
    )

    try:
        with urlopen(request, timeout=timeout) as response, partial_path.open("wb") as output:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                output.write(chunk)
                digest.update(chunk)
                downloaded += len(chunk)
                if progress_callback and release.size:
                    progress_callback(min(100, downloaded * 100 // release.size))

        if downloaded != release.size:
            raise UpdateError("다운로드한 파일 크기가 릴리즈 정보와 다릅니다.")
        if digest.hexdigest().lower() != release.digest.lower():
            raise UpdateError("다운로드한 파일의 SHA-256 검증에 실패했습니다.")

        os.replace(partial_path, destination)
    except Exception as error:
        partial_path.unlink(missing_ok=True)
        destination.unlink(missing_ok=True)
        if isinstance(error, UpdateError):
            raise
        raise UpdateError(f"업데이트 파일을 다운로드하지 못했습니다: {error}") from error

    if progress_callback:
        progress_callback(100)
    return destination


def update_download_path():
    update_dir = Path(tempfile.gettempdir()) / "To-Do-program-update"
    return update_dir / RELEASE_ASSET_NAME


def can_self_update():
    return bool(getattr(sys, "frozen", False)) and os.name == "nt"


def _new_process_environment():
    environment = os.environ.copy()
    # 실행 중인 PyInstaller onefile과 별개로 새 EXE가 자체 임시 폴더를 사용하게 한다.
    environment["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
    return environment


def launch_update_helper(downloaded_path):
    if not can_self_update():
        raise UpdateError("자동 업데이트는 Windows 릴리즈 EXE에서만 사용할 수 있습니다.")

    creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    subprocess.Popen(
        [
            str(downloaded_path),
            "--apply-update",
            str(Path(sys.executable).resolve()),
            str(os.getpid()),
        ],
        close_fds=True,
        creationflags=creation_flags,
        env=_new_process_environment(),
    )


def _launch_application(executable_path):
    creation_flags = 0
    if os.name == "nt":
        creation_flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS
    subprocess.Popen(
        [str(executable_path)],
        close_fds=True,
        creationflags=creation_flags,
        env=_new_process_environment(),
    )


def replace_executable(source_path, target_path, launcher=_launch_application):
    """새 EXE 교체와 실행을 하나의 복구 가능한 작업으로 처리한다."""
    source_path = Path(source_path)
    target_path = Path(target_path)
    swap_path = Path(f"{target_path}.new")
    backup_path = Path(f"{target_path}.bak")
    had_target = target_path.exists()

    swap_path.unlink(missing_ok=True)
    backup_path.unlink(missing_ok=True)
    shutil.copy2(source_path, swap_path)

    try:
        if had_target:
            os.replace(target_path, backup_path)
        os.replace(swap_path, target_path)
        launcher(target_path)
    except Exception:
        target_path.unlink(missing_ok=True)
        if backup_path.exists():
            os.replace(backup_path, target_path)
        raise
    else:
        backup_path.unlink(missing_ok=True)
    finally:
        swap_path.unlink(missing_ok=True)


def wait_for_process_exit(process_id, timeout=UPDATE_WAIT_SECONDS):
    if os.name != "nt":
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                os.kill(process_id, 0)
            except OSError:
                return True
            time.sleep(0.2)
        return False

    synchronize = 0x00100000
    process_handle = ctypes.windll.kernel32.OpenProcess(synchronize, False, process_id)
    if not process_handle:
        return True
    try:
        wait_result = ctypes.windll.kernel32.WaitForSingleObject(
            process_handle,
            int(timeout * 1000),
        )
        return wait_result == 0
    finally:
        ctypes.windll.kernel32.CloseHandle(process_handle)


def _show_update_error(message):
    if os.name == "nt":
        ctypes.windll.user32.MessageBoxW(0, str(message), "업데이트 실패", 0x10)


def run_update_helper(target_path, previous_process_id):
    source_path = Path(sys.executable).resolve()
    target_path = Path(target_path).resolve()

    if not wait_for_process_exit(int(previous_process_id)):
        _show_update_error("기존 프로그램이 종료되지 않아 업데이트를 적용하지 못했습니다.")
        return 1

    deadline = time.monotonic() + UPDATE_WAIT_SECONDS
    while True:
        try:
            replace_executable(source_path, target_path)
            return 0
        except OSError as error:
            if time.monotonic() >= deadline:
                _show_update_error(f"실행 파일을 교체하지 못했습니다.\n\n{error}")
                return 1
            time.sleep(0.5)


class UpdateCheckWorker(QThread):
    update_available = pyqtSignal(object)
    up_to_date = pyqtSignal()
    failed = pyqtSignal(str)

    def __init__(self, current_version, parent=None):
        super().__init__(parent)
        self.current_version = current_version

    def run(self):
        try:
            release = fetch_latest_release()
            if is_newer_version(release.version, self.current_version):
                self.update_available.emit(release)
            else:
                self.up_to_date.emit()
        except Exception as error:
            self.failed.emit(str(error))


class UpdateDownloadWorker(QThread):
    progress = pyqtSignal(int)

    def __init__(self, release, parent=None):
        super().__init__(parent)
        self.release = release
        self.downloaded_path = None
        self.error = None

    def run(self):
        try:
            self.downloaded_path = download_release(
                self.release,
                update_download_path(),
                progress_callback=self.progress.emit,
            )
        except Exception as error:
            self.error = str(error)
