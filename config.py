import os
import configparser
from datetime import datetime
from PyQt5.QtWidgets import QDialog, QCheckBox, QVBoxLayout, QLabel, QHBoxLayout, QInputDialog, QPushButton, QWidget
from PyQt5.QtCore import Qt


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
        layout.setAlignment(Qt.AlignCenter)

        # 삭제시 확인 옵션 체크박스 생성
        remove_todo_alert_config = QWidget(self)
        remove_todo_alert_layout = QHBoxLayout(self)
        remove_todo_alert_layout.setAlignment(Qt.AlignCenter)
        remove_todo_alert_checkbox = QCheckBox('일정 삭제시 한번 더 확인', self)
        remove_todo_alert_checkbox.setChecked(self.parent.remove_todo_alert)
        remove_todo_alert_checkbox.setLayoutDirection(Qt.RightToLeft)
        remove_todo_alert_checkbox.clicked.connect(lambda: update_config(self.parent, 'Settings', 'remove_todo_alert', 1 if remove_todo_alert_checkbox.isChecked() else 0))
        remove_todo_alert_layout.addWidget(remove_todo_alert_checkbox)
        remove_todo_alert_config.setLayout(remove_todo_alert_layout)

        # 일정 남은 기한 표시 옵션 체크박스 생성
        show_remaining_time_config = QWidget(self)
        show_remaining_time_layout = QHBoxLayout(self)
        show_remaining_time_layout.setAlignment(Qt.AlignCenter)
        show_remaining_time_checkbox = QCheckBox('일정 남은 기한 표시', self)
        show_remaining_time_checkbox.setChecked(self.parent.show_remaining_time)
        show_remaining_time_checkbox.setLayoutDirection(Qt.RightToLeft)
        show_remaining_time_checkbox.clicked.connect(lambda: update_config(self.parent, 'Settings', 'show_remaining_time', 1 if show_remaining_time_checkbox.isChecked() else 0))
        show_remaining_time_layout.addWidget(show_remaining_time_checkbox)
        show_remaining_time_config.setLayout(show_remaining_time_layout)

        # 시간초과 경고 옵션 체크박스 생성
        timeout_warn_config = QWidget(self)
        timeout_warn_layout = QHBoxLayout(self)
        timeout_warn_layout.setAlignment(Qt.AlignCenter)
        self.timeout_warn_text = QLabel(f'일정 남은 기한이 {self.parent.timeout_warn}일 이하이면 경고', self)
        timeout_warn_layout.addWidget(self.timeout_warn_text)
        timeout_warn_text_input = QPushButton('수정', self) # 옵션 수정용 버튼
        timeout_warn_text_input.setFixedSize(40, 20)
        timeout_warn_text_input.clicked.connect(lambda: self.get_text_update(self.parent, 'Settings', 'timeout_warn'))
        timeout_warn_layout.addWidget(timeout_warn_text_input)
        timeout_warn_config.setLayout(timeout_warn_layout)

        layout.addWidget(remove_todo_alert_config)
        layout.addWidget(show_remaining_time_config)
        layout.addWidget(timeout_warn_config)

        self.setLayout(layout)


    # 옵션 수정용 텍스트 입력 받기
    def get_text_update(self, app, section, key):
        text, ok = QInputDialog.getText(self, '입력', '경고 기한 설정(일) ( -1 : 사용 안함 )')
        if ok and text:  # 사용자가 '확인'을 누르고, 입력값이 있을 때만 처리
            update_config(app, section, key, text)
            self.timeout_warn_text.setText(f'일정 남은 기한이 {self.parent.timeout_warn}일 이하이면 경고')


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
    app.timeout_warn = app.config.getint('Settings', 'timeout_warn', fallback = -1)
    app.lastchecktime = app.config.get('Variables', 'lastchecktime', fallback = datetime.now().strftime('%Y-%m-%d %H:%M:%S'))