import util
from PyQt5.QtWidgets import QWidget, QPushButton, QListWidget, QCheckBox, QListWidgetItem, QHBoxLayout, QLabel, QAbstractItemView, QMessageBox
from datetime import datetime, timedelta

class DragList(QListWidget):
    def __init__(self, parent = ...):
        super().__init__(parent)
        self.parent = parent

    # 드래그 위치에 따라 드래그드롭모드 변경
    def dragEnterEvent(self, event):
        if event.source() is self:
            self.setDragDropMode(QAbstractItemView.InternalMove)
        else:
            self.setDragDropMode(QAbstractItemView.DragDrop)
        super().dragEnterEvent(event)
    

    # 드롭이벤트 오버라이드
    def dropEvent(self, event):
        source_list = event.source()
        item = source_list.currentItem()
        widget = source_list.itemWidget(item)

        drop_pos = event.pos()  # 드롭된 위치의 좌표
        item_at_pos = self.itemAt(drop_pos)  # 드롭된 위치에 해당하는 아이템

        if item_at_pos:
            # 아이템의 절반 위치를 기준으로 앞/뒤 삽입 결정
            item_widget = self.itemWidget(item_at_pos)
            item_rect = item_widget.geometry()
            item_center = item_rect.top() + item_rect.height() / 2  # 아이템의 중간 좌표

            # 드롭된 위치가 아이템의 상단 절반에 위치하면 해당 아이템 앞에 삽입
            if drop_pos.y() < item_center:
                row = self.row(item_at_pos)
            else:
                # 드롭된 위치가 하단 절반에 위치하면 해당 아이템 뒤에 삽입
                row = self.row(item_at_pos) + 1
        else:
            # 드롭된 위치에 아이템이 없다면, 마지막 아이템의 다음 위치
            row = self.count()

        if source_list is self: # 같은 블록내에서 드롭시
            new_item = QListWidgetItem(item.text())
            self.insertItem(row, new_item)
            self.setItemWidget(new_item, widget)

        else: # 다른 블록으로 드롭시
            todo_title = item.data(0)
            checked = widget.layout().itemAt(widget.layout().count() - 2).widget().isChecked()
            todo_reset_method = widget.layout().itemAt(0).widget().text()
            todo_reset_time = widget.layout().itemAt(1).widget().text()
            resetparam0 = widget.layout().itemAt(2).widget().text()
            resetparam1 = widget.layout().itemAt(3).widget().text()

            todo_reset_method, todo_reset_time, resetparam0, resetparam1 = util.formatting_data(todo_reset_method, todo_reset_time, resetparam0, resetparam1)
            self.add_todo(todo_title, todo_reset_method, todo_reset_time, resetparam0, resetparam1, checked, row)

        source_list.remove_todo(item)

        
    def update_param(self, item, reset_method, reset_time, param0, param1, checked):
        checkbox = QCheckBox()

        if checked:
            checkbox.setChecked(True)
        else:
            checkbox.setChecked(False)  # 초기 상태는 선택되지 않음
        
        # 디버그
        #checkbox.clicked.connect(lambda: print(self.todo_list.row(item))) # 체크시 해당 아이템이 리스트의 몇번째 아이템인지 출력
        #checkbox.clicked.connect(lambda: print(item.data(0))) # 체크시 해당 아이템의 이름 출력
        #checkbox.clicked.connect(lambda: print(checkbox.checkState())) # 체크시 해당 아이템의 체크상태 출력
        checkbox.clicked.connect(lambda: util.save_data(self.parent)) # 체크시 save 예정

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
                cycle_label = f'{next_reset_datetime.strftime('%H:%M')}  {difference.days}일 남음'
            else:
                cycle_label = f'{next_reset_datetime.strftime('%H:%M')}'

            param0label = QLabel(f'{param0}') # 초기화 주기 int
            param1label = QLabel(f'{param1}') # 기준 날짜 str
            param0label.setVisible(False)
            param1label.setVisible(False)

            timelabel = QLabel(cycle_label)
            
        item_layout.addWidget(methodlabel)
        item_layout.addWidget(timelabel)
        
        if 'param0label' not in locals():
            param0label = QLabel('-1')
            param0label.setVisible(False)
        if 'param1label' not in locals():
            param1label = QLabel('-1')
            param1label.setVisible(False)
        item_layout.addWidget(param0label)
        item_layout.addWidget(param1label)

        item_layout.addStretch(1)
        item_layout.addWidget(checkbox)
        item_layout.addWidget(remove_button)

        item_layout.setSpacing(8)

        self.setItemWidget(item, widget)


    def add_todo(self, todo_title, reset_method, reset_time, param0, param1, checked = 0, row = -1):
        # todo_title이 비어 있지 않으면 리스트에 추가
        if todo_title:
            if row == -1:
                row = self.count()
            else:
                row = row
            item = QListWidgetItem(todo_title)

            self.insertItem(row, item)
            self.update_param(item, reset_method, reset_time, param0, param1, checked)
            
        else:
            print('할 일을 입력해주세요.')


    def remove_todo(self, item):
        # 설정에 따라 삭제 전 한번 더 확인
        if self.parent.remove_todo_alert == 1:
            reply = QMessageBox.question(self, '삭제 확인', '삭제하시겠습니까?', QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)
            if reply == QMessageBox.Yes:
                row = self.row(item)
                self.takeItem(row)
                util.save_data(self.parent)
        else:
            row = self.row(item)
            self.takeItem(row)
            util.save_data(self.parent)
