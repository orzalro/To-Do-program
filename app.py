import sys
import util
import config
import dialog as dia
import draglist
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QDialog, QAbstractItemView, QAction, QMainWindow
from PyQt5.QtCore import QTimer, QTime


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        config.read_config(self)
        self.init_ui()
        self.auto_save()


    def init_ui(self):
        # 메뉴바 생성 및 File 메뉴 생성
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu('&File')

        # Exit 액션 생성
        exitAction = QAction('종료', self)
        exitAction.setShortcut('Ctrl+W')
        exitAction.triggered.connect(self.close)
        filemenu.addAction(exitAction)

        # Config 메뉴 생성 및 환경설정 액션 생성
        configmenu = menubar.addMenu('&Config')
        configAction = QAction('환경 설정', self)
        configAction.triggered.connect(lambda: self.open_config_dialog())
        configmenu.addAction(configAction)

        # 창의 제목과 크기 설정
        self.setWindowTitle('일정 관리 앱')
        self.resize(self.window_width, self.window_height) #(x, y, width, height)

        # 화면 중앙 정렬
        self.show()
        app_frame = self.frameGeometry()
        center_pos = QApplication.screenAt(self.pos()).availableGeometry().center()
        app_frame.moveCenter(center_pos)
        self.move(app_frame.topLeft())

        self.create_todo_list()
        self.show_grid()
        
        util.load_data(self)


    def open_config_dialog(self):
        dialog = config.ConfigDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            print()


    def open_add_todo_dialog(self, row, col):
        dialog = dia.AddTodoDialog()
        if dialog.exec_() == QDialog.Accepted:
            # 다이얼로그에서 받은 데이터
            todo_title = dialog.title_input.text()
            todo_reset_method, todo_reset_time, resetparam0, resetparam1 = dialog.get_data()
            todo_list = self.todo_list[f'list{row * self.grid_col + col}']
            todo_list.add_todo(todo_title, todo_reset_method, todo_reset_time, resetparam0, resetparam1)

            util.save_data(self)


    def create_todo_list(self):
        self.todo_list = {}
        for i in range(self.grid_row):
            for j in range(self.grid_col):
                # 일정 리스트 (DragList(QListWidget))
                self.todo_list[f'list{i * self.grid_col + j}'] = draglist.DragList(self)
                self.todo_list[f'list{i * self.grid_col + j}'].setDragDropMode(QAbstractItemView.InternalMove)


    def show_grid(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 그리드 레이아웃 생성
        self.central_widget.main_layout = QGridLayout()

        for i in range(self.grid_row):
            self.central_widget.main_layout.setRowMinimumHeight(i, 200) # 행 최소높이 설정
            for j in range(self.grid_col):
                self.central_widget.main_layout.setColumnMinimumWidth(j, 300) # 열 최소너비 설정
                list_vbox = QVBoxLayout()
                list_vbox.setSpacing(0)
                list_vbox.setContentsMargins(0, 10, 0, 10) # (좌, 상, 우, 하) 여백
                list_vbox.addWidget(self.todo_list[f'list{i * self.grid_col + j}'])
                # 일정 추가 버튼
                add_button = QPushButton('일정 추가', self)
                # 버튼 클릭 시 add_todo 메소드 실행을 위한 정보 입력을 받는 다이얼로그 창을 띄움
                add_button.clicked.connect(lambda _, row = i, col = j: self.open_add_todo_dialog(row, col)) 
                list_vbox.addWidget(add_button)
                self.central_widget.main_layout.addLayout(list_vbox, i, j)
        
        # 레이아웃을 창에 설정
        self.central_widget.setLayout(self.central_widget.main_layout)


    def show_todo(self, row, col,  todo_title, todo_reset_method, todo_reset_time, resetparam0, resetparam1, checked):
        self.todo_list[f'list{row * 3 + col}'].add_todo(todo_title, todo_reset_method, todo_reset_time, resetparam0, resetparam1, checked)


    def resizeEvent(self, event):
        # 창 크기가 변경될 때마다 현재 크기를 저장
        self.config['Settings']['window_width'] = str(self.width())
        self.config['Settings']['window_height'] = str(self.height())
        super().resizeEvent(event)


    def auto_save(self):
        now = QTime.currentTime()
        seconds_until_next_minute = 60 - now.second()  # 다음 00초까지 남은 시간
        QTimer.singleShot(seconds_until_next_minute * 1000, lambda: self.run_auto_save())  # 다음 정각에 실행


    def run_auto_save(self):
        util.save_data(self)
        self.auto_save()  # 다음 세이브 예약
    

    def closeEvent(self, event):
        util.save_data(self)

        # # 메시지박스를 띄워 사용자에게 확인 요청
        # reply = QMessageBox.question(self, '종료 확인', '종료하시겠습니까?', 
        #                              QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
        
        # if reply == QMessageBox.Yes:
        #     event.accept()  # 창을 종료
        # else:
        #     event.ignore()  # 창을 종료하지 않음


app = QApplication(sys.argv)
window = MyApp()
sys.exit(app.exec_())