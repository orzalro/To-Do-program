from PyQt5.QtWidgets import QWidget, QLineEdit, QPushButton, QHBoxLayout, QDialog, QFormLayout, QDialogButtonBox, QStackedWidget, QLabel, QCalendarWidget, QTimeEdit
from PyQt5.QtCore import QDate
from datetime import datetime, time

class AddTodoDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()


    def init_ui(self):
        # 창 설정
        self.setWindowTitle('할 일 추가')
        self.setGeometry(810, 340, 300, 200)

        # 레이아웃 설정
        layout = QFormLayout(self)
        button_layout = QHBoxLayout()

        self.title_input = QLineEdit(self)
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
        self.daily_btn.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(0), self.update_button_styles(0)))
        button_layout.addWidget(self.daily_btn)

        self.weekly_btn = QPushButton('weekly')
        self.weekly_btn.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(1), self.update_button_styles(1)))
        button_layout.addWidget(self.weekly_btn)

        self.monthly_btn = QPushButton('monthly')
        self.monthly_btn.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(2), self.update_button_styles(2)))
        button_layout.addWidget(self.monthly_btn)

        self.cycle_btn = QPushButton('cycle')
        self.cycle_btn.clicked.connect(lambda: (self.stacked_widget.setCurrentIndex(3), self.update_button_styles(3)))
        button_layout.addWidget(self.cycle_btn)

        self.update_button_styles(0) # 초기 선택된 버튼 표시
        layout.addRow(button_layout)
        layout.addWidget(self.stacked_widget)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)


    def update_button_styles(self, active_index):
        # 모든 버튼 초기화 (기본 스타일)
        self.daily_btn.setStyleSheet("background-color: none;")
        self.weekly_btn.setStyleSheet("background-color: none;")
        self.monthly_btn.setStyleSheet("background-color: none;")
        self.cycle_btn.setStyleSheet("background-color: none;")
        
        # 현재 활성화된 버튼 강조 (배경색 변경 및 스타일 설정)
        if active_index == 0:
            self.daily_btn.setStyleSheet("border-radius: 10px; padding: 5px; background-color: lightblue;")
        elif active_index == 1:
            self.weekly_btn.setStyleSheet("border-radius: 10px; padding: 5px; background-color: lightblue;")
        elif active_index == 2:
            self.monthly_btn.setStyleSheet("border-radius: 10px; padding: 5px; background-color: lightblue;")
        elif active_index == 3:
            self.cycle_btn.setStyleSheet("border-radius: 10px; padding: 5px; background-color: lightblue;")


    # 선택된 알고리즘에 따라 입력필드 변경
    def init_daily_layout(self):
        layout = QFormLayout()
        self.daily_reset_time = QLineEdit(self)
        self.daily_reset_time.setPlaceholderText('0-1439(분)')
        layout.addRow('초기화 시간:', self.daily_reset_time)
        self.daily_layout.setLayout(layout)


    def init_weekly_layout(self):
        layout = QFormLayout()
        self.weekly_reset_time = QLineEdit(self)
        self.weekly_reset_time.setPlaceholderText('0-1439(분)')
        layout.addRow('초기화 시간:', self.weekly_reset_time)
        self.weekly_resetparam0 = QLineEdit(self)
        self.weekly_resetparam0.setPlaceholderText('0-6(월-일)')
        layout.addRow('초기화 요일:', self.weekly_resetparam0)
        self.weekly_layout.setLayout(layout)


    def init_monthly_layout(self):
        layout = QFormLayout()
        self.monthly_reset_time = QLineEdit(self)
        self.monthly_reset_time.setPlaceholderText('0-1439(분)')
        layout.addRow('초기화 시간:', self.monthly_reset_time)
        self.monthly_resetparam0 = QLineEdit(self)
        self.monthly_resetparam0.setPlaceholderText('1-31(일)')
        layout.addRow('초기화 날짜:', self.monthly_resetparam0)
        self.monthly_layout.setLayout(layout)


    def init_cycle_layout(self):
        layout = QFormLayout()
        self.cycle_resetparam0 = QLineEdit(self)
        self.cycle_resetparam0.setPlaceholderText('(분)')
        layout.addRow('초기화 주기:', self.cycle_resetparam0)
        self.cycle_reset_time = QLineEdit(self)
        self.cycle_reset_time.setPlaceholderText('0-1439(분)')
        layout.addRow('기준 시간:', self.cycle_reset_time)
        self.cycle_resetparam1 = QLabel("기준 날짜를 선택하세요", self)
        self.cycle_calendar = QCalendarWidget(self)
        self.show_calender_date(QDate.currentDate())
        self.cycle_calendar.clicked.connect(self.show_calender_date)
        layout.addWidget(self.cycle_calendar)
        layout.addWidget(self.cycle_resetparam1)
        self.cycle_layout.setLayout(layout)
    
    def show_calender_date(self, date):
        self.cycle_resetparam1.setText(f"기준 날짜: {date.toString('yyyy-MM-dd')}")

    # 다이얼로그 데이터 리턴
    def get_data(self):
        current_index = self.stacked_widget.currentIndex()
        if current_index == 0:
            return current_index, int(self.daily_reset_time.text()), -1
        elif current_index == 1:
            return current_index, int(self.weekly_reset_time.text()), int(self.weekly_resetparam0.text()), -1
        elif current_index == 2:
            return current_index, int(self.monthly_reset_time.text()), int(self.monthly_resetparam0.text()), -1
        elif current_index == 3:
            reset_time = time(int(self.cycle_reset_time.text()) // 60, int(self.cycle_reset_time.text()) % 60, 0)
            base_datetime = datetime.combine(datetime.strptime(self.cycle_resetparam1.text()[7:], '%Y-%m-%d'), reset_time)
            return current_index, -1, int(self.cycle_resetparam0.text()), base_datetime.strftime('%Y-%m-%d %H:%M:%S')
        return ""
