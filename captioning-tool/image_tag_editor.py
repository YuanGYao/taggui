from PySide6.QtCore import QPersistentModelIndex, QStringListModel, Qt, Slot
from PySide6.QtWidgets import (QAbstractItemView, QCompleter, QDockWidget,
                               QLineEdit,
                               QListView, QVBoxLayout,
                               QWidget)

from image_list import ImageListModel
from tag_counter_model import TagCounterModel


class ImageTagList(QListView):
    def __init__(self, model: QStringListModel, parent):
        super().__init__(parent)
        self.model = model
        self.setModel(self.model)
        self.setSpacing(4)
        self.setWordWrap(True)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            selected_indexes = [QPersistentModelIndex(index) for index
                                in self.selectedIndexes()]
            for index in selected_indexes:
                self.model.removeRow(index.row())
            # Select the next tag in the list, or the last tag if there is no
            # next tag.
            index_to_select = (
                self.model.index(self.currentIndex().row() + 1, 0)
                if self.currentIndex().row() + 1 < self.model.rowCount()
                else self.model.index(self.model.rowCount() - 1, 0))
            self.setCurrentIndex(index_to_select)
        else:
            super().keyPressEvent(event)


class ImageTagEditor(QDockWidget):
    def __init__(self, tag_counter_model: TagCounterModel,
                 image_list_model: ImageListModel, parent):
        super().__init__(parent)
        self.tag_counter_model = tag_counter_model
        self.image_list_model = image_list_model

        self.setObjectName('image_tag_editor')
        self.setWindowTitle('Tags')
        self.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.input_box = QLineEdit(self)
        completer = QCompleter(self.tag_counter_model, self)
        completer.activated.connect(self.add_tag, Qt.QueuedConnection)
        self.input_box.setCompleter(completer)
        self.input_box.setStyleSheet('padding: 8px;')
        self.input_box.setPlaceholderText('Add tag')
        self.input_box.returnPressed.connect(self.add_tag, Qt.QueuedConnection)

        self.image_index = None
        self.model = QStringListModel(self)
        self.model.dataChanged.connect(self.update_image_list_model)
        self.model.rowsRemoved.connect(self.update_image_list_model)
        self.image_tag_list = ImageTagList(self.model, self)

        container = QWidget(self)
        layout = QVBoxLayout(container)
        layout.addWidget(self.input_box)
        layout.addWidget(self.image_tag_list)
        self.setWidget(container)

    def load_tags(self, index: QPersistentModelIndex, tags: list[str]):
        self.image_index = index
        self.model.setStringList(tags)

    @Slot()
    def add_tag(self):
        tag = self.input_box.text()
        if not tag:
            return
        self.model.insertRow(self.model.rowCount())
        self.model.setData(self.model.index(self.model.rowCount() - 1), tag)
        self.input_box.clear()
        self.image_tag_list.scrollToBottom()

    @Slot()
    def update_image_list_model(self):
        self.image_list_model.update_tags(self.image_index,
                                          self.model.stringList())
