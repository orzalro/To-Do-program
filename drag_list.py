import util
import dialog as dia
from PyQt5.QtWidgets import QWidget, QPushButton, QListWidget, QCheckBox, QListWidgetItem, QHBoxLayout
from PyQt5.QtWidgets import QLabel, QAbstractItemView, QMessageBox, QDialog
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QBrush, QColor
from datetime import datetime, timedelta

class DragList(QListWidget):
    def __init__(self, parent = ...):
        super().__init__(parent)
        self.parent = parent
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)  # 1초마다 update_time 실행
        self.timer.start(1000)

        self.itemDoubleClicked.connect(lambda: self.open_edit_todo_dialog(self.currentItem()))
    

    def open_edit_todo_dialog(self, item):
        widget = self.itemWidget(item)
        todo_reset_method = widget.findChild(QLabel, 'methodlabel').text()
        todo_reset_time = widget.findChild(QLabel, 'timelabel').text()
        resetparam0 = widget.findChild(QLabel, 'param0label').text()
        resetparam1 = widget.findChild(QLabel, 'param1label').text()
        todo_reset_method, todo_reset_time, resetparam0, resetparam1 = util.formatting_data(todo_reset_method, todo_reset_time, resetparam0, resetparam1)
        dialog = dia.AddTodoDialog(self.parent, item.text(), todo_reset_method, todo_reset_time, resetparam0, resetparam1)
        if dialog.exec_() == QDialog.Accepted:
            # 다이얼로그에서 받은 데이터
            item.setData(0, dialog.title_input.text())
            todo_reset_method, todo_reset_time, resetparam0, resetparam1 = dialog.get_data()
            self.update_param(item, todo_reset_method, todo_reset_time, resetparam0, resetparam1, checked = 0)

            util.save_data(self.parent)


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

        todo_title = item.data(0)
        checked = widget.findChild(QCheckBox, 'checkbox').isChecked()
        todo_reset_method = widget.findChild(QLabel, 'methodlabel').text()
        todo_reset_time = widget.findChild(QLabel, 'timelabel').text()
        resetparam0 = widget.findChild(QLabel, 'param0label').text()
        resetparam1 = widget.findChild(QLabel, 'param1label').text()

        todo_reset_method, todo_reset_time, resetparam0, resetparam1 = util.formatting_data(todo_reset_method, todo_reset_time, resetparam0, resetparam1)
        self.add_todo(todo_title, todo_reset_method, todo_reset_time, resetparam0, resetparam1, checked, row)

        row = source_list.row(item)
        source_list.takeItem(row)
        util.save_data(self.parent)


    def update_time(self):
        for i in range(self.count()):
            item = self.item(i)
            widget = self.itemWidget(item)
            next_reset_datetime = item.data(Qt.UserRole)
            difference = next_reset_datetime - datetime.now()
            seconds_left = round(difference.total_seconds())
            days = seconds_left // 86400
            seconds_left %= 86400
            hours = seconds_left // 3600
            seconds_left %= 3600
            minutes = seconds_left // 60
            seconds = seconds_left % 60
            widget.findChild(QLabel, 'next_reset_time_label').setText(f'{days:>2} 일, {hours}:{minutes}:{seconds} 남음')

            # 남은 기한 표시
            if self.parent.show_remaining_time == 0:
                widget.findChild(QLabel, 'textlabel').setVisible(True)
                widget.findChild(QLabel, 'next_reset_time_label').setVisible(False)
            else:
                widget.findChild(QLabel, 'textlabel').setVisible(False)
                widget.findChild(QLabel, 'next_reset_time_label').setVisible(True)

            # 시간초과 경고
            warn_time = int(self.parent.timeout_warn) if int(self.parent.timeout_warn) != -1 else 0
            if warn_time * 86400 > round(difference.total_seconds()) and widget.findChild(QCheckBox, 'checkbox').isChecked() == 0:
                item.setBackground(QColor(255, 0, 0, 64))
            else:
                item.setBackground(QBrush())

        
    def update_param(self, item, reset_method, reset_time, param0, param1, checked):
        checkbox = QCheckBox()
        if checked: checkbox.setChecked(True)
        else: checkbox.setChecked(False)  # 초기 상태는 선택되지 않음
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
            next_reset_datetime = util.daily_reset(reset_time, self.parent.lastchecktime, 1)
            reset_time = f'{reset_time // 60:02}:{reset_time % 60:02}'
            timelabel = QLabel(reset_time)
            textlabel = QLabel(f'일간 {reset_time}')
        
        elif reset_method == 1:
            methodlabel = QLabel('주간')
            weekday_dict = {0: '월요일', 1: '화요일', 2: '수요일', 3: '목요일', 4: '금요일', 5: '토요일', 6: '일요일'}
            param0label = QLabel(str(param0))
            next_reset_datetime = util.weekly_reset(reset_time, self.parent.lastchecktime, param0, 1)
            next_reset_weekday = next_reset_datetime.weekday()
            reset_time = f'{reset_time // 60:02}:{reset_time % 60:02}'
            timelabel = QLabel(reset_time)
            textlabel = QLabel(f'주간 {reset_time}  {weekday_dict[next_reset_weekday]}')
        
        elif reset_method == 2:
            methodlabel = QLabel('월간')
            param0label = QLabel(f'{param0}일')
            next_reset_datetime = util.monthly_reset(reset_time, self.parent.lastchecktime, param0, 1)
            reset_time = f'{reset_time // 60:02}:{reset_time % 60:02}'
            timelabel = QLabel(reset_time)
            textlabel = QLabel(f'월간 {reset_time}  {param0}일')
        
        elif reset_method == 3:
            methodlabel = QLabel('주기')
            next_reset_datetime = datetime.strptime(param1, '%Y-%m-%d %H:%M:%S') + timedelta(minutes = int(param0))
            cycle_label = f'{next_reset_datetime.strftime('%H:%M  %#m월 %#d일')}'
            param0label = QLabel(f'{param0}') # 초기화 주기 int
            param1label = QLabel(f'{param1}') # 기준 날짜 str
            timelabel = QLabel()
            textlabel = QLabel(f'주기 {cycle_label}')

        methodlabel.setObjectName('methodlabel')
        methodlabel.setVisible(False)
        item_layout.addWidget(methodlabel)

        timelabel.setObjectName('timelabel')
        timelabel.setVisible(False)
        item_layout.addWidget(timelabel)

        if 'param0label' not in locals():param0label = QLabel()
        param0label.setObjectName('param0label')
        param0label.setVisible(False)
        item_layout.addWidget(param0label)

        if 'param1label' not in locals():param1label = QLabel()
        param1label.setObjectName('param1label')
        param1label.setVisible(False)
        item_layout.addWidget(param1label)

        textlabel.setObjectName('textlabel') # 일정 설정 표시용 QLabel
        item_layout.addWidget(textlabel)

        next_reset_time_label = QLabel() # 남은 시간 표시용 QLabel
        next_reset_time_label.setObjectName('next_reset_time_label')
        item_layout.addWidget(next_reset_time_label) 

        item_layout.addStretch(1)

        checkbox.setObjectName('checkbox')
        item_layout.addWidget(checkbox)
        
        remove_button.setObjectName('remove_button')
        item_layout.addWidget(remove_button)

        item_layout.setSpacing(8)

        self.setItemWidget(item, widget)

        item.setData(Qt.UserRole, next_reset_datetime)
        self.update_time()


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