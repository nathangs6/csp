from PyQt6.QtCore import Qt, QTimer, QTime, QDir, QModelIndex
from PyQt6.QtGui import QImage, QPixmap, QFileSystemModel
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QSlider,
    QScrollArea,
    QTextEdit,
    QTreeView
)
import fitz


class StaticLeafFileSystemModel(QFileSystemModel):
    def hasChildren(self, parent=QModelIndex()):
        if not parent.isValid():
            return super().hasChildren(parent)
        file_info = self.fileInfo(parent)

        if file_info.isDir():
            subdirs = QDir(file_info.absoluteFilePath()).entryList(
                QDir.Filter.AllDirs | QDir.Filter.NoDotAndDotDot
            )
            return len(subdirs) > 0
        return False


class DirectoryExplorer(QWidget):
    """
    Widget for displaying and allowing interaction with the user's file system.
    """
    def __init__(self):
        super().__init__()
        
        self.file_system_model = StaticLeafFileSystemModel()
        self.file_system_model.setRootPath(QDir.rootPath())

        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_system_model)
        self.tree_view.setRootIndex(self.file_system_model.index(QDir.rootPath()))

        self.open_lesson_button = QPushButton("Open Lesson")
        self.make_lesson_button = QPushButton("Make Lesson")

        layout = QVBoxLayout(self)
        self.directory_controls = QHBoxLayout()
        self.directory_controls.addWidget(self.make_lesson_button)
        self.directory_controls.addWidget(self.open_lesson_button)
        layout.addWidget(self.tree_view, 9)
        layout.addLayout(self.directory_controls, 1)
        self.setLayout(layout)

    def set_root_directory(self, folder):
        self.file_system_model.setRootPath(folder)
        self.tree_view.setRootIndex(self.file_system_model.index(folder))

    def get_folder_selection(self):
        current_index = self.tree_view.selectionModel().currentIndex()
        file_info = self.file_system_model.fileInfo(current_index)

        if file_info.isDir():
            folder_path = file_info.absoluteFilePath()
            return folder_path



class AudioPlayerWidget(QWidget):
    """
    Widget for playing audio.
    """
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)

        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setRange(0, 100)
        self.time_slider.sliderMoved.connect(self.set_position)
        self.current_time_label = QLabel("00:00")
        self.duration_label = QLabel("00:00")
        time_layout = QHBoxLayout()
        time_layout.addWidget(self.current_time_label)
        time_layout.addWidget(self.time_slider)
        time_layout.addWidget(self.duration_label)

        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.play_audio)
        self.play_button.setEnabled(False)

        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.pause_audio)
        self.pause_button.setEnabled(False)

        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.set_volume)

        layout.addLayout(time_layout, 15)
        layout.addWidget(self.play_button, 1)
        layout.addWidget(self.pause_button, 1)
        layout.addWidget(self.volume_slider, 3)

        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer()
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(self.volume_slider.value() / 100)

        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)
    
    def open_file(self, file_path):
        if file_path:
            self.media_player.setSource(file_path)
            self.play_button.setEnabled(True)
            self.pause_button.setEnabled(True)
            
    
    def play_audio(self):
        self.media_player.play()
    
    def pause_audio(self):
        self.media_player.pause()
    
    def set_volume(self, value):
        self.audio_output.setVolume(value / 100)

    def set_position(self, position):
        self.media_player.setPosition(position)
    
    def update_position(self, position):
        self.time_slider.setValue(position)
        self.current_time_label.setText(self.format_time(position))

    def update_duration(self, duration):
        self.time_slider.setRange(0, duration)
        self.duration_label.setText(self.format_time(duration))

    def format_time(self, ms):
        seconds = (ms//1000) % 60
        minutes = (ms//(1000*60)) % 60
        return f"{minutes:02}:{seconds:02}"


class PDFReaderWidget(QWidget):
    """
    Widget for viewing PDFs in a scrollable format.
    """
    def __init__(self):
        super().__init__()
        self.doc = None

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.pages_widget = QWidget()
        self.pages_layout = QVBoxLayout(self.pages_widget)
        self.scroll_area.setWidget(self.pages_widget)
        
        self.zoom_level = 1
        self.controls_layout = QHBoxLayout()
        self.zoom_in_button = QPushButton("Zoom In")
        self.zoom_in_button.clicked.connect(self.zoom_in)
        self.zoom_in_button.setEnabled(False)
        self.zoom_out_button = QPushButton("Zoom Out")
        self.zoom_out_button.clicked.connect(self.zoom_out)
        self.zoom_out_button.setEnabled(False)
        self.controls_layout.addWidget(self.zoom_in_button)
        self.controls_layout.addWidget(self.zoom_out_button)

        layout = QVBoxLayout(self)
        layout.addLayout(self.controls_layout, 1)
        layout.addWidget(self.scroll_area, 19)
        self.setLayout(layout)

    def zoom_in(self):
        self.zoom_level *= 1.2
        self.display_pages()

    def zoom_out(self):
        self.zoom_level /= 1.2
        self.display_pages()

    def open_file(self, file_path):
        if file_path:
            self.doc = fitz.open(file_path)
            self.display_pages()
            self.zoom_in_button.setEnabled(True)
            self.zoom_out_button.setEnabled(True)

    def display_pages(self):
        if not self.doc:
            return
        
        for i in reversed(range(self.pages_layout.count())):
            widget_to_remove = self.pages_layout.itemAt(i).widget()
            self.pages_layout.removeWidget(widget_to_remove)
            widget_to_remove.setParent(None)
        
        for page_num in range(len(self.doc)):
            page = self.doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(self.zoom_level, self.zoom_level))
            if pix.width == 0 or pix.height == 0:
                print(f"Empty pixmap for page {page_num}")

            image_format = QImage.Format.Format_RGBA8888 if pix.alpha else QImage.Format.Format_RGB888
            image = QImage(pix.samples, pix.width, pix.height, pix.stride, image_format)

            pixmap = QPixmap.fromImage(image)

            page_label = QLabel()
            page_label.setPixmap(pixmap)
            page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            page_label.adjustSize()
            self.pages_layout.addWidget(page_label)


class TextFileWidget(QWidget):
    """
    Widget for interacting with text.
    """
    def __init__(self, editable):
        super().__init__()

        self.editable = editable
        self.file_path = None

        layout = QVBoxLayout(self)
        self.text_edit = QTextEdit()
        
        if editable:
            self.save_button = QPushButton("Save File")
            self.save_button.clicked.connect(self.save_file)
            if not self.file_path:
                self.save_button.setEnabled(False)
            layout.addWidget(self.text_edit, 9)
            layout.addWidget(self.save_button, 1)
        else:
            self.text_edit.setReadOnly(True)
            layout.addWidget(self.text_edit)

        self.setLayout(layout)
    
    def open_file(self, file_path):
        if file_path:
            with open(file_path, 'r') as file:
                content = file.read()
                self.text_edit.setPlainText(content)
            self.file_path = file_path
            if self.editable:
                self.save_button.setEnabled(True)

    def save_file(self):
        if self.file_path:
            with open(self.file_path, 'w') as file:
                content = self.text_edit.toPlainText()
                file.write(content)


class StopwatchWithLog(QWidget):
    """
    Stopwatch widget with functionality to allow storage of times.
    """
    def __init__(self):
        super().__init__()

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.time = QTime(0, 0, 0)
        self.ms = 0

        self.time_display = QLabel("00:00.00")
        self.time_display.setStyleSheet("font-size: 36px;")
        self.time_display.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start)
        self.start_button.setEnabled(False)
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop)
        self.stop_button.setEnabled(False)
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset)
        self.reset_button.setEnabled(False)
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save)
        self.save_button.setEnabled(False)

        self.file_path = None
        self.log_label = QLabel("Log")
        self.log_label.setStyleSheet("font-size: 24px;")
        self.log_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.log = TextFileWidget(False)

        layout = QVBoxLayout(self)
        self.stopwatch_layout = QVBoxLayout()
        self.stopwatch_controls = QHBoxLayout()

        self.stopwatch_controls.addWidget(self.start_button)
        self.stopwatch_controls.addWidget(self.stop_button)
        self.stopwatch_controls.addWidget(self.reset_button)

        self.stopwatch_layout.addWidget(self.time_display)
        self.stopwatch_layout.addLayout(self.stopwatch_controls)
        self.stopwatch_layout.addWidget(self.save_button)

        layout.addLayout(self.stopwatch_layout)
        layout.addWidget(self.log_label)
        layout.addWidget(self.log)

        self.setLayout(layout)

    def start(self):
        self.timer.start(10)

    def stop(self):
        self.timer.stop()

    def reset(self):
        self.timer.stop()
        self.time.setHMS(0, 0, 0)
        self.ms = 0
        self.update_display()

    def update_time(self):
        self.ms += 10
        if self.ms >= 1000:
            self.ms -= 1000
            self.time = self.time.addSecs(1)
        self.update_display()
    
    def update_display(self):
        ms_display = str(self.ms)[:-1]
        self.time_display.setText(f"{self.time.toString("mm:ss")}.{ms_display:02}")

    def open_file(self, file_path):
        if file_path:
            self.file_path = file_path
            self.log.open_file(file_path)
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(True)
            self.reset_button.setEnabled(True)
            self.save_button.setEnabled(True)

    def save(self):
        if self.file_path:
            content = self.log.text_edit.toPlainText()
            num_lines = content.count('\n')
            ms_display = str(self.ms)[:-1]
            content = str(num_lines+1) + ": " + f"{self.time.toString("mm:ss")}.{ms_display:02}" + "\n" + content
            self.log.text_edit.setText(content)
            self.log.save_file()



def create_practice_layout():
    widgets = {}
    main_layout = QHBoxLayout()
    left_layout = QVBoxLayout()
    right_layout = QVBoxLayout()
    right_mid_layout = QHBoxLayout()

    main_layout.addLayout(left_layout, 2)
    main_layout.addLayout(right_layout, 18)
    
    widgets["directory_explorer"] = DirectoryExplorer()
    left_layout.addWidget(widgets["directory_explorer"], 5)
    widgets["timer"] = StopwatchWithLog()
    left_layout.addWidget(widgets["timer"], 5)

    widgets["pdf_reader"] = PDFReaderWidget()
    right_layout.addWidget(widgets["pdf_reader"], 13)
    right_layout.addLayout(right_mid_layout, 6)
    widgets["audio_player"] = AudioPlayerWidget()
    right_layout.addWidget(widgets["audio_player"], 1)

    widgets["story_text"] = TextFileWidget(True)
    right_mid_layout.addWidget(widgets["story_text"], 5)
    widgets["homework_text"] = TextFileWidget(True)
    right_mid_layout.addWidget(widgets["homework_text"], 5)

    return main_layout, widgets
