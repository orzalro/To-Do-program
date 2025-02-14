import sys
import util
import dialog as dia
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget, QCheckBox, QListWidgetItem, QHBoxLayout, QDialog, QLabel, QAbstractItemView


class DragList(QListWidget):
    def dragEnterEvent(self, event):
        if event.source() is self:
            self.setDragDropMode(QAbstractItemView.InternalMove)
        else:
            self.setDragDropMode(QAbstractItemView.DragDrop)
        super().dragEnterEvent(event)
    

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

            todo_reset_method, todo_reset_time, resetparam0 = util.formatting_data(todo_reset_method, todo_reset_time, resetparam0)
            self.add_todo(todo_title, todo_reset_method, todo_reset_time, resetparam0, checked)
            source_list.remove_todo(item)
    

    def add_todo(self, todo_title, reset_method, reset_time, param, checked = 0):
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
            item_layout.setContentsMargins(100, 0, 0, 0)

            if reset_method == 0:
                methodlabel = QLabel('일간')
            elif reset_method == 1:
                methodlabel = QLabel('주간')
                weekday_dict = {0: '월요일 (Monday)', 1: '화요일', 2: '수요일', 3: '목요일', 4: '금요일', 5: '토요일', 6: '일요일'}
                paramlabel = QLabel(weekday_dict[param])
            elif reset_method == 2:
                methodlabel = QLabel('월간')
                paramlabel = QLabel(f'{param}일')
            reset_time = f'{reset_time // 60:02}:{reset_time % 60:02}'

            timelabel = QLabel(reset_time)
            item_layout.addWidget(methodlabel)
            item_layout.addWidget(timelabel)
            if 'paramlabel' in locals():
                item_layout.addWidget(paramlabel)

            item_layout.addWidget(checkbox)
            item_layout.addWidget(remove_button)
            item_layout.addStretch(1)

            # 체크박스를 항목에 추가
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
        self.setGeometry(760, 290, 400, 300)

        # 레이아웃 생성
        layout = QVBoxLayout()
        
        # Todo 추가 버튼 (QPushButton)
        add_button = QPushButton('일정 추가', self)
        add_button.clicked.connect(self.open_add_todo_dialog)  # 버튼 클릭 시 add_todo 메소드 실행을 위한 정보 입력을 받는 다이얼로그 창을 띄움

        # Todo 리스트 (QListWidget)
        self.todo_list = DragList(self)
        self.todo_list.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)

        # 레이아웃에 위젯 추가
        layout.addWidget(add_button)
        layout.addWidget(self.todo_list)

        self.todo_list2 = DragList(self)
        self.todo_list2.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
        layout.addWidget(self.todo_list2)

        # 레이아웃을 창에 설정
        self.setLayout(layout)
        util.load_data(self)


    def open_add_todo_dialog(self):
        dialog = dia.AddTodoDialog()
        if dialog.exec_() == QDialog.Accepted:
            # 다이얼로그에서 받은 데이터
            todo_title = dialog.title_input.text()
            todo_reset_method, todo_reset_time, resetparam0 = dialog.get_data()
            self.todo_list.add_todo(todo_title, todo_reset_method, todo_reset_time, resetparam0)
            util.save_data(self)


    def show_todo(self, todo_title, todo_reset_method, todo_reset_time, resetparam0, checked):
        self.todo_list.add_todo(todo_title, todo_reset_method, todo_reset_time, resetparam0, checked)


app = QApplication(sys.argv)
window = MyApp()
window.show()
sys.exit(app.exec_())