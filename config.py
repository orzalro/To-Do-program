import os
import configparser
from datetime import datetime
from PyQt5.QtWidgets import QDialog, QCheckBox, QVBoxLayout


CONFIG_FILE_PATH = 'data/config.ini'


class ConfigDialog(QDialog):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()


    def init_ui(self):
        # 창 설정
        self.setWindowTitle('환경설정')
        self.setGeometry(810, 340, 300, 200)

        layout = QVBoxLayout(self)

        # 삭제시 확인 옵션 체크박스 생성
        remove_todo_alert_checkbox = QCheckBox('일정 삭제시 한번 더 확인', self)
        remove_todo_alert_checkbox.setChecked(self.parent.remove_todo_alert)
        remove_todo_alert_checkbox.clicked.connect(lambda: update_config(self.parent, 'Settings', 'remove_todo_alert', 1 if remove_todo_alert_checkbox.isChecked() else 0))
        layout.addWidget(remove_todo_alert_checkbox)

        # 일정 남은 기한 표시 옵션 체크박스 생성
        show_remaining_time_checkbox = QCheckBox('일정 남은 기한 표시', self)
        show_remaining_time_checkbox.setChecked(self.parent.show_remaining_time)
        show_remaining_time_checkbox.clicked.connect(lambda: update_config(self.parent, 'Settings', 'show_remaining_time', 1 if show_remaining_time_checkbox.isChecked() else 0))
        layout.addWidget(show_remaining_time_checkbox)

        # 시간초과 경고 옵션 체크박스 생성
        timeout_warn_checkbox = QCheckBox('시간초과 경고', self)
        timeout_warn_checkbox.setChecked(self.parent.timeout_warn)
        timeout_warn_checkbox.clicked.connect(lambda: update_config(self.parent, 'Settings', 'timeout_warn', 1 if timeout_warn_checkbox.isChecked() else 0))
        layout.addWidget(timeout_warn_checkbox)

        self.setLayout(layout)


def update_config(app, section, key, value):
    #config 값을 업데이트하고 즉시 저장하는 함수
    app.config.set(section, key, str(value))  # 문자열로 변환하여 저장
    setattr(app, f'{key}', value)

    # 변경된 설정을 config.ini 파일에 저장
    with open(CONFIG_FILE_PATH, 'w') as configfile:
        app.config.write(configfile)

    print(f'설정 변경됨: [{section}] {key} = {value}')  # 디버깅용


def write_config(app):
    with open(CONFIG_FILE_PATH, 'w') as configfile:
        app.config.write(configfile)


def read_config(app):
    app.config = configparser.ConfigParser()
    if os.path.exists(CONFIG_FILE_PATH):
        app.config.read(CONFIG_FILE_PATH)
    else: # 경로에 config파일이 없을 시 생성 후 read_config 재호출
        app.config['Settings'] = {}
        app.config['Variables'] = {}
        write_config(app)
        read_config(app)
    app.window_width = app.config.getint('Settings', 'window_width', fallback = 1000)
    app.window_height = app.config.getint('Settings', 'window_height', fallback = 600)
    app.grid_col = app.config.getint('Settings', 'grid_col', fallback = 3)
    app.grid_row = app.config.getint('Settings', 'grid_row', fallback = 2)
    app.remove_todo_alert = app.config.getint('Settings', 'remove_todo_alert', fallback = 0)
    app.show_remaining_time = app.config.getint('Settings', 'show_remaining_time', fallback = 0)
    app.timeout_warn = app.config.getint('Settings', 'timeout_warn', fallback = 0)
    app.lastchecktime = app.config.get('Variables', 'lastchecktime', fallback = datetime.now().strftime('%Y-%m-%d %H:%M:%S'))