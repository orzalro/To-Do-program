import sys
import util
import dialog as dia
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QListWidget, QCheckBox, QListWidgetItem, QHBoxLayout, QDialog, QLabel, QAbstractItemView
from datetime import datetime, timedelta

class DragList(QListWidget):
    # 드래그 위치에 따라 드래그드롭모드 변경
    def dragEnterEvent(self, event):
        if event.source() is self:
            self.setDragDropMode(QAbstractItemView.InternalMove)
        else:
            self.setDragDropMode(QAbstractItemView.DragDrop)
        super().dragEnterEvent(event)
    
    # 다른 리스트에 드롭시 드롭이벤트 오버라이드
    def dropEvent(self, event):
        source_list = event.source()
        if source_list is self:
            super().dropEvent(event) #같은 자리 드롭시 위젯 사라지는 문제 있음. 같은 자리인지 확인하는 코드 필요
            util.save_data(window)
        else:
            item = source_list.currentItem()
            widget = source_list.itemWidget(item)

            todo_title = item.data(0)
            checked = widget.layout().itemAt(widget.layout().count() - 3).widget().isChecked()
            todo_reset_method = widget.layout().itemAt(0).widget().text()
            todo_reset_time = widget.layout().itemAt(1).widget().text()
            resetparam0 = widget.layout().itemAt(2).widget().text()
            resetparam1 = widget.layout().itemAt(3).widget().text()

            todo_reset_method, todo_reset_time, resetparam0, resetparam1 = util.formatting_data(todo_reset_method, todo_reset_time, resetparam0, resetparam1)
            self.add_todo(todo_title, todo_reset_method, todo_reset_time, resetparam0, resetparam1, checked)
            source_list.remove_todo(item)
    

    def add_todo(self, todo_title, reset_method, reset_time, param0, param1, checked = 0):
        # todo_title이 비어 있지 않으면 리스트에 추가
        if todo_title:
            item = QListWidgetItem(todo_title)
            checkbox = QCheckBox()

            if checked:
                checkbox.setChecked(True)
            else:
                checkbox.setChecked(False)  # 초기 상태는 선택되지 않음
            
            # 디버그
            #checkbox.clicked.connect(lambda: print(self.todo_list.row(item))) # 체크시 해당 아이템이 리스트의 몇번째 아이템인지 출력
            #checkbox.clicked.connect(lambda: print(item.data(0))) # 체크시 해당 아이템의 이름 출력
            #checkbox.clicked.connect(lambda: print(checkbox.checkState())) # 체크시 해당 아이템의 체크상태 출력
            checkbox.clicked.connect(lambda: util.save_data(window)) # 체크시 save 예정

            remove_button = QPushButton('X')
            remove_button.setFixedSize(15, 15)
            remove_button.clicked.connect(lambda: self.remove_todo(item))  # 제거 버튼 클릭 시 remove_todo 메서드 실행

            widget = QWidget()
            item_layout = QHBoxLayout(widget)
            item_layout.setContentsMargins(130, 0, 0, 0)

            # 초기화 알고리즘에 따라 다른 정보 출력
            if reset_method == 0:
                methodlabel = QLabel('일간')
                reset_time = f'{reset_time // 60:02}:{reset_time % 60:02}'
                timelabel = QLabel(reset_time)
           
            elif reset_method == 1:
                methodlabel = QLabel('주간')
                weekday_dict = {0: '월요일', 1: '화요일', 2: '수요일', 3: '목요일', 4: '금요일', 5: '토요일', 6: '일요일'}
                param0label = QLabel(weekday_dict[param0])
                reset_time = f'{reset_time // 60:02}:{reset_time % 60:02}'
                timelabel = QLabel(reset_time)
            
            elif reset_method == 2:
                methodlabel = QLabel('월간')
                param0label = QLabel(f'{param0}일')
                reset_time = f'{reset_time // 60:02}:{reset_time % 60:02}'
                timelabel = QLabel(reset_time)
            
            elif reset_method == 3:
                methodlabel = QLabel('주기')
                next_reset_datetime = datetime.strptime(param1, '%Y-%m-%d %H:%M:%S') + timedelta(minutes = int(param0))

                difference = next_reset_datetime - datetime.now() # 다음 초기화까지의 차이
                if difference.days != 0:
                    cycle_label = f'{next_reset_datetime.strftime('%H:%M')} {difference.days}일 남음'
                else:
                    cycle_label = f'{next_reset_datetime.strftime('%H:%M')}'

                param0label = QLabel(f'{param0}') # 초기화 주기 int
                param0label.setVisible(False)
                param1label = QLabel(f'{param1}') # 기준 날짜 str
                param1label.setVisible(False)
                timelabel = QLabel(cycle_label)
                

            item_layout.addWidget(methodlabel)
            item_layout.addWidget(timelabel)
            if 'param0label' in locals(): item_layout.addWidget(param0label)
            if 'param1label' in locals(): item_layout.addWidget(param1label)

            item_layout.addWidget(checkbox)
            item_layout.addWidget(remove_button)
            item_layout.addStretch(1)

            self.addItem(item)
            self.setItemWidget(item, widget)
            
        else:
            print("할 일을 입력해주세요.")


    def remove_todo(self, item):
        row = self.row(item)
        self.takeItem(row)  # 리스트에서 해당 항목 제거
        util.save_data(window)


class MyApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()


    def init_ui(self):
        # 창의 제목과 크기 설정
        self.setWindowTitle('일정 관리 앱')
        self.setGeometry(490, 190, 1000, 600) #(x, y, width, height)

        # 그리드 레이아웃 생성
        self.main_layout = QGridLayout()
        self.show_grid(2, 3)
        
        # 레이아웃을 창에 설정
        self.setLayout(self.main_layout)
        util.load_data(self)


    def open_add_todo_dialog(self, row, col):
        dialog = dia.AddTodoDialog()
        if dialog.exec_() == QDialog.Accepted:
            # 다이얼로그에서 받은 데이터
            todo_title = dialog.title_input.text()
            todo_reset_method, todo_reset_time, resetparam0, resetparam1 = dialog.get_data()
            self.todo_list[f'list{row * 3 + col}'].add_todo(todo_title, todo_reset_method, todo_reset_time, resetparam0, resetparam1)
            util.save_data(self)


    def show_grid(self, row, col):
        self.grid_row = row
        self.grid_col = col
        
        # 일정 리스트 (DragList(QListWidget))
        self.todo_list = {}
        for i in range(self.grid_row):
            for j in range(self.grid_col):
                list_vbox = QVBoxLayout()
                list_vbox.setSpacing(0)
                list_vbox.setContentsMargins(0, 10, 0, 10) # (좌, 상, 우, 하) 여백

                self.todo_list[f'list{i * 3 + j}'] = DragList(self)
                self.todo_list[f'list{i * 3 + j}'].setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
                list_vbox.addWidget(self.todo_list[f'list{i * 3 + j}'])

                # 일정 추가 버튼
                add_button = QPushButton('일정 추가', self) 
                add_button.clicked.connect(lambda _, row = i, col = j: self.open_add_todo_dialog(row, col)) # 버튼 클릭 시 add_todo 메소드 실행을 위한 정보 입력을 받는 다이얼로그 창을 띄움
                list_vbox.addWidget(add_button)

                self.main_layout.addLayout(list_vbox, i * 2, j * 2)


    def show_todo(self, row, col,  todo_title, todo_reset_method, todo_reset_time, resetparam0, resetparam1, checked):
        self.todo_list[f'list{row * 3 + col}'].add_todo(todo_title, todo_reset_method, todo_reset_time, resetparam0, resetparam1, checked)


app = QApplication(sys.argv)
window = MyApp()
window.show()
sys.exit(app.exec_())