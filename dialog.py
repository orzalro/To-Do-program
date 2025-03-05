from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QHBoxLayout, QDialog, QFormLayout, QDialogButtonBox, QStackedWidget, QLabel, QCalendarWidget
from PyQt5.QtWidgets import QTimeEdit, QAbstractSpinBox
from PyQt5.QtCore import QDate, QTime
from PyQt5.QtGui import QFont
from datetime import datetime


class AddTodoDialog(QDialog):
    def __init__(self, todo_title='',todo_reset_method=0, todo_reset_time=0, resetparam0=-1, resetparam1=-1):
        super().__init__()
        self.todo_reset_time = int(todo_reset_time)
        self.resetparam0 = resetparam0
        self.resetparam1 = resetparam1
        self.init_ui(todo_title, todo_reset_method)


    def init_ui(self, todo_title, todo_reset_method):
        # 창 설정
        self.setWindowTitle('할 일 추가')
        self.setGeometry(810, 340, 300, 400)

        # 레이아웃 설정
        layout = QFormLayout(self)
        button_layout = QHBoxLayout()

        self.title_input = QLineEdit(self)
        self.title_input.setText(todo_title)
        self.title_input.setMaxLength(10)
        layout.addRow('제목:', self.title_input)

        # 각 페이지별 레이아웃 설정
        self.stacked_widget = QStackedWidget()
        self.daily_layout = QWidget()
        self.weekly_layout = QWidget()
        self.monthly_layout = QWidget()
        self.cycle_layout = QWidget()

        self.init_daily_layout()
        self.init_weekly_layout()
        self.init_monthly_layout()
        self.init_cycle_layout()

        self.stacked_widget.addWidget(self.daily_layout)
        self.stacked_widget.addWidget(self.weekly_layout)
        self.stacked_widget.addWidget(self.monthly_layout)
        self.stacked_widget.addWidget(self.cycle_layout)

        # 버튼 클릭시 레이아웃 변경
        self.daily_btn = QPushButton('daily')
        self.daily_btn.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(0), self.update_button_styles(0), self.update_button_state()))
        button_layout.addWidget(self.daily_btn)

        self.weekly_btn = QPushButton('weekly')
        self.weekly_btn.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(1), self.update_button_styles(1), self.update_button_state()))
        button_layout.addWidget(self.weekly_btn)

        self.monthly_btn = QPushButton('monthly')
        self.monthly_btn.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(2), self.update_button_styles(2), self.update_button_state()))
        button_layout.addWidget(self.monthly_btn)

        self.cycle_btn = QPushButton('cycle')
        self.cycle_btn.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(3), self.update_button_styles(3), self.update_button_state()))
        button_layout.addWidget(self.cycle_btn)

        self.stacked_widget.setCurrentIndex(todo_reset_method)
        self.update_button_styles(todo_reset_method) # 초기 선택된 버튼 표시

        layout.addRow(button_layout)
        layout.addWidget(self.stacked_widget)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        layout.addWidget(self.button_box)

        self.ok_button = self.button_box.button(QDialogButtonBox.Ok)
        self.ok_button.setEnabled(False)
        self.update_button_state()  # 초기 버튼 상태 설정

        self.setLayout(layout)

        for line_edit in self.findChildren(QLineEdit):
            line_edit.textChanged.connect(self.update_button_state)


    def update_button_state(self):
        # 입력 필드가 비어 있으면 OK 버튼을 비활성화
        current_index = self.stacked_widget.currentIndex()
        if current_index == 0: state = 1
        elif current_index == 1: state = bool(self.weekly_resetparam0.text().strip())
        elif current_index == 2: state = bool(self.monthly_resetparam0.text().strip())
        elif current_index == 3: state = bool(self.cycle_resetparam0.text().strip())
        state = bool(self.title_input.text().strip() and state)
        self.ok_button.setEnabled(state)


    def update_button_styles(self, active_index):
        # 모든 버튼 초기화 (기본 스타일)
        btn_qss = '''
        QPushButton {
            border-width: 1px;
            border-radius: 6px;
            border-bottom-color: rgb(150,150,150);
            border-right-color: rgb(165,165,165);
            border-left-color: rgb(165,165,165);
            border-top-color: rgb(180,180,180);
            border-style: solid;
            padding: 4px;
            background-color: qlineargradient(spread:pad, x1:0.5, y1:1, x2:0.5, y2:0, stop:0 rgba(220, 220, 220, 255), stop:1 rgba(255, 255, 255, 255));
        }

        QPushButton:hover {
            border-top-color: rgb(180,230,255);
            border-right-color: qlineargradient(spread:pad, x1:0, y1:1, x2:1, y2:0, stop:0 rgba(173, 216, 230, 255), stop:1 rgba(180, 230, 255, 255));
            border-left-color:  qlineargradient(spread:pad, x1:1, y1:0, x2:0, y2:0, stop:0 rgba(173, 216, 230, 255), stop:1 rgba(180, 230, 255, 255));
            border-bottom-color: rgb(173,216,230);
        }
        '''
        self.daily_btn.setStyleSheet(btn_qss)
        self.weekly_btn.setStyleSheet(btn_qss)
        self.monthly_btn.setStyleSheet(btn_qss)
        self.cycle_btn.setStyleSheet(btn_qss)

        # 현재 활성화된 버튼 강조 (배경색 변경 및 스타일 설정)
        if active_index == 0:
            self.daily_btn.setStyleSheet('border-radius: 10px; padding: 6px; background-color: lightblue;')
        elif active_index == 1:
            self.weekly_btn.setStyleSheet('border-radius: 10px; padding: 6px; background-color: lightblue;')
        elif active_index == 2:
            self.monthly_btn.setStyleSheet('border-radius: 10px; padding: 6px; background-color: lightblue;')
        elif active_index == 3:
            self.cycle_btn.setStyleSheet('border-radius: 10px; padding: 6px; background-color: lightblue;')

    
    def init_time_edit(self):
        time_edit = QTimeEdit(self)
        time_edit.setTime(QTime(self.todo_reset_time // 60, self.todo_reset_time % 60))
        time_edit.setButtonSymbols(QAbstractSpinBox.NoButtons)  # 위/아래 버튼 숨김
        time_edit.setKeyboardTracking(False)  # 키 입력이 완료될 때만 업데이트

        # 폰트 크기 변경 및 스타일 변경
        font = QFont('Arial', 15, QFont.Bold)  # 폰트 크기 조정
        time_edit.setFont(font)
        time_edit.setMinimumHeight(30)  # 높이
        time_edit.setMaximumWidth(150)  # 너비
        time_edit.setStyleSheet('padding: 5px; border: 2px solid #ccc; border-radius: 5px;')

        return time_edit
    
    # 선택된 알고리즘에 따라 입력필드 변경
    def init_daily_layout(self):
        layout = QFormLayout()
        self.daily_reset_time = self.init_time_edit()
        layout.addRow('초기화 시간:', self.daily_reset_time)
        self.daily_layout.setLayout(layout)


    def init_weekly_layout(self):
        layout = QFormLayout()
        self.weekly_reset_time = self.init_time_edit()
        layout.addRow('초기화 시간:', self.weekly_reset_time)
        self.weekly_resetparam0 = QLineEdit(self)
        self.weekly_resetparam0.setText(str(self.resetparam0) if self.resetparam0 != -1 else '')
        self.weekly_resetparam0.setPlaceholderText('0-6(월-일)')
        layout.addRow('초기화 요일:', self.weekly_resetparam0)
        self.weekly_layout.setLayout(layout)


    def init_monthly_layout(self):
        layout = QFormLayout()
        self.monthly_reset_time = self.init_time_edit()
        layout.addRow('초기화 시간:', self.monthly_reset_time)
        self.monthly_resetparam0 = QLineEdit(self)
        self.monthly_resetparam0.setText(str(self.resetparam0 if self.resetparam0 != -1 else ''))
        self.monthly_resetparam0.setPlaceholderText('1-31(일)')
        layout.addRow('초기화 날짜:', self.monthly_resetparam0)
        self.monthly_layout.setLayout(layout)


    def init_cycle_layout(self):
        if self.resetparam1 != -1:
            self.todo_reset_time = int(self.resetparam1[-8:-6]) * 60 + int(self.resetparam1[-5:-3])
            default_date = QDate.fromString(self.resetparam1[:10], 'yyyy-MM-dd')
        else:
            default_date = QDate.currentDate()
        layout = QFormLayout()
        self.cycle_reset_time = self.init_time_edit()
        layout.addRow('기준 시간:', self.cycle_reset_time)
        self.cycle_resetparam0 = QLineEdit(self)
        self.cycle_resetparam0.setText(str(self.resetparam0) if self.resetparam0 != -1 else '')
        self.cycle_resetparam0.setPlaceholderText('(분)')
        layout.addRow('초기화 주기:', self.cycle_resetparam0)
        self.cycle_resetparam1 = QLabel('기준 날짜를 선택하세요', self)
        self.cycle_calendar = QCalendarWidget(self)
        self.cycle_calendar.setSelectedDate(default_date)
        self.show_calender_date(self.cycle_calendar.selectedDate())
        self.cycle_calendar.clicked.connect(self.show_calender_date)
        layout.addWidget(self.cycle_calendar)
        layout.addWidget(self.cycle_resetparam1)
        self.cycle_layout.setLayout(layout)
    

    def show_calender_date(self, date):
        self.cycle_resetparam1.setText(f'기준 날짜: {date.toString('yyyy-MM-dd')}')


    # 다이얼로그 데이터 리턴
    def get_data(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index == 0:
            time = self.daily_reset_time.time()
            reset_time = time.hour() * 60 + time.minute()
            return current_index, reset_time, -1, -1
        elif current_index == 1:
            time = self.weekly_reset_time.time()
            reset_time = time.hour() * 60 + time.minute()
            return current_index, reset_time, int(self.weekly_resetparam0.text()), -1
        elif current_index == 2:
            time = self.monthly_reset_time.time()
            reset_time = time.hour() * 60 + time.minute()
            return current_index, reset_time, int(self.monthly_resetparam0.text()), -1
        elif current_index == 3:
            reset_time = self.cycle_reset_time.time().toPyTime()
            base_datetime = datetime.combine(datetime.strptime(self.cycle_resetparam1.text()[7:], '%Y-%m-%d'), reset_time)
            return current_index, -1, int(self.cycle_resetparam0.text()), base_datetime.strftime('%Y-%m-%d %H:%M:%S')
        return ''
