import os
import configparser
import util
import draglist
from datetime import datetime
from PyQt5.QtWidgets import QDialog, QCheckBox, QVBoxLayout, QLabel, QHBoxLayout, QInputDialog, QPushButton, QWidget, QAbstractItemView
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
        remove_todo_alert_layout = QHBoxLayout()
        remove_todo_alert_layout.setAlignment(Qt.AlignCenter)
        remove_todo_alert_checkbox = QCheckBox('일정 삭제시 한번 더 확인', self)
        remove_todo_alert_checkbox.setChecked(self.parent.remove_todo_alert)
        remove_todo_alert_checkbox.setLayoutDirection(Qt.RightToLeft)
        remove_todo_alert_checkbox.clicked.connect(lambda: update_config(self.parent, 'Settings', 'remove_todo_alert', 1 if remove_todo_alert_checkbox.isChecked() else 0))
        remove_todo_alert_layout.addWidget(remove_todo_alert_checkbox)
        remove_todo_alert_config.setLayout(remove_todo_alert_layout)

        # 일정 남은 기한 표시 옵션 체크박스 생성
        show_remaining_time_config = QWidget(self)
        show_remaining_time_layout = QHBoxLayout()
        show_remaining_time_layout.setAlignment(Qt.AlignCenter)
        show_remaining_time_checkbox = QCheckBox('일정 남은 기한 표시', self)
        show_remaining_time_checkbox.setChecked(self.parent.show_remaining_time)
        show_remaining_time_checkbox.setLayoutDirection(Qt.RightToLeft)
        show_remaining_time_checkbox.clicked.connect(lambda: update_config(self.parent, 'Settings', 'show_remaining_time', 1 if show_remaining_time_checkbox.isChecked() else 0))
        show_remaining_time_layout.addWidget(show_remaining_time_checkbox)
        show_remaining_time_config.setLayout(show_remaining_time_layout)

        # 시간초과 경고 옵션 체크박스 생성
        timeout_warn_config = QWidget(self)
        timeout_warn_layout = QHBoxLayout()
        timeout_warn_layout.setAlignment(Qt.AlignCenter)
        self.timeout_warn_text = QLabel(f'일정 남은 기한이 {self.parent.timeout_warn}일 이하이면 경고', self)
        timeout_warn_layout.addWidget(self.timeout_warn_text)
        timeout_warn_text_input = QPushButton('기한 수정', self) # 옵션 수정용 버튼
        timeout_warn_text_input.setFixedSize(60, 20)
        timeout_warn_text_input.clicked.connect(lambda: self.get_text_update(self.parent, 'Settings', 'timeout_warn'))
        timeout_warn_layout.addWidget(timeout_warn_text_input)
        timeout_warn_config.setLayout(timeout_warn_layout)

        # 그리드 행, 열 설정
        grid_config = QWidget(self)
        grid_config_layout = QHBoxLayout()
        grid_config_layout.setAlignment(Qt.AlignCenter)
        self.grid_config_text = QLabel(f'현재 그리드 {self.parent.grid_row}행 x {self.parent.grid_col}열', self)
        grid_config_layout.addWidget(self.grid_config_text)
        grid_row_text_input = QPushButton('행 수정', self)
        grid_row_text_input.setFixedSize(50, 20)
        grid_row_text_input.clicked.connect(lambda: (self.get_text_update(self.parent, 'Settings', 'grid_row'), self.set_grid(self.parent, self.parent.grid_row, self.parent.grid_col)))
        grid_col_text_input = QPushButton('열 수정', self)
        grid_col_text_input.setFixedSize(50, 20)
        grid_col_text_input.clicked.connect(lambda: (self.get_text_update(self.parent, 'Settings', 'grid_col'), self.set_grid(self.parent, self.parent.grid_row, self.parent.grid_col)))
        grid_config_layout.addWidget(grid_row_text_input)
        grid_config_layout.addWidget(grid_col_text_input)
        grid_config.setLayout(grid_config_layout)

        layout.addWidget(remove_todo_alert_config)
        layout.addWidget(show_remaining_time_config)
        layout.addWidget(timeout_warn_config)
        layout.addWidget(grid_config)

        self.setLayout(layout)


    # 옵션 수정용 텍스트 입력 받기
    def get_text_update(self, app, section, key):
        text, ok = QInputDialog.getText(self, '입력', '값을 입력하시오.', text = str(getattr(app, key)))
        if ok and text:  # 사용자가 '확인'을 누르고, 입력값이 있을 때만 처리
            update_config(app, section, key, text)
            self.timeout_warn_text.setText(f'일정 남은 기한이 {self.parent.timeout_warn}일 이하이면 경고')
            self.grid_config_text.setText(f'현재 그리드 {self.parent.grid_row}행 x {self.parent.grid_col}열')


    def set_grid(self, app, row, col):
        app.grid_row = int(row)
        app.grid_col = int(col)

        if app.grid_row * app.grid_col < len(app.todo_list):  # 그리드 크기가 작아지면 남은 일정을 다음 그리드로 이동
            for i in range(app.grid_row * app.grid_col, len(app.todo_list)):
                todo_list = app.todo_list[f'list{i}']
                for j in range(todo_list.count()):
                    item = todo_list.item(j)
                    widget = todo_list.itemWidget(item)

                    todo_title = item.data(0)
                    checked = widget.findChild(QCheckBox, 'checkbox').isChecked()
                    todo_reset_method = widget.findChild(QLabel, 'methodlabel').text()
                    todo_reset_time = widget.findChild(QLabel, 'timelabel').text()
                    resetparam0 = widget.findChild(QLabel, 'param0label').text()
                    resetparam1 = widget.findChild(QLabel, 'param1label').text()

                    todo_reset_method, todo_reset_time, resetparam0, resetparam1 = util.formatting_data(todo_reset_method, todo_reset_time, resetparam0, resetparam1)
                    app.todo_list[f'list{app.grid_row * app.grid_col - 1}'].add_todo(todo_title, todo_reset_method, todo_reset_time, resetparam0, resetparam1, checked)
                app.todo_list[f'list{i}'].clear()  # 기존 리스트 비우기
                del app.todo_list[f'list{i}']  # 기존 리스트 삭제
        else:
            for i in range(app.grid_row * app.grid_col):
                if f'list{i}' not in app.todo_list:
                    app.todo_list[f'list{i}'] = draglist.DragList(app)
                    app.todo_list[f'list{i}'].setDragDropMode(QAbstractItemView.InternalMove)
        app.show_grid()


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