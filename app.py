import sys
import util
import config
import dialog
import drag_list
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QPushButton, QDialog, QAbstractItemView, QAction, QMainWindow, QScrollArea, QHBoxLayout, QLabel, QFrame, QToolButton, QMenu, QInputDialog, QMessageBox
from PyQt5.QtCore import QTimer, QTime, Qt, QEvent, QMimeData
from PyQt5.QtGui import QDrag


class BlockFrame(QFrame):
    def __init__(self, owner, block_index):
        super().__init__(owner)
        self.owner = owner
        self.block_index = block_index
        self.drag_start_pos = None
        self.setAcceptDrops(True)


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.owner.select_block(self.block_index)
            self.drag_start_pos = event.pos()
            event.accept()
            return
        super().mousePressEvent(event)


    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if self.drag_start_pos is None:
            return
        if (event.pos() - self.drag_start_pos).manhattanLength() < QApplication.startDragDistance():
            return

        self.owner.start_block_drag(self.block_index)
        self.drag_start_pos = None
        event.accept()


    def mouseReleaseEvent(self, event):
        self.drag_start_pos = None
        super().mouseReleaseEvent(event)


    def dragEnterEvent(self, event):
        if event.mimeData().hasText() and event.mimeData().text().startswith('block:'):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)


    def dropEvent(self, event):
        if not event.mimeData().hasText():
            super().dropEvent(event)
            return

        mime_text = event.mimeData().text()
        if not mime_text.startswith('block:'):
            super().dropEvent(event)
            return

        source_index = int(mime_text.split(':', 1)[1])
        self.owner.move_block(source_index, self.block_index)
        event.acceptProposedAction()


class BlockSurfaceWidget(QWidget):
    def __init__(self, owner, block_index):
        super().__init__(owner)
        self.owner = owner
        self.block_index = block_index
        self.drag_start_pos = None


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.owner.select_block(self.block_index)
            self.drag_start_pos = event.pos()
            event.accept()
            return
        super().mousePressEvent(event)


    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if self.drag_start_pos is None:
            return
        if (event.pos() - self.drag_start_pos).manhattanLength() < QApplication.startDragDistance():
            return

        self.owner.start_block_drag(self.block_index)
        self.drag_start_pos = None
        event.accept()


    def mouseReleaseEvent(self, event):
        self.drag_start_pos = None
        super().mouseReleaseEvent(event)


class BlockTitleLabel(QLabel):
    def __init__(self, owner, block_index, text):
        super().__init__(text, owner)
        self.owner = owner
        self.block_index = block_index
        self.drag_start_pos = None


    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.owner.select_block(self.block_index)
            self.drag_start_pos = event.pos()
            event.accept()
            return
        super().mousePressEvent(event)


    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
        if self.drag_start_pos is None:
            return
        if (event.pos() - self.drag_start_pos).manhattanLength() < QApplication.startDragDistance():
            return

        self.owner.start_block_drag(self.block_index)
        self.drag_start_pos = None
        event.accept()


    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.owner.select_block(self.block_index)
            self.drag_start_pos = None
            self.owner.open_rename_block_dialog(self.block_index)
            event.accept()
            return
        super().mouseDoubleClickEvent(event)


    def mouseReleaseEvent(self, event):
        self.drag_start_pos = None
        super().mouseReleaseEvent(event)


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        config.read_config(self)
        util.load_block_data(self)
        self.block_clipboard = None
        self.selected_block_index = 0
        self.block_frames = {}
        self.main_window_init_ui()
        util.load_data(self)
        self.auto_save()


    @util.elapsed_time_decorator
    def main_window_init_ui(self):
        menubar = self.menuBar()
        menubar.setNativeMenuBar(False)
        filemenu = menubar.addMenu('&File')

        exit_action = QAction('종료', self)
        exit_action.setShortcut('Ctrl+W')
        exit_action.triggered.connect(self.close)
        filemenu.addAction(exit_action)

        configmenu = menubar.addMenu('&Config')
        config_action = QAction('환경 설정', self)
        config_action.triggered.connect(lambda: config.ConfigDialog(self).exec_())
        configmenu.addAction(config_action)

        copy_block_action = QAction(self)
        copy_block_action.setShortcut('Ctrl+C')
        copy_block_action.setShortcutContext(Qt.WindowShortcut)
        copy_block_action.triggered.connect(self.copy_selected_block)
        self.addAction(copy_block_action)

        paste_block_action = QAction(self)
        paste_block_action.setShortcut('Ctrl+V')
        paste_block_action.setShortcutContext(Qt.WindowShortcut)
        paste_block_action.triggered.connect(self.paste_selected_block)
        self.addAction(paste_block_action)

        reset_block_action = QAction(self)
        reset_block_action.setShortcut('Delete')
        reset_block_action.setShortcutContext(Qt.WindowShortcut)
        reset_block_action.triggered.connect(self.reset_selected_block)
        self.addAction(reset_block_action)

        self.setWindowTitle('일정 관리자')
        self.resize(self.window_width, self.window_height)

        self.scroll_area = QScrollArea(self)
        self.setCentralWidget(self.scroll_area)

        self.show()
        app_frame = self.frameGeometry()
        center_pos = QApplication.screenAt(self.pos()).availableGeometry().center()
        app_frame.moveCenter(center_pos)
        self.move(app_frame.topLeft())

        self.todo_list = {}
        for i in range(self.grid_row):
            for j in range(self.grid_col):
                list_index = i * self.grid_col + j
                todo_list = drag_list.DragList(self)
                todo_list.block_index = list_index
                todo_list.setDragDropMode(QAbstractItemView.InternalMove)
                self.todo_list[f'list{list_index}'] = todo_list

        self.show_grid()


    def eventFilter(self, obj, event):
        interaction = obj.property('block_interaction')
        block_index = obj.property('block_index')

        if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            if interaction == 'select' and block_index is not None:
                self.select_block(int(block_index))
            elif interaction == 'clear':
                self.clear_block_selection()

        return super().eventFilter(obj, event)


    def bind_block_interaction(self, widget, interaction, block_index = None):
        widget.setProperty('block_interaction', interaction)
        if block_index is not None:
            widget.setProperty('block_index', block_index)
        widget.installEventFilter(self)


    def select_block(self, block_index):
        total_blocks = self.grid_row * self.grid_col
        if total_blocks == 0:
            self.selected_block_index = None
            return

        self.clear_todo_item_selection()
        block_index = max(0, min(block_index, total_blocks - 1))
        self.selected_block_index = block_index
        self.refresh_block_selection()


    def clear_block_selection(self):
        self.clear_todo_item_selection()
        self.selected_block_index = None
        self.refresh_block_selection()


    def clear_todo_item_selection(self, except_list = None):
        for todo_list in self.todo_list.values():
            if todo_list is except_list:
                continue
            todo_list.clearSelection()
            todo_list.setCurrentItem(None)


    def refresh_block_selection(self):
        for block_index, block_frame in self.block_frames.items():
            is_selected = block_index == self.selected_block_index
            block_frame.setProperty('selected', is_selected)
            block_frame.style().unpolish(block_frame)
            block_frame.style().polish(block_frame)
            block_frame.update()


    def get_block_name(self, block_index):
        util.ensure_block_data(self)
        return self.block_data[block_index]['name']


    def set_block_name(self, block_index, name):
        name = name.strip()
        if not name:
            return

        util.ensure_block_data(self)
        self.block_data[block_index]['name'] = name
        util.save_block_data(self)


    def get_block_snapshot(self, block_index):
        todo_list = self.todo_list[f'list{block_index}']
        return {
            'name': self.get_block_name(block_index),
            'todos': todo_list.get_todo_payloads(),
        }


    def apply_block_snapshot(self, block_index, snapshot):
        self.block_data[block_index]['name'] = snapshot['name']
        self.todo_list[f'list{block_index}'].load_todo_payloads(snapshot['todos'])


    def start_block_drag(self, block_index):
        source_frame = self.block_frames.get(block_index)
        if source_frame is None:
            return

        drag = QDrag(source_frame)
        mime_data = QMimeData()
        mime_data.setText(f'block:{block_index}')
        drag.setMimeData(mime_data)
        drag.setPixmap(source_frame.grab())
        drag.exec_(Qt.MoveAction)


    def move_block(self, source_index, target_index):
        if source_index == target_index:
            return

        source_snapshot = self.get_block_snapshot(source_index)
        target_snapshot = self.get_block_snapshot(target_index)

        self.apply_block_snapshot(source_index, target_snapshot)
        self.apply_block_snapshot(target_index, source_snapshot)
        util.save_block_data(self)
        util.save_data(self)
        self.select_block(target_index)
        self.show_grid()


    def copy_block(self, block_index):
        self.select_block(block_index)
        self.block_clipboard = self.get_block_snapshot(block_index)


    def copy_selected_block(self):
        if self.selected_block_index is None:
            return
        self.copy_block(self.selected_block_index)


    def paste_block(self, block_index):
        if self.block_clipboard is None:
            return

        self.select_block(block_index)
        todo_list = self.todo_list[f'list{block_index}']
        if todo_list.count() > 0:
            reply = QMessageBox.question(
                self,
                '블럭 붙여넣기',
                '현재 블럭 내용을 덮어쓸까요?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply != QMessageBox.Yes:
                return

        self.set_block_name(block_index, self.block_clipboard['name'])
        todo_list.load_todo_payloads(self.block_clipboard['todos'])
        util.save_data(self)
        self.show_grid()


    def paste_selected_block(self):
        if self.selected_block_index is None:
            return
        self.paste_block(self.selected_block_index)


    def reset_selected_block(self):
        if self.selected_block_index is None:
            return
        self.reset_block(self.selected_block_index)


    def reset_block(self, block_index):
        self.select_block(block_index)
        reply = QMessageBox.question(
            self,
            '블럭 초기화',
            '블럭 이름과 일정을 모두 초기화할까요?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self.set_block_name(block_index, util.default_block_name(block_index))
        self.todo_list[f'list{block_index}'].clear()
        util.save_data(self)
        self.show_grid()


    def open_rename_block_dialog(self, block_index):
        self.select_block(block_index)
        current_name = self.get_block_name(block_index)
        text, ok = QInputDialog.getText(self, '블럭 이름', '블럭 이름을 입력하세요.', text = current_name)
        if ok and text.strip():
            self.set_block_name(block_index, text)
            self.show_grid()


    def create_block_menu_button(self, row, col, block_index):
        button = QToolButton(self)
        button.setText('...')
        button.setPopupMode(QToolButton.InstantPopup)
        button.setToolTip('블럭 메뉴')
        self.bind_block_interaction(button, 'select', block_index)

        menu = QMenu(button)

        add_action = menu.addAction('일정 추가')
        add_action.triggered.connect(lambda _, current_row = row, current_col = col: self.open_add_todo_dialog(current_row, current_col))

        rename_action = menu.addAction('블럭 이름 변경')
        rename_action.triggered.connect(lambda _, current_index = block_index: self.open_rename_block_dialog(current_index))

        copy_action = menu.addAction('블럭 복사')
        copy_action.triggered.connect(lambda _, current_index = block_index: self.copy_block(current_index))

        paste_action = menu.addAction('블럭 붙여넣기')
        paste_action.triggered.connect(lambda _, current_index = block_index: self.paste_block(current_index))

        reset_action = menu.addAction('블럭 초기화')
        reset_action.triggered.connect(lambda _, current_index = block_index: self.reset_block(current_index))

        menu.aboutToShow.connect(lambda current_action = paste_action: current_action.setEnabled(self.block_clipboard is not None))
        button.setMenu(menu)
        return button


    def open_add_todo_dialog(self, row, col):
        block_index = row * self.grid_col + col

        add_todo_dialog = dialog.AddTodoDialog(self)
        if add_todo_dialog.exec_() == QDialog.Accepted:
            todo_title = add_todo_dialog.title_input.text()
            todo_reset_method, todo_reset_time, resetparam0, resetparam1 = add_todo_dialog.get_data()
            todo_list = self.todo_list[f'list{block_index}']
            todo_list.add_todo(todo_title, todo_reset_method, todo_reset_time, resetparam0, resetparam1)
            util.save_data(self)


    def build_block_frame(self, row, col, block_index):
        block_frame = BlockFrame(self, block_index)
        block_frame.setObjectName('todoBlock')
        block_frame.setStyleSheet(
            'QFrame#todoBlock {'
            'border: 1px solid #b8c4d6;'
            'border-radius: 10px;'
            'background-color: #f7fbff;'
            '}'
            'QFrame#todoBlock[selected="true"] {'
            'border: 2px solid #2b6cb0;'
            'background-color: #eaf4ff;'
            '}'
            'QLabel#blockTitle {'
            'font-size: 14px;'
            'font-weight: bold;'
            'color: #23364d;'
            '}'
        )
        block_layout = QVBoxLayout()
        block_layout.setSpacing(8)
        block_layout.setContentsMargins(12, 12, 12, 12)

        header_widget = BlockSurfaceWidget(self, block_index)
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(6)

        block_title = BlockTitleLabel(self, block_index, self.get_block_name(block_index))
        block_title.setObjectName('blockTitle')
        header_layout.addWidget(block_title)
        header_layout.addStretch(1)
        header_layout.addWidget(self.create_block_menu_button(row, col, block_index))
        header_widget.setLayout(header_layout)
        block_layout.addWidget(header_widget)

        body_widget = BlockSurfaceWidget(self, block_index)
        body_layout = QVBoxLayout()
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(8)

        todo_list = self.todo_list[f'list{block_index}']
        todo_list.block_index = block_index
        body_layout.addWidget(todo_list)

        add_button = QPushButton('일정 추가', self)
        add_button.clicked.connect(lambda _, current_row = row, current_col = col: self.open_add_todo_dialog(current_row, current_col))
        self.bind_block_interaction(add_button, 'clear')
        body_layout.addWidget(add_button)

        body_widget.setLayout(body_layout)
        block_layout.addWidget(body_widget)

        block_frame.setLayout(block_layout)
        return block_frame


    def show_grid(self):
        central_widget = QWidget()
        util.ensure_block_data(self)
        self.bind_block_interaction(central_widget, 'clear')
        self.bind_block_interaction(self.scroll_area.viewport(), 'clear')

        total_blocks = self.grid_row * self.grid_col
        if total_blocks == 0:
            self.selected_block_index = None
        elif self.selected_block_index is None or self.selected_block_index >= total_blocks:
            self.selected_block_index = 0

        central_widget.main_layout = QGridLayout()
        central_widget.main_layout.setContentsMargins(12, 12, 12, 12)
        central_widget.main_layout.setSpacing(12)

        self.block_frames = {}
        for i in range(self.grid_row):
            central_widget.main_layout.setRowMinimumHeight(i, 200)
            for j in range(self.grid_col):
                central_widget.main_layout.setColumnMinimumWidth(j, 305)
                block_index = i * self.grid_col + j
                block_frame = self.build_block_frame(i, j, block_index)
                self.block_frames[block_index] = block_frame
                central_widget.main_layout.addWidget(block_frame, i, j)

        central_widget.setLayout(central_widget.main_layout)
        self.scroll_area.setWidget(central_widget)
        self.scroll_area.setWidgetResizable(True)
        self.refresh_block_selection()


    def resizeEvent(self, event):
        self.config['Settings']['window_width'] = str(self.width())
        self.config['Settings']['window_height'] = str(self.height())
        super().resizeEvent(event)


    def auto_save(self):
        now = QTime.currentTime()
        seconds_until_next_minute = 60 - now.second()
        QTimer.singleShot(seconds_until_next_minute * 1000, lambda: self.run_auto_save())


    def run_auto_save(self):
        util.save_data(self)
        self.auto_save()


    def closeEvent(self, event):
        util.save_block_data(self)
        util.save_data(self)


app = QApplication(sys.argv)
window = MyApp()
sys.exit(app.exec_())
